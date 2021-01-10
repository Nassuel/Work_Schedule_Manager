import cv2
import numpy as np
import pytesseract
import matplotlib.pyplot as plt

# Mention the installed location of Tesseract-OCR in your system
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# Read image from which text needs to be extracted
file = r'D:\\Repos\\Create_Calendar_Event_From_Pic\\Pictures\\142021-1102021_schedule.jpg'
img = cv2.imread(file)

y = 375
h = 330

x = 40
w = 1312
crop_img = img[y:y+h, x:x+w]

cv2.imshow('image', crop_img)
cv2.waitKey(0)
# cv2.namedWindow('detecttable', cv2.WINDOW_NORMAL)
# cv2.imwrite('detecttable.jpg',img)