from config import MAPS_DIR
from datetime import datetime
from typing import Optional, List, Tuple

import json
import os


class GridMap:
    FREE = 0
    OBSTACLE = 1
    START = 2
    GOAL = 3
    PATH = 4

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.grid = [[self.FREE for _ in range(width)] for _ in range(height)]

        self.start: Optional[Tuple[int, int]] = None
        self.goal: Optional[Tuple[int, int]] = None

    def is_inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def is_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return True

        return self.grid[y][x] == self.OBSTACLE

    def set_obstacle(self, x: int, y: int, value: bool) -> bool:
        if not self.is_inside(x, y):
            return False

        if (x, y) == self.start or (x, y) == self.goal:
            return False

        if value:
            self.grid[y][x] = self.OBSTACLE
        else:
            self.grid[y][x] = self.FREE

        return True

    def toggle_obstacle(self, x: int, y: int) -> bool:
        if not self.is_inside(x, y):
            return False

        if (x, y) == self.start or (x, y) == self.goal:
            return False

        if self.grid[y][x] == self.OBSTACLE:
            self.grid[y][x] = self.FREE
        else:
            self.grid[y][x] = self.OBSTACLE

        return True

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

    def get_obstacles(self) -> List[Tuple[int, int]]:
        obstacles = []

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == self.OBSTACLE:
                    obstacles.append((x, y))

        return obstacles

    def get_neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
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

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_inside(nx, ny) and not self.is_obstacle(nx, ny):
                neighbors.append((nx, ny))

        return neighbors

    def save_map(self, filepath: Optional[str] = None) -> Optional[str]:
        try:
            if filepath is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                maps_dir = os.path.join(MAPS_DIR, timestamp)
                filepath = os.path.join(maps_dir, "map.json")

            maps_dir = os.path.dirname(filepath)

            data = {
                "width": self.width,
                "height": self.height,
                "start": list(self.start) if self.start else None,
                "goal": list(self.goal) if self.goal else None,
                "obstacles": self.get_obstacles(),
            }
            json_str = json.dumps(data, indent=2)

            os.makedirs(maps_dir, exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

            print(f"Map saved: {filepath}")
            return maps_dir
        except Exception as e:
            print(f"Error saving map: {e}")
            return None

    def load_map(self, filepath: str) -> bool:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.width = data["width"]
            self.height = data["height"]
            self.grid = [
                [self.FREE for _ in range(self.width)] for _ in range(self.height)
            ]

            if data.get("start"):
                self.set_start(data["start"][0], data["start"][1])

            if data.get("goal"):
                self.set_goal(data["goal"][0], data["goal"][1])

            for obs in data.get("obstacles", []):
                self.set_obstacle(obs[0], obs[1], True)

            return True
        except Exception as e:
            print(f"Error loading map: {e}")
            return False

    @staticmethod
    def load_from_path(filepath: str) -> Optional["GridMap"]:
        try:
            if os.path.isdir(filepath):
                filepath = os.path.join(filepath, "map.json")

            if not os.path.exists(filepath):
                print(f"File not found: {filepath}")
                return None

            grid = GridMap(1, 1)
            if grid.load_map(filepath):
                return grid
            return None
        except Exception as e:
            print(f"Error loading map: {e}")
            return None

    @staticmethod
    def list_saved_maps() -> List[str]:
        try:
            if not os.path.exists(MAPS_DIR):
                return []

            return [
                os.path.join(MAPS_DIR, d)
                for d in sorted(os.listdir(MAPS_DIR), reverse=True)
                if os.path.isdir(os.path.join(MAPS_DIR, d))
            ]
        except Exception as e:
            print(f"Error listing maps: {e}")
            return []
