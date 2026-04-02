#!/usr/bin/env python3
"""
Complete Integration Test Suite for Robot Navigation
Tests all components: Planning, Control, RL, Visualization
"""

import unittest
import numpy as np
import sys
import os
import time

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from astar import AStarPlanner as AStar
from dijkstra import DijkstraPlanner as Dijkstra
from greedy import GreedyPlanner as GreedyBestFirstSearch
from navigation_controller import PIDController, TrajectoryTrackingController, ObstacleAvoidanceController, CombinedNavigationController
from performance_benchmark import MetricsCollector

try:
    from rl_environment import TurtleBot3NavEnv
    from rl_agent import DQNAgent, SimpleQLearningAgent
    HAS_RL = True
except:
    HAS_RL = False


class TestPlanningAlgorithms(unittest.TestCase):
    """Test path planning algorithms"""
    
    def setUp(self):
        """Create test environment"""
        # Simple grid
        self.grid = np.zeros((10, 10))
        self.grid[3:7, 3:7] = 1  # Obstacle
        
        self.start = (1, 1)
        self.goal = (8, 8)
    
    def test_astar_finds_path(self):
        """Test A* finds valid path"""
        planner = AStar(grid=self.grid)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
        print(f"✓ A* path length: {len(path)}")
    
    def test_dijkstra_finds_path(self):
        """Test Dijkstra finds valid path"""
        planner = Dijkstra(grid=self.grid)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
        print(f"✓ Dijkstra path length: {len(path)}")
    
    def test_greedy_finds_path(self):
        """Test Greedy BFS finds valid path"""
        planner = GreedyBestFirstSearch(grid=self.grid)
        path = planner.plan(self.start, self.goal)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], self.start)
        self.assertEqual(path[-1], self.goal)
        print(f"✓ Greedy path length: {len(path)}")
    
    def test_algorithm_comparison(self):
        """Compare algorithm performance"""
        planners = {
            'astar': AStar(grid=self.grid),
            'dijkstra': Dijkstra(grid=self.grid),
            'greedy': GreedyBestFirstSearch(grid=self.grid)
        }
        
        results = {}
        for name, planner in planners.items():
            start_time = time.time()
            path = planner.plan(self.start, self.goal)
            elapsed = time.time() - start_time
            
            results[name] = {
                'path_length': len(path) if path else 0,
                'time': elapsed,
                'found': path is not None
            }
        
        print("\n📊 Algorithm Comparison:")
        for name, res in results.items():
            print(f"  {name:12} | path_len={res['path_length']:3} | time={res['time']*1000:6.2f}ms | found={res['found']}")
        
        # All should find path
        for res in results.values():
            self.assertTrue(res['found'])
    
    def test_no_path_exists(self):
        """Test when no path exists"""
        # Create blocked grid
        blocked_grid = np.ones((10, 10))
        blocked_grid[5, :] = 0  # Path
        blocked_grid[5, 5] = 1  # Block path
        start = (0, 5)
        goal = (9, 5)
        
        planner = AStar(grid=blocked_grid)
        path = planner.plan(start, goal)
        
        self.assertIsNone(path)
        print("✓ Correctly detected unreachable goal")


class TestControllers(unittest.TestCase):
    """Test navigation controllers"""
    
    def test_pid_controller_stability(self):
        """Test PID controller converges"""
        from navigation_controller import PIDController
        
        pid = PIDController(kp=1.0, ki=0.1, kd=0.1)
        
        errors = np.linspace(1.0, 0.0, 100)
        outputs = []
        
        for error in errors:
            output = pid.update(error)
            outputs.append(output)
        
        # Output should decrease
        self.assertFalse(np.all(np.diff(outputs) > 0))
        print(f"✓ PID converges: final output={outputs[-1]:.4f}")
    
    def test_trajectory_error_computation(self):
        """Test trajectory tracking error calculation"""
        controller = TrajectoryTrackingController()
        
        # Mock path
        controller.waypoint_path = [
            np.array([0.0, 0.0]),
            np.array([1.0, 1.0]),
            np.array([2.0, 2.0])
        ]
        controller.current_position = np.array([0.5, 0.0])
        controller.current_waypoint_idx = 0
        
        error = controller.compute_trajectory_error()
        self.assertGreaterEqual(error, 0.0)
        print(f"✓ Trajectory error computed: {error:.3f}m")


class TestMetricsCollector(unittest.TestCase):
    """Test metrics collection"""
    
    def test_metrics_computation(self):
        """Test metric computation"""
        collector = MetricsCollector()
        collector.set_goal(5.0, 5.0)
        
        # Simulate trajectory
        for i in range(50):
            x = i * 0.1
            y = i * 0.1
            collector.update_position(x, y)
        
        collector.goal_reached = True
        metrics = collector.compute_metrics()
        
        self.assertIn('path_length', metrics)
        self.assertIn('path_efficiency', metrics)
        self.assertGreater(metrics['path_length'], 0)
        print(f"✓ Metrics computed: efficiency={metrics['path_efficiency']:.1%}")
    
    def test_collision_detection(self):
        """Test collision detection"""
        collector = MetricsCollector()
        
        collector.update_position(0.0, 0.0)
        collector.check_laser_collision(0.2)  # Collision
        
        self.assertTrue(collector.collision_occurred)
        print("✓ Collision detected correctly")


