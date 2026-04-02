#!/usr/bin/env python3
"""
Advanced Navigation Controllers for TurtleBot3
Implements PID trajectory tracking and obstacle avoidance
"""

import numpy as np
import rospy
import math
from geometry_msgs.msg import Twist, Pose2D, PoseStamped
from nav_msgs.msg import Path, Odometry
from sensor_msgs.msg import LaserScan
import tf2_ros
import tf2_geometry_msgs
from geometry_msgs.msg import PointStamped


class PIDController:
    """Generic PID Controller"""
    
    def __init__(self, kp, ki, kd, max_output=1.0, min_output=-1.0):
        """
        Initialize PID Controller
        
        Args:
            kp: Proportional gain
            ki: Integral gain
            kd: Derivative gain
            max_output: Maximum output value
            min_output: Minimum output value
        """
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.max_output = max_output
        self.min_output = min_output
        
        self.integral = 0.0
        self.prev_error = 0.0
        self.last_time = None
    
    def update(self, error, current_time=None):
        """
        Update PID controller
        
        Args:
            error: Current error
            current_time: Current time (for dt calculation)
        
        Returns:
            Controller output
        """
        if current_time is None:
            if self.last_time is None:
                dt = 0.01  # Default 10ms
                self.last_time = current_time
            else:
                dt = (current_time - self.last_time).total_seconds()
                self.last_time = current_time
        else:
            if self.last_time is None:
                dt = 0.01
            else:
                dt = current_time - self.last_time
            self.last_time = current_time
        
        # PID terms
        p_term = self.kp * error
        
        self.integral += error * dt
        i_term = self.ki * self.integral
        
        if dt > 0:
            d_term = self.kd * (error - self.prev_error) / dt
        else:
            d_term = 0
        
        self.prev_error = error
        
        # Total output
        output = p_term + i_term + d_term
        
        # Clamp output
        output = np.clip(output, self.min_output, self.max_output)
        
        return output
    
    def reset(self):
        """Reset controller state"""
        self.integral = 0.0
        self.prev_error = 0.0
        self.last_time = None


class TrajectoryTrackingController:
    """
    PID-based trajectory tracking controller
    Follows a planned path with distance and heading control
    """
    
    def __init__(self,
                 max_linear_speed=0.5,
                 max_angular_speed=1.0,
                 lookahead_distance=0.3,
                 goal_tolerance=0.1):
        """
        Initialize trajectory tracking controller
        
        Args:
            max_linear_speed: Maximum linear velocity
            max_angular_speed: Maximum angular velocity
            lookahead_distance: Distance to next waypoint
            goal_tolerance: Distance tolerance to goal
        """
        self.max_linear_speed = max_linear_speed
        self.max_angular_speed = max_angular_speed
        self.lookahead_distance = lookahead_distance
        self.goal_tolerance = goal_tolerance
        
        # PID controllers
        # Linear velocity: based on distance to path
        self.linear_pid = PIDController(
            kp=1.0, ki=0.1, kd=0.2,
            max_output=max_linear_speed,
            min_output=0.0
        )
        
        # Angular velocity: based on heading error
        self.angular_pid = PIDController(
            kp=2.0, ki=0.05, kd=0.3,
            max_output=max_angular_speed,
            min_output=-max_angular_speed
        )
        
        # State
        self.current_position = np.array([0.0, 0.0])
        self.current_heading = 0.0
        self.waypoint_path = []
        self.current_waypoint_idx = 0
        
        # Publishers/Subscribers
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        rospy.Subscriber('/odom', Odometry, self._odom_callback)
        rospy.Subscriber('/plan', Path, self._path_callback)
        
        print("[TrajectoryController] Initialized")
    
    def _odom_callback(self, msg):
        """Update position and heading"""
        self.current_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        ])
        
        # Extract yaw
        quat = msg.pose.pose.orientation
        siny_cosp = 2 * (quat.w * quat.z + quat.x * quat.y)
        cosy_cosp = 1 - 2 * (quat.y**2 + quat.z**2)
        self.current_heading = math.atan2(siny_cosp, cosy_cosp)
    
    def _path_callback(self, msg):
        """Update path to follow"""
        self.waypoint_path = [
            np.array([p.pose.position.x, p.pose.position.y])
            for p in msg.poses
        ]
        self.current_waypoint_idx = 0
    
    def get_target_waypoint(self):
        """Get next waypoint to reach"""
        if not self.waypoint_path:
            return None
        
        if self.current_waypoint_idx >= len(self.waypoint_path):
            return self.waypoint_path[-1]
        
        return self.waypoint_path[self.current_waypoint_idx]
    
    def distance_to_goal(self):
        """Distance to final goal"""
        if not self.waypoint_path:
            return float('inf')
        return np.linalg.norm(self.current_position - self.waypoint_path[-1])
    
    def update_control(self):
        """
        Compute control commands
        
        Returns:
            (linear_velocity, angular_velocity)
        """
        target_waypoint = self.get_target_waypoint()
        
        if target_waypoint is None:
            return 0.0, 0.0
        
        # Vector to target
        to_target = target_waypoint - self.current_position
        distance_to_target = np.linalg.norm(to_target)
        
        # Update waypoint if reached
        if distance_to_target < self.lookahead_distance:
            if self.current_waypoint_idx < len(self.waypoint_path) - 1:
                self.current_waypoint_idx += 1
                target_waypoint = self.waypoint_path[self.current_waypoint_idx]
                to_target = target_waypoint - self.current_position
                distance_to_target = np.linalg.norm(to_target)
        
        # Desired heading
        desired_heading = math.atan2(to_target[1], to_target[0])
        
        # Heading error (normalized to [-pi, pi])
        heading_error = desired_heading - self.current_heading
        heading_error = math.atan2(math.sin(heading_error), math.cos(heading_error))
        
        # Linear velocity: based on distance to target
        linear_vel = self.linear_pid.update(distance_to_target)
        
        # Angular velocity: based on heading error
        angular_vel = self.angular_pid.update(heading_error)
        
        return linear_vel, angular_vel
    
    def compute_trajectory_error(self):
        """Compute current trajectory tracking error"""
        if not self.waypoint_path or self.current_waypoint_idx >= len(self.waypoint_path):
            return 0.0
        
        # Cross-track error: perpendicular distance to path segment
        prev_waypoint = self.waypoint_path[max(0, self.current_waypoint_idx - 1)]
        curr_waypoint = self.waypoint_path[self.current_waypoint_idx]
        
        # Vector along path
        path_vec = curr_waypoint - prev_waypoint
        path_length = np.linalg.norm(path_vec)
        
        if path_length == 0:
            return np.linalg.norm(self.current_position - curr_waypoint)
        
        # Vector from path start to robot
        robot_vec = self.current_position - prev_waypoint
        
        # Cross product (2D)
        cross = abs(path_vec[0] * robot_vec[1] - path_vec[1] * robot_vec[0])
        
        return cross / path_length


class ObstacleAvoidanceController:
    """
    Obstacle avoidance using laser scan data
    Uses potential field method with repulsive forces
    """
    
    def __init__(self,
                 safety_distance=0.5,
                 max_avoidance_speed=0.5):
        """
        Initialize obstacle avoidance controller
        
        Args:
            safety_distance: Minimum safe distance from obstacles
            max_avoidance_speed: Maximum speed during avoidance
        """
        self.safety_distance = safety_distance
        self.max_avoidance_speed = max_avoidance_speed
        
        self.laser_ranges = None
        self.laser_angles = None
        
        rospy.Subscriber('/scan', LaserScan, self._laser_callback)
    
    def _laser_callback(self, msg):
        """Process laser scan"""
        self.laser_ranges = np.array(msg.ranges)
        
        # Replace inf values
        max_range = msg.range_max
        self.laser_ranges = np.clip(self.laser_ranges, 0, max_range)
        
        # Compute angles
        num_beams = len(self.laser_ranges)
        self.laser_angles = np.linspace(
            msg.angle_min,
            msg.angle_max,
            num_beams
        )
    
    def compute_avoidance_command(self, desired_linear, desired_angular):
        """
        Modulate velocity commands based on obstacles
        
        Args:
            desired_linear: Desired linear velocity
            desired_angular: Desired angular velocity
        
        Returns:
            (adjusted_linear, adjusted_angular)
        """
        if self.laser_ranges is None:
            return desired_linear, desired_angular
        
        # Find closest obstacle in front
        front_range = 60  # Degrees
        front_indices = np.where(np.abs(self.laser_angles) <= np.radians(front_range))[0]
        
        if len(front_indices) == 0:
            return desired_linear, desired_angular
        
        min_distance = np.min(self.laser_ranges[front_indices])
        min_angle = self.laser_angles[np.argmin(self.laser_ranges[front_indices])]
        
        # Linear velocity modulation
        if min_distance < self.safety_distance:
            # Scale down velocity based on distance
            speed_factor = min_distance / self.safety_distance
            adjusted_linear = desired_linear * max(0, speed_factor)
        else:
            adjusted_linear = desired_linear
        
        # Angular velocity modulation (avoid obstacle)
        if min_distance < self.safety_distance * 2:
            # Turn away from obstacle
            avoidance_angular = -np.sign(min_angle) * 0.5
            adjusted_angular = desired_angular + avoidance_angular
            adjusted_angular = np.clip(adjusted_angular, -1.0, 1.0)
        else:
            adjusted_angular = desired_angular
        
        return adjusted_linear, adjusted_angular
    
    def is_collision_imminent(self):
        """Check if collision is about to happen"""
        if self.laser_ranges is None:
            return False
        
        min_distance = np.min(self.laser_ranges[~np.isinf(self.laser_ranges)])
        return min_distance < 0.25


class CombinedNavigationController:
    """
    Combines trajectory tracking and obstacle avoidance
    """
    
    def __init__(self):
        self.trajectory_controller = TrajectoryTrackingController()
        self.obstacle_controller = ObstacleAvoidanceController()
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        
        self.rate = rospy.Rate(10)  # 10 Hz
    
    def control_loop(self):
        """Main control loop"""
        print("[CombinedController] Starting control loop")
        
        while not rospy.is_shutdown():
            # Get trajectory tracking commands
            linear_vel, angular_vel = self.trajectory_controller.update_control()
            
            # Apply obstacle avoidance
            linear_vel, angular_vel = self.obstacle_controller.compute_avoidance_command(
                linear_vel, angular_vel
            )
            
            # Publish commands
            twist = Twist()
            twist.linear.x = linear_vel
            twist.angular.z = angular_vel
            self.cmd_vel_pub.publish(twist)
            
            # Log
            error = self.trajectory_controller.compute_trajectory_error()
            print(f"[Controller] v={linear_vel:.2f} m/s, w={angular_vel:.2f} rad/s, error={error:.3f}m")
            
            self.rate.sleep()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run navigation controller')
    parser.add_argument('--controller', type=str, default='combined',
                       choices=['trajectory', 'obstacle', 'combined'],
                       help='Controller type')
    
    args = parser.parse_args()
    
    rospy.init_node('navigation_controller', anonymous=True)
    
    if args.controller == 'trajectory':
        controller = TrajectoryTrackingController()
    elif args.controller == 'obstacle':
        controller = ObstacleAvoidanceController()
    else:  # combined
        controller = CombinedNavigationController()
        controller.control_loop()
        return
    
    print(f"[Main] Running {args.controller} controller")
    rospy.spin()


if __name__ == "__main__":
    main()
