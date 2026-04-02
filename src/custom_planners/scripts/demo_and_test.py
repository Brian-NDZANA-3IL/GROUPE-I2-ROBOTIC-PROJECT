#!/usr/bin/env python3
"""
Demonstration and Testing Scripts
Provides easy-to-use commands for testing and demonstrating the system
"""

import subprocess
import sys
import os
import time
import argparse
from pathlib import Path


class RobotNavigationDemo:
    """Orchestrates demonstrations"""
    
    def __init__(self):
        self.workspace_dir = Path(os.path.expanduser("~/workspace"))
        self.scripts_dir = self.workspace_dir / "src/custom_planners/scripts"
    
    def run_command(self, cmd, description="", background=False):
        """Execute command with logging"""
        print(f"\n{'='*70}")
        if description:
            print(f"📌 {description}")
        print(f"{'='*70}")
        print(f"$ {cmd}\n")
        
        if background:
            subprocess.Popen(cmd, shell=True)
            time.sleep(2)
        else:
            subprocess.run(cmd, shell=True)
    
    def demo_path_planning(self):
        """Demonstrate path planning algorithms"""
        print("\n" + "▓"*70)
        print("DEMO 1: PATH PLANNING ALGORITHMS")
        print("▓"*70)
        
        print("""
This demo shows three path planning algorithms:
1. A* - Uses heuristic to find optimal path (fastest)
2. Dijkstra - Guarantees optimal path but slower
3. Greedy Best-First - Very fast but may not be optimal

Requirements:
- ROS Master running (roscore)
- Gazebo simulation running
        """)
        
        input("Press Enter to start...")
        
        os.chdir(self.scripts_dir)
        self.run_command(
            "python3 integration_tests.py TestPlanningAlgorithms",
            "Running Path Planning Tests"
        )
        
        print("""
📊 ANALYSIS:
- Look at the path lengths (shorter is better)
- Compare execution times (faster is better)
- All algorithms should find valid paths
        """)
    
    def demo_navigation_control(self):
        """Demonstrate navigation controller"""
        print("\n" + "▓"*70)
        print("DEMO 2: NAVIGATION CONTROL (PID + Obstacle Avoidance)")
        print("▓"*70)
        
        print("""
This demo shows:
1. PID-based trajectory tracking
2. Cross-track error computation
3. Obstacle avoidance with laser input

The robot will:
- Follow a planned path
- Correct heading and position errors
- Avoid obstacles autonomously

Requirements:
- ROS Master running
- Gazebo with robot spawned
        """)
        
        input("Press Enter to start...")
        
        print("""
🚀 Starting demonstration...
The robot should now follow the path while avoiding obstacles.

Monitor the terminal for:
- Velocity commands (linear & angular)
- Trajectory error metrics
- Collision warnings
        """)
        
        os.chdir(self.scripts_dir)
        self.run_command(
            "python3 navigation_controller.py --controller combined",
            "Running Combined Navigation Controller"
        )
    
    def demo_slam_mapping(self):
        """Demonstrate SLAM and mapping"""
        print("\n" + "▓"*70)
        print("DEMO 3: SLAM MAPPING with gmapping")
        print("▓"*70)
        
        print("""
This demo shows:
1. Real-time simultaneous localization and mapping
2. Map generation from laser scans
3. Robot localization within the map

Commands to execute:
        """)
        
        print("""
Terminal 1: Start ROS Master
$ roscore

Terminal 2: Launch Gazebo simulation
$ source devel/setup.bash
$ export TURTLEBOT3_MODEL=burger
$ roslaunch custom_planners labyrinthe_gazebo.launch

Terminal 3: Launch SLAM
$ roslaunch turtlebot3_slam turtlebot3_slam.launch slam_methods:=gmapping

Terminal 4: Explore environment
$ python3 explore_robot.py

Terminal 5: Save map when done
$ rosrun map_server map_saver -f maps/test_map
        """)
        
        input("Press Enter after following instructions...")
        print("✅ SLAM demonstration complete!")
    
    def demo_reinforcement_learning(self, episodes=50):
        """Demonstrate RL training"""
        print("\n" + "▓"*70)
        print("DEMO 4: REINFORCEMENT LEARNING - DQN Training")
        print("▓"*70)
        
        print(f"""
This demo trains a Deep Q-Network to navigate:
- Episodes: {episodes}
- State space: 15D (goal distance, angle, laser sectors)
- Action space: 5 (forward, backward, left, right, stop)
- Network: 2 hidden layers (128 neurons each)

The agent learns to:
✓ Reach goal positions
✓ Avoid collisions
✓ Navigate efficiently

This will take ~{episodes//10} minutes...
        """)
        
        input("Press Enter to start training...")
        
        os.chdir(self.scripts_dir)
        self.run_command(
            f"python3 rl_training.py --agent dqn --episodes {episodes} --eval-freq 5",
            f"Training DQN Agent ({episodes} episodes)"
        )
        
        print("""
📈 RESULTS:
- Check training_results_dqn.png for convergence plots
- Success rate should increase over time
- Model saved to final_agent_dqn.pt
        """)
    
    def demo_performance_comparison(self, trials=1):
        """Benchmark all algorithms"""
        print("\n" + "▓"*70)
        print("DEMO 5: PERFORMANCE BENCHMARKING")
        print("▓"*70)
        
        print(f"""
Comparing performance of all navigation approaches:
- A* Algorithm
- Dijkstra Algorithm  
- Greedy Best-First
- DQN (Reinforcement Learning)

Metrics:
✓ Path efficiency
✓ Execution time
✓ Success rate
✓ Collision avoidance
✓ Smoothness of motion

Running {trials} trial(s) per algorithm...
        """)
        
        input("Press Enter to start benchmarking...")
        
        os.chdir(self.scripts_dir)
        self.run_command(
            f"python3 performance_benchmark.py --algorithms astar,dijkstra,greedy --trials {trials}",
            "Running Performance Benchmarks"
        )
        
        print("""
📊 Results saved to:
- benchmark_results.json (detailed metrics)
- benchmark_results.png (comparison charts)

Compare classical vs learning approaches!
        """)
    
    def run_complete_tests(self):
        """Run complete integration test suite"""
        print("\n" + "▓"*70)
        print("COMPLETE INTEGRATION TEST SUITE")
        print("▓"*70)
        
        print("""
Running all tests:
1. Path Planning (A*, Dijkstra, Greedy)
2. Controllers (PID, Obstacle Avoidance)
3. Metrics Collection
4. RL Components (DQN, Q-Learning)
5. Full Integration Tests

Expected duration: 2-3 minutes
        """)
        
        input("Press Enter to start...")
        
        os.chdir(self.scripts_dir)
        self.run_command(
            "python3 integration_tests.py",
            "Running Complete Integration Tests"
        )
    
    def prepare_for_presentation(self):
        """Prepare everything for the 20-minute presentation"""
        print("\n" + "▓"*70)
        print("PRESENTATION PREPARATION CHECKLIST")
        print("▓"*70)
        
        checklist = """
PRE-DEMONSTRATION SETUP:

Environment:
☐ Ensure ROS environment is sourced: source devel/setup.bash
☐ Set robot model: export TURTLEBOT3_MODEL=burger
☐ Start ROS Master: roscore (in a terminal)

Gazebo:
☐ Launch simulation: roslaunch custom_planners labyrinthe_gazebo.launch
☐ Check robot spawns correctly
☐ Verify sensors (lidar shows data)

RViz:
☐ Launch RViz: roslaunch custom_planners rviz.launch
☐ Verify all displays are working
☐ Check map, laser, robot footprint are visible

Pre-compute Results:
☐ Run path planning tests
☐ Run performance benchmarks
☐ Have screenshots ready

20-MINUTE PRESENTATION FLOW:
├─ 0:00-2:00   System Overview & Architecture
├─ 2:00-4:00   Simulation & Environment
├─ 4:00-7:00   Path Planning Algorithms (live demo)
├─ 7:00-10:00  Navigation Control (live demo)
├─ 10:00-14:00 Reinforcement Learning (show training results)
├─ 14:00-18:00 Performance Comparison & Analysis
├─ 18:00-20:00 Conclusions & Questions

TECHNICAL TALKING POINTS:

Path Planning:
- "A* uses heuristic to find optimal paths efficiently"
- "Dijkstra guarantees global optimality but is slower"
- "Greedy is fastest but may not be optimal"

Navigation Control:
- "PID controller maintains desired trajectory"
- "Obstacle avoidance modulates velocity based on laser"
- "Cross-track error shows how well we follow the path"

Reinforcement Learning:
- "DQN learns navigation policy through trial and error"
- "Reward function encourages reaching goals and avoiding collisions"
- "Performance improves with more training episodes"

Performance:
- "Classical methods are deterministic and fast"
- "RL methods are adaptive and improve over time"
- "Hybrid approach could combine benefits of both"

SLIDES SHOULD INCLUDE:
1. Title slide
2. Problem statement & objectives
3. Architecture diagram
4. System components (with code snippets)
5. Algorithm pseudocode
6. Simulation environment screenshots
7. Path planning comparison plots
8. Navigation control metrics
9. RL training curves
10. Performance benchmark results
11. Conclusions & future work
12. References
        """
        
        print(checklist)
        print("\n" + "="*70)
        print("🎯 Ready for presentation!")
        print("="*70 + "\n")
    
    def show_file_structure(self):
        """Show project file structure"""
        print("\n" + "▓"*70)
        print("PROJECT FILE STRUCTURE")
        print("▓"*70)
        
        structure = """
workspace/
├── 📄 PROJECT_DOCUMENTATION.md        [Complete guide]
├── 📄 PROJECT_INVENTORY.md            [Component list]
├── 📊 frames.gv                       [TF tree visualization]
│
├── src/
│   ├── custom_planners/
│   │   ├── scripts/
│   │   │   ├── ✅ astar.py              [A* implementation]
│   │   │   ├── ✅ dijkstra.py           [Dijkstra implementation]
│   │   │   ├── ✅ greedy.py             [Greedy BFS implementation]
│   │   │   ├── ✅ planner_node.py       [ROS planner node]
│   │   │   ├── ✅ navigation_controller.py [PID + Obstacle Avoidance]
│   │   │   ├── ✅ rl_environment.py     [Gymnasium environment]
│   │   │   ├── ✅ rl_agent.py           [DQN & Q-Learning]
│   │   │   ├── ✅ rl_training.py        [Training pipeline]
│   │   │   ├── ✅ performance_benchmark.py [Benchmarking]
│   │   │   ├── ✅ integration_tests.py  [Test suite]
│   │   │   ├── 📜 test_planners.py     [Unit tests]
│   │   │   └── demo_and_test.py        [THIS FILE]
│   │   ├── launch/
│   │   │   ├── 📝 custom_navigation.launch
│   │   │   ├── 📝 labyrinthe_gazebo.launch
│   │   │   └── 📝 rviz.launch
│   │   ├── config/
│   │   │   └── 📋 navigation config files
│   │   └── CMakeLists.txt
│   │
│   ├── custom_worlds/
│   │   ├── worlds/
│   │   │   └── 🌍 labyrinthe.world  [Simulation environment]
│   │   └── models/                    [Object models]
│   │
│   ├── turtlebot3_simulations/       [TurtleBot3 URDF]
│   └── ... [other packages]
│
├── maps/
│   ├── 🗺️  labyrinthe_map.pgm/.yaml   [Maze environment]
│   ├── 🗺️  my_map.pgm/.yaml           [Test map]
│   ├── 🗺️  ma_nouvelle_map.pgm/.yaml  [Environment variant]
│   └── 🗺️  ma_nouvel1_map.pgm/.yaml   [Environment variant 2]
│
├── devel/                             [Built files]
├── build/                             [Build directory]
│
┣ 📊 Results/
│   ├── training_results_dqn.png       [Training convergence]
│   ├── benchmark_results.png          [Performance comparison]
│   ├── benchmark_results.json         [Detailed metrics]
│   └── presentation_images/           [Screenshots for report]
│
└── scripts/
    ├── 🚀 demo_and_test.py            [This demonstration script]
    ├── check_tf_chain.py              [TF debugging]
    └── run_astar_pipeline.sh          [Example pipeline]

LEGEND:
✅ Newly implemented complete
📄 Documentation
📊 Results/outputs
📝 Configuration/Launch files
📋 Config files
🌍 Simulation environment
🗺️  Map files
🚀 Executable scripts
        """
        
        print(structure)
    
    def main(self):
        """Main menu"""
        parser = argparse.ArgumentParser(
            description="Robot Navigation System - Demo & Testing"
        )
        parser.add_argument('demo', type=str, nargs='?',
                          choices=['planning', 'control', 'slam', 'rl', 'benchmark', 
                                 'all_tests', 'prepare', 'structure', 'full'],
                          help='Which demo to run')
        parser.add_argument('--episodes', type=int, default=50,
                          help='Number of RL training episodes')
        parser.add_argument('--trials', type=int, default=1,
                          help='Number of benchmark trials')
        
        args = parser.parse_args()
        
        if not args.demo:
            print("""
╔════════════════════════════════════════════════════════╗
║   ROBOT NAVIGATION SYSTEM - DEMO & TESTING TOOL       ║
╚════════════════════════════════════════════════════════╝

Usage:
  python3 demo_and_test.py <command> [options]

Commands:
  planning     Test path planning algorithms
  control      Test navigation controller
  slam         Demo SLAM mapping
  rl           Train RL agent (DQN)
  benchmark    Run performance benchmarks
  all_tests    Run complete test suite
  prepare      Prepare for presentation
  structure    Show project file structure
  full         Run complete demo sequence

Examples:
  python3 demo_and_test.py planning
  python3 demo_and_test.py rl --episodes 100
  python3 demo_and_test.py benchmark --trials 3
  python3 demo_and_test.py full
            """)
            return
        
        if args.demo == 'planning':
            self.demo_path_planning()
        elif args.demo == 'control':
            self.demo_navigation_control()
        elif args.demo == 'slam':
            self.demo_slam_mapping()
        elif args.demo == 'rl':
            self.demo_reinforcement_learning(args.episodes)
        elif args.demo == 'benchmark':
            self.demo_performance_comparison(args.trials)
        elif args.demo == 'all_tests':
            self.run_complete_tests()
        elif args.demo == 'prepare':
            self.prepare_for_presentation()
        elif args.demo == 'structure':
            self.show_file_structure()
        elif args.demo == 'full':
            self.demo_path_planning()
            self.demo_navigation_control()
            self.demo_reinforcement_learning(args.episodes)
            self.demo_performance_comparison(args.trials)
            self.prepare_for_presentation()


if __name__ == "__main__":
    demo = RobotNavigationDemo()
    demo.main()
