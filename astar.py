from config.parameter import MIN_CLEARANCE
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

        # openset = [(f_score, h_score, g_score, pos)]
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
        start_heuristic = euclidean_distance(start, goal)
        self.f_score = {start: start_heuristic}

        self.visited = set()
        # open_set = [(f_score, h_score, g_score, pos)] - sorted by f_score
        self.open_set = [(start_heuristic, start_heuristic, 0, start)]

        while self.open_set:
            _, _, current_cost, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)

            if current == goal:
                path = self._reconstruct_path(current)

                return path

            for neighbor in self._get_neighbors(current):
                if neighbor in self.visited:
                    continue

                if self.min_clearance > 0.0:
                    if (
                        min_distance_line_to_obstacle(current, neighbor, self.grid_map)
                        <= self.min_clearance
                    ):
                        continue

                cost = euclidean_distance(current, neighbor)
                tentative_g_score = current_cost + cost

                if (
                    neighbor not in self.g_score
                    or tentative_g_score < self.g_score[neighbor]
                ):
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g_score

                    neighbor_heuristic = euclidean_distance(neighbor, goal)
                    self.f_score[neighbor] = tentative_g_score + neighbor_heuristic

                    heapq.heappush(
                        self.open_set,
                        (
                            self.f_score[neighbor],
                            neighbor_heuristic,
                            tentative_g_score,
                            neighbor,
                        ),
                    )

        return None

    def _get_neighbors(self, pos: tuple[float, float]) -> list[tuple[float, float]]:
        neighbors = []

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

        position_x, position_y = pos[0], pos[1]

        for offset_x, offset_y in directions:
            neighbor_x, neighbor_y = position_x + offset_x, position_y + offset_y

            if self.grid_map.is_inside(
                neighbor_x, neighbor_y
            ) and not self.grid_map.is_obstacle(neighbor_x, neighbor_y):
                neighbors.append((neighbor_x, neighbor_y))

        return neighbors

    def _reconstruct_path(
        self, current: tuple[float, float]
    ) -> list[tuple[float, float]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path
