#!/usr/bin/env python

import cv2
from copy import deepcopy
import numpy as np
import os
import rospy
import rospkg
rospack = rospkg.RosPack()
from std_msgs.msg import Float64, String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError

# Helpers
from helpers.cvlib import Detection
detection = Detection()

from helpers.control import Control
control = Control()


class Detect(object):
    def __init__(self):
        rospy.init_node('detect_node', anonymous=True)
        rate = rospy.Rate(30)
        
        self.bridge = CvBridge()
        self.frame = None
        self.keypress = -1

        rospy.Subscriber('/tello/image_raw', Image, self.img_callback)
        rospy.Subscriber('/keypress', String, self.key_callback)

        self.yaw_pub = rospy.Publisher('tello/yaw_angle', Float64, queue_size=1)
        
        while not rospy.is_shutdown():
            if self.frame is not None:
                frame = deepcopy(self.frame)
                frame = cv2.resize(frame, (640,480))
                centroids, bboxes = detection.detect(frame)
                if len(centroids) != 0:
                    # if self.keypress != -1 and self.keypress < len(centroids):
                    #     cent = centroids[self.keypress]
                    target = centroids[0]
                    yaw_angle = control.yaw(target)
                    print(yaw_angle)
                    self.yaw_pub.publish(yaw_angle)
                    
                    cv2.arrowedLine(frame, (320, target[1]), target, (250, 150, 0), 4)

                cv2.imshow("", frame)
                cv2.waitKey(1)

            rate.sleep()

    def img_callback(self, data):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(data)
        except CvBridgeError as e:
            print(e)
        self.frame = cv_image

    def key_callback(self, data):
        if data.data != "":
            self.keypress = int(data.data)
        else:
            self.keypress = -1


if __name__ == '__main__':
    try:
        Detect()
    except rospy.ROSInterruptException:
        pass
    finally:
        cv2.destroyAllWindows()