#!/usr/bin/env python3
"""
Training script for RL Agent
Trains DQN or Q-Learning agent on TurtleBot3 navigation task
"""

import numpy as np
import argparse
import sys
import os
import time
import rospy
from pathlib import Path

# Add scripts directory to Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from rl_environment import TurtleBot3NavEnv
from rl_agent import DQNAgent, SimpleQLearningAgent
import matplotlib.pyplot as plt


class RLTrainer:
    """Trainer for RL agents"""
    
    def __init__(self, agent, env, config):
        """
        Initialize trainer
        
        Args:
            agent: RL agent instance
            env: Gymnasium environment
            config: Training configuration dict
        """
        self.agent = agent
        self.env = env
        self.config = config
        
        self.episode_rewards = []
        self.episode_lengths = []
        self.episode_successes = []
        self.start_time = None
    
    def train_episode(self):
        """Train for one episode"""
        state, _ = self.env.reset()
        episode_reward = 0.0
        episode_length = 0
        success = False
        
        while True:
            # Select and execute action
            action = self.agent.select_action(state, training=True)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            episode_reward += reward
            episode_length += 1
            
            # Store experience
            self.agent.remember(state, action, reward, next_state, terminated)
            
            # Train agent
            if hasattr(self.agent, 'train'):
                self.agent.train()
            elif hasattr(self.agent, 'update'):
                self.agent.update(state, action, reward, next_state, terminated)
            
            # Check success
            if info.get('goal_reached'):
                success = True
            
            state = next_state
            
            if terminated or truncated:
                break
        
        # Decay epsilon
        self.agent.decay_epsilon()
        
        return episode_reward, episode_length, success
    
    def evaluate_episode(self):
        """Evaluate agent on one episode (no training)"""
        state, _ = self.env.reset()
        episode_reward = 0.0
        episode_length = 0
        success = False
        
        while True:
            action = self.agent.select_action(state, training=False)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            episode_reward += reward
            episode_length += 1
            
            if info.get('goal_reached'):
                success = True
            
            state = next_state
            
            if terminated or truncated:
                break
        
        return episode_reward, episode_length, success
    
    def train(self):
        """Main training loop"""
        num_episodes = self.config.get('num_episodes', 100)
        eval_frequency = self.config.get('eval_frequency', 10)
        save_frequency = self.config.get('save_frequency', 50)
        checkpoint_dir = self.config.get('checkpoint_dir', './checkpoints')
        
        # Create checkpoint directory
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
        
        self.start_time = time.time()
        
        print(f"\n[RL Trainer] Starting training for {num_episodes} episodes")
        print(f"[RL Trainer] Evaluation every {eval_frequency} episodes")
        print(f"[RL Trainer] Saving every {save_frequency} episodes\n")
        
        for episode in range(1, num_episodes + 1):
            # Training episode
            train_reward, train_length, train_success = self.train_episode()
            self.episode_rewards.append(train_reward)
            self.episode_lengths.append(train_length)
            self.episode_successes.append(int(train_success))
            
            # Evaluation
            if episode % eval_frequency == 0:
                eval_rewards = []
                eval_successes = []
                
                for _ in range(5):  # 5 evaluation runs
                    eval_reward, eval_length, eval_success = self.evaluate_episode()
                    eval_rewards.append(eval_reward)
                    eval_successes.append(int(eval_success))
                
                avg_eval_reward = np.mean(eval_rewards)
                eval_success_rate = np.mean(eval_successes)
                
                elapsed_time = time.time() - self.start_time
                
                print(f"Episode {episode:4d} | "
                      f"Train Reward: {train_reward:7.2f} | "
                      f"Eval Reward: {avg_eval_reward:7.2f} | "
                      f"Success Rate: {eval_success_rate:5.1%} | "
                      f"Time: {elapsed_time:6.1f}s")
                
                # Print agent stats
                if hasattr(self.agent, 'get_training_stats'):
                    stats = self.agent.get_training_stats()
                    print(f"  -> Epsilon: {stats['epsilon']:.3f}, "
                          f"Avg Loss: {stats['avg_loss']:.4f}, "
                          f"Replay Buffer: {stats['replay_buffer_size']}")
            
            # Save checkpoint
            if episode % save_frequency == 0:
                checkpoint_path = os.path.join(checkpoint_dir, f"agent_ep{episode}.pt")
                self.agent.save(checkpoint_path)
        
        print(f"\n[RL Trainer] Training completed in {time.time() - self.start_time:.1f}s")
        
        return self.episode_rewards, self.episode_lengths, self.episode_successes
    
    def plot_results(self, output_path="training_results.png"):
        """Plot training results"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        
        # Episode rewards
        axes[0, 0].plot(self.episode_rewards)
        axes[0, 0].set_xlabel('Episode')
        axes[0, 0].set_ylabel('Total Reward')
        axes[0, 0].set_title('Episode Rewards')
        axes[0, 0].grid(True)
        
        # Moving average
        window = 10
        moving_avg = np.convolve(self.episode_rewards, np.ones(window)/window, mode='valid')
        axes[0, 1].plot(moving_avg)
        axes[0, 1].set_xlabel('Episode')
        axes[0, 1].set_ylabel('Moving Avg Reward')
        axes[0, 1].set_title(f'Moving Average (window={window})')
        axes[0, 1].grid(True)
        
        # Episode lengths
        axes[1, 0].plot(self.episode_lengths)
        axes[1, 0].set_xlabel('Episode')
        axes[1, 0].set_ylabel('Episode Length')
        axes[1, 0].set_title('Episode Lengths')
        axes[1, 0].grid(True)
        
        # Success rate
        window = 20
        success_rate = np.convolve(self.episode_successes, np.ones(window)/window, mode='valid')
        axes[1, 1].plot(success_rate * 100)
        axes[1, 1].set_xlabel('Episode')
        axes[1, 1].set_ylabel('Success Rate (%)')
        axes[1, 1].set_title(f'Success Rate (window={window})')
        axes[1, 1].grid(True)
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        print(f"[RL Trainer] Saved plot to {output_path}")
        plt.close()


def main():
    parser = argparse.ArgumentParser(description='Train RL agent for robot navigation')
    parser.add_argument('--agent', type=str, default='dqn', 
                       choices=['dqn', 'qlearning'],
                       help='Agent type to train')
    parser.add_argument('--episodes', type=int, default=100,
                       help='Number of training episodes')
    parser.add_argument('--eval-freq', type=int, default=10,
                       help='Evaluation frequency')
    parser.add_argument('--save-freq', type=int, default=50,
                       help='Save frequency')
    parser.add_argument('--checkpoint', type=str, default=None,
                       help='Path to checkpoint to load')
    parser.add_argument('--no-sim', action='store_true',
                       help='Run without simulation (test mode)')
    
    args = parser.parse_args()
    
    print(f"\n{'='*60}")
    print(f"RL NAVIGATION TRAINING")
    print(f"Agent: {args.agent.upper()}")
    print(f"Episodes: {args.episodes}")
    print(f"{'='*60}\n")
    
    # Initialize ROS
    if not args.no_sim:
        rospy.init_node('rl_training_node', anonymous=True)
        time.sleep(2)
    
    # Create environment
    print("[Main] Creating environment...")
    env = TurtleBot3NavEnv(max_steps=200)
    
    # Create agent
    print(f"[Main] Creating {args.agent.upper()} agent...")
    if args.agent == 'dqn':
        agent = DQNAgent(
            state_size=15,
            action_size=5,
            learning_rate=0.0005,
            gamma=0.99,
            epsilon=1.0,
            epsilon_decay=0.995,
            batch_size=32
        )
    else:  # q-learning
        agent = SimpleQLearningAgent(
            state_bins=[5, 5, 5, 5, 5],
            action_size=5,
            learning_rate=0.1,
            gamma=0.99,
            epsilon=1.0
        )
    
    # Load checkpoint if provided
    if args.checkpoint and os.path.exists(args.checkpoint):
        print(f"[Main] Loading checkpoint from {args.checkpoint}")
        agent.load(args.checkpoint)
    
    # Create trainer
    config = {
        'num_episodes': args.episodes,
        'eval_frequency': args.eval_freq,
        'save_frequency': args.save_freq,
        'checkpoint_dir': f'./checkpoints_{args.agent}'
    }
    
    trainer = RLTrainer(agent, env, config)
    
    try:
        # Train
        rewards, lengths, successes = trainer.train()
        
        # Save final model
        final_checkpoint = f'final_agent_{args.agent}.pt'
        agent.save(final_checkpoint)
        
        # Plot results
        trainer.plot_results(f'training_results_{args.agent}.png')
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"TRAINING SUMMARY")
        print(f"{'='*60}")
        print(f"Total Episodes: {len(rewards)}")
        print(f"Avg Reward: {np.mean(rewards):.2f}")
        print(f"Final Reward: {rewards[-1]:.2f}")
        print(f"Success Rate: {np.mean(successes)*100:.1f}%")
        print(f"Avg Episode Length: {np.mean(lengths):.1f}")
        print(f"{'='*60}\n")
        
    except KeyboardInterrupt:
        print("\n[Main] Training interrupted by user")
        agent.save('interrupted_agent.pt')
    finally:
        env.close()


if __name__ == "__main__":
    main()
