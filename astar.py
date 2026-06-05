from config.parameter import (
    MIN_CLEARANCE,
)
from grid_map import GridMap
from typing import Optional
from utils import euclidean_distance, min_distance_line_to_obstacle

import heapq


class Astar:
    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.min_clearance = float(min_clearance)

        self.g_score: dict[tuple[float, float], float] = {}
        self.f_score: dict[tuple[float, float], float] = {}

        self.came_from: dict[tuple[float, float], tuple[float, float]] = {}
        self.visited: set[tuple[float, float]] = set()

        # open_set = [(f_score, h_score, g_score, pos)]
        self.open_set: list[tuple[float, float, float, tuple[float, float]]] = []

    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.start
        goal = self.goal

        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        if start == goal:
            return [start, goal]

        self.came_from = {}
        self.g_score = {start: 0}
        start_h = euclidean_distance(start, goal)
        self.f_score = {start: start_h}
        self.visited = set()
        self.open_set = [(start_h, start_h, 0, start)]

        while self.open_set:
            _, _, g_curr, curr = heapq.heappop(self.open_set)

            if curr in self.visited:
                continue

            self.visited.add(curr)

            if curr == goal:
                return self._reconstruct_path(curr)

            for neighbor in self._get_neighbors(curr):
                if neighbor in self.visited:
                    continue

                if self.min_clearance > 0.0:
                    if (
                        min_distance_line_to_obstacle(curr, neighbor, self.grid_map)
                        <= self.min_clearance
                    ):
                        continue

                move_cost = euclidean_distance(curr, neighbor)
                tentative_g = g_curr + move_cost

                if neighbor not in self.g_score or tentative_g < self.g_score[neighbor]:
                    self.came_from[neighbor] = curr
                    self.g_score[neighbor] = tentative_g

                    neighbor_h = euclidean_distance(neighbor, goal)
                    self.f_score[neighbor] = tentative_g + neighbor_h

                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], neighbor_h, tentative_g, neighbor),
                    )

        return None

    def _get_neighbors(self, pos: tuple[float, float]) -> list[tuple[float, float]]:
        directions = [
            (0, -1),
            (0, 1),
            (-1, 0),
            (1, 0),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]

        px, py = pos
        neighbors = []

        for dx, dy in directions:
            nx, ny = px + dx, py + dy

            if self.grid_map.is_inside(nx, ny) and not self.grid_map.is_obstacle(
                nx, ny
            ):
                neighbors.append((nx, ny))

        return neighbors

    def _reconstruct_path(self, curr: tuple[float, float]) -> list[tuple[float, float]]:
        path = [curr]

        while curr in self.came_from:
            curr = self.came_from[curr]
            path.append(curr)

        path.reverse()
        return path
