from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import cv2
import os

def main():
    file_location = os.path.join("Pictures", "2-8-2021_2-14-2021_schedule_snip.png")
    # pre_file = os.path.join("Pictures", "pre.png")
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    detected_table_img = img_rd_prsr.detect_table(img_rd_prsr.img)
    # array = img_rd_prsr.chop_image(img_rd_prsr._image_cropper(pre_file, aug_x=10, aug_y=30))
    array = img_rd_prsr.chop_image(img_rd_prsr.img)
    # cv2.imshow('image', img_rd_prsr._image_cropper())
    # cv2.waitKey(0)
    # print(array)
    for index, d in enumerate(array):
        # cv2.imshow('image', d['img'])
        # cv2.waitKey(0)
        img_rd_prsr.image_processor(d['img'], index)
    
    fl_prsr = FileParser(file_location)
    lines_of_data = fl_prsr.parse_file()
    fl_prsr.parse_dataframe(lines_of_data)
    # print(fl_prsr.df_file_location)
    # fl_prsr._output_df()

    df = fl_prsr.df.dropna(axis=0)
    print(df)
    v_crtn = EventTerminal(df)
    v_crtn.build_events(subject='Día de Trabajo', location='Costco (1175 N 205th St, Shoreline, WA  98133, United States)', recipients=['valeracuevan@spu.edu'])
    for event in v_crtn.appointment_list:
        print(event)
        print()
    # v_crtn.send_events()
    return

if __name__ == "__main__":
    main()