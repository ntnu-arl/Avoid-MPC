#!/usr/bin/env python

import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import cv2

class DepthImageConverter:
    def __init__(self):
        rospy.init_node('depth_image_converter', anonymous=True)

        self.bridge = CvBridge()

        # Parameters (can be customized via ROS params)
        self.input_topic = rospy.get_param('~input_topic', '/depth')
        self.output_topic = rospy.get_param('~output_topic', '/depth_converted')

        self.sub = rospy.Subscriber(self.input_topic, Image, self.callback)
        self.pub = rospy.Publisher(self.output_topic, Image, queue_size=1)

    def callback(self, msg):
        try:
            # Convert incoming depth image from ROS to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="passthrough")

            if cv_image.dtype != np.uint16:
                rospy.logwarn("Expected uint16 depth image. Got: {}".format(cv_image.dtype))
                return

            # Convert from mm (uint16) to meters (float32)
            depth_meters = cv_image.astype(np.float32) / 1000.0

            # Convert back to ROS image message with encoding 32FC1
            depth_msg = self.bridge.cv2_to_imgmsg(depth_meters, encoding="32FC1")

            # Copy over header info (timestamp, frame_id)
            depth_msg.header = msg.header

            # Publish converted image
            self.pub.publish(depth_msg)

        except CvBridgeError as e:
            rospy.logerr("CvBridge Error: {}".format(e))

if __name__ == '__main__':
    try:
        DepthImageConverter()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass