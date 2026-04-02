#!/usr/bin/env python3
import heapq

class DijkstraPlanner:
    def __init__(self, grid):
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0])

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
        heapq.heappush(open_set, (0, start))
        came_from = {}
        cost = {start: 0}

        closed_set = set()
        while open_set:
            _, current = heapq.heappop(open_set)

            if current in closed_set:
                continue
            closed_set.add(current)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            for n in self.neighbors(current):
                if n in closed_set:
                    continue

                new_cost = cost[current] + 1
                if n not in cost or new_cost < cost[n]:
                    cost[n] = new_cost
                    heapq.heappush(open_set, (new_cost, n))
                    came_from[n] = current

        return None

    def reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        return path[::-1]
