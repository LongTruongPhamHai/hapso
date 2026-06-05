"""
RRT Path Planning Algorithm Module.

Triển khai RRT (Rapidly-exploring Random Tree) dưới dạng module độc lập.
Thiết kế tương tự các planner khác trong project: không dùng base class,
mỗi planner có `plan()` trả về danh sách waypoint hoặc `None`.

Luồng chính:
- Lấy `start`/`goal` từ `GridMap`
- Lặp sampling & steer để mở rộng cây
- Kiểm tra va chạm bằng Bresenham + kiểm tra `min_clearance`
- Khi tìm thấy goal, dựng lại đường đi từ node đến root
"""

from config.parameter import (
    MIN_CLEARANCE,
    RRT_GOAL_SAMPLE_RATE,
    RRT_MAX_ITER,
    RRT_MAX_SAMPLE_ATTEMPTS,
    RRT_STEP_SIZE,
)
from grid_map import GridMap
from utils import euclidean_distance, min_distance_line_to_obstacle

import math
import random


class RRTNode:
    def __init__(
        self,
        x: int,
        y: int,
        came_from: "RRTNode | None" = None,
    ) -> None:
        self.x = x
        self.y = y
        self.came_from = came_from


class RRT:
    def __init__(
        self,
        grid_map: GridMap,
        max_iter: int = RRT_MAX_ITER,
        step_size: int = RRT_STEP_SIZE,
        goal_sample_rate: float = RRT_GOAL_SAMPLE_RATE,
        max_sample_attempts: int = RRT_MAX_SAMPLE_ATTEMPTS,
        min_clearance: float = MIN_CLEARANCE,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.max_iter = max_iter
        self.step_size = step_size
        self.goal_sample_rate = goal_sample_rate
        self.max_sample_attempts = max_sample_attempts
        self.min_clearance = float(min_clearance)
        # Ghi chú tham số:
        # - max_iter: số vòng lặp tối đa để tìm path
        # - step_size: bước tiến tối đa mỗi lần steer (đơn vị ô)
        # - goal_sample_rate: xác suất trực tiếp sample goal (bias towards goal)
        # - max_sample_attempts: số lần thử sampling hợp lệ trước khi trả về goal

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

        # Khởi tạo cây với nút gốc là start
        nodes = [RRTNode(start[0], start[1])]

        # Vòng lặp chính: sampling, steer, collision check, append node
        for _ in range(self.max_iter):
            sample = self._sample_point(goal)  # sample point (goal-biased)
            nearest = self._nearest_node(nodes, sample)  # find nearest in tree
            new_point = self._steer(nearest, sample)  # attempt to step towards sample

            if new_point is None:
                continue

            # Kiểm tra va chạm đoạn nearest -> new_point
            if self._segment_has_collision((nearest.x, nearest.y), new_point):
                continue

            new_node = RRTNode(new_point[0], new_point[1], nearest)
            nodes.append(new_node)

            # Nếu đạt goal (trong khoảng step_size) và đoạn tới goal an toàn -> reconstruct
            if self._is_goal_reached(new_node, goal):
                if not self._segment_has_collision((new_node.x, new_node.y), goal):
                    goal_node = RRTNode(goal[0], goal[1], new_node)
                    return self._reconstruct_path(goal_node)

        return None

    def _sample_point(self, goal: tuple[int, int]) -> tuple[int, int]:
        if random.random() < self.goal_sample_rate:
            return goal

        # Thử sampling nhiều lần để tìm ô hợp lệ (không phải obstacle)
        for _ in range(self.max_sample_attempts):
            x = random.randint(0, self.grid_map.width - 1)
            y = random.randint(0, self.grid_map.height - 1)
            if self.grid_map.is_inside(x, y) and not self.grid_map.is_obstacle(x, y):
                return (x, y)

        # Nếu không tìm được sample hợp lệ sau nhiều lần thử -> fallback về goal
        return goal

    def _nearest_node(self, nodes: list[RRTNode], point: tuple[int, int]) -> RRTNode:
        return min(nodes, key=lambda node: euclidean_distance((node.x, node.y), point))

    def _steer(
        self, from_node: RRTNode, to_point: tuple[int, int]
    ) -> tuple[int, int] | None:
        delta_x = to_point[0] - from_node.x
        delta_y = to_point[1] - from_node.y
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        # Nếu khoảng cách quá nhỏ -> không tạo node mới
        if distance < 1e-9:
            return None

        # Nếu trong bước, đi thẳng tới điểm đích, nếu không chỉ đi tối đa `step_size`
        if distance <= self.step_size:
            new_x, new_y = to_point
        else:
            ratio = self.step_size / distance
            new_x = int(round(from_node.x + delta_x * ratio))
            new_y = int(round(from_node.y + delta_y * ratio))

        # Kiểm tra ranh giới và chướng ngại tại điểm mới
        if not self.grid_map.is_inside(new_x, new_y):
            return None

        if self.grid_map.is_obstacle(new_x, new_y):
            return None

        # Nếu điểm mới trùng điểm cũ -> bỏ
        if new_x == from_node.x and new_y == from_node.y:
            return None

        return (new_x, new_y)

    def _is_goal_reached(self, node: RRTNode, goal: tuple[int, int]) -> bool:
        return euclidean_distance((node.x, node.y), goal) <= self.step_size

    def _segment_has_collision(self, a: tuple[int, int], b: tuple[int, int]) -> bool:
        for x, y in self._bresenham_line(a[0], a[1], b[0], b[1]):
            if not self.grid_map.is_inside(x, y) or self.grid_map.is_obstacle(x, y):
                return True

        if self.min_clearance > 0.0:
            if min_distance_line_to_obstacle(a, b, self.grid_map) <= self.min_clearance:
                return True

        return False

    def _reconstruct_path(self, node: RRTNode) -> list[tuple[int, int]]:
        path: list[tuple[int, int]] = []
        current: RRTNode | None = node

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
        points = []
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
