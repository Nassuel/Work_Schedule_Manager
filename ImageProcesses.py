import os
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt

from typing import Any, List

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = os.path.join("D:\\","Repos", "Libraries","Tesseract-OCR","tesseract.exe")

class ImageReaderAndParser():
    # Read image from which text needs to be extracted
    
    def __init__(self, img_filename_path: str, show_detect_jpg=False, verbose=False) -> None:
        # super().__init__() # Is this Java, wth? Lmao
        self.verbose = verbose
        self.file = img_filename_path
        self.show_detected_text_pic = show_detect_jpg
        self.file_name = self.file.split('\\')[-1].split('.')[0]
        self.img = cv2.imread(self.file)

    def _image_info(self) -> None:
        height, width, channels = self.img.shape
        if self.verbose: print(height, width, channels)
        cv2.imshow('image', self._image_cropper())
        # print(self.y, self.h, self.x, self.w)
        cv2.waitKey(0)
        return

    def _image_cropper(self, save_in_file, aug_x=0, aug_y=0) -> Any:
        """
        Crops the work schedule table on the image

        Further work: Make the cropping more dynamic as it's pretty hardcoded atm
        """
        # file = r'D:\\Repos\\Create_Calendar_Event_From_Pic\\142021-1102021_schedule.jpg'
        # img = cv2.imread(file)
        set_width = 2426
        set_height = 1286
        img = cv2.resize(self.img, dsize=(set_width, set_height), interpolation=cv2.INTER_AREA)
        height, width, channels = img.shape
        # print('Resized', height, width, channels)

        self.y = int(height * 615/1286)
        self.h = int(height * 560/1286) # 560

        self.x = int(width * 50 /2426)
        self.w = int(width * 1325/2426) # 2290 ((width * 2120) / width) * 5/8
        crop_img = img[self.y+aug_y:self.y+self.h, self.x+aug_x:self.x+self.w].copy()

        if save_in_file is not None:
            cv2.imwrite(save_in_file, crop_img)

        return crop_img
    
    def chop_image(self, img) -> List[Any]:
        """
        Chops image into pieces to have an easier time when parsing through each row of the schedule table of the image

        Further work:
        """
        # img = self._image_cropper()
        height, width, channels = img.shape
        slice_height = int(height / 8)
        changing_y = 0
        img_slices = []

        # print(changing_y, self.h)
        while changing_y <= height - slice_height:
            img_slices.append({'img':img[changing_y:changing_y+slice_height+10, 0:width].copy(), 'changing_y': changing_y})
            changing_y += slice_height

        return img_slices

    def detect_table(self, img):
        """        
        TODO: Make it work. Doesn't quite detect the table in the picture 😭
        """
        # Convert the image to gray scale 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Performing OTSU threshold 
        ret, thresh1 = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

        # Specify structure shape and kernel size.  
        # Kernel size increases or decreases the area  
        # of the rectangle to be detected. 
        # A smaller value like (10, 10) will detect  
        # each word instead of a sentence. 
        # rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        kernel = np.ones((50,50),np.uint8)
        
        # Appplying dilation on the threshold image 
        dilation = cv2.dilate(thresh1, kernel, iterations = 1)
        
        # Finding contours 
        contours, hierarchy = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        
        # Creating a copy of image 
        im2 = img.copy()

        sums = []
        coordinates = []
        # Need to get the biggest countured rectangle on the image and then getting its coordinates
        for index, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt)

            # return im2[y+90:y+h-80, x:x+w-170].copy()
            sums.append(x+y+w+h)
            coordinates.append((x,y,w,h))

        x, y, w, h = coordinates[sums.index(max(sums))]
        return im2[y:y+h, x:x+w].copy()

    def image_processor(self, img, img_slice_index, unique_divider='|||') -> None:
        """
        Pass through an slice of an image and its index, appending to the same file.
        """
        # Convert the image to gray scale 
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Performing OTSU threshold 
        ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

        # Specify structure shape and kernel size.  
        # Kernel size increases or decreases the area  
        # of the rectangle to be detected. 
        # A smaller value like (10, 10) will detect  
        # each word instead of a sentence. 
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        
        # Appplying dilation on the threshold image 
        dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
        
        # Finding contours 
        contours, hierarchy = cv2.findContours(dilation,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
        
        # Creating a copy of image 
        im2 = img.copy()
        
        txt_filename = os.path.join(".","Recognized_Texts","recognized_{0}.txt".format(self.file_name))
        if img_slice_index == 0:
            # A text file is created and flushed
            file = open(txt_filename, "w+")
            file.write("") 
            file.close()
        else:
            # File has been created already, so just append to it
            pass
        
        # Looping through the identified contours 
        # Then rectangular part is cropped and passed on 
        # to pytesseract for extracting text from it 
        # Extracted text is then written into the text file 
        # Open the file in append mode 
        file = open(txt_filename, "a")
        for cnt in contours: 
            x, y, w, h = cv2.boundingRect(cnt) 
            
            # Drawing a rectangle on copied image
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if self.show_detected_text_pic: cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
            
            # Cropping the text block for giving input to OCR 
            cropped = im2[y:y + h, x:x + w]
            
            # Apply OCR on the cropped image
            text = pytesseract.image_to_string(cropped)
            
            # Appending the text into file 
            file.write(text.strip()) 
            file.write("\n")

        # Writing a divisor into the file
        file.write(unique_divider)
        file.write("\n")
        file.close()

        if self.show_detected_text_pic:
            plt.imshow(img)
            cv2.namedWindow('detecttable_{0}'.format(img_slice_index), cv2.WINDOW_NORMAL)
            cv2.imwrite('./Slices_Output/detecttable_{0}.jpg'.format(img_slice_index), img)
            
        return

def main():
    file_location = os.path.join("Pictures", "2-1-2021_2-7-2021_schedule.jpg")
    pre_file = os.path.join("Pictures", "pre.png")
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    # detected_table_img = img_rd_prsr.detect_table(img_rd_prsr.img)
    array = img_rd_prsr.chop_image(img_rd_prsr._image_cropper(pre_file, aug_y=5))
    # cv2.imshow('image', img_rd_prsr._image_cropper())
    # cv2.waitKey(0)
    # print(array)
    # for index, dict in enumerate(array):
    #     cv2.imshow('image', dict['img'])
    #     cv2.waitKey(0)
        # img_rd_prsr.image_processor(dict['img'], index)

    
        
if __name__ == '__main__':
    main()