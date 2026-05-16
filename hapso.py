from config.parameter import (
    MIN_CLEARANCE,
    ASTAR_REMOVE_REDUNDANT,
    ASTAR_REMOVE_TRANSITION,
    PSO_N_PARTICLES,
    PSO_MAX_ITER,
    PSO_WEIGHT,
    PSO_COGNITIVE_COEFF,
    PSO_SOCIAL_COEFF,
    PSO_VMAX_K,
    PSO_USE_SIW,
    PSO_W_MAX,
    PSO_W_MIN,
    PSO_USE_TVAC,
    PSO_COG_INIT,
    PSO_COG_FINAL,
    PSO_SOC_INIT,
    PSO_SOC_FINAL,
    PSO_USE_SOBL,
    PSO_SOBL_MU,
    PSO_SOBL_SIGMA,
)
from grid_map import GridMap
from math import sqrt
from typing import Optional
from utils import min_distance_line_to_obstacle

import heapq


class HAPSO:
    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
        remove_redundant: bool = ASTAR_REMOVE_REDUNDANT,
        remove_transition: bool = ASTAR_REMOVE_TRANSITION,
        n_particles: int = PSO_N_PARTICLES,
        max_iter: int = PSO_MAX_ITER,
        weight: float = PSO_WEIGHT,
        cognitive_coeff: float = PSO_COGNITIVE_COEFF,
        social_coeff: float = PSO_SOCIAL_COEFF,
        vmax_k: float = PSO_VMAX_K,
        use_siw: bool = PSO_USE_SIW,
        w_min: float = PSO_W_MIN,
        w_max: float = PSO_W_MAX,
        use_tvac: bool = PSO_USE_TVAC,
        cog_init: float = PSO_COG_INIT,
        cog_final: float = PSO_COG_FINAL,
        soc_init: float = PSO_SOC_INIT,
        soc_final: float = PSO_SOC_FINAL,
        use_sobl: bool = PSO_USE_SOBL,
        sobl_mu: float = PSO_SOBL_MU,
        sobl_signma: float = PSO_SOBL_SIGMA,
        animate: bool = False,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.min_clearance = float(min_clearance)
        self.remove_redundant = remove_redundant
        self.remove_transition = remove_transition

        self.g_score: dict[tuple[float, float], float] = {}
        self.f_score: dict[tuple[float, float], float] = {}

        self.came_from: dict[tuple[float, float], tuple[float, float]] = {}
        self.visited: set[tuple[float, float]] = set()
        self.visited_order: list[tuple[float, float]] = []

        self.open_set: list[tuple[float, float, float, tuple[float, float]]] = []

        self.n_particles = n_particles
        self.max_iter = max_iter
        self.weight = weight
        self.cognitive_coeff = cognitive_coeff
        self.social_coeff = social_coeff
        self.vmax_k = vmax_k

        self.use_siw = use_siw
        self.w_min = w_min
        self.w_max = w_max

        self.use_tvac = use_tvac
        self.cog_init = cog_init
        self.cog_final = cog_final
        self.soc_init = soc_init
        self.soc_final = soc_final

        self.use_sobl = use_sobl
        self.sobl_mu = sobl_mu
        self.sobl_sigma = self.sobl_sigma

        self.animate = animate
        self.visual_trace: list[tuple] = []

    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.start
        goal = self.goal
        self.visual_trace = []

        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        if start == goal:
            self.visited_order = [start]

            if self.animate:
                self.visual_trace.append(("visit", start))
                self.visual_trace.append(("path", [start, goal]))

            return [start, goal]

        self.came_from = {}
        self.g_score = {start: 0}
        start_heuristic = self._movement_cost(start, goal)
        self.f_score = {start: start_heuristic}
        self.visited = set()
        self.visited_order = []
        self.open_set = [(start_heuristic, start_heuristic, 0, start)]

        while self.open_set:
            _, _, current_cost, current = heapq.heappop(self.open_set)

            if current in self.visited:
                continue

            self.visited.add(current)
            self.visited_order.append(current)

            if self.animate:
                self.visual_trace.append(("visit", current))

            if current == goal:
                path = self._reconstruct_path(current)
                improved_path = self._improve_astar_path(path)

                if self.animate:
                    self.visual_trace.append(("path", improved_path))

                return improved_path

            for neighbor in self._get_neighbors(current):
                if neighbor in self.visited:
                    continue

                if self.min_clearance > 0.0:
                    if (
                        min_distance_line_to_obstacle(current, neighbor, self.grid_map)
                        <= self.min_clearance
                    ):
                        continue

                cost = self._movement_cost(current, neighbor)
                tentative_g_score = current_cost + cost

                if (
                    neighbor not in self.g_score
                    or tentative_g_score < self.g_score[neighbor]
                ):
                    self.came_from[neighbor] = current
                    self.g_score[neighbor] = tentative_g_score

                    neighbor_heuristic = self._movement_cost(neighbor, goal)
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

    @staticmethod
    def _movement_cost(start: tuple[float, float], end: tuple[float, float]) -> float:
        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]

        return sqrt(delta_x * delta_x + delta_y * delta_y)

    def _reconstruct_path(
        self, current: tuple[float, float]
    ) -> list[tuple[float, float]]:
        path = [current]

        while current in self.came_from:
            current = self.came_from[current]
            path.append(current)

        path.reverse()
        return path

    def _improve_astar_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        current_path = path

        if self.remove_redundant and len(current_path) > 2:
            filtered_path = [current_path[0]]
            index = 1

            while index < len(current_path) - 1:
                prev_x, prev_y = filtered_path[-1]
                curr_x, curr_y = current_path[index]
                next_x, next_y = current_path[index + 1]

                v1_x = curr_x - prev_x
                v1_y = curr_y - prev_y

                v2_x = next_x - prev_x
                v2_y = next_y - prev_y

                cross_product = v1_x * v2_y - v1_y * v2_x
                is_collinear = abs(cross_product) < 1e-99

                if not is_collinear:
                    filtered_path.append((curr_x, curr_y))

                index += 1

            filtered_path.append(current_path[-1])
            current_path = filtered_path

        if self.remove_transition and len(current_path) > 2:
            transition_filtered_path = [current_path[0]]
            index = 1

            while index < len(current_path) - 1:
                prev_point = transition_filtered_path[-1]
                curr_point = current_path[index]
                next_point = current_path[index + 1]

                safe = (
                    min_distance_line_to_obstacle(prev_point, next_point, self.grid_map)
                    > self.min_clearance
                )

                if not safe:
                    transition_filtered_path.append(curr_point)

                index += 1

            transition_filtered_path.append(current_path[-1])
            current_path = transition_filtered_path

        return current_path

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
