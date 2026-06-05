"""
PRM Path Planning Algorithm Module.

PRM (Probabilistic Roadmap) xây dựng một đồ thị các điểm sample hợp lệ
trên không gian (roadmap) rồi kết nối các điểm lân cận nếu đoạn nối không va chạm.
Sau đó dùng thuật toán ngắn nhất (Dijkstra) trên roadmap để tìm đường từ start->goal.
"""

from config.parameter import (
    PRM_CONNECTION_RADIUS,
    PRM_MAX_SAMPLE_ATTEMPTS,
    PRM_N_SAMPLES,
)
from grid_map import GridMap
from utils import euclidean_distance

import heapq
import random


class PRMNode:
    def __init__(self, x: int, y: int, node_id: int) -> None:
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
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal
        self.n_samples = n_samples
        self.connection_radius = connection_radius
        self.max_sample_attempts = max_sample_attempts
        self.roadmap: dict[int, PRMNode] = {}
        self.node_counter = 0
        # Ghi chú tham số:
        # - n_samples: số điểm sample để xây dựng roadmap
        # - connection_radius: khoảng cách tối đa để tạo cạnh giữa 2 node
        # - max_sample_attempts: số lần thử để tìm sample hợp lệ

    def plan(self) -> list[tuple[float, float]] | None:
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

        # Bước 1: Xây dựng roadmap (chỉ sample các điểm hợp lệ trên bản đồ)
        self._build_roadmap()

        # Bước 2: Kết nối start và goal vào roadmap như các node tạm thời
        start_node = self._connect_point(start)
        goal_node = self._connect_point(goal)

        # Nếu không thể kết nối start/goal vào đồ thị, trả về None
        if start_node is None or goal_node is None:
            self._remove_query_nodes([start_node, goal_node])
            return None

        # Bước 3: Tìm đường ngắn nhất trên roadmap giữa start_node và goal_node
        path = self._search(start_node, goal_node)

        # Bước 4: Dọn các node tạm (start/goal) khỏi roadmap để giữ nguyên trạng
        self._remove_query_nodes([start_node, goal_node])
        return path

    def _build_roadmap(self) -> None:
        self.roadmap = {}
        self.node_counter = 0

        samples: list[tuple[int, int]] = []
        attempts = 0
        max_attempts = self.n_samples * self.max_sample_attempts

        # Thực hiện sampling ngẫu nhiên để thu thập các điểm hợp lệ
        while len(samples) < self.n_samples and attempts < max_attempts:
            attempts += 1
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)
            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                samples.append((x, y))

        # Tạo node cho mỗi sample
        for x, y in samples:
            self.roadmap[self.node_counter] = PRMNode(x, y, self.node_counter)
            self.node_counter += 1

        # Kết nối các node nếu trong bán kính kết nối và đoạn nối không va chạm
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

    def _connect_point(self, point: tuple[int, int]) -> PRMNode | None:
        node = PRMNode(point[0], point[1], self.node_counter)
        connected = False

        # Kết nối điểm truy vấn (start/goal) vào đồ thị nếu có neighbor hợp lệ
        for other_id, other_node in self.roadmap.items():
            distance = euclidean_distance(
                (node.x, node.y), (other_node.x, other_node.y)
            )
            if distance <= self.connection_radius and not self._segment_has_collision(
                (node.x, node.y), (other_node.x, other_node.y)
            ):
                node.neighbors.append((other_id, distance))
                other_node.neighbors.append((node.node_id, distance))
                connected = True

        if not connected:
            return None

        self.roadmap[node.node_id] = node
        self.node_counter += 1
        return node

    def _remove_query_nodes(self, nodes: list[PRMNode | None]) -> None:
        for node in nodes:
            if node is None:
                continue

            current = self.roadmap.pop(node.node_id, None)
            if current is None:
                continue

            # Loại bỏ các cạnh trỏ tới node bị xoá trong neighbor list của các node còn lại
            for neighbor_id, _ in current.neighbors:
                neighbor = self.roadmap.get(neighbor_id)
                if neighbor is None:
                    continue

                neighbor.neighbors = [
                    (existing_neighbor_id, distance)
                    for existing_neighbor_id, distance in neighbor.neighbors
                    if existing_neighbor_id != current.node_id
                ]

    def _search(
        self, start_node: PRMNode, goal_node: PRMNode
    ) -> list[tuple[int, int]] | None:
        distances: dict[int, float] = {
            node_id: float("inf") for node_id in self.roadmap
        }
        came_from: dict[int, int | None] = {node_id: None for node_id in self.roadmap}
        distances[start_node.node_id] = 0.0
        open_set: list[tuple[float, int]] = [(0.0, start_node.node_id)]

        # Dijkstra trên đồ thị roadmap
        while open_set:
            current_dist, current_id = heapq.heappop(open_set)

            if current_dist > distances[current_id]:
                continue

            if current_id == goal_node.node_id:
                return self._reconstruct_path(goal_node.node_id, came_from)

            current = self.roadmap[current_id]
            for neighbor_id, edge_distance in current.neighbors:
                new_dist = current_dist + edge_distance
                if new_dist < distances[neighbor_id]:
                    distances[neighbor_id] = new_dist
                    came_from[neighbor_id] = current_id
                    heapq.heappush(open_set, (new_dist, neighbor_id))

        return None

    def _reconstruct_path(
        self,
        goal_id: int,
        came_from: dict[int, int | None],
    ) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current_id: int | None = goal_id

        while current_id is not None:
            node = self.roadmap[current_id]
            path.append((node.x, node.y))
            current_id = came_from[current_id]

        path.reverse()
        return path

    def _segment_has_collision(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        for x, y in self._bresenham_line(a[0], a[1], b[0], b[1]):
            if not self.grid_map.is_inside(x, y) or self.grid_map.is_obstacle(x, y):
                return True

        return False

    def _bresenham_line(
        self,
        x_start: int,
        y_start: int,
        x_end: int,
        y_end: int,
    ) -> list[tuple[int, int]]:
        points: list[tuple[int, int]] = []
        delta_x = abs(x_end - x_start)
        delta_y = abs(y_end - y_start)
        step_x = 1 if x_start < x_end else -1
        step_y = 1 if y_start < y_end else -1
        err = delta_x - delta_y

        x, y = x_start, y_start
        while True:
            points.append((x, y))
            if x == x_end and y == y_end:
                break
            e2 = 2 * err
            if e2 > -delta_y:
                err -= delta_y
                x += step_x
            if e2 < delta_x:
                err += delta_x
                y += step_y

        return points
