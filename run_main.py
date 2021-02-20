from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import cv2
import os

def main():
    file_location = os.path.join("Pictures", "1-18-2021_1-24-2021_schedule.jpg")
    pre_file = os.path.join("Pictures", "pre.png")
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    pre_processed = img_rd_prsr.pre_process_image(img_rd_prsr.img, pre_file, morph_size=(15, 15))
    text_boxes = img_rd_prsr.find_text_boxes(pre_processed, max_text_height_limit=52)
    cells = img_rd_prsr.find_table_in_boxes(text_boxes, 10, 2)
    hor_lines, ver_lines = img_rd_prsr.build_lines(cells)
    img_rd_prsr.image_processor(img_rd_prsr.img, hor_lines, ver_lines, cells, limit_col=4)
    
    # fl_prsr = FileParser(file_location)
    # lines_of_data = fl_prsr.parse_file()
    # fl_prsr.parse_dataframe(lines_of_data)
    # # print(fl_prsr.df_file_location)
    # # fl_prsr._output_df()

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