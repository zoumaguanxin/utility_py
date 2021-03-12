import rospy
from nav_msgs.msg import Odometry
import argparse
import os
import tf
#from scipy.spatial.transform import Rotation
import numpy as np

parser = argparse.ArgumentParser(description="preocess")
args = parser.add_argument("--num",dest="num",type=int,default=0,help="the number will be appended to the file, for example pose0.txt")
args = parser.parse_args()

#file = os.path.join()

file_path = str("pose")+str(args.num)+".txt"

file = open(file_path,"w")

def odomCallback(data):
	r = tf.transformations.quaternion_matrix([data.pose.pose.orientation.x,data.pose.pose.orientation.y,data.pose.pose.orientation.z,data.pose.pose.orientation.w])
	#r = Rotation.from_quat([data.pose.pose.orientation.x,data.pose.pose.orientation.y,data.pose.pose.orientation.z,data.pose.pose.orientation.w])
	a = np.zeros((3,4))
	a[:,0:3] = r[0:3,0:3]
	a[:,3] = [data.pose.pose.position.x, data.pose.pose.position.y,data.pose.pose.position.z]
	for i in range(3):
		for j in range(4):
			file.write(str(a[i][j]))
			file.write(' ')
	file.write("\n")
	return


def main():
	rospy.init_node("save_floam_traj",anonymous=False)
	rospy.Subscriber("odom",Odometry,odomCallback)
	rospy.spin()
	
if __name__=="__main__":
	main()
