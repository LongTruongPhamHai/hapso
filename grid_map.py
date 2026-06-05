from config.parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH

import numpy as np


class GridMap:
    FREE = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3

    def __init__(
        self, width: int = GRID_MAP_WIDTH, height: int = GRID_MAP_HEIGHT
    ) -> None:
        self.width = width
        self.height = height

        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]
        self.start: tuple[int, int] | None = None
        self.goal: tuple[int, int] | None = None

        self._obstacle_set: set[tuple[int, int]] = set()

    def rebuild_obstacle_set(self) -> None:
        self._obstacle_set = set()

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    self._obstacle_set.add((x, y))

    def get_obstacles(self) -> list[tuple[int, int]]:
        return list(self._obstacle_set)

    def get_obstacle_set(self) -> set[tuple[int, int]]:
        return set(self._obstacle_set)

    def get_obstacle_count(self) -> int:
        return len(self.get_obstacles())

    def get_obstacles_as_centers(self) -> np.ndarray:
        return np.array([[x + 0.5, y + 0.5] for x, y in self.get_obstacles()])

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True

        return (x, y) in self._obstacle_set

    def set_start(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False

        if self.start is not None:
            old_x, old_y = self.start

            if self.grid[old_y][old_x] == self.START:
                self.grid[old_y][old_x] = self.FREE

        self.start = (x, y)
        self.grid[y][x] = self.START

        return True

    def set_goal(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y) or self.is_obstacle(x, y):
            return False

        if self.goal is not None:
            old_x, old_y = self.goal

            if self.grid[old_y][old_x] == self.GOAL:
                self.grid[old_y][old_x] = self.FREE

        self.goal = (x, y)
        self.grid[y][x] = self.GOAL

        return True

    def set_obstacle(self, x: int, y: int, value: bool | None = None) -> bool:
        if not self.is_inside(x, y):
            return False

        if (x, y) == self.start or (x, y) == self.goal:
            return False

        if value is None:
            currently = self.grid[y][x] == self.OBSTACLE
            value = not currently

        if value:
            self.grid[y][x] = self.OBSTACLE
            self._obstacle_set.add((x, y))

        else:
            self.grid[y][x] = self.FREE
            self._obstacle_set.discard((x, y))

        return True

    def resize(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]
        self.start = None
        self.goal = None

        self._obstacle_set = set()
