#!/usr/bin/env python3
"""
Performance Benchmarking Framework for Navigation Algorithms
Compares Classical Planning vs RL-based Navigation
"""

import numpy as np
import rospy
import time
import json
from pathlib import Path
from collections import defaultdict
from geometry_msgs.msg import Twist, Pose2D
from nav_msgs.msg import Path, Odometry
from sensor_msgs.msg import LaserScan
from std_srvs.srv import Empty
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from astar import AStarPlanner
from dijkstra import DijkstraPlanner
from greedy import GreedyPlanner

try:
    from rl_agent import DQNAgent, SimpleQLearningAgent
except:
    pass


class MetricsCollector:
    """Collects and analyzes navigation metrics"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all metrics"""
        self.start_time = None
        self.start_position = None
        self.current_position = np.array([0.0, 0.0])
        self.goal_position = np.array([0.0, 0.0])
        self.trajectory = []
        self.timestamps = []
        self.laser_collisions = []
        self.planned_path = None
        self.distance_to_goal = []
        self.velocity_commands = []
        self.goal_reached = False
        self.collision_occurred = False
        self.completion_time = 0.0
    
    def update_position(self, x, y):
        """Update current position"""
        if self.start_position is None:
            self.start_position = np.array([x, y])
        
        self.current_position = np.array([x, y])
        self.trajectory.append(self.current_position.copy())
        self.timestamps.append(time.time())
        
        # Distance to goal
        dist = np.linalg.norm(self.current_position - self.goal_position)
        self.distance_to_goal.append(dist)
    
    def check_laser_collision(self, min_range):
        """Check for collision based on laser"""
        collision_threshold = 0.3
        if min_range < collision_threshold:
            self.collision_occurred = True
            self.laser_collisions.append(len(self.trajectory))
    
    def set_goal(self, x, y):
        """Set goal position"""
        self.goal_position = np.array([x, y])
    
    def set_planned_path(self, path_points):
        """Set planned path"""
        self.planned_path = path_points
    
    def record_velocity(self, linear_x, angular_z):
        """Record velocity command"""
        self.velocity_commands.append((linear_x, angular_z))
    
    def compute_metrics(self):
        """Compute all metrics"""
        if len(self.trajectory) < 2:
            return {}
        
        trajectory = np.array(self.trajectory)
        timestamps = np.array(self.timestamps)
        
        # Total distance traveled
        distances = np.diff(trajectory, axis=0)
        path_length = np.sum(np.linalg.norm(distances, axis=1))
        
        # Time metrics
        total_time = timestamps[-1] - timestamps[0]
        
        # Straight line distance (optimal)
        straight_line = np.linalg.norm(trajectory[-1] - trajectory[0])
        
        # Path efficiency (straight line / actual path)
        path_efficiency = straight_line / path_length if path_length > 0 else 0
        
        # Average velocity
        avg_velocity = path_length / total_time if total_time > 0 else 0
        
        # Final distance to goal
        final_distance = np.linalg.norm(trajectory[-1] - self.goal_position)
        
        # Smoothness (variance of velocity changes)
        if len(self.velocity_commands) > 1:
            vel_array = np.array(self.velocity_commands)
            vel_changes = np.diff(vel_array, axis=0)
            smoothness = np.mean(np.linalg.norm(vel_changes, axis=1))
        else:
            smoothness = 0
        
        # Collision count
        collision_count = len(set(self.laser_collisions))
        
        metrics = {
            'path_length': float(path_length),
            'straight_line': float(straight_line),
            'path_efficiency': float(path_efficiency),
            'total_time': float(total_time),
            'avg_velocity': float(avg_velocity),
            'final_distance': float(final_distance),
            'collision_count': int(collision_count),
            'smoothness': float(smoothness),
            'goal_reached': self.goal_reached,
            'collision_occurred': self.collision_occurred
        }
        
        return metrics
    
    def get_summary(self):
        """Get formatted summary"""
        metrics = self.compute_metrics()
        
        summary = f"""
        ├─ Path Length: {metrics.get('path_length', 0):.2f} m
        ├─ Straight Line: {metrics.get('straight_line', 0):.2f} m
        ├─ Path Efficiency: {metrics.get('path_efficiency', 0):.1%}
        ├─ Total Time: {metrics.get('total_time', 0):.2f} s
        ├─ Average Velocity: {metrics.get('avg_velocity', 0):.2f} m/s
        ├─ Final Distance: {metrics.get('final_distance', 0):.2f} m
        ├─ Collisions: {metrics.get('collision_count', 0)}
        ├─ Smoothness: {metrics.get('smoothness', 0):.3f}
        ├─ Goal Reached: {metrics.get('goal_reached', False)}
        └─ Collision Occurred: {metrics.get('collision_occurred', False)}
        """
        return summary


