#!/usr/bin/env python3
"""Unit tests for custom planners A*, Dijkstra, Greedy."""

from astar import AStarPlanner
from dijkstra import DijkstraPlanner
from greedy import GreedyPlanner


def make_test_grid():
    # 0 libre, 1 obstacle
    return [
        [0, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0],
        [0, 0, 0, 1, 0],
    ]


def run_test(planner_class, name):
    grid = make_test_grid()
    planner = planner_class(grid)
    start = (0, 0)
    goal = (4, 4)
    path = planner.plan(start, goal)
    assert path is not None, f"{name} a renvoyé None"
    assert path[0] == start, f"{name}: début invalide {path[0]}"
    assert path[-1] == goal, f"{name}: but invalide {path[-1]}"
    print(f"{name}: path length = {len(path)}")
    print(path)


if __name__ == '__main__':
    run_test(AStarPlanner, 'A*')
    run_test(DijkstraPlanner, 'Dijkstra')
    run_test(GreedyPlanner, 'Greedy')
    print('Tous les tests sont passés.')
