
import rospy
from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from cv_bridge import CvBridge
import cv2
import sys
import matplotlib
import matplotlib.pyplot as plt
import queue

import sys
import tty
import termios
import signal
import time

limgque = queue.Queue()
rightimgque = queue.Queue()
rgbimagequeue = queue.Queue()
depthqueue =queue.Queue()

#import pdb
#pdb.set_trace()

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def readkey(getchar_fn=None):
    getchar = getchar_fn or readchar
    c1 = getchar()
    if ord(c1) != 0x1b:
        return c1
    c2 = getchar()
    if ord(c2) != 0x5b:
        return c1
    c3 = getchar()
    return chr(0x10 + ord(c3) - 65)
 
def set_timeout(num, callback):
	def wrap(func):
		def handle(signum, frame):
			raise RuntimeError
		
		def to_do(*args, **kwargs):
			try:
				signal.signal(signal.SIGALRM, handle)  
				signal.alarm(num) 
				print('press e to stop this program...')
				r = func(*args, **kwargs)
				print('Detected Key pressed.\n')
				signal.alarm(0)  
				return r
			except RuntimeError as e:
				callback()
 
		return to_do 
	
	return wrap

def after_timeout():  
    print("No key pressed!\n")
 
@set_timeout(2, after_timeout) 
def press_pause():
    key = readkey()
    return key

def limageCallback(data):
	global sub1, plt
	bridge = CvBridge()
	cv_image = bridge.imgmsg_to_cv2(data)
	limgque.put(cv_image)

	
def rimageCallback(data):
	bridge = CvBridge()
	cv_image = bridge.imgmsg_to_cv2(data)
	rightimgque.put(cv_image)

	
def rgbimageCallback(data):
	bridge = CvBridge()
	cv_image = bridge.imgmsg_to_cv2(data)
	rgbimagequeue.put(cv_image)

	
def depthimageCallback(data):
	bridge = CvBridge()
	cv_image = bridge.imgmsg_to_cv2(data)
	depthqueue.put(cv_image)

def main(args):
	rospy.init_node('image_test', anonymous=True)
	rospy.Subscriber("/camera/infra1/image_rect_raw",Image,limageCallback)
	rospy.Subscriber("/camera/infra2/image_rect_raw",Image,rimageCallback)
	rospy.Subscriber("/camera/color/image_raw",Image,rgbimageCallback)
	rospy.Subscriber("/camera/aligned_depth_to_color/image_raw",Image,depthimageCallback)
	
	ficture = plt.figure(1)
	
	sub1 = ficture.subplots(2,2)
	while True:
		if not limgque.empty():
			print "get image"
			cv_image = limgque.get()
			sub1[0][0].imshow(cv_image)
			plt.pause(0.1)
		if not rightimgque.empty():
			cv_image = rightimgque.get()
			sub1[0][1].imshow(cv_image)
			plt.pause(0.1)
		if not rgbimagequeue.empty():
			cv_image = rgbimagequeue.get()
			sub1[1][0].imshow(cv_image)
		if not depthqueue.empty():
			cv_image = depthqueue.get()
			sub1[1][1].imshow(cv_image)
		key = press_pause()
		if key != None:
			print(key+'\n')
			if key == 'e':
				print('exit')
				break
	rospy.spin()


if __name__ == '__main__':
	main(sys.argv)

	
	