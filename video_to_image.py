import cv2
import numpy as np
import os
import argparse
from datetime import datetime
import sys


def save_image(image,addr,num,prefix = None):
	n = "%06d" % num
	# str_n = str(num)
	# str_n = str_n.zfill(4)
	if not prefix is None:
		address = os.path.join(addr, prefix+'_'+str(n)+ '.jpg')
	else:
		address = os.path.join(addr, str(n)+ '.jpg')	
	cv2.imwrite(address,image)

parser = argparse.ArgumentParser(description='Process some integers.')
args = parser.add_argument('--dir',dest='dir',type=str,help='vedio directory')
args = parser.add_argument('--fps',dest='fps',type=int,default=10,help='vedio directory')
args = parser.add_argument('--bidx',dest='begin_idx',type=int,default=0,help='Number the image from this number')
args = parser.add_argument('--bt',dest='begin_time',type=int,default=0,help='Number the image from this number')
args = parser.add_argument('--et',dest='end_time',type=int,default=9999999,help='Number the image from this number')
args = parser.parse_args()

vedio_dir = args.dir
bidx = args.begin_idx
bt = args.begin_time
et = args.end_time
fps = args.fps

fname,fename=os.path.split(vedio_dir)
file_name, suffix = fename.split('.')


image_dir = os.path.join(fname,"image")
if os.path.exists(image_dir):
	for i in range(99999):
		tem_dir = image_dir + str(i)
		if os.path.exists(tem_dir):
			continue
		else:
			os.mkdir(tem_dir)
			image_dir = tem_dir
			break
else:
	os.mkdir(image_dir)
	
i = 0	
j=bidx
start = False

cap = cv2.VideoCapture(vedio_dir)
# cap=cv2.VideoCapture(1)
frame_counter = int(cap.get(cv2.CAP_PROP_FPS))
print("video FPS:", frame_counter)
frame_interval = 1
if frame_counter > fps:
	frame_interval = frame_counter // fps
begin_time = datetime.now()
success, frame = cap.read()
while success :
	end_time = datetime.now()
	shift_time = (end_time - begin_time).seconds
	if not start and shift_time >= bt:
		begin_time = end_time
		start = True
	if (i % frame_interval == 0) and  start:
		save_image(frame,image_dir,i+j,file_name)
		print('save image:',i)
	success, frame = cap.read()
	i = i + 1
	if bt + shift_time > et:
		break
