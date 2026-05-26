from grid_map import GridMap
from math import atan2, ceil, degrees, floor, sqrt
from config.parameter import MARGIN_CELL, ROUND_NUM


def round_pos(
    point: tuple[float, float], round_num: int = ROUND_NUM
) -> tuple[float, float]:
    return (round(point[0], round_num), round(point[1], round_num))


def euclidean_distance(
    start_point: tuple[float, float], end_point: tuple[float, float]
) -> float:
    delta_x = end_point[0] - start_point[0]
    delta_y = end_point[1] - start_point[1]

    return sqrt(delta_x * delta_x + delta_y * delta_y)


def turning_angle(
    prev_point: tuple[float, float],
    curr_point: tuple[float, float],
    next_point: tuple[float, float],
) -> float:
    vector_1 = (curr_point[0] - prev_point[0], curr_point[1] - prev_point[1])
    vector_2 = (next_point[0] - curr_point[0], next_point[1] - curr_point[1])

    dot_product = vector_1[0] * vector_2[0] + vector_1[1] * vector_2[1]
    cross_product = vector_1[0] * vector_2[1] - vector_1[1] * vector_2[0]

    angle = abs(degrees(atan2(cross_product, dot_product)))

    return angle


def distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle: tuple[float, float],
) -> float:
    start_x, start_y = start_point[0] + 0.5, start_point[1] + 0.5
    end_x, end_y = end_point[0] + 0.5, end_point[1] + 0.5
    obstacle_x, obstacle_y = obstacle[0] + 0.5, obstacle[1] + 0.5

    delta_x = end_x - start_x
    delta_y = end_y - start_y

    if delta_x == 0 and delta_y == 0:
        return euclidean_distance((obstacle_x, obstacle_y), (start_x, start_y))

    projection_factor = (
        (obstacle_x - start_x) * delta_x + (obstacle_y - start_y) * delta_y
    ) / (delta_x * delta_x + delta_y * delta_y)

    projection_factor = max(0, min(1, projection_factor))

    nearest_x = start_x + projection_factor * delta_x
    nearest_y = start_y + projection_factor * delta_y

    return euclidean_distance((obstacle_x, obstacle_y), (nearest_x, nearest_y))


def get_nearby_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle_set: set[tuple[int, int]],
    margin_cells: int = MARGIN_CELL,
) -> list[tuple[float, float]]:
    start_x, start_y = start_point[0] + 0.5, start_point[1] + 0.5
    end_x, end_y = end_point[0] + 0.5, end_point[1] + 0.5

    min_x = ceil(min(start_x, end_x) - margin_cells)
    max_x = floor(max(start_x, end_x) + margin_cells)

    min_y = ceil(min(start_y, end_y) - margin_cells)
    max_y = floor(max(start_y, end_y) + margin_cells)

    nearby_obstacles = [
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) in obstacle_set
    ]

    return nearby_obstacles


def min_turning_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    min_angle = 180.0

    for i in range(1, len(path) - 1):
        segment_angle = turning_angle(path[i - 1], path[i], path[i + 1])

        if segment_angle <= min_angle:
            min_angle = segment_angle

    return min_angle


def max_turning_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    max_angle = 0.0

    for i in range(1, len(path) - 1):
        segment_angle = turning_angle(path[i - 1], path[i], path[i + 1])

        if segment_angle >= max_angle:
            max_angle = segment_angle

    return max_angle


def total_turning_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    total_angle = 0.0

    for i in range(1, len(path) - 1):
        segment_angle = turning_angle(path[i - 1], path[i], path[i + 1])

        total_angle += segment_angle

    return total_angle


def average_turning_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    return total_turning_angle(path) / (len(path) - 2)


def min_distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    grid_map: GridMap,
) -> float:
    nearby_obstacles = get_nearby_obstacle(
        start_point, end_point, grid_map.get_obstacles()
    )

    closest_distance = grid_map.height * grid_map.width

    for obstacle_cell in nearby_obstacles:
        distance = distance_line_to_obstacle(start_point, end_point, obstacle_cell)

        if distance < closest_distance:
            closest_distance = distance

    return closest_distance


