#!/usr/bin/env python3
import heapq
import math

class GreedyPlanner:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

    def heuristic(self, a, b):
        return math.dist(a, b)

    def neighbors(self, node):
        x, y = node
        moves = [(1,0),(-1,0),(0,1),(0,-1)]
        for dx, dy in moves:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.rows and 0 <= ny < self.cols:
                if self.grid[nx][ny] == 0:
                    yield (nx, ny)

    def plan(self, start, goal):
        open_set = []
        heapq.heappush(open_set, (self.heuristic(start, goal), start))
        came_from = {}
        visited = set()

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            visited.add(current)

            for n in self.neighbors(current):
                if n not in visited:
                    heapq.heappush(open_set, (self.heuristic(n, goal), n))
                    came_from[n] = current

        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
