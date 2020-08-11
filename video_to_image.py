import cv2
import numpy as np
 

def save_image(image,addr,num):
    address = addr + str(num)+ '.jpg'
    cv2.imwrite(address,image)
 

videoCapture = cv2.VideoCapture("/home/shawn/Videos/yolo_cup/video/VID_20200807_112757.mp4")


# videoCapture=cv2.VideoCapture(1)
 

success, frame = videoCapture.read()
i = 0
timeF = 12
j=0
while success :
    i = i + 1
    if (i % timeF == 0):
        j = j + 1
        save_image(frame,'/home/shawn/Videos/yolo_cup/video/images_VID_20200807_112757/',j)
        print('save image:',i)
    success, frame = videoCapture.read()
