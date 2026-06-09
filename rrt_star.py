"""
RRT* Path Planning Algorithm Module.

RRT* là phiên bản cải tiến của RRT cho phép tối ưu chi phí trong quá trình
xây dựng cây bằng cách chọn parent tốt nhất cho mỗi node và rewire các
nút lân cận khi tìm thấy chi phí tốt hơn.

Module này giữ phong cách độc lập (không kế thừa base class) giống các
planner khác trong project.
"""

from config.parameter import (
    MIN_CLEARANCE,
    RRT_STAR_GOAL_SAMPLE_RATE,
    RRT_STAR_MAX_ITER,
    RRT_STAR_MAX_SAMPLE_ATTEMPTS,
    RRT_STAR_NEIGHBOR_RADIUS,
    RRT_STAR_STEP_SIZE,
)
from grid_map import GridMap
from utils import euclidean_distance, min_distance_line_to_obstacle

import math
import random


class RRTStarNode:
    def __init__(
        self,
        x: int,
        y: int,
        came_from: "RRTStarNode | None" = None,
        cost: float = 0.0,
    ) -> None:
        self.x = x
        self.y = y
        self.came_from = came_from
        self.cost = cost


class RRTStar:
    def __init__(
        self,
        grid_map: GridMap,
        max_iter: int = RRT_STAR_MAX_ITER,
        step_size: int = RRT_STAR_STEP_SIZE,
        goal_sample_rate: float = RRT_STAR_GOAL_SAMPLE_RATE,
        max_sample_attempts: int = RRT_STAR_MAX_SAMPLE_ATTEMPTS,
        neighbor_radius: float = RRT_STAR_NEIGHBOR_RADIUS,
        min_clearance: float = MIN_CLEARANCE,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.max_sample_attempts = max_sample_attempts
        self.neighbor_radius = neighbor_radius
        self.min_clearance = float(min_clearance)
        # Ghi chú tham số:
        # - neighbor_radius: bán kính tìm neighbor để lựa chọn parent/rewire
        # - adaptive radius: được tính trong _near_nodes để điều chỉnh theo kích thước cây

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

        nodes = [RRTStarNode(start[0], start[1])]
        best_goal_node: RRTStarNode | None = None

        # Vòng lặp chính: sample -> steer -> chọn parent tốt nhất -> rewire
        for _ in range(self.max_iter):
            sample = self._sample_point(goal)
            nearest = self._nearest_node(nodes, sample)
            new_point = self._steer(nearest, sample)

            if new_point is None:
                continue

            # Tìm các node lân cận để xem xét chọn parent tốt nhất
            neighbors = self._near_nodes(nodes, new_point)
            parent = self._choose_parent(neighbors, nearest, new_point)
            if parent is None:
                continue

            # Kiểm tra va chạm cho đoạn parent -> new_point
            if self._segment_has_collision((parent.x, parent.y), new_point):
                continue

            new_cost = parent.cost + euclidean_distance((parent.x, parent.y), new_point)
            new_node = RRTStarNode(new_point[0], new_point[1], parent, new_cost)
            nodes.append(new_node)

            # Rewire: nếu new_node cung cấp chi phí tốt hơn cho neighbor thì cập nhật
            self._rewire(neighbors, new_node, nodes)

            # Nếu new_node đủ gần goal, cập nhật best_goal_node nếu chi phí tốt hơn
            if self._is_goal_reached(new_node, goal):
                goal_cost = new_node.cost + euclidean_distance(
                    (new_node.x, new_node.y), goal
                )
                if best_goal_node is None or goal_cost < best_goal_node.cost:
                    if not self._segment_has_collision((new_node.x, new_node.y), goal):
                        best_goal_node = RRTStarNode(
                            goal[0], goal[1], new_node, goal_cost
                        )

        if best_goal_node is None:
            return None

        return self._reconstruct_path(best_goal_node)

    def _sample_point(self, goal: tuple[int, int]) -> tuple[int, int]:
        if random.random() < self.goal_sample_rate:
            return goal

        for _ in range(self.max_sample_attempts):
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)
            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                return (x, y)

        return goal

    def _nearest_node(
        self, nodes: list[RRTStarNode], point: tuple[int, int]
    ) -> RRTStarNode:
        return min(nodes, key=lambda node: euclidean_distance((node.x, node.y), point))

    def _steer(
        self, from_node: RRTStarNode, to_point: tuple[int, int]
    ) -> tuple[int, int] | None:
        delta_x = to_point[0] - from_node.x
        delta_y = to_point[1] - from_node.y
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        if distance < 1e-9:
            return None

        if distance <= self.step_size:
            new_x, new_y = to_point
        else:
            ratio = self.step_size / distance
            new_x = int(round(from_node.x + delta_x * ratio))
            new_y = int(round(from_node.y + delta_y * ratio))

        if not self.grid_map.is_inside(new_x, new_y):
            return None

        if self.grid_map.is_obstacle(new_x, new_y):
            return None

        if new_x == from_node.x and new_y == from_node.y:
            return None

        return (new_x, new_y)

    def _near_nodes(
        self, nodes: list[RRTStarNode], point: tuple[int, int]
    ) -> list[RRTStarNode]:
        node_count = len(nodes)
        if node_count <= 1:
            radius = self.neighbor_radius
        else:
            adaptive_radius = 10.0 * math.sqrt(
                math.log(node_count + 1) / (node_count + 1)
            )
            radius = min(adaptive_radius, self.step_size * 3)

        return [
            node
            for node in nodes
            if euclidean_distance((node.x, node.y), point) <= radius
        ]

    def _choose_parent(
        self,
        neighbors: list[RRTStarNode],
        nearest: RRTStarNode,
        point: tuple[int, int],
    ) -> RRTStarNode | None:
        candidates = neighbors if neighbors else [nearest]
        best_node = None
        best_cost = float("inf")

        for node in candidates:
            if self._segment_has_collision((node.x, node.y), point):
                continue

            cost = node.cost + euclidean_distance((node.x, node.y), point)
            if cost < best_cost:
                best_cost = cost
                best_node = node

        return best_node

    def _rewire(
        self,
        neighbors: list[RRTStarNode],
        new_node: RRTStarNode,
        nodes: list[RRTStarNode],
    ) -> None:
        for node in neighbors:
            if node is new_node.came_from:
                continue

            if self._segment_has_collision((new_node.x, new_node.y), (node.x, node.y)):
                continue

            new_cost = new_node.cost + euclidean_distance(
                (new_node.x, new_node.y), (node.x, node.y)
            )
            if new_cost < node.cost:
                node.came_from = new_node
                node.cost = new_cost
                self._propagate_cost(node, nodes)

    def _propagate_cost(self, node: RRTStarNode, nodes: list[RRTStarNode]) -> None:
        for child in nodes:
            if child.came_from is node:
                child.cost = node.cost + euclidean_distance(
                    (node.x, node.y), (child.x, child.y)
                )
                self._propagate_cost(child, nodes)

    def _is_goal_reached(self, node: RRTStarNode, goal: tuple[int, int]) -> bool:
        return euclidean_distance((node.x, node.y), goal) <= self.step_size

    def _segment_has_collision(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        for x, y in self._bresenham_line(a[0], a[1], b[0], b[1]):
            if not self.grid_map.is_inside(x, y) or self.grid_map.is_obstacle(x, y):
                return True

        if self.min_clearance > 0.0:
            if min_distance_line_to_obstacle(a, b, self.grid_map) <= self.min_clearance:
                return True

        return False

    def _reconstruct_path(self, node: RRTStarNode) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current: RRTStarNode | None = node

        while current is not None:
            path.append((current.x, current.y))
            current = current.came_from

        path.reverse()
        return path

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
