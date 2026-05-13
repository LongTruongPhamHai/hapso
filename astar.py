from math import sqrt
from typing import Optional
from grid_map import GridMap

import heapq


class Astar:
    def __init__(
        self,
        grid_map: GridMap,
        remove_redundant: bool = False,
        remove_transition: bool = False,
        min_clearance: float = 0.0,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.remove_redundant = remove_redundant
        self.remove_transition = remove_transition
        self.min_clearance = float(min_clearance)

        self.g_score: dict[tuple[int, int], float] = {}
        self.f_score: dict[tuple[int, int], float] = {}

        self.came_from: dict[tuple[int, int], tuple[int, int]] = {}
        self.visited: set[tuple[int, int]] = set()

        # openset = [(f_score, h_score, g_score, pos)]
        self.open_set: list[tuple[float, float, float, tuple[int, int]]] = []

    def plan(self) -> Optional[list[tuple[int, int]]]:
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
        start_h = self._movement_cost(start, goal)
        self.f_score = {start: start_h}
        self.visited = set()
        self.open_set = [(start_h, start_h, 0, start)]

        while self.open_set:
            _, _, current_g, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)

            if current == goal:
                path = self._reconstruct_path(current)
                # improve path

            for neighbor in self._get_neighbors(current):
                if neighbor in self.visited:
                    continue

                if self.min_clearance > 0.0:
                    if min

                cost = self._movement_cost(current, neighbor)

                new_g_score = current_g + cost

                if neighbor not in self.g_score or new_g_score < self.g_score[neighbor]:
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = new_g_score
                    neighbor_h = self._movement_cost(neighbor, goal)
                    self.f_score[neighbor] = new_g_score + neighbor_h

                    heapq.heappush(
                        self.open_set,
                        (self.f_score[neighbor], neighbor_h, new_g_score, neighbor),
                    )

        return None

    def _movement_cost(start: tuple[int, int], end: tuple[int, int]) -> float:
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return sqrt(dx * dx + dy * dy)

    def _reconstruct_path(self, current: tuple[int, int]) -> list[tuple[int, int]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def _improve_astar_path(self, path: list[tuple[int, int]]) -> list[tuple[int, int]]:
        optimized_path = path

        if self.remove_redundant:
            if len(optimized_path) <= 2:
                return optimized_path

            rr_path = [optimized_path[0]]
            i = 1
            while i < len(optimized_path) - 1:
                prev_x, prev_y = rr_path[-1]
                curr_x, curr_y = optimized_path[i]
                next_x, next_y = optimized_path[i + 1]

                v1_x = curr_x - prev_x
                v1_y = curr_y - prev_y

                v2_x = next_x - prev_x
                v2_y = next_y - prev_y

                cross_product = v1_x * v2_y - v1_y * v2_x
                is_collinear = abs(cross_product) < 1e-99

                if not is_collinear:
                    rr_path.append((curr_x, curr_y))

                i += 1

            rr_path.append(optimized_path[-1])

        if self.remove_transition:
            obstacle_centers = self.grid_map.get_obstacles_as_centers()

    def _get_neighbors(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
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
        x, y = pos[0], pos[1]

        for dx, dy in directions:
            neighbor_x, neighbor_y = x + dx, y + dy

            if self.grid_map.is_inside(
                neighbor_x, neighbor_y
            ) and not self.grid_map.is_obstacle(neighbor_x, neighbor_y):
                neighbors.append((neighbor_x, neighbor_y))

        return neighbors