@unittest.skipUnless(HAS_RL, "RL modules not available")
class TestRLComponents(unittest.TestCase):
    """Test reinforcement learning components"""
    
    def test_dqn_agent_creation(self):
        """Test DQN agent initialization"""
        agent = DQNAgent(state_size=10, action_size=5)
        
        self.assertIsNotNone(agent.q_network)
        self.assertIsNotNone(agent.memory)
        print("✓ DQN agent created successfully")
    
    def test_dqn_action_selection(self):
        """Test DQN action selection"""
        agent = DQNAgent(state_size=10, action_size=5)
        state = np.random.randn(10).astype(np.float32)
        
        action = agent.select_action(state, training=True)
        
        self.assertIn(action, range(5))
        print(f"✓ DQN selected action: {action}")
    
    def test_dqn_training(self):
        """Test DQN training step"""
        agent = DQNAgent(state_size=10, action_size=5, batch_size=4)
        
        # Add some experience
        for _ in range(10):
            state = np.random.randn(10).astype(np.float32)
            action = np.random.randint(5)
            reward = np.random.randn()
            next_state = np.random.randn(10).astype(np.float32)
            done = np.random.rand() > 0.9
            
            agent.remember(state, action, reward, next_state, done)
        
        loss = agent.train()
        
        self.assertIsNotNone(loss)
        print(f"✓ DQN training loss: {loss:.4f}")
    
    def test_ql_agent_creation(self):
        """Test Q-Learning agent initialization"""
        agent = SimpleQLearningAgent(state_bins=[5, 5, 5])
        
        self.assertIsNotNone(agent.q_table)
        self.assertEqual(agent.q_table.shape, (5, 5, 5, 5))
        print("✓ Q-Learning agent created successfully")
    
    def test_ql_discretization(self):
        """Test Q-Learning state discretization"""
        agent = SimpleQLearningAgent(state_bins=[5, 5, 5])
        
        state = np.array([1.5, 0.0, 2.0])
        discrete_state = agent.discretize_state(state)
        
        self.assertEqual(len(discrete_state), 3)
        print(f"✓ State discretized: {state} -> {discrete_state}")


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple components"""
    
    def test_planning_and_tracking(self):
        """Test planning path and controller integration"""
        # Create simple grid
        grid = np.zeros((15, 15))
        start = (1, 1)
        goal = (13, 13)
        
        # Plan path
        planner = AStar(grid=grid)
        path = planner.plan(start, goal)
        
        self.assertIsNotNone(path)
        
        # Verify path continuity
        for i in range(len(path) - 1):
            p1 = np.array(path[i])
            p2 = np.array(path[i+1])
            distance = np.linalg.norm(p2 - p1)
            self.assertLessEqual(distance, np.sqrt(2) + 0.01)  # 8-connected
        
        print(f"✓ Path planning and continuity verified: {len(path)} waypoints")
    
    def test_full_navigation_pipeline(self):
        """Test complete navigation pipeline"""
        # Mock components
        grid = np.zeros((20, 20))
        start = (2, 2)
        goal = (18, 18)
        
        # 1. Planning
        planner = AStar(grid=grid)
        path = planner.plan(start, goal)
        self.assertIsNotNone(path)
        
        # 2. Metrics
        collector = MetricsCollector()
        collector.set_goal(goal[0], goal[1])
        collector.set_planned_path(path)
        
        # 3. Simulate trajectory
        for waypoint in path[:10]:  # Simulate following first 10 points
            collector.update_position(waypoint[0], waypoint[1])
            collector.record_velocity(0.2, 0.0)
        
        metrics = collector.compute_metrics()
        
        self.assertGreater(metrics['path_length'], 0)
        self.assertGreater(metrics['path_efficiency'], 0)
        
        print(f"✓ Full pipeline test passed")
        print(f"  - Planned path: {len(path)} points")
        print(f"  - Path efficiency: {metrics['path_efficiency']:.1%}")


def run_test_suite():
    """Run complete test suite"""
    print("\n" + "="*70)
    print("ROBOT NAVIGATION INTEGRATION TEST SUITE")
    print("="*70 + "\n")
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPlanningAlgorithms))
    suite.addTests(loader.loadTestsFromTestCase(TestControllers))
    suite.addTests(loader.loadTestsFromTestCase(TestMetricsCollector))
    
    if HAS_RL:
        suite.addTests(loader.loadTestsFromTestCase(TestRLComponents))
    else:
        print("⚠️  RL components not available, skipping RL tests\n")
    
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_test_suite()
    sys.exit(0 if success else 1)
