from grid_map import GridMap
from math import sqrt


def distance_line_to_obstacle(
    start_cell: tuple[int, int],
    end_cell: tuple[int, int],
    obstacle: tuple[float, float],
) -> float:
    start_x, start_y = start_cell[0] + 0.5, start_cell[1] + 0.5
    end_x, end_y = end_cell[0] + 0.5, end_cell[1] + 0.5
    obstacle_x, obstacle_y = obstacle[0] + 0.5, obstacle[1] + 0.5

    delta_x = end_x - start_x
    delta_y = end_y - start_y

    if delta_x == 0 and delta_y == 0:
        return sqrt((obstacle_x - start_x) ** 2 + (obstacle_y - start_y) ** 2)

    projection_factor = (
        (obstacle_x - start_x) * delta_x + (obstacle_y - start_y) * delta_y
    ) / (delta_x * delta_x + delta_y * delta_y)

    projection_factor = max(0, min(1, projection_factor))

    nearest_x = start_x + projection_factor * delta_x
    nearest_y = start_y + projection_factor * delta_y

    return sqrt((obstacle_x - nearest_x) ** 2 + (obstacle_y - nearest_y) ** 2)


def min_distance_to_obstacle(
    start_cell: tuple[int, int],
    end_cell: tuple[int, int],
    grid_map: GridMap,
    margin_cells: int = 3,
) -> float:
    obstacle_cells = grid_map.get_obstacles()

    start_x, start_y = start_cell[0] + 0.5, start_cell[1] + 0.5
    end_x, end_y = end_cell[0] + 0.5, end_cell[1] + 0.5

    min_x = min(start_x, end_x) - margin_cells
    max_x = max(start_x, end_x) + margin_cells

    min_y = min(start_y, end_y) - margin_cells
    max_y = max(start_y, end_y) + margin_cells

    nearby_obstacles = [
        (obstacle_x, obstacle_y)
        for obstacle_x, obstacle_y in obstacle_cells
        if min_x <= obstacle_x <= max_x and min_y <= obstacle_y <= max_y
    ]

    closest_distance = grid_map.height * grid_map.width

    for obstacle_cell in nearby_obstacles:
        distance = distance_line_to_obstacle(start_cell, end_cell, obstacle_cell)

        if distance < closest_distance:
            closest_distance = distance

    return closest_distance
