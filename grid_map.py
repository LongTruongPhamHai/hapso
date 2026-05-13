import numpy as np


class GridMap:
    FREE = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3

    def __init__(self, width: int, height: int) -> None:
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

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "grid": self.grid,
            "start": self.start,
            "goal": self.goal,
        }

    # def clear_map
    # def from_dict
    # def get_neighbors
    # def set_goal
    # def set_obstacle
    # def set_start
    # def toggle_obstacle
