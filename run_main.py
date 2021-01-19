from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import cv2
import os

def main():
    # file_location = os.path.join("Pictures", "2-1-2021_2-7-2021_schedule.jpg")
    pre_file = os.path.join("Pictures", "pre.png")
    # img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    # detected_table_img = img_rd_prsr.detect_table(img_rd_prsr.img)
    # array = img_rd_prsr.chop_image(img_rd_prsr._image_cropper(pre_file, aug_y=5))
    # cv2.imshow('image', img_rd_prsr._image_cropper())
    # cv2.waitKey(0)
    # print(array)
    # for index, dict in enumerate(array):
        # cv2.imshow('image', dict['img'])
        # cv2.waitKey(0)
        # img_rd_prsr.image_processor(dict['img'], index)
    
    # fl_prsr = FileParser(file_location)
    # lines_of_data = []
    # for i in range(1,8):
    #     lines_of_data.append(fl_prsr.parse_file(i))
    # print(lines_of_data)
    # fl_prsr.parse_dataframe(lines_of_data)
    # print(fl_prsr.df_file_location)
    # fl_prsr._output_df()

    # df = fl_prsr.df.dropna(axis=0)
    # print(df)
    # v_crtn = EventTerminal(df)
    # v_crtn.build_events(subject='Día de Trabajo', location='Costco (1175 N 205th St, Shoreline, WA  98133, United States)', recipients=['valeracuevan@spu.edu'])
    # for event in v_crtn.appointment_list:
    #     print(event)
    #     print()
    # v_crtn.send_events()
    return

if __name__ == "__main__":
    main()