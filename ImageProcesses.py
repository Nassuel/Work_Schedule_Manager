import os
import cv2
import pytesseract
import numpy as np
import matplotlib.pyplot as plt

from typing import Any, List

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = os.path.join("D:\\","Repos", "Libraries","Tesseract-OCR","tesseract.exe")

class ImageReaderAndParser():
    # Read and parse image from which text needs to be extracted
    
    def __init__(self, img_filename_path: str, show_detect_jpg=False, verbose=False) -> None:
        self.verbose = verbose
        self.show_detected_text_pic = show_detect_jpg
        self.file_name = img_filename_path.split('\\')[-1].split('.')[0]
        self.img = cv2.imread(img_filename_path)

    def _image_info(self) -> None:
        height, width, channels = self.img.shape
        print(height, width, channels)
        # print(self.y, self.h, self.x, self.w)
        cv2.waitKey(0)
        return

    def pre_process_image(self, img, save_in_file, morph_size=(8, 8)):

        # get rid of the color
        pre = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Otsu threshold
        pre = cv2.threshold(pre, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

        # dilate the text to make it solid spot
        cpy = pre.copy()

        # Specify structure shape and kernel size.  
        # Kernel size increases or decreases the area  
        # of the rectangle to be detected. 
        # A smaller value like (10, 10) will detect  
        # each word instead of a sentence.
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, morph_size)
        cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
        pre = ~cpy

        if save_in_file is not None:
            cv2.imwrite(save_in_file, pre)
        return pre

    def find_text_boxes(self, pre, min_text_height_limit=6, max_text_height_limit=40):
        # Looking for the text spots contours
        # OpenCV 3
        # img, contours, hierarchy = cv2.findContours(pre, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        # OpenCV 4
        contours, hierarchy = cv2.findContours(pre, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        # Getting the texts bounding boxes based on the text size assumptions and table position
        boxes = []
        height, width = pre.shape
        for contour in contours:
            box = cv2.boundingRect(contour)
            (x, y, w, h) = box

            if (min_text_height_limit < h < max_text_height_limit and 
                    int(height - height * .55) <= y <= int(height * .9)):
                boxes.append(box)

        return boxes

    def find_table_in_boxes(self, boxes, cell_threshold=10, min_columns=2):
        rows = {}
        cols = {}

        # Clustering the bounding boxes by their positions
        for box in boxes:
            (x, y, w, h) = box
            col_key = x // cell_threshold
            row_key = y // cell_threshold

            # Needed to be added since boxes that are off by 1 px should be in the same cluster
            delta_values = [row_key + i for i in range(-1,2)]
            delta_check = [i in cols.keys() for i in delta_values]
            if True in delta_check:
                row_key = delta_values[delta_check.index(True)]
            cols[row_key] = [box] if col_key not in cols else cols[col_key] + [box]
            rows[row_key] = [box] if row_key not in rows else rows[row_key] + [box]

        # Filtering out boxes that are too small
        table_cells = list(rows.values())
        for r_index, row in enumerate(table_cells):
            filtered_row = [box for box in row if box[2] > cell_threshold]
            table_cells[r_index] = filtered_row

        # Filtering out the clusters having less than 2 cols
        table_cells = list(filter(lambda r: len(r) >= min_columns, table_cells))
        # Sorting the row cells by x coord
        table_cells = [list(sorted(tb)) for tb in table_cells]
        # Sorting rows by the y coord
        table_cells = list(sorted(table_cells, key=lambda r: r[0][1]))

        return table_cells

    def build_lines(self, table_cells):
        if table_cells is None or len(table_cells) <= 0:
            return [], []

        max_last_col_width_row = max(table_cells, key=lambda b: b[-1][2])
        max_x = max_last_col_width_row[-1][0] + max_last_col_width_row[-1][2]
        
        max_last_row_height_box = max(table_cells[-1], key=lambda b: b[3])
        max_y = max_last_row_height_box[1] + max_last_row_height_box[3]

        left_most_box = min(table_cells, key=lambda b: b[0][0])[0]
        hor_lines = [(left_most_box[0], box[0][1], max_x, box[0][1]) for box in table_cells]

        optimal_boxes = table_cells[0]
        ver_lines = [None] * len(optimal_boxes)
        changed_indexes = []

        # Code to get the biggest line of text within the column in question
        # Ultimately, fitting all of the values within the rows
        for row in table_cells[1:]:
            for cur_box in row:
                for index, base_box in enumerate(optimal_boxes):
                    (x, y, w, h) = cur_box
                    (b_x, b_y, b_w, b_h) = base_box
                    if (x, b_y, x, max_y) not in optimal_boxes and b_x > x >= b_x - 65:
                        ver_lines[index] = (x, b_y, x, max_y)
                        changed_indexes.append(index)
                        break # As soon as it changes one, break, no way one box will change 2 
                            # vertical lines

        # Parsing through indexes that weren't visited on the previous line construction
        # Indexes which are still None
        for index, box in enumerate(optimal_boxes):
            if index not in changed_indexes:
                (x, y, w, h) = box
                ver_lines[index] = (x, y, x, max_y)
        
        # Last vertical and horizontal line
        (x, y, w, h) = table_cells[0][-1]
        ver_lines.append((max_x, y, max_x, max_y))
        (x, y, w, h) = left_most_box
        hor_lines.append((x, max_y, max_x, max_y))

        return hor_lines, ver_lines

    def detect_table(self, img=None, pre_file=None, schedule_type='') -> None:
        cur_img = self.img if img is None else img
        if schedule_type == 'Costco':
            pre_processed = self.pre_process_image(cur_img, pre_file, morph_size=(15, 15))
            text_boxes = self.find_text_boxes(pre_processed, max_text_height_limit=52)
            cells = self.find_table_in_boxes(text_boxes, 10, 2)
            hor_lines, ver_lines = self.build_lines(cells)
            self.image_processor(cur_img, hor_lines, ver_lines, cells)

    def image_processor(self, img, hor_lines, ver_lines, cells, unique_divider='|||') -> None:
        """
        Pass through an slice of an image and its index, appending to the same file.
        """
        # Creating a copy of image 
        im2 = img.copy()
        
        txt_filename = os.path.join(".","Recognized_Texts","recognized_{0}.txt".format(self.file_name))

        # Create file and flush
        file = open(txt_filename, "w+")
        file.write("") 
        file.close()

        prev_y = hor_lines[0][1]
        for img_slice_index, line in enumerate(hor_lines[1:]):
            [x1, y1, x2, y2] = line
            # cv2.imshow('image', img[prev_y:prev_y+(y1-prev_y), x1:x1+(x2-x1)])
            # cv2.waitKey(0)

            slice = im2[prev_y:prev_y+(y1-prev_y), x1:x1+(x2-x1)]
            prev_y = y1
            # File has been created already, so just append to it
            file = open(txt_filename, "a")
            # Looping through the identified contours 
            # Then rectangular part is cropped and passed on 
            # to pytesseract for extracting text from it 
            # Extracted text is then written into the text file
            for cnt in cells[img_slice_index]:
                x, y, w, h = cnt
                # Cropping the text block for giving input to OCR
                cropped = im2[y:y + h, x:x + w]
                
                # Apply OCR on the cropped image
                text = pytesseract.image_to_string(cropped).strip()
                file.write(text)
                file.write("\n")
            
            # Writing a divisor into the file
            file.write(unique_divider)
            file.write("\n")
            file.close()
        
        # Open the file in append mode 
        # file = open(txt_filename, "a")
        # for cnt in contours: 
        #     x, y, w, h = cv2.boundingRect(cnt) 
            
        #     # Drawing a rectangle on copied image
        #     rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #     if self.show_detected_text_pic: cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),1)
            
        #     # Cropping the text block for giving input to OCR 
        #     cropped = im2[y:y + h, x:x + w]
            
        #     # Apply OCR on the cropped image
        #     text = pytesseract.image_to_string(cropped)
            
        #     # Appending the text into file 
        #     file.write(text.strip()) 
        #     file.write("\n")

        # Writing a divisor into the file
        # file.write(unique_divider)
        # file.write("\n")
        # file.close()

        if self.show_detected_text_pic:
            plt.imshow(img)
            cv2.namedWindow('detecttable_{0}'.format(img_slice_index), cv2.WINDOW_NORMAL)
            cv2.imwrite('./Slices_Output/detecttable_{0}.jpg'.format(img_slice_index), img)
            
        return

def main():
    file_location = os.path.join("Pictures", "1-18-2021_1-24-2021_schedule.jpg")
    pre_file = os.path.join("Pictures", "pre.png")
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    img_rd_prsr.detect_table(schedule_type='Costco')    
        
if __name__ == '__main__':
    main()