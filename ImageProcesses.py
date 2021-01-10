import cv2
import pytesseract
import matplotlib.pyplot as plt

from typing import Any, List

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

class ImageReaderAndParser(object):
    # Read image from which text needs to be extracted
    
    def __init__(self, img_filename_path: str, show_detect_jpg=False, verbose=False) -> None:
        # super().__init__() # Is this Java, wth? Lmao
        self.verbose = verbose
        self.file = img_filename_path
        self.show_detected_text_pic = show_detect_jpg
        self.file_name = self.file.split('/')[-1].split('.')[0]
        self.output_textfile_name = "./Recognized_Texts/recognized_{0}.txt".format(self.file_name)
        self.img = cv2.imread(self.file)

    def _image_info(self) -> None:
        height, width, channels = self.img.shape
        if self.verbose: print(height, width, channels)
        cv2.imshow('image', self._image_cropper())
        cv2.waitKey(0)
        return

    def _image_cropper(self) -> Any:
        """
        Crops the work schedule table on the image

        Further work: Make the cropping more dynamic as it's pretty hardcoded atm
        """
        # file = r'D:\\Repos\\Create_Calendar_Event_From_Pic\\142021-1102021_schedule.jpg'
        # img = cv2.imread(file)
        height, width, channels = self.img.shape
        self.y = int(height * 630 / height)
        self.h = int(height * 560 / height) # 560

        self.x = int(width * 100 / width)
        self.w = int(((width * 2120) / width) * 5/8) # 2290
        crop_img = self.img[self.y:self.y+self.h, self.x:self.x+self.w].copy()

        return crop_img
    
    def chop_image(self) -> List[Any]:
        """
        Chops image into pieces to have an easier time when parsing through each row of the schedule table of the image

        Further work:
        """
        img = self._image_cropper()
        slice_height = int(self.h / 8)
        changing_y = self.y
        img_slices = []

        print(changing_y, self.h)
        while changing_y <= self.h + self.y - slice_height:
            img_slices.append({'img':self.img[changing_y:changing_y+slice_height, self.x:self.x+self.w].copy(), 
                                'changing_y': changing_y})
            changing_y += slice_height

        return img_slices

    def image_processor(self, img, img_slice_index) -> None:
        """
        Pass through an slice of an image and its index for a file to be created.
        
        Further work: Could be reworked to append to the same file and have a unique divider in between slices
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
        
        # A text file is created and flushed
        txt_filename = "./Recognized_Texts/recognized_{0}_{1}.txt".format(self.file_name, str(img_slice_index))
        file = open(txt_filename, "w+") 
        file.write("") 
        file.close() 
        
        # Looping through the identified contours 
        # Then rectangular part is cropped and passed on 
        # to pytesseract for extracting text from it 
        # Extracted text is then written into the text file 
        for cnt in contours: 
            x, y, w, h = cv2.boundingRect(cnt) 
            
            # Drawing a rectangle on copied image
            rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
            if self.show_detected_text_pic: cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
            
            # Cropping the text block for giving input to OCR 
            cropped = im2[y:y + h, x:x + w]
            
            # Open the file in append mode 
            file = open(txt_filename, "a")
            
            # Apply OCR on the cropped image
            text = pytesseract.image_to_string(cropped)
            
            # Appending the text into file 
            file.write(text.strip()) 
            file.write("\n") 
            
            # Close the file 
            file.close()

        if self.show_detected_text_pic:
            plt.imshow(img)
            cv2.namedWindow('detecttable_{0}'.format(img_slice_index), cv2.WINDOW_NORMAL)
            cv2.imwrite('./Slices_Output/detecttable_{0}.jpg'.format(img_slice_index), img)
            
        return


def main():
    file_location = './Pictures/1-11-2021_1-17-2021_schedule.jpg'
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    # cv2.imshow('image', img_rd_prsr._image_cropper())
    # cv2.waitKey(0)
    array = img_rd_prsr.chop_image()
    print(array)
    for index, dict in enumerate(array):
        img_rd_prsr.image_processor(dict['img'], index)

    
        
if __name__ == '__main__':
    main()