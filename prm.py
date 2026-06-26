from config.parameter import (
    MIN_CLEARANCE,
    PRM_CONNECTION_RADIUS,
    PRM_MAX_SAMPLE_ATTEMPTS,
    PRM_N_SAMPLES,
)
from grid_map import GridMap
from typing import Optional
from utils import euclidean_distance, min_distance_line_to_obstacle

import heapq
import random


class PRMNode:
    def __init__(
        self,
        x: int,
        y: int,
        node_id: int,
    ) -> None:
        self.x = x
        self.y = y
        self.node_id = node_id
        self.neighbors: list[tuple[int, float]] = []


class PRM:
    def __init__(
        self,
        grid_map: GridMap,
        n_samples: int = PRM_N_SAMPLES,
        connection_radius: float = PRM_CONNECTION_RADIUS,
        max_sample_attempts: int = PRM_MAX_SAMPLE_ATTEMPTS,
        min_clearance: float = MIN_CLEARANCE,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.n_samples = n_samples
        self.connection_radius = connection_radius
        self.max_sample_attempts = max_sample_attempts
        self.min_clearance = float(min_clearance)

        self.roadmap: dict[int, PRMNode] = {}
        self.node_counter = 0

    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.grid_map.start
        goal = self.grid_map.goal

        if start is None or goal is None:
            return None

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

        self._build_roadmap()

        start_node = self._connect_point(start)
        goal_node = self._connect_point(goal)

        if start_node is None or goal_node is None:
            self._remove_query_nodes([start_node, goal_node])
            return None

        path = self._search(start_node, goal_node)

        self._remove_query_nodes([start_node, goal_node])

        return path

    def _build_roadmap(self) -> None:
        self.roadmap = {}
        self.node_counter = 0

        samples: list[tuple[int, int]] = []
        attempts = 0
        max_attempts = self.n_samples * self.max_sample_attempts

        while len(samples) < self.n_samples and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)

            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                samples.append((x, y))

        for x, y in samples:
            self.roadmap[self.node_counter] = PRMNode(x, y, self.node_counter)
            self.node_counter += 1

        for node_id, node in list(self.roadmap.items()):
            for other_id, other_node in list(self.roadmap.items()):
                if other_id == node_id:
                    continue

                distance = euclidean_distance(
                    (node.x, node.y), (other_node.x, other_node.y)
                )

                if (
                    distance <= self.connection_radius
                    and not self._segment_has_collision(
                        (node.x, node.y), (other_node.x, other_node.y)
                    )
                ):
                    node.neighbors.append((other_id, distance))

    def _connect_point(self, point: tuple[int, int]) -> Optional[PRMNode]:
        new_node = PRMNode(point[0], point[1], self.node_counter)
        is_connected = False

        for other_id, other_node in self.roadmap.items():
            distance = euclidean_distance(
                (new_node.x, new_node.y), (other_node.x, other_node.y)
            )

            if distance <= self.connection_radius and not self._segment_has_collision(
                (new_node.x, new_node.y), (other_node.x, other_node.y)
            ):
                new_node.neighbors.append((other_id, distance))
                other_node.neighbors.append((new_node.node_id, distance))
                is_connected = True

        if not is_connected:
            return None

        self.roadmap[new_node.node_id] = new_node
        self.node_counter += 1

        return new_node

    def _remove_query_nodes(self, nodes: list[Optional[PRMNode]]) -> None:
        for node in nodes:
            if node is None:
                continue

            removed_node = self.roadmap.pop(node.node_id, None)

            if removed_node is None:
                continue

            for neighbor_id, _ in removed_node.neighbors:
                neighbor = self.roadmap.get(neighbor_id)

                if neighbor is None:
                    continue

                neighbor.neighbors = [
                    (existing_id, dist)
                    for existing_id, dist in neighbor.neighbors
                    if existing_id != removed_node.node_id
                ]

    def _search(
        self,
        start_node: PRMNode,
        goal_node: PRMNode,
    ) -> Optional[list[tuple[int, int]]]:
        distances: dict[int, float] = {
            node_id: float("inf") for node_id in self.roadmap
        }
        came_from: dict[int, Optional[int]] = {
            node_id: None for node_id in self.roadmap
        }
        distances[start_node.node_id] = 0.0
        open_set: list[tuple[float, int]] = [(0.0, start_node.node_id)]

        while open_set:
            current_dist, current_id = heapq.heappop(open_set)

            if current_dist > distances[current_id]:
                continue

            if current_id == goal_node.node_id:
                return self._reconstruct_path(goal_node.node_id, came_from)

            current_node = self.roadmap[current_id]

            for neighbor_id, edge_distance in current_node.neighbors:
                new_dist = current_dist + edge_distance

                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    came_from[neighbor_id] = current_id
                    heapq.heappush(open_set, (new_dist, neighbor_id))

        return None

    def _reconstruct_path(
        self,
        goal_id: int,
        came_from: dict[int, Optional[int]],
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current_id: Optional[int] = goal_id

        while current_id is not None:
            node = self.roadmap[current_id]
            path.append((node.x, node.y))
            current_id = came_from[current_id]

        path.reverse()
        return path

    def _segment_has_collision(
        self,
        point_a: tuple[float, float],
        point_b: tuple[float, float],
    ) -> bool:
        if (
            min_distance_line_to_obstacle(point_a, point_b, self.grid_map)
            <= self.min_clearance
        ):
            return True

        return False
