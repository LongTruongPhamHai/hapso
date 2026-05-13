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

    def get_obstacles(self) -> list[tuple[int, int]]:
        obstacles = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    obstacles.append((x, y))

        return obstacles

    def get_obstacle_count(self) -> int:
        return len(self.get_obstacles())

    def get_obstacles_as_centers(self) -> np.ndarray:
        return np.array([[x + 0.5, y + 0.5] for x, y in self.get_obstacles()])

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True

        return self.grid[y][x] == self.OBSTACLE

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
            self.grid[y][x] = (
                self.FREE if self.grid[y][x] == self.OBSTACLE else self.OBSTACLE
            )
        else:
            self.grid[y][x] = self.OBSTACLE if value else self.FREE

        return True