def min_distance_path_to_obstacle(
    path: list[tuple[float, float]], grid_map: GridMap
) -> float:
    if not path or len(path) < 2:
        return 10000

    min_distance = 10000
    for i in range(len(path) - 1):
        start_point = path[i]
        end_point = path[i + 1]

        segment_distance = min_distance_line_to_obstacle(
            start_point, end_point, grid_map
        )

        if segment_distance <= min_distance:
            min_distance = segment_distance

    return min_distance


def total_path_length(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 2:
        return 0.0

    total_length = 0.0
    for i in range(len(path) - 1):
        segment_distance = euclidean_distance(path[i], path[i + 1])
        total_length += segment_distance

    return total_length


def compute_reference_metrics(
    start: tuple[float, float],
    goal: tuple[float, float],
    min_clearance: float,
    grid_map: GridMap,
    astar_path: list[tuple[float, float]] | None = None,
) -> dict:
    if astar_path is None:
        return {
            "distance": euclidean_distance(start, goal),
            "avg_angle": 1.0,
            "max_angle": 1.0,
            "clearance": 1.0 / (min_clearance + 1e-6),
        }
    return {
        "distance": total_path_length(astar_path),
        "avg_angle": average_turning_angle(astar_path) or 1.0,
        "max_angle": max_turning_angle(astar_path) or 1.0,
        "clearance": 1.0 / (min_distance_path_to_obstacle(astar_path, grid_map) + 1e-6),
    }


def total_fitness(
    path: list[tuple[float, float]],
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict,
) -> float:
    total_distance = total_path_length(path)
    avg_angle = average_turning_angle(path)
    max_angle = max_turning_angle(path)
    min_dist = min_distance_path_to_obstacle(path, grid_map)

    if min_dist < min_clearance:
        return collision_penalty

    norm_distance = total_distance / (reference_metrics["distance"] + 1e-6)
    norm_avg_angle = avg_angle / (reference_metrics["avg_angle"] + 1e-6)
    norm_max_angle = max_angle / (reference_metrics["max_angle"] + 1e-6)
    norm_clearance = (1.0 / (min_dist + 1e-6)) / (reference_metrics["clearance"] + 1e-6)

    return (
        0.3 * norm_distance
        + 0.3 * norm_avg_angle
        + 0.1 * norm_max_angle
        + 0.3 * norm_clearance
    )


def calculator_path_metrics(
    path: list[tuple[float, float]],
    algorithm_name: str,
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict | None = None,
) -> dict:
    return {
        algorithm_name: {
            "Total distance": total_path_length(path),
            "Total waypoint": len(path),
            "Total angle": total_turning_angle(path),
            "Min angle": min_turning_angle(path),
            "Max angle": max_turning_angle(path),
            "Average angle": average_turning_angle(path),
            "Min clearance": min_distance_path_to_obstacle(path, grid_map),
            "TOTAL FITNESS": total_fitness(
                path, grid_map, min_clearance, collision_penalty, reference_metrics
            ),
        }
    }


def print_path_metrics(path_metrics: dict) -> None:
    metrics = [
        "Total distance",
        "Total waypoint",
        "Total angle",
        "Min angle",
        "Max angle",
        "Average angle",
        "Min clearance",
        "Execution time",
        "TOTAL FITNESS",
    ]

    algorithms = list(path_metrics.keys())

    print("=" * 120)

    print(f"{'Metric':<25}", end="")
    for algorithm in algorithms:
        print(f"| {algorithm:<15}", end="")

    print()
    print("-" * 120)

    for metric in metrics:
        print(f"{metric:<25}", end="")

        for algorithm in algorithms:
            value = path_metrics[algorithm].get(metric, "-")

            if isinstance(value, float):
                value = f"{value:.4f}"

            print(f"| {str(value):<15}", end="")

        print()

    print("=" * 120)
