from typing import List, Optional, Tuple

import math
import numpy as np


def has_corner_obstacle(grid, p1: Tuple[float, float], p2: Tuple[float, float]) -> bool:
    x1, y1 = int(round(p1[0])), int(round(p1[1]))
    x2, y2 = int(round(p2[0])), int(round(p2[1]))

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    if dx == 1 and dy == 1:
        corner1_x = x1 if x2 < x1 else x2
        corner1_y = y1 if y2 > y1 else y2

        corner2_x = x1 if x2 > x1 else x2
        corner2_y = y1 if y2 < y1 else y2

        if grid.is_obstacle(corner1_x, corner1_y) or grid.is_obstacle(
            corner2_x, corner2_y
        ):
            return True

    return False


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)
