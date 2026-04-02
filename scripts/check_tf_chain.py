#!/usr/bin/env python3
import rospy
import tf2_ros

if __name__ == '__main__':
    rospy.init_node('check_tf_chain')
    tf_buffer = tf2_ros.Buffer()
    listener = tf2_ros.TransformListener(tf_buffer)

    rate = rospy.Rate(1.0)
    while not rospy.is_shutdown():
        try:
            t = tf_buffer.lookup_transform('map', 'base_footprint', rospy.Time(0), rospy.Duration(1.0))
            rospy.loginfo('OK map->base_footprint: x=%.3f y=%.3f z=%.3f' % (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z))
        except Exception as e:
            rospy.logwarn('map->base_footprint transform unavailable: %s' % e)

        try:
            t = tf_buffer.lookup_transform('map', 'odom', rospy.Time(0), rospy.Duration(1.0))
            rospy.loginfo('OK map->odom: x=%.3f y=%.3f z=%.3f' % (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z))
        except Exception as e:
            rospy.logwarn('map->odom transform unavailable: %s' % e)

        try:
            t = tf_buffer.lookup_transform('odom', 'base_footprint', rospy.Time(0), rospy.Duration(1.0))
            rospy.loginfo('OK odom->base_footprint: x=%.3f y=%.3f z=%.3f' % (t.transform.translation.x, t.transform.translation.y, t.transform.translation.z))
        except Exception as e:
            rospy.logwarn('odom->base_footprint transform unavailable: %s' % e)

        rate.sleep()
