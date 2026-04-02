#!/usr/bin/env python3
"""
Deep Q-Network (DQN) Agent for TurtleBot3 Navigation
Implements experience replay, target network, and epsilon-greedy exploration
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import pickle
import os
from datetime import datetime


class DQNNetwork(nn.Module):
    """Deep Q-Network with two hidden layers"""
    
    def __init__(self, state_size, action_size, hidden_size=128):
        super(DQNNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, action_size)
        
        self.relu = nn.ReLU()
    
    def forward(self, state):
        """Forward pass through network"""
        x = self.relu(self.fc1(state))
        x = self.relu(self.fc2(x))
        q_values = self.fc3(x)
        return q_values


class ReplayBuffer:
    """Experience replay buffer with fixed capacity"""
    
    def __init__(self, capacity=5000):
        self.capacity = capacity
        self.buffer = deque(maxlen=capacity)
    
    def add(self, state, action, reward, next_state, done):
        """Add experience to buffer"""
        self.buffer.append((state, action, reward, next_state, done))
    
    def sample(self, batch_size):
        """Sample random batch"""
        batch = random.sample(self.buffer, batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)
        
        return (np.array(states), np.array(actions), np.array(rewards),
                np.array(next_states), np.array(dones))
    
    def __len__(self):
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network Agent for navigation
    Features: Experience Replay, Target Network, Epsilon-Greedy
    """
    
    def __init__(self,
                 state_size,
                 action_size,
                 learning_rate=0.0005,
                 gamma=0.99,
                 epsilon=1.0,
                 epsilon_decay=0.995,
                 epsilon_min=0.01,
                 batch_size=32,
                 hidden_size=128,
                 device=None):
        """
        Initialize DQN Agent
        
        Args:
            state_size: Dimension of state space
            action_size: Number of discrete actions
            learning_rate: Learning rate for optimizer
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
            epsilon_min: Minimum epsilon
            batch_size: Batch size for training
            hidden_size: Hidden layer size
            device: torch device (cpu/cuda)
        """
        self.state_size = state_size
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        self.batch_size = batch_size
        
        # Device
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = device
        
        print(f"[DQN Agent] Using device: {self.device}")
        
        # Networks
        self.q_network = DQNNetwork(state_size, action_size, hidden_size).to(self.device)
        self.target_network = DQNNetwork(state_size, action_size, hidden_size).to(self.device)
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        self.loss_fn = nn.MSELoss()
        
        # Replay buffer
        self.memory = ReplayBuffer(capacity=5000)
        
        # Training stats
        self.training_losses = []
        self.episode_rewards = []
        self.update_counter = 0
    
    def select_action(self, state, training=True):
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: Whether in training mode (affects epsilon)
        
        Returns:
            Action index
        """
        if training and random.random() < self.epsilon:
            # Explore: random action
            return random.randint(0, self.action_size - 1)
        else:
            # Exploit: greedy action
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return q_values.argmax(dim=1).item()
    
    def remember(self, state, action, reward, next_state, done):
        """Store experience in replay buffer"""
        self.memory.add(state, action, reward, next_state, done)
    
    def train(self):
        """Train on batch from replay buffer"""
        if len(self.memory) < self.batch_size:
            return None  # Not enough samples yet
        
        # Sample batch
        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)
        
        # Q-values from primary network
        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Target Q-values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.loss_fn(q_values, target_q_values)
        
        # Backprop
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), 1.0)
        self.optimizer.step()
        
        self.update_counter += 1
        self.training_losses.append(loss.item())
        
        # Update target network periodically
        if self.update_counter % 100 == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        return loss.item()
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    def save(self, filepath):
        """Save agent checkpoint"""
        checkpoint = {
            'q_network': self.q_network.state_dict(),
            'target_network': self.target_network.state_dict(),
            'optimizer': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'training_losses': self.training_losses,
            'episode_rewards': self.episode_rewards,
            'update_counter': self.update_counter
        }
        torch.save(checkpoint, filepath)
        print(f"[DQN Agent] Saved checkpoint to {filepath}")
    
    def load(self, filepath):
        """Load agent checkpoint"""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network'])
        self.target_network.load_state_dict(checkpoint['target_network'])
        self.optimizer.load_state_dict(checkpoint['optimizer'])
        self.epsilon = checkpoint['epsilon']
        self.training_losses = checkpoint['training_losses']
        self.episode_rewards = checkpoint['episode_rewards']
        self.update_counter = checkpoint['update_counter']
        print(f"[DQN Agent] Loaded checkpoint from {filepath}")
    
    def get_training_stats(self):
        """Return training statistics"""
        return {
            'updates': self.update_counter,
            'avg_loss': np.mean(self.training_losses[-100:]) if self.training_losses else 0,
            'epsilon': self.epsilon,
            'replay_buffer_size': len(self.memory)
        }


class SimpleQLearningAgent:
    """
    Simple Q-Learning agent (alternative to DQN)
    Uses discretized state space with a lookup table
    """
    
    def __init__(self,
                 state_bins=[5, 5, 5, 5, 5],  # Discretization bins
                 action_size=5,
                 learning_rate=0.1,
                 gamma=0.99,
                 epsilon=1.0,
                 epsilon_decay=0.995):
        """
        Initialize Simple Q-Learning Agent
        
        Args:
            state_bins: Number of bins for discretizing each state dimension
            action_size: Number of actions
            learning_rate: Learning rate (alpha)
            gamma: Discount factor
            epsilon: Initial exploration rate
            epsilon_decay: Decay rate for epsilon
        """
        self.state_bins = state_bins
        self.action_size = action_size
        self.learning_rate = learning_rate
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        
        # Create Q-table
        q_table_shape = tuple(state_bins) + (action_size,)
        self.q_table = np.zeros(q_table_shape)
        
        # Stats
        self.visits = np.zeros(q_table_shape)
        self.training_losses = []
        self.episode_rewards = []
    
    def discretize_state(self, state):
        """Convert continuous state to discrete indices"""
        # Normalize state values
        normalized_state = []
        state_ranges = [
            (0, 3),     # goal_distance
            (-np.pi, np.pi),  # goal_angle
            (0, 3),     # min_laser
        ] + [(0, 3)] * len(self.state_bins[3:])
        
        for i, (val, (low, high)) in enumerate(zip(state, state_ranges)):
            if i < len(self.state_bins):
                normalized = (val - low) / (high - low)
                normalized = np.clip(normalized, 0, 0.9999)
                bin_idx = int(normalized * self.state_bins[i])
                normalized_state.append(bin_idx)
        
        return tuple(normalized_state)
    
    def select_action(self, state, training=True):
        """Select action using epsilon-greedy policy"""
        discrete_state = self.discretize_state(state)
        
        if training and random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else:
            return np.argmax(self.q_table[discrete_state])
    
    def update(self, state, action, reward, next_state, done):
        """Update Q-table"""
        discrete_state = self.discretize_state(state)
        discrete_next_state = self.discretize_state(next_state)
        
        # Q-learning update
        current_q = self.q_table[discrete_state + (action,)]
        max_next_q = np.max(self.q_table[discrete_next_state])
        
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q * (1 - int(done)) - current_q
        )
        
        self.q_table[discrete_state + (action,)] = new_q
        self.visits[discrete_state + (action,)] += 1
        
        return abs(new_q - current_q)
    
    def decay_epsilon(self):
        """Decay exploration rate"""
        self.epsilon = max(0.01, self.epsilon * self.epsilon_decay)
    
    def save(self, filepath):
        """Save Q-table"""
        data = {
            'q_table': self.q_table,
            'visits': self.visits,
            'epsilon': self.epsilon
        }
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
        print(f"[Q-Learning] Saved to {filepath}")
    
    def load(self, filepath):
        """Load Q-table"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        self.q_table = data['q_table']
        self.visits = data['visits']
        self.epsilon = data['epsilon']
        print(f"[Q-Learning] Loaded from {filepath}")


if __name__ == "__main__":
    # Test agents
    state_size = 15
    action_size = 5
    
    print("Testing DQN Agent...")
    dqn_agent = DQNAgent(state_size, action_size)
    
    # Simulate some experience
    for _ in range(100):
        state = np.random.randn(state_size).astype(np.float32)
        action = dqn_agent.select_action(state)
        next_state = np.random.randn(state_size).astype(np.float32)
        reward = np.random.randn()
        done = np.random.rand() > 0.9
        
        dqn_agent.remember(state, action, reward, next_state, done)
        loss = dqn_agent.train()
        if loss:
            print(f"Loss: {loss:.4f}")
    
    print(f"Stats: {dqn_agent.get_training_stats()}")
    
    print("\nTesting Q-Learning Agent...")
    ql_agent = SimpleQLearningAgent()
    print(f"Q-table shape: {ql_agent.q_table.shape}")
