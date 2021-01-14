from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import cv2

def main():
    file_location = './Pictures/1-24-2021_1-31-2021_schedule.jpg'
    img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False, verbose=True)
    img_rd_prsr._image_info()
    # cv2.imshow('image', img_rd_prsr._image_cropper())
    # cv2.waitKey(0)
    # array = img_rd_prsr.chop_image()
    # print(array)
    # for index, dict in enumerate(array):
        # img_rd_prsr.image_processor(dict['img'], index)
    
    # fl_prsr = FileParser(file_location)
    # lines_of_data = []
    # for i in range(1,8):
    #     lines_of_data.append(fl_prsr.parse_file(i))
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