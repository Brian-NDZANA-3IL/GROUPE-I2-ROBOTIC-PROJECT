#!/usr/bin/env python3
"""
Reinforcement Learning Environment for TurtleBot3 Navigation
Handles state representation, action execution, and reward computation
"""

import numpy as np
import rospy
import gymnasium as gym
from gymnasium import spaces
from geometry_msgs.msg import Twist, Pose2D
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from std_srvs.srv import Empty
import math
from collections import deque
import time


class TurtleBot3NavEnv(gym.Env):
    """
    Gymnasium environment wrapper for TurtleBot3 navigation
    State: [goal_distance, goal_angle, min_laser_distance, 8 laser sectors]
    Action: Forward, Left, Right, Backward
    Reward: Distance progress - collision penalty + goal bonus
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 10}
    
    def __init__(self, 
                 max_steps=500,
                 max_distance=5.0,
                 goal_threshold=0.3,
                 collision_threshold=0.25):
        """
        Initialize the TurtleBot3 Navigation Environment
        
        Args:
            max_steps: Maximum steps per episode
            max_distance: Maximum goal distance (m)
            goal_threshold: Distance to goal for success (m)
            collision_threshold: Distance for collision (m)
        """
        super().__init__()
        
        # Environment parameters
        self.max_steps = max_steps
        self.max_distance = max_distance
        self.goal_threshold = goal_threshold
        self.collision_threshold = collision_threshold
        
        # Robot state
        self.current_position = np.array([0.0, 0.0])
        self.current_angle = 0.0
        self.goal_position = np.array([1.0, 1.0])
        self.laser_ranges = np.ones(12) * self.max_distance
        
        # Episode tracking
        self.step_count = 0
        self.episode_distance_traveled = 0.0
        self.last_position = np.array([0.0, 0.0])
        self.distance_history = deque(maxlen=10)
        
        # Action space: 0=stop, 1=forward, 2=left, 3=right, 4=backward
        self.action_space = spaces.Discrete(5)
        
        # State space: goal_distance, goal_angle, min_laser, 12 laser sectors
        self.observation_space = spaces.Box(
            low=np.array([0, -np.pi, 0] + [0]*12),
            high=np.array([self.max_distance, np.pi, self.max_distance]*1 + [self.max_distance]*12),
            dtype=np.float32
        )
        
        # ROS publishers and subscribers
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)
        self.reset_pub = rospy.Publisher('/reset_simulation', Empty, queue_size=1)
        
        rospy.Subscriber('/odom', Odometry, self._odom_callback)
        rospy.Subscriber('/scan', LaserScan, self._laser_callback)
        rospy.Subscriber('/goal_pose', Pose2D, self._goal_callback)
        
        # Initialize ROS node if not already
        try:
            rospy.get_node_uri()
        except:
            rospy.init_node('rl_navigation_env', anonymous=True)
        
        # Give subscribers time to connect
        time.sleep(1.0)
        
        print("[RL_ENV] TurtleBot3 Navigation Environment initialized")
    
    def _odom_callback(self, msg):
        """Update robot position and orientation from odometry"""
        self.current_position = np.array([
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        ])
        
        # Extract yaw from quaternion
        quat = msg.pose.pose.orientation
        siny_cosp = 2 * (quat.w * quat.z + quat.x * quat.y)
        cosy_cosp = 1 - 2 * (quat.y**2 + quat.z**2)
        self.current_angle = math.atan2(siny_cosp, cosy_cosp)
    
    def _laser_callback(self, msg):
        """Process laser scan data into sectors"""
        ranges = np.array(msg.ranges)
        # Replace inf with max_distance
        ranges = np.clip(ranges, 0, self.max_distance)
        
        # Downsample 360 beams to 12 sectors (30 degrees each)
        num_sectors = 12
        sector_size = len(ranges) // num_sectors
        self.laser_ranges = np.array([
            np.min(ranges[i*sector_size:(i+1)*sector_size])
            for i in range(num_sectors)
        ])
    
    def _goal_callback(self, msg):
        """Update goal position from ROS topic"""
        self.goal_position = np.array([msg.x, msg.y])
    
    def _get_state(self):
        """
        Compute state representation
        Returns: [goal_distance, goal_angle, min_laser, 12_laser_sectors]
        """
        # Goal relative to robot
        goal_rel = self.goal_position - self.current_position
        goal_distance = np.linalg.norm(goal_rel)
        goal_angle = math.atan2(goal_rel[1], goal_rel[0]) - self.current_angle
        # Normalize angle to [-pi, pi]
        goal_angle = math.atan2(math.sin(goal_angle), math.cos(goal_angle))
        
        min_laser = np.min(self.laser_ranges)
        
        state = np.array(
            [goal_distance, goal_angle, min_laser] + list(self.laser_ranges),
            dtype=np.float32
        )
        return state
    
    def _execute_action(self, action):
        """Execute action and return velocity command"""
        twist = Twist()
        
        if action == 0:  # Stop
            twist.linear.x = 0.0
            twist.angular.z = 0.0
        elif action == 1:  # Forward
            twist.linear.x = 0.3
            twist.angular.z = 0.0
        elif action == 2:  # Left
            twist.linear.x = 0.15
            twist.angular.z = 0.5
        elif action == 3:  # Right
            twist.linear.x = 0.15
            twist.angular.z = -0.5
        elif action == 4:  # Backward
            twist.linear.x = -0.2
            twist.angular.z = 0.0
        
        self.cmd_vel_pub.publish(twist)
        return twist
    
    def _compute_reward(self, action, goal_distance, collision):
        """
        Reward function:
        - Positive reward for getting closer to goal
        - Negative reward for collision
        - Bonus for reaching goal
        - Small penalty for inefficient actions
        """
        reward = 0.0
        
        # Distance reward (decrease = positive reward)
        if len(self.distance_history) > 0:
            prev_distance = self.distance_history[-1]
            distance_progress = prev_distance - goal_distance
            reward += distance_progress * 1.0  # Scale reward
        
        # Collision penalty
        if collision:
            reward -= 10.0
        
        # Goal bonus
        if goal_distance < self.goal_threshold:
            reward += 50.0
        
        # Small step penalty to encourage efficiency
        reward -= 0.01
        
        return reward
    
    def step(self, action):
        """
        Execute one step of the environment
        
        Returns:
            observation, reward, terminated, truncated, info
        """
        self.step_count += 1
        
        # Execute action
        self._execute_action(action)
        time.sleep(0.1)  # Wait for action to take effect
        
        # Get new state
        state = self._get_state()
        goal_distance = state[0]
        min_laser = state[2]
        
        # Check termination conditions
        collision = min_laser < self.collision_threshold
        goal_reached = goal_distance < self.goal_threshold
        max_steps_reached = self.step_count >= self.max_steps
        
        # Record distance
        self.distance_history.append(goal_distance)
        
        # Compute reward
        reward = self._compute_reward(action, goal_distance, collision)
        
        # Determine termination
        terminated = collision or goal_reached
        truncated = max_steps_reached
        
        # Info dict
        info = {
            "goal_distance": float(goal_distance),
            "collision": collision,
            "goal_reached": goal_reached,
            "step": self.step_count
        }
        
        return state, reward, terminated, truncated, info
    
    def reset(self, seed=None):
        """
        Reset environment and robot position
        
        Returns:
            observation, info
        """
        super().reset(seed=seed)
        
        # Reset ROS simulation
        try:
            reset_service = rospy.ServiceProxy('/gazebo/reset_world', Empty)
            reset_service()
        except:
            print("Warning: Could not reset Gazebo simulation")
        
        # Reset internal state
        self.step_count = 0
        self.distance_history.clear()
        self.current_position = np.array([0.0, 0.0])
        self.current_angle = 0.0
        
        # Set random goal
        self.goal_position = np.random.uniform(-2.0, 2.0, 2)
        
        # Wait for state updates
        time.sleep(0.5)
        
        # Get initial state
        state = self._get_state()
        info = {"initial_distance": float(state[0])}
        
        return state, info
    
    def render(self):
        """Render environment (can be extended with visualization)"""
        print(f"Position: {self.current_position}, Goal: {self.goal_position}")
        print(f"Laser ranges (min={np.min(self.laser_ranges):.2f}): {self.laser_ranges}")
    
    def set_goal(self, goal_x, goal_y):
        """Set goal position"""
        self.goal_position = np.array([goal_x, goal_y])
    
    def close(self):
        """Clean up resources"""
        twist = Twist()
        self.cmd_vel_pub.publish(twist)
        super().close()


if __name__ == "__main__":
    # Test environment
    env = TurtleBot3NavEnv()
    
    print("Testing environment...")
    obs, info = env.reset()
    print(f"Initial observation shape: {obs.shape}")
    print(f"Initial observation: {obs}")
    
    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        print(f"Step {i}, Action: {action}, Reward: {reward:.2f}, Info: {info}")
        
        if terminated or truncated:
            break
    
    env.close()
