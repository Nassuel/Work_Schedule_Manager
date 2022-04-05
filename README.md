# Work_Schedule_Manager

All (ImageProcesses, FileProcesses, EventProcesses) files have "helper" functions which get the job done with a couple lines of code.

In `run_main.py`, a workflow example can be seen. There are some commented lines since I discovered that the table the Costco employee site renders is an html table
which can be easily parsed using pandas rather than using image processing. Yet, I left the setup for using OpenCV and Tesseract on there 😀

##### Sources

[Image text detection and extraction with OpenCV and Tesseract OCR](https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/ "Geeks for Geeks OpenCV Text Detection/Extraction")\
[Great help on table detection](https://stackoverflow.com/questions/50829874/how-to-find-table-like-structure-in-image/ "Stack Overflow FTW")

##### Notes

Due to py32win dependency, EventProcesses.py is fully operational on Windows with Outlook installed.

If you have any questions, you can email [me](mailto:valeranassuel@protonmail.com?subject="Work_Schedule_Manager")
