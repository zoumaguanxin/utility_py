import cv2
import numpy as np
import os
import argparse



def save_image(image,addr,num):
	n = "%04d" % num
	# str_n = str(num)
	# str_n = str_n.zfill(4)
	address = os.path.join(addr, str(n)+ '.jpg')
	cv2.imwrite(address,image)

parser = argparse.ArgumentParser(description='Process some integers.')
args = parser.add_argument('--dir',dest='dir',type=str,help='vedio directory')
args = parser.parse_args()

vedio_dir = args.dir

fname,fename=os.path.split(vedio_dir)

videoCapture = cv2.VideoCapture(vedio_dir)


# videoCapture=cv2.VideoCapture(1)

image_dir = os.path.join(fname,"image/")
if os.path.exists(image_dir):
	for i in range(99999):
		tem = "image"
		tem = tem+str(i)
		image_dir = os.path.join(fname,tem)
		if os.path.exists(image_dir):
			continue
		else:
			os.mkdir(image_dir)
			break
else:
	os.mkdir(image_dir)

success, frame = videoCapture.read()
i = 0
timeF = 4
j=0
while success :
	i = i + 1
	if (i % timeF == 0):
		j = j + 1
		save_image(frame,image_dir,j)
		print('save image:',i)
	success, frame = videoCapture.read()
