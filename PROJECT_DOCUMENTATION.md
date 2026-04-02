# 🤖 Robot Navigation System - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Installation & Setup](#installation--setup)
4. [Component Guide](#component-guide)
5. [How to Test Each Component](#how-to-test-each-component)
6. [Taking Screenshots for Report](#taking-screenshots-for-report)
7. [Live Demonstration Guide](#live-demonstration-guide)
8. [Performance Comparison](#performance-comparison)
9. [Troubleshooting](#troubleshooting)

---

## Project Overview

This project implements two autonomous navigation paradigms for TurtleBot3 robots:
- **Classical Navigation**: Planner → Path → Controller → Robot Motion
- **Learning-Based Navigation**: State → RL Policy → Robot Motion

### Objectives
✅ Implement and compare path planning algorithms (A*, Dijkstra, Greedy Best-First)
✅ Design trajectory tracking controller with obstacle avoidance
✅ Implement Deep Q-Network for learning-based navigation
✅ Benchmark performance across both paradigms
✅ Analyze computational cost and path optimality

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     NAVIGATION SYSTEM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────┐        ┌──────────────────────┐       │
│  │ CLASSICAL NAVIGATION │        │   RL NAVIGATION      │       │
│  ├──────────────────────┤        ├──────────────────────┤       │
│  │ • Path Planning      │        │ • State Representation│      │
│  │   - A*               │        │ • DQN Agent          │       │
│  │   - Dijkstra         │        │ • Policy Network     │       │
│  │   - Greedy BFS       │        │ • Reward Function    │       │
│  │                      │        │                      │       │
│  │ • Controllers        │        │ • Training Pipeline  │       │
│  │   - PID Tracking     │        │ • Exploration        │       │
│  │   - Obs. Avoidance   │        │                      │       │
│  └──────┬───────────────┘        └──────┬───────────────┘       │
│         │                                │                       │
│         ├────────────────┬───────────────┘                       │
│         │                │                                       │
│         v                v                                       │
│  ┌─────────────────────────────────────┐                        │
│  │    Command Velocity Controller      │                        │
│  │    (/cmd_vel topic)                 │                        │
│  └────────────────┬────────────────────┘                        │
│                   │                                              │
│                   v                                              │
│  ┌─────────────────────────────────────┐                        │
│  │   TurtleBot3 (Physical/Gazebo)      │                        │
│  └─────────────────────────────────────┘                        │
│                                                                   │
│  ┌─────────────────────────────────────┐                        │
│  │   Sensors: Lidar, Odometry          │                        │
│  └─────────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Installation & Setup

### Prerequisites
```bash
# ROS Installation (if needed)
# Ubuntu 20.04: ROS Noetic
# Ubuntu 22.04: ROS Humble

# Python packages
pip install gymnasium torch numpy matplotlib scipy scikit-image

# ROS packages
sudo apt-get install ros-noetic-turtlebot3*
sudo apt-get install ros-noetic-gmapping
sudo apt-get install ros-noetic-navigation
```

### Setup Your Environment
```bash
cd /home/ubuntu/workspace
source devel/setup.bash

# Set TurtleBot3 model
export TURTLEBOT3_MODEL=burger

# Build the project
catkin_make
```

### Verify Installation
```bash
# List all custom packages
rospack list | grep custom

# Check Python modules
python3 -c "from rl_environment import TurtleBot3NavEnv; print('✓ RL modules OK')"
python3 -c "from astar import AStar; print('✓ Planning modules OK')"
```

---

## Component Guide

### 1. Path Planning Algorithms

**Files:**
- `astar.py` - A* algorithm with Euclidean heuristic
- `dijkstra.py` - Dijkstra's algorithm
- `greedy.py` - Greedy Best-First Search
- `planner_node.py` - ROS integration

**Key Features:**
- Grid-based pathfinding
- 4-directional and 8-directional movement
- ROS topic-based integration
- Performance timing built-in

**Usage:**
```python
from astar import AStar
planner = AStar(grid=occupancy_grid)
path = planner.plan(start=(1,1), goal=(10,10))
```

### 2. Navigation Controllers

**Files:**
- `navigation_controller.py` - PID + Obstacle Avoidance

**Components:**
```
PIDController
├─ Proportional term
├─ Integral term (with anti-windup)
└─ Derivative term

TrajectoryTrackingController
├─ Waypoint following
├─ Cross-track error computation
└─ Smooth heading control

ObstacleAvoidanceController
├─ Laser-based collision detection
├─ Potential field method
└─ Emergency stop logic
```

**Usage:**
```python
from navigation_controller import TrajectoryTrackingController
controller = TrajectoryTrackingController(
    max_linear_speed=0.5,
    lookahead_distance=0.3
)
linear_vel, angular_vel = controller.update_control()
```

### 3. Reinforcement Learning

**Files:**
- `rl_environment.py` - Gymnasium environment wrapper
- `rl_agent.py` - DQN and Q-Learning agents
- `rl_training.py` - Training pipeline

**State Space (15D):**
```
[goal_distance, goal_angle, min_laser_distance, laser_sector_0, ..., laser_sector_11]
```

**Action Space (5 discrete):**
```
0: Stop
1: Forward
2: Left turn
3: Right turn
4: Backward
```

**Reward Function:**
```
r = distance_progress - collision_penalty + goal_bonus - step_penalty
```

---

## How to Test Each Component

### Test 1: Path Planning Algorithms

**Objective:** Verify all three algorithms work correctly and compare performance

```bash
# Terminal 1: Start ROS Master
roscore

# Terminal 2: Launch Gazebo simulation
source devel/setup.bash
export TURTLEBOT3_MODEL=burger
roslaunch custom_planners labyrinthe_gazebo.launch

# Terminal 3: Run unit tests
cd ~/workspace/src/custom_planners/scripts
python3 integration_tests.py TestPlanningAlgorithms

# Expected Output:
# ✓ test_astar_finds_path: PASS
# ✓ test_dijkstra_finds_path: PASS
# ✓ test_greedy_finds_path: PASS
# ✓ algorithm_comparison: [timing and path length comparison]
```

**📸 Screenshots to Take:**
1. Terminal showing test results
2. RViz with planned paths (one for each algorithm)
3. Performance timing comparison graph

### Test 2: SLAM Mapping

**Objective:** Generate and save environment maps using gmapping

```bash
# Terminal 1: Start ROS Master
roscore

# Terminal 2: Launch simulation
source devel/setup.bash
export TURTLEBOT3_MODEL=burger
roslaunch custom_planners labyrinthe_gazebo.launch

# Terminal 3: Launch SLAM
roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping

# Terminal 4: Manually explore or use provided exploration script
python3 scripts/exploration_script.py

# Terminal 5: Save map when done exploring
rosrun map_server map_saver -f ~/workspace/maps/my_test_map
```

**📸 Screenshots to Take:**
1. RViz showing SLAM mapping in progress
2. Final generated map (OccupancyGrid visualization)
3. Saved map files verification

### Test 3: Navigation Controller

**Objective:** Test trajectory tracking and obstacle avoidance

```bash
# Terminal 1: Start ROS Master
roscore

# Terminal 2: Launch navigation with controller
source devel/setup.bash
export TURTLEBOT3_MODEL=burger
roslaunch custom_planners custom_navigation.launch \
    planner:=astar \
    use_custom_controller:=true

# Terminal 3: Publish goal
rostopic pub /goal_pose geometry_msgs/Pose2D "x: 2.0
y: 2.0
theta: 0"

# Terminal 4: Monitor trajectory
python3 scripts/navigate_and_record.py
```

**📸 Screenshots to Take:**
1. RViz with robot path overlaid on map
2. Terminal showing trajectory tracking error
3. Collision avoidance in action (if obstacles exist)

### Test 4: Reinforcement Learning Training

**Objective:** Train DQN agent and monitor convergence

```bash
# Terminal 1: ROS Master
roscore

# Terminal 2: Launch simulation (no move_base)
roslaunch custom_worlds labyrinthe.launch

# Terminal 3: Run training
cd ~/workspace/src/custom_planners/scripts
python3 rl_training.py --agent dqn --episodes 100 --eval-freq 10

# Expected Output:
# Episode   10 | Train Reward: -5.23 | Eval Reward:  2.15 | Success Rate: 20.0%
# Episode   20 | Train Reward:  8.42 | Eval Reward: 15.32 | Success Rate: 40.0%
# Episode   30 | Train Reward: 22.18 | Eval Reward: 28.91 | Success Rate: 80.0%
# ...training continues...
```

**📸 Screenshots to Take:**
1. Training progress (episode rewards graph)
2. Success rate convergence
3. Final checkpoint saved confirmation
4. Example trained agent navigation

### Test 5: Performance Benchmarking

**Objective:** Compare classical vs RL navigation

```bash
# Terminal 1: ROS Master
roscore

# Terminal 2: Launch simulation
roslaunch custom_planners labyrinthe_gazebo.launch

# Terminal 3: Run benchmarks
python3 performance_benchmark.py \
    --algorithms astar,dijkstra,greedy \
    --trials 3

# Expected Output:
# ========== PLANNING ALGORITHM BENCHMARKS ==========
# Testing: ASTAR
# ─────────────────────────────────────────────────
#   Goal 1: (1.0, 1.0)
#     ├─ Avg Path Length: 12.45 m
#     ├─ Avg Efficiency: 85.3%
#     ├─ Success Rate: 100%
#     └─ Collision Rate: 0%
#   ...
```

**📸 Screenshots to Take:**
1. Comparison bar charts (all algorithms)
2. Efficiency metrics
3. Execution time comparison
4. Success rates across scenarios

### Test 6: Complete Integration Test

**Objective:** Run entire test suite

```bash
cd ~/workspace/src/custom_planners/scripts
python3 integration_tests.py

# Expected Output:
# ====== ROBOT NAVIGATION INTEGRATION TEST SUITE ======
# test_astar_finds_path ... ok
# test_dijkstra_finds_path ... ok
# test_greedy_finds_path ... ok
# test_pid_controller_stability ... ok
# test_trajectory_error_computation ... ok
# test_metrics_computation ... ok
# test_dqn_agent_creation ... ok
# ...
# Ran 15 tests in 2.3s → OK
```

**📸 Screenshots to Take:**
1. Full test suite results
2. Each test status
3. Summary statistics

---

## Taking Screenshots for Report

### Best Practices for Documentation Photos

**1. RViz Visualization Setup**
```bash
# Use provided RViz config
roslaunch custom_planners rviz.launch

# Key displays to enable:
# □ Map (from map_server)
# □ Path (planned path)
# □ Laser Scan
# □ Odometry/robot footprint
# □ Goal position
```

**2. Screenshot Sequence for Each Section**

**Section 1: Simulation & Environment**
```
Screenshot 1: Gazebo world overview
  - Show: Labyrinthe world, robot, obstacles
  - Command: roslaunch custom_planners labyrinthe_gazebo.launch

Screenshot 2: RVIZ visualization
  - Show: Map, laser scans, coordinate frames
  - Command: roslaunch custom_planners rviz.launch
```

**Section 2: Path Planning**
```
Screenshot 1: A* Algorithm Result
  - RViz with A* planned path highlighted

Screenshot 2: Dijkstra Algorithm Result
  - RViz with Dijkstra planned path highlighted

Screenshot 3: Greedy Best-First Result
  - RViz with Greedy planned path highlighted

Screenshot 4: Performance Comparison
  - Terminal output with timing data
  - Matplotlib figure: benchmark_results.png
```

**Section 3: Navigation Control**
```
Screenshot 1: Trajectory Tracking in Progress
  - RViz showing: actual robot path, desired path, heading vector

Screenshot 2: Obstacle Avoidance Activated
  - RViz showing: robot avoiding obstacle, modified trajectory

Screenshot 3: Controller Metrics
  - Terminal output: trajectory error, velocity commands
```

**Section 4: Reinforcement Learning**
```
Screenshot 1: Training Progress (Rewards)
  - Matplotlib: training_results_dqn.png (episode rewards)

Screenshot 2: Convergence Analysis
  - Matplotlib: success rate over episodes

Screenshot 3: Trained Agent Navigation
  - RViz: trained agent successfully navigating to goal

Screenshot 4: Comparison
  - Matplotlib: classical vs RL performance side-by-side
```

### Recommended Screenshot Resolution
- Minimum: 1280×720 (720p)
- Recommended: 1920×1080 (1080p)
- For high-quality: 2560×1440 (2K)

### Tools for Screenshots
```bash
# Built-in Linux screenshot
gnome-screenshot -a  # Interactive area selection

# ROS RViz recording
# RViz → File → Export... → PNG/Video

# Matplotlib saving
plt.savefig('figure.png', dpi=150, bbox_inches='tight')

# Terminal recording
script terminal_log.txt  # Then exit to stop recording
```

---

## Live Demonstration Guide

### 10-Minute Demo Script

**Minute 0-1: System Overview**
```
"This is a complete autonomous navigation system with two paradigms.
Let me show you how it works..."
```
- Show architecture diagram on slides
- Highlight key components

**Minute 1-3: Simulation Environment**
```bash
# Show Gazebo world
roslaunch custom_planners labyrinthe_gazebo.launch
```
- Point out robot, obstacles, map boundaries
- Explain sensor setup (Lidar, odometry)

**Minute 3-5: Path Planning**
```bash
# Terminal 1: ROS master + Gazebo
# Terminal 2: RViz with path visualization
# Terminal 3: Trigger path planning
python3 test_planner.py --algorithm astar --goal 2.0 2.0
```
- Show A* path being computed
- Explain algorithm parameters
- Discuss optimality

**Minute 5-7: Navigation Control**
```bash
# Terminal with controller active
# Watch robot follow planned path in RViz
# Point out: trajectory tracking error, obstacle avoidance
```
- Demonstrate path following
- Show obstacle detection
- Explain PID control

**Minute 7-9: Reinforcement Learning**
```bash
# Show training progress
cat training_results_dqn.png
# Show trained agent navigating
python3 test_rl_agent.py --load final_agent_dqn.pt
```
- Explain neural network architecture
- Show learning convergence
- Demonstrate learned policy

**Minute 9-10: Performance Comparison**
```bash
# Show performance metrics
cat benchmark_results.png
```
- Compare all algorithms
- Discuss trade-offs
- Conclusions

---

## Performance Comparison

### Metrics Definition

**1. Path Efficiency** = Straight-line distance / Actual path length
```
Optimal path: 100%
Good navigation: > 85%
Fair: 70-85%
Poor: < 70%
```

**2. Success Rate** = Reached goal / Total attempts
```
Target: ≥ 90%
Acceptable: 70-90%
```

**3. Computation Time** = Time to plan + time to execute
```
Real-time capable: < 100ms planning
Acceptable: < 1s planning
```

**4. Collision Rate** = Collisions / Total attempts
```
Target: 0%
Acceptable: < 10%
```

### Expected Results

| Metric | A* | Dijkstra | Greedy | DQN |
|--------|-----|----------|--------|------|
| Path Efficiency | 92% | 95% | 78% | 82% |
| Success Rate | 98% | 100% | 95% | 92% |
| Avg Time | 45ms | 120ms | 8ms | 15ms |
| Collision Rate | 0% | 0% | 5% | 3% |

---

## Troubleshooting

### Common Issues & Solutions

**Issue 1: ROS Connection Error**
```
Error: unable to connect to master at localhost:11311
Solution:
  1. Make sure roscore is running: roscore
  2. Check ROS_MASTER_URI: echo $ROS_MASTER_URI
  3. Network connectivity: ping localhost
```

**Issue 2: No Laser Scan Data**
```
Error: /scan topic empty or not publishing
Solution:
  1. Check Gazebo plugins are loaded
  2. Verify URDF includes lidar
  3. Check LaserScan subscriber active
```

**Issue 3: Path Planning No Solution**
```
Error: Plan not found
Solution:
  1. Lower occupancy threshold
  2. Ensure goal is reachable
  3. Increase grid resolution
```

**Issue 4: RL Training Too Slow**
```
Solution:
  1. Use GPU acceleration (install CUDA)
  2. Reduce state dimensions
  3. Increase batch size
  4. Lower episode time limit
```

**Issue 5: Import Errors**
```
Error: No module named 'gymnasium'
Solution:
  pip install gymnasium torch
  # Or use conda
  conda install gymnasium pytorch
```

---

## Project Structure

```
workspace/
├── src/
│   ├── custom_planners/
│   │   ├── scripts/
│   │   │   ├── astar.py              [A* algorithm]
│   │   │   ├── dijkstra.py           [Dijkstra algorithm]
│   │   │   ├── greedy.py             [Greedy Best-First]
│   │   │   ├── planner_node.py       [ROS planner node]
│   │   │   ├── navigation_controller.py [PID + Obstacle Avoidance]
│   │   │   ├── rl_environment.py     [Gymnasium environment]
│   │   │   ├── rl_agent.py           [DQN & Q-Learning agents]
│   │   │   ├── rl_training.py        [Training pipeline]
│   │   │   ├── performance_benchmark.py [Benchmarking framework]
│   │   │   └── integration_tests.py  [Complete test suite]
│   │   ├── launch/
│   │   │   ├── custom_navigation.launch
│   │   │   ├── labyrinthe_gazebo.launch
│   │   │   └── rviz.launch
│   │   └── CMakeLists.txt
│   ├── custom_worlds/
│   │   ├── worlds/
│   │   │   └── labyrinthe.world
│   │   ├── models/
│   │   └── launch/
│   ├── turtlebot3_simulations/
│   └── ... [other packages]
│
├── maps/
│   ├── labyrinthe_map.pgm/.yaml
│   ├── my_map.pgm/.yaml
│   └── ... [other maps]
│
├── devel/                           [Built files]
├── build/                           [Build directory]
└── README.md                        [This file]
```

---

## Quick Start Checklist

- [ ] Source environment: `source devel/setup.bash`
- [ ] Set robot model: `export TURTLEBOT3_MODEL=burger`
- [ ] Start ROS: `roscore` (Terminal 1)
- [ ] Launch simulation: `roslaunch custom_planners labyrinthe_gazebo.launch` (Terminal 2)
- [ ] Run RViz: `roslaunch custom_planners rviz.launch` (Terminal 3)
- [ ] Test planner: `python3 integration_tests.py TestPlanningAlgorithms` (Terminal 4)
- [ ] Verify controllers: `python3 integration_tests.py TestControllers`
- [ ] Run RL training: `python3 rl_training.py --episodes 50`
- [ ] Benchmark: `python3 performance_benchmark.py`

---

## References

- A* Algorithm: Hart et al. (1968)
- DQN: Mnih et al. (2015)
- ROS Navigation Stack: https://wiki.ros.org/navigation
- TurtleBot3: https://emanual.robotis.com/docs/en/platform/turtlebot3/

**Last Updated:** 2026-03-31
**Version:** 1.0
**For Support:** Check ROS wiki or project GitHub issues

