from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import variables_in as var

import os

def main():
    print(var.file_location)

    # img_rd_prsr = ImageReaderAndParser(var.file_location,show_detect_jpg=False)
    # pre_processed = img_rd_prsr.pre_process_image(img_rd_prsr.img, var.pre_file, morph_size=(15, 15))
    # text_boxes = img_rd_prsr.find_text_boxes(pre_processed, 6, 52)
    # cells = img_rd_prsr.find_table_in_boxes(text_boxes, 10, 2)
    # hor_lines, ver_lines = img_rd_prsr.build_lines(cells)
    # img_rd_prsr.image_processor(img_rd_prsr.img, hor_lines, ver_lines, cells, limit_col=4)
    # img_rd_prsr.output_detection(img_rd_prsr.img, text_boxes, hor_lines, ver_lines, var.out_file)
    
    fl_prsr = FileParser(var.file_location)
    lines_of_data = fl_prsr.parse_file()
    fl_prsr.parse_dataframe(lines_of_data)
    # print(fl_prsr.df_file_location)
    # fl_prsr._output_df()

    df = fl_prsr.df.dropna(axis=0)#.reset_index()
    print(df)

    v_crtn = EventTerminal(df)
    v_crtn.build_events(**var.event_info)
    for event in v_crtn.appointment_list:
        print(event)
        # print(os.path.join(rel_path,'Checking.MSG'),'olMSG')
        # event.COMObject_appt.SaveAs(os.path.join(rel_path,'Checking.MSG')) # Use this to have a preview of the Appt on Outlook
        print()
    v_crtn.send_events()
    return

if __name__ == "__main__":
    main()