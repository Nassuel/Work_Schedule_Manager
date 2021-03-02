from ImageProcesses import ImageReaderAndParser
from FileProcesses import FileParser
from EventProcesses import EventTerminal

import cv2
import os

def main():
    rel_path = os.path.dirname(__file__)
    file_location = os.path.join(rel_path, "Pictures", "3-1-2021_3-7-2021_schedule.png")
    pre_file = os.path.join("Pictures", "pre.png")
    out_file = os.path.join("Pictures", "out.png")
    print(file_location)
    # img_rd_prsr = ImageReaderAndParser(file_location,show_detect_jpg=False)
    # pre_processed = img_rd_prsr.pre_process_image(img_rd_prsr.img, pre_file, morph_size=(20, 20))
    # text_boxes = img_rd_prsr.find_text_boxes(pre_processed, 15, 52)
    # cells = img_rd_prsr.find_table_in_boxes(text_boxes, 10, 2)
    # hor_lines, ver_lines = img_rd_prsr.build_lines(cells)
    # img_rd_prsr.image_processor(img_rd_prsr.img, hor_lines, ver_lines, cells, limit_col=4)
    # img_rd_prsr.output_detection(img_rd_prsr.img, text_boxes, hor_lines, ver_lines, out_file)
    
    fl_prsr = FileParser(file_location)
    lines_of_data = fl_prsr.parse_file()
    fl_prsr.parse_dataframe(lines_of_data)
    print(fl_prsr.df_file_location)
    # fl_prsr._output_df()

    df = fl_prsr.df.dropna(axis=0).reset_index()
    print(df)
    v_crtn = EventTerminal(df)
    event_info = {
        'subject': 'Día de Trabajo',
        'location':'Costco (1175 N 205th St, Shoreline, WA  98133, United States)',
        'recipients':['valeracuevan@spu.edu'], 
        'attachments':[file_location]
    }
    v_crtn.build_events(**event_info)
    for event in v_crtn.appointment_list:
        print(event)
        # print(os.path.join(rel_path,'Checking.MSG'),'olMSG')
        # event.COMObject_appt.SaveAs(os.path.join(rel_path,'Checking.MSG')) # Use this to have a preview of the Appt on Outlook
        print()
        break
    # v_crtn.send_events()
    return

if __name__ == "__main__":
    main()