import os, sys
sys.path.append('./src')

from FileProcesses import FileParser
from EventProcesses import EventTerminal
from ImageProcesses import ImageParser

import variables_in as var
from main_logger import logger

if __name__ == "__main__":
    logger.info(var.file_location)

    # logger.info('Starting image processing')
    # img_rd_prsr = ImageParser(var.file_location,show_detect_jpg=False)
    # pre_processed = img_rd_prsr.pre_process_image(img_rd_prsr.img, var.pre_file, morph_size=(16, 16))
    # text_boxes = img_rd_prsr.find_text_boxes(pre_processed, 6, 52)
    # cells = img_rd_prsr.find_table_in_boxes(text_boxes, 10, 2)
    # hor_lines, ver_lines = img_rd_prsr.build_lines(cells)
    # img_rd_prsr.output_detection(img_rd_prsr.img, text_boxes, hor_lines, ver_lines, var.out_file) # Output the bounds before parsing the image
    # img_rd_prsr.image_processor(img_rd_prsr.img, hor_lines, ver_lines, cells, limit_col=4)
    # logger.info('Finishing image processing')
    
    logger.info('Starting file parser')
    fl_prsr = FileParser(var.file_location, from_file=var.from_file)
    # lines_of_data = fl_prsr.parse_file()
    fl_prsr.parse_dataframe()
    # fl_prsr._output_df()
    logger.info('Finishing file parser')

    df = fl_prsr.df #.dropna(axis=0)
    print(df)
    # print(df.dtypes)
    df_checker = input('Does the df look correct?: ')
    if df_checker in ['yes', 'y', 'Y', 'YES']:
        print('Ok, we good!')
    else:
        quit()

    logger.info('Starting event terminal')
    v_crtn = EventTerminal(df)
    v_crtn.build_events(**var.event_info)
    # for event in v_crtn.appointment_list:
    #     print(event)

    v_crtn.send_events()

    logger.info('Finishing event terminal')