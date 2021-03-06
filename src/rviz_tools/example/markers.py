#!/usr/bin/env python

# Python includes
import numpy
import random

# ROS includes
import roslib
import rospy
from geometry_msgs.msg import Point
import rviz_tools_py as rviz_tools
from nav_msgs.msg import OccupancyGrid, Odometry
from geometry_msgs.msg import PoseStamped, Vector3, Pose, Quaternion
from std_msgs.msg import Float32
from tf import transformations # rotation_matrix(), concatenate_matrices()
import math
from tf.transformations import euler_from_quaternion, quaternion_from_euler

# Initialize the ROS Node
rospy.init_node('markers_node')
markers = rviz_tools.RvizMarkers('/odom', 'visualization_marker')

curr_locX = None
curr_locY = None
goal_locX = None
goal_locY = None
orientation = None
orientation_GOSELO = None

def callbackStart(data):
    global curr_locX, curr_locY
    curr_locX = data.pose.pose.position.x
    curr_locY = data.pose.pose.position.y

def callbackGoal(data):
    global goal_locX, goal_locY
    goal_locX = data.pose.position.x
    goal_locY = data.pose.position.y


def callbackDir(data):
    global orientation
    orientation = data.data*math.pi/4


def callbackDirGOSELO(data):
    global orientation_GOSELO
    orientation_GOSELO = data.data*math.pi/4

odom_sub = rospy.Subscriber("/odom",Odometry,callbackStart,queue_size = 1)
goal_s = rospy.Subscriber("/move_base_simple/goal",PoseStamped,callbackGoal,queue_size = 1)
direction_corrected = rospy.Subscriber("/dir_corrected",Float32,callbackDir,queue_size = 1)
direction_goselo = rospy.Subscriber("/goselo_direction",Float32,callbackDirGOSELO,queue_size = 1)


while not rospy.is_shutdown():

    if (curr_locX != None):
        # Publish a sphere by passing diameter as a float
        point = Point(curr_locX,curr_locY,0.2)
        diameter = 0.2
        markers.publishSphere(point, 'green', diameter, 0.01) # pose, color, diameter, lifetime

    if (goal_locX != None):
        # Publish a sphere by passing diameter as a float
        point = Point(goal_locX,goal_locY,0.2)
        diameter = 0.2
        markers.publishSphere(point, 'red', diameter, 0.01) # pose, color, diameter, lifetime

    # Publish an arrow using a numpy transform matrix
    if (orientation != None and curr_locX != None ):
        quat = quaternion_from_euler(0.0, 0.0, orientation)
        q1 = quat[0]
        q2 = quat[1]
        q3 = quat[2]
        q4 = quat[3]

        P = Pose(Point(curr_locX,curr_locY,0.085),Quaternion(q1, q2, q3, q4))

        scale = Vector3(0.6,0.05,0.05) # x=length, y=height, z=height
        markers.publishArrow(P, 'green', scale, 0.01) # pose, color, scale, lifetime


    # Publish an arrow using a numpy transform matrix
    if (orientation_GOSELO != None and curr_locX != None ):
        quat = quaternion_from_euler(0.0, 0.0, orientation_GOSELO)
        q1 = quat[0]
        q2 = quat[1]
        q3 = quat[2]
        q4 = quat[3]

        P = Pose(Point(curr_locX,curr_locY,0.085),Quaternion(q1, q2, q3, q4))

        scale = Vector3(0.6,0.05,0.05) # x=length, y=height, z=height
        markers.publishArrow(P, 'blue', scale, 0.01) # pose, color, scale, lifetime

    rospy.Rate(1000).sleep() #1 Hz
