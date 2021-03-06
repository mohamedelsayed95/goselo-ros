#!/usr/bin/env python
import sys
import rospy
import cv2
import numpy as np
from nav_msgs.msg import OccupancyGrid
from sensor_msgs.msg import LaserScan
from tf.transformations import euler_from_quaternion
import tf
import math
import threading
from std_msgs.msg import Float32MultiArray


class publish_global_plan:

    def __init__(self):
        self.object_avoidance_range = rospy.get_param('object_avoidance_range', 1.0)
        self.down_scale = rospy.get_param('down_scale', 10)
        self.n_directions = rospy.get_param('n_directions', 8)
        
        self.cell_size = None
        self.the_map =  np.zeros((0,0))
        self.lock = threading.Lock()
        self.obstacles_directions = []
        self.origin_x = None
        self.origin_y = None

        self.curr_map_sub = rospy.Subscriber("/map",OccupancyGrid,self.callbackMap,queue_size = 1)
        self.laserscan_sub = rospy.Subscriber("/scan",LaserScan,self.callLaserScan,queue_size = 1)
        self.obstacles_pub = rospy.Publisher('/obstacles', Float32MultiArray, queue_size=1)

    def callLaserScan(self, data):
        if not self.lock.locked():
            self.lock.acquire()             
            try:
                (trans,orientation_q) = listener.lookupTransform('/odom', '/rplidar_link', rospy.Time(0))
            except:
                print "couldn't get right transformaton"
                self.lock.release()
                return

            ranges = data.ranges
            min_ang = data.angle_min
            max_ang = data.angle_max
            inc = data.angle_increment

            orientation_list = [orientation_q[0], orientation_q[1], orientation_q[2], orientation_q[3]]
            _, _, yaw = euler_from_quaternion (orientation_list)
            current_rotation = yaw
            current_x = trans[0]
            current_y = trans[1]
            
            #laser standalone
            my_map = np.zeros(self.the_map.shape)
            
            # measurements in laser scanner frame
            np_ranges = np.array(ranges)
            np_indicies = np.arange(len(ranges))

            indicies = np.isfinite(np_ranges)
            correct_values = np_ranges[indicies]
            correct_indicies = np_indicies[indicies]
            correct_indicies = correct_indicies[correct_values<2.0]
            correct_values = correct_values[correct_values<2.0]

            self.obstacles_directions = []
            small_ranges = correct_values[correct_values<self.object_avoidance_range]*inc 
            angles = (correct_indicies[correct_values<self.object_avoidance_range]*inc) + current_rotation

            if angles.size:
                
                if angles[(angles <= math.pi*0.125) | (angles >= 1.875*math.pi)].size:
                    self.obstacles_directions.append(0)
                if angles[(angles <= math.pi*0.375) & (angles > 0.125*math.pi)].size:
                    self.obstacles_directions.append(1)
                if angles[(angles <= math.pi*0.675) & (angles > 0.375*math.pi)].size:
                    self.obstacles_directions.append(2)
                if angles[(angles <= math.pi*0.875) & (angles > 0.675*math.pi)].size:
                    self.obstacles_directions.append(3)
                if angles[(angles <= math.pi*1.125) & (angles > 0.875*math.pi)].size:
                    self.obstacles_directions.append(4)
                if angles[(angles <= math.pi*1.375) & (angles > 1.125*math.pi)].size:
                    self.obstacles_directions.append(5)
                if angles[(angles <= math.pi*1.625) & (angles > 1.375*math.pi)].size:
                    self.obstacles_directions.append(6)
                if angles[(angles <= math.pi*1.875) & (angles >= 1.625*math.pi)].size:
                    self.obstacles_directions.append(7)
            
            # print self.obstacles_directions
            my_array_for_publishing = Float32MultiArray(data=self.obstacles_directions)
            self.obstacles_pub.publish(my_array_for_publishing)
            self.lock.release()

        else:
            print "I am blocked"
            return


    def callbackMap(self,data):
        self.cell_size = data.info.resolution
        self.origin_x = data.info.origin.position.x
        self.origin_y = data.info.origin.position.y
        self.the_map = np.zeros((data.info.height/self.down_scale, data.info.width/self.down_scale))


if __name__ == '__main__':
  rospy.init_node('laser_to_dirs')
  listener = tf.TransformListener()
  pgp = publish_global_plan()
  try:
    rospy.spin()
  except KeyboardInterrupt:
    print "Shutting down"
  cv2.destroyAllWindows()