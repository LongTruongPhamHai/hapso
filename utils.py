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
    dx = end_point[0] - start_point[0]
    dy = end_point[1] - start_point[1]

    return sqrt(dx * dx + dy * dy)


def count_waypoints(path: list[tuple[float, float]]) -> int:
    return len(path) if path else 0


def turning_angle(
    prev_point: tuple[float, float],
    curr_point: tuple[float, float],
    next_point: tuple[float, float],
) -> float:
    v1 = (curr_point[0] - prev_point[0], curr_point[1] - prev_point[1])
    v2 = (next_point[0] - curr_point[0], next_point[1] - curr_point[1])

    dot = v1[0] * v2[0] + v1[1] * v2[1]
    cross = v1[0] * v2[1] - v1[1] * v2[0]

    return abs(degrees(atan2(cross, dot)))


def distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle: tuple[float, float],
) -> float:
    sx, sy = start_point[0] + 0.5, start_point[1] + 0.5
    ex, ey = end_point[0] + 0.5, end_point[1] + 0.5
    ox, oy = obstacle[0] + 0.5, obstacle[1] + 0.5

    dx = ex - sx
    dy = ey - sy

    if dx == 0 and dy == 0:
        return euclidean_distance((ox, oy), (sx, sy))

    t = ((ox - sx) * dx + (oy - sy) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    nearest_x = sx + t * dx
    nearest_y = sy + t * dy

    return euclidean_distance((ox, oy), (nearest_x, nearest_y))


def compute_path_length(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 2:
        return 0.0

    return sum(euclidean_distance(path[i], path[i + 1]) for i in range(len(path) - 1))


def compute_total_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    return sum(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_min_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    return min(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_max_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    return max(
        turning_angle(path[i - 1], path[i], path[i + 1])
        for i in range(1, len(path) - 1)
    )


def compute_avg_angle(path: list[tuple[float, float]]) -> float:
    if not path or len(path) < 3:
        return 0.0

    return compute_total_angle(path) / (len(path) - 2)


def get_nearby_obstacles(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle_set: set[tuple[int, int]],
    margin_cells: int = MARGIN_CELL,
) -> list[tuple[float, float]]:
    sx, sy = start_point[0] + 0.5, start_point[1] + 0.5
    ex, ey = end_point[0] + 0.5, end_point[1] + 0.5

    min_x = ceil(min(sx, ex) - margin_cells)
    max_x = floor(max(sx, ex) + margin_cells)
    min_y = ceil(min(sy, ey) - margin_cells)
    max_y = floor(max(sy, ey) + margin_cells)

    return [
        (x, y)
        for x in range(min_x, max_x + 1)
        for y in range(min_y, max_y + 1)
        if (x, y) in obstacle_set
    ]


def min_distance_line_to_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    grid_map: GridMap,
) -> float:
    nearby = get_nearby_obstacles(start_point, end_point, grid_map.get_obstacle_set())

    min_dist = float(grid_map.height * grid_map.width)
    for obs in nearby:
        d = distance_line_to_obstacle(start_point, end_point, obs)
        if d < min_dist:
            min_dist = d

    return min_dist


def min_distance_path_to_obstacle(
    path: list[tuple[float, float]], grid_map: GridMap
) -> float:
    if not path or len(path) < 2:
        return 10000.0

    return min(
        min_distance_line_to_obstacle(path[i], path[i + 1], grid_map)
        for i in range(len(path) - 1)
    )


def compute_fitness(
    path: list[tuple[float, float]],
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict | None = None,
) -> float:
    total_dist = compute_path_length(path)
    avg_angle = compute_avg_angle(path)
    max_angle = compute_max_angle(path)
    min_dist = min_distance_path_to_obstacle(path, grid_map)

    if min_dist < min_clearance:
        return collision_penalty

    if reference_metrics is not None:
        norm_dist = total_dist / (reference_metrics.get("distance", 1.0) + 1e-6)
        norm_avg_angle = avg_angle / (reference_metrics.get("avg_angle", 1.0) + 1e-6)
        norm_max_angle = max_angle / (reference_metrics.get("max_angle", 1.0) + 1e-6)
        norm_clearance = (1.0 / (min_dist + 1e-6)) / (
            reference_metrics.get("clearance", 1.0) + 1e-6
        )
    else:
        grid_diag = euclidean_distance((0, 0), (grid_map.width, grid_map.height))
        norm_dist = total_dist / (grid_diag + 1e-6)
        norm_avg_angle = avg_angle / 180.0
        norm_max_angle = max_angle / 180.0
        norm_clearance = (1.0 / (min_dist + 1e-6)) * min_clearance

    return (
        0.3 * norm_dist
        + 0.3 * norm_avg_angle
        + 0.1 * norm_max_angle
        + 0.3 * norm_clearance
    )


def total_fitness(
    path: list[tuple[float, float]],
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict | None = None,
) -> float:
    return compute_fitness(
        path, grid_map, min_clearance, collision_penalty, reference_metrics
    )


def get_nearby_obstacle(
    start_point: tuple[float, float],
    end_point: tuple[float, float],
    obstacle_set: set[tuple[int, int]],
    margin_cells: int = MARGIN_CELL,
) -> list[tuple[float, float]]:
    return get_nearby_obstacles(start_point, end_point, obstacle_set, margin_cells)


def total_path_length(path: list[tuple[float, float]]) -> float:
    return compute_path_length(path)


def total_turning_angle(path: list[tuple[float, float]]) -> float:
    return compute_total_angle(path)


def min_turning_angle(path: list[tuple[float, float]]) -> float:
    return compute_min_angle(path)


def max_turning_angle(path: list[tuple[float, float]]) -> float:
    return compute_max_angle(path)


def average_turning_angle(path: list[tuple[float, float]]) -> float:
    return compute_avg_angle(path)


def waypoint_count(path: list[tuple[float, float]]) -> int:
    return count_waypoints(path)


def compute_path_metrics(
    path: list[tuple[float, float]],
    algorithm_name: str,
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict | None = None,
) -> dict:
    return {
        algorithm_name: {
            "Total distance": compute_path_length(path),
            "Total waypoint": len(path),
            "Total angle": compute_total_angle(path),
            "Min angle": compute_min_angle(path),
            "Max angle": compute_max_angle(path),
            "Average angle": compute_avg_angle(path),
            "Min clearance": min_distance_path_to_obstacle(path, grid_map),
            "TOTAL FITNESS": compute_fitness(
                path, grid_map, min_clearance, collision_penalty, reference_metrics
            ),
        }
    }


def calculator_path_metrics(
    path: list[tuple[float, float]],
    algorithm_name: str,
    grid_map: GridMap,
    min_clearance: float,
    collision_penalty: float,
    reference_metrics: dict | None = None,
) -> dict:
    return compute_path_metrics(
        path,
        algorithm_name,
        grid_map,
        min_clearance,
        collision_penalty,
        reference_metrics,
    )


def print_path_metrics(path_metrics: dict) -> None:
    metric_keys = [
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
    for algo in algorithms:
        print(f"| {algo:<15}", end="")
    print()
    print("-" * 120)

    for key in metric_keys:
        print(f"{key:<25}", end="")

        for algo in algorithms:
            val = path_metrics[algo].get(key, "-")

            if isinstance(val, float):
                val = f"{val:.4f}"
            print(f"| {str(val):<15}", end="")

        print()

    print("=" * 120)