class PlanningBenchmark:
    """Benchmarks path planning algorithms"""
    
    def __init__(self, planner_node_name='/planner'):
        self.planner_topic = f'{planner_node_name}/plan'
        
        self.results = defaultdict(list)
        self.metrics = MetricsCollector()
        
        # Load map for planning
        self.map_image = mpimg.imread('/home/ubuntu/workspace/maps/labyrinthe_map.pgm')
        # Convert to grid: 0 = free, 1 = occupied
        self.grid = (self.map_image < 0.5).astype(int)
        
        # Map parameters from yaml
        self.resolution = 0.05
        self.origin_x = -10.0
        self.origin_y = -10.0
        
        # Create planners
        self.planners = {
            'astar': AStarPlanner(self.grid),
            'dijkstra': DijkstraPlanner(self.grid),
            'greedy': GreedyPlanner(self.grid)
        }
    
    def world_to_grid(self, x, y):
        """Convert world coordinates to grid indices"""
        i = int((x - self.origin_x) / self.resolution)
        j = int((y - self.origin_y) / self.resolution)
        return (i, j)
    
    def grid_to_world(self, i, j):
        """Convert grid indices to world coordinates"""
        x = i * self.resolution + self.origin_x
        y = j * self.resolution + self.origin_y
        return (x, y)
    
    def plot_path(self, path, algorithm_name, goal_x, goal_y, output_file=None):
        """Plot path on map"""
        if output_file is None:
            output_file = f"path_{algorithm_name}_{goal_x}_{goal_y}.png"
        
        plt.figure(figsize=(10, 10))
        plt.imshow(self.map_image, cmap='gray', origin='lower', extent=[self.origin_x, self.origin_x + self.grid.shape[1]*self.resolution, self.origin_y, self.origin_y + self.grid.shape[0]*self.resolution])
        
        if path:
            # Convert path to world coordinates
            world_path = [self.grid_to_world(i, j) for i, j in path]
            xs = [p[0] for p in world_path]
            ys = [p[1] for p in world_path]
            plt.plot(xs, ys, 'r-', linewidth=3, label='Planned Path')
            
            # Mark start and goal
            plt.plot(xs[0], ys[0], 'go', markersize=10, label='Start')
            plt.plot(xs[-1], ys[-1], 'ro', markersize=10, label='Goal')
        
        plt.title(f'{algorithm_name.upper()} Path to ({goal_x:.1f}, {goal_y:.1f})')
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"[Benchmark] Saved path plot to {output_file}")
        plt.close()
    
    def _odom_callback(self, msg):
        """Callback for odometry"""
        self.metrics.update_position(
            msg.pose.pose.position.x,
            msg.pose.pose.position.y
        )
    
    def _laser_callback(self, msg):
        """Callback for laser scan"""
        ranges = np.array(msg.ranges)
        min_range = np.min(ranges[~np.isinf(ranges)])
        self.metrics.check_laser_collision(min_range)
    
    def benchmark_planner(self, algorithm_name, goal_x, goal_y, max_time=60.0):
        """
        Benchmark a planning algorithm
        
        Args:
            algorithm_name: Name of algorithm ('astar', 'dijkstra', 'greedy')
            goal_x, goal_y: Goal position
            max_time: Maximum time for test
        
        Returns:
            metrics dictionary
        """
        print(f"\n[Benchmark] Testing {algorithm_name.upper()}")
        print(f"[Benchmark] Goal: ({goal_x:.2f}, {goal_y:.2f})")
        
        # Assume start at (0, 0)
        start_x, start_y = 0.0, 0.0
        start_grid = self.world_to_grid(start_x, start_y)
        goal_grid = self.world_to_grid(goal_x, goal_y)
        
        # Plan path
        start_time = time.time()
        path = self.planners[algorithm_name].plan(start_grid, goal_grid)
        planning_time = time.time() - start_time
        
        # Plot path
        self.plot_path(path, algorithm_name, goal_x, goal_y)
        
        # Compute metrics from path
        if path:
            # Convert path to world coordinates
            world_path = np.array([self.grid_to_world(i, j) for i, j in path])
            
            # Path length
            distances = np.diff(world_path, axis=0)
            path_length = np.sum(np.linalg.norm(distances, axis=1))
            
            # Straight line distance
            straight_line = np.linalg.norm(world_path[-1] - world_path[0])
            
            # Efficiency
            path_efficiency = straight_line / path_length if path_length > 0 else 0
            
            # Final distance to goal
            final_distance = np.linalg.norm(world_path[-1] - np.array([goal_x, goal_y]))
            
            goal_reached = final_distance < 0.1  # Close enough
            
        else:
            path_length = 0
            straight_line = np.linalg.norm(np.array([goal_x, goal_y]) - np.array([start_x, start_y]))
            path_efficiency = 0
            final_distance = straight_line
            goal_reached = False
        
        # Dummy metrics for other fields
        metrics = {
            'path_length': float(path_length),
            'straight_line': float(straight_line),
            'path_efficiency': float(path_efficiency),
            'total_time': float(planning_time),
            'avg_velocity': 0.0,  # Not applicable
            'final_distance': float(final_distance),
            'collision_count': 0,  # Assume no collisions in planning
            'smoothness': 0.0,
            'goal_reached': goal_reached,
            'collision_occurred': False
        }
        
        self.results[algorithm_name].append(metrics)
        
        print(f"""
        ├─ Path Length: {metrics['path_length']:.2f} m
        ├─ Straight Line: {metrics['straight_line']:.2f} m
        ├─ Path Efficiency: {metrics['path_efficiency']:.1%}
        ├─ Total Time: {metrics['total_time']:.4f} s
        ├─ Average Velocity: {metrics['avg_velocity']:.2f} m/s
        ├─ Final Distance: {metrics['final_distance']:.2f} m
        ├─ Collisions: {metrics['collision_count']}
        ├─ Smoothness: {metrics['smoothness']:.3f}
        ├─ Goal Reached: {metrics['goal_reached']}
        └─ Collision Occurred: {metrics['collision_occurred']}
        """)
        
        return metrics
    
    def compare_algorithms(self, algorithms, goals, num_trials=3):
        """
        Compare multiple algorithms on same goals
        
        Args:
            algorithms: List of algorithm names
            goals: List of (x, y) goal positions
            num_trials: Number of trials per algorithm-goal pair
        """
        print(f"\n{'='*60}")
        print(f"PLANNING ALGORITHM BENCHMARKS")
        print(f"{'='*60}")
        print(f"Algorithms: {algorithms}")
        print(f"Test Goals: {goals}")
        print(f"Trials per pair: {num_trials}")
        print(f"{'='*60}\n")
        
        for algorithm in algorithms:
            print(f"\n📊 TESTING: {algorithm.upper()}")
            print(f"{'─'*60}")
            
            for goal_idx, (goal_x, goal_y) in enumerate(goals):
                print(f"\n  Goal {goal_idx+1}: ({goal_x:.1f}, {goal_y:.1f})")
                
                algo_goal_results = []
                for trial in range(num_trials):
                    metrics = self.benchmark_planner(algorithm, goal_x, goal_y, max_time=30)
                    algo_goal_results.append(metrics)
                    time.sleep(2)
                
                # Pause for user to take photos
                print(f"\n📸 Prêt pour prendre des photos du chemin {algorithm.upper()} vers ({goal_x:.1f}, {goal_y:.1f})")
                print("Appuyez sur Entrée quand vous avez fini...")
                input()
                
                # Average metrics
                avg_metrics = {
                    k: np.mean([m.get(k, 0) for m in algo_goal_results])
                    for k in algo_goal_results[0].keys()
                    if isinstance(algo_goal_results[0][k], (int, float))
                }
                
                print(f"    ├─ Avg Path Length: {avg_metrics['path_length']:.2f} m")
                print(f"    ├─ Avg Efficiency: {avg_metrics['path_efficiency']:.1%}")
                print(f"    ├─ Success Rate: {np.mean([m['goal_reached'] for m in algo_goal_results])*100:.0f}%")
                print(f"    └─ Collision Rate: {np.mean([m['collision_count'] for m in algo_goal_results])*100:.0f}%")
    
    def get_comparison_stats(self):
        """Get comparison statistics"""
        stats = {}
        for algo_name, results in self.results.items():
            if not results:
                continue
            
            results_array = np.array([
                [r.get(k, 0) for k in ['path_length', 'path_efficiency', 'total_time']]
                for r in results
            ])
            
            stats[algo_name] = {
                'avg_path': float(np.mean(results_array[:, 0])),
                'avg_efficiency': float(np.mean(results_array[:, 1])),
                'avg_time': float(np.mean(results_array[:, 2])),
                'success_rate': float(np.mean([r['goal_reached'] for r in results])),
                'collision_rate': float(np.mean([r['collision_occurred'] for r in results]))
            }
        
        return stats
    
    def plot_comparison(self, output_path="benchmark_results.png"):
        """Plot benchmark results"""
        stats = self.get_comparison_stats()
        
        if not stats:
            print("[Benchmark] No results to plot")
            return
        
        algorithms = list(stats.keys())
        
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Path length
        path_lengths = [stats[a]['avg_path'] for a in algorithms]
        axes[0, 0].bar(algorithms, path_lengths)
        axes[0, 0].set_ylabel('Path Length (m)')
        axes[0, 0].set_title('Average Path Length')
        axes[0, 0].grid(axis='y')
        
        # Efficiency
        efficiencies = [stats[a]['avg_efficiency']*100 for a in algorithms]
        axes[0, 1].bar(algorithms, efficiencies)
        axes[0, 1].set_ylabel('Efficiency (%)')
        axes[0, 1].set_title('Path Efficiency')
        axes[0, 1].set_ylim([0, 100])
        axes[0, 1].grid(axis='y')
        
        # Execution time
        times = [stats[a]['avg_time'] for a in algorithms]
        axes[1, 0].bar(algorithms, times)
        axes[1, 0].set_ylabel('Time (s)')
        axes[1, 0].set_title('Average Execution Time')
        axes[1, 0].grid(axis='y')
        
        # Success rate
        success_rates = [stats[a]['success_rate']*100 for a in algorithms]
        axes[1, 1].bar(algorithms, success_rates)
        axes[1, 1].set_ylabel('Success Rate (%)')
        axes[1, 1].set_title('Goal Reaching Success Rate')
        axes[1, 1].set_ylim([0, 100])
        axes[1, 1].grid(axis='y')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"[Benchmark] Saved plot to {output_path}")
        plt.close()
    
    def save_results(self, output_file="benchmark_results.json"):
        """Save results to JSON"""
        # Convert numpy types to Python types
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, np.bool_):
                return bool(obj)
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            else:
                return obj
        
        data = {
            'results': {
                algo: [convert_types(m) for m in results]
                for algo, results in self.results.items()
            },
            'stats': convert_types(self.get_comparison_stats())
        }
        
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"[Benchmark] Saved results to {output_file}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Benchmark navigation algorithms')
    parser.add_argument('--algorithms', type=str, default='astar,dijkstra,greedy',
                       help='Comma-separated list of algorithms to test')
    parser.add_argument('--trials', type=int, default=3,
                       help='Number of trials per algorithm')
    
    args = parser.parse_args()
    
    benchmark = PlanningBenchmark()
    
    # Test goals (x, y)
    test_goals = [
        (1.0, 1.0),
        (2.0, -1.0),
        (-1.5, 1.5)
    ]
    
    algorithms = args.algorithms.split(',')
    
    # Run benchmarks
    benchmark.compare_algorithms(algorithms, test_goals, num_trials=args.trials)
    
    # Save and plot results
    benchmark.save_results()
    benchmark.plot_comparison()
    
    # Print stats
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    stats = benchmark.get_comparison_stats()
    for algo, algo_stats in stats.items():
        print(f"\n{algo.upper()}:")
        print(f"  Avg Path Length: {algo_stats['avg_path']:.2f} m")
        print(f"  Path Efficiency: {algo_stats['avg_efficiency']:.1%}")
        print(f"  Avg Time: {algo_stats['avg_time']:.4f} s")
        print(f"  Success Rate: {algo_stats['success_rate']:.1%}")
        print(f"  Collision Rate: {algo_stats['collision_rate']:.1%}")
    print("="*60)


if __name__ == "__main__":
    main()
