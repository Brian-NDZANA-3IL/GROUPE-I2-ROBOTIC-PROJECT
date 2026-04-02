#!/usr/bin/env python3
"""
Robot Exploration Script for SLAM
Automatically explores the environment to generate maps
"""

import rospy
import math
import numpy as np
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
import time


class ExplorationBot:
    """Autonomous exploration using frontier-based approach"""
    
    def __init__(self):
        """Initialize exploration robot"""
        rospy.init_node('exploration_bot', anonymous=True)
        
        # Publishers
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        
        # Subscribers
        rospy.Subscriber('/odom', Odometry, self._odom_callback)
        rospy.Subscriber('/scan', LaserScan, self._laser_callback)
        
        # State
        self.position = np.array([0.0, 0.0])
        self.orientation = 0.0
        self.laser_ranges = np.ones(360) * 3.5
        
        # Exploration parameters
        self.max_exploration_time = 300  # 5 minutes
        self.linear_speed = 0.3
        self.angular_speed = 0.5
        
        print("[ExplorationBot] Initialized")
    
    def _odom_callback(self, msg):
        """Update robot position"""
        self.position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        ])
        
        # Extract orientation
        quat = msg.pose.pose.orientation
        siny_cosp = 2 * (quat.w * quat.z + quat.x * quat.y)
        cosy_cosp = 1 - 2 * (quat.y**2 + quat.z**2)
        self.orientation = math.atan2(siny_cosp, cosy_cosp)
    
    def _laser_callback(self, msg):
        """Update laser scan"""
        self.laser_ranges = np.array(msg.ranges)
        self.laser_ranges = np.clip(self.laser_ranges, 0, 3.5)
    
    def find_frontier(self):
        """
        Find frontier (boundary between known and unknown space)
        Returns angle to frontier
        """
        # Analyze laser scan for frontier
        front_ranges = self.laser_ranges[60:120]  # Front hemisphere
        
        # Find largest gap (frontier)
        max_gap_angle = np.argmax(front_ranges) + 60
        
        # Convert to radians
        frontier_angle = np.radians(max_gap_angle - 180)
        return frontier_angle
    
    def is_stuck(self):
        """Check if robot is stuck"""
        min_distance = np.min(self.laser_ranges)
        return min_distance < 0.25
    
    def explore_step(self):
        """One exploration step"""
        twist = Twist()
        
        # Get frontier direction
        frontier_angle = self.find_frontier()
        
        min_distance = np.min(self.laser_ranges)
        
        # If stuck, rotate
        if self.is_stuck() or min_distance < 0.4:
            twist.linear.x = 0.0
            twist.angular.z = self.angular_speed
            print(f"[Explorer] Obstacle detected (dist={min_distance:.2f}m), rotating")
        else:
            # Combine frontier direction with forward motion
            twist.linear.x = self.linear_speed
            twist.angular.z = frontier_angle * 0.5  # Adjust heading toward frontier
        
        self.cmd_vel_pub.publish(twist)
        return twist
    
    def explore(self):
        """Main exploration loop"""
        print(f"[Explorer] Starting exploration (max {self.max_exploration_time}s)")
        
        start_time = time.time()
        step_count = 0
        
        rate = rospy.Rate(2)  # 2 Hz
        
        while not rospy.is_shutdown():
            elapsed = time.time() - start_time
            
            if elapsed > self.max_exploration_time:
                print(f"[Explorer] Exploration time limit reached")
                break
            
            twist = self.explore_step()
            step_count += 1
            
            # Log progress
            if step_count % 5 == 0:
                min_dist = np.min(self.laser_ranges)
                print(f"[Explorer] Step {step_count:3d} | Time: {elapsed:6.1f}s | "
                      f"Pos: ({self.position[0]:5.2f}, {self.position[1]:5.2f}) | "
                      f"Min dist: {min_dist:5.2f}m")
            
            rate.sleep()
        
        # Stop robot
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        
        print(f"\n[Explorer] Exploration complete!")
        print(f"[Explorer] Total steps: {step_count}")
        print(f"[Explorer] Total time: {elapsed:.1f}s")
        print(f"[Explorer] Final position: ({self.position[0]:.2f}, {self.position[1]:.2f})")


def main():
    explorer = ExplorationBot()
    
    try:
        explorer.explore()
    except KeyboardInterrupt:
        print("\n[Explorer] Interrupted by user")
        # Stop robot
        twist = Twist()
        explorer.cmd_vel_pub.publish(twist)
    except Exception as e:
        print(f"[Explorer] Error: {e}")


if __name__ == "__main__":
    main()
