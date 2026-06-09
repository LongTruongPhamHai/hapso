from config.parameter import MARGIN_CELL, ROUND_NUM
from grid_map import GridMap
from math import atan2, ceil, degrees, floor, sqrt
from statistics import median, stdev


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


def _fmt(val) -> str:
    if val is None or val == "-":
        return "-"

    if isinstance(val, bool):
        return "SUCCESS" if val else "FAILED"

    if isinstance(val, float):
        return f"{val:.4f}"

    return str(val)


def print_path_metrics(
    path_metrics: dict,
    *,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    path: list[tuple[float, float]] | None = None,
) -> None:
    algo = next(iter(path_metrics))
    metrics = path_metrics[algo]

    success = bool(path) and path is not None
    result_str = "SUCCESS" if success else "FAILED"

    print("=" * 120)
    print("[ALGORITHM] ALGORITHM REPORT")
    print("=" * 120)
    print(f"{'Algorithm':<16}: {algo}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {start_time}")
    print(f"{'End time':<16}: {end_time}")
    print(f"{'Result':<16}: {result_str}")
    # print(f"{'Path':<16}: {path if path else '[]'}")
    print("-" * 120)
    print("FITNESS / PATH METRICS:")

    _print_metric_row("Total distance", metrics.get("Total distance"))
    _print_metric_row("Average angle", metrics.get("Average angle"))
    _print_metric_row("Min clearance", metrics.get("Min clearance"))
    _print_metric_row("Execution time", metrics.get("Execution time"))
    _print_metric_row("TOTAL FITNESS", metrics.get("TOTAL FITNESS"))

    print("=" * 120)


def _print_metric_row(key: str, val) -> None:
    print(f"{key:<16}: {_fmt(val)}")


def print_all_path_metrics(
    all_path_metrics: dict,
    all_paths: dict,
    *,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    algo_start_times: dict | None = None,
    algo_end_times: dict | None = None,
) -> None:
    algos = list(all_path_metrics.keys())
    algo_start_times = algo_start_times or {}
    algo_end_times = algo_end_times or {}

    col = 14

    def row(key: str, getter) -> None:
        line = f"{key:<{16}}"

        for a in algos:
            val = getter(a)
            line += f"| {_fmt(val):<{col}}"

        print(line)

    print("=" * 120)
    print("[ALGORITHM ALL] ALL ALGORITHM REPORT")
    print("=" * 120)
    print(f"{'Algorithms':<16}: {', '.join(algos)}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {start_time}")
    print(f"{'End time':<16}: {end_time}")
    print("-" * 120)
    print("[ALGORITHM ALL] FITNESS / PATH METRICS:")

    header = f"{'Metrics':<{16}}"
    for a in algos:
        header += f"| {a:<{col}}"
    print(header)
    print("-" * 120)

    row("Result", lambda a: "SUCCESS" if all_paths.get(a) else "FAILED")

    for metric_key in ("Total distance", "Average angle", "Min clearance"):
        row(metric_key, lambda a, k=metric_key: all_path_metrics[a].get(k))

    row("Start time", lambda a: algo_start_times.get(a, "N/A").split()[1])
    row("End time", lambda a: algo_end_times.get(a, "N/A").split()[1])
    row("Execution time", lambda a: all_path_metrics[a].get("Execution time (s)"))
    row("TOTAL FITNESS", lambda a: all_path_metrics[a].get("TOTAL FITNESS"))

    # print("-" * 120)
    # print("PATH DETAIL:")
    # for a in algos:
    #     pts = all_paths.get(a) or []
    #     print(f"{a} path: {pts}")

    print("=" * 120)


def print_batch_run_report(
    run_idx: int,
    run_count: int,
    algo_name: str,
    map_name: str,
    start_time: str,
    end_time: str,
    success: bool,
    path: list[tuple[float, float]],
    metrics: dict | None,
    run_time: float,
) -> None:
    result_str = "SUCCESS" if success else "FAILED"

    # print("=" * 120)
    # print(f"[BATCH] ALGORITHM REPORT ({run_idx}/{run_count})")

    # print("-" * 120)
    # print(f"{'Algorithm':<16}: {algo_name}")
    # print(f"{'Map':<16}: {map_name}")
    # print(f"{'Start time':<16}: {start_time}")
    # print(f"{'End time':<16}: {end_time}")
    # print(f"{'Result':<16}: {result_str}")
    # # print(f"{'Path':<16}: {path if path else '[]'}")

    # print("-" * 120)
    # print("FITNESS / PATH METRICS:")
    # if metrics:
    #     _print_metric_row("Total distance", metrics.get("Total distance"))
    #     _print_metric_row("Average angle", metrics.get("Average angle"))
    #     _print_metric_row("Min clearance", metrics.get("Min clearance"))
    #     _print_metric_row("Execution time", run_time)
    #     _print_metric_row("TOTAL FITNESS", metrics.get("TOTAL FITNESS"))

    # else:
    #     print("  (no metrics — run failed)")


def print_batch_summary_report(
    algo_name: str,
    map_name: str,
    batch_start_time: str,
    batch_end_time: str,
    run_count: int,
    successful_runs: int,
    total_time: float,
    excel_path: str,
    best_run: dict | None,
    run_records: list[dict],
) -> None:
    def _series(key: str) -> list[float]:
        return [
            r[key] for r in run_records if r.get("Success") and r.get(key) is not None
        ]

    dist_vals = _series("Total_Distance")
    angle_vals = _series("Average_Angle")
    clear_vals = _series("Min_Clearance")
    time_vals = _series("Execution_Time_s")
    fit_vals = _series("TOTAL_FITNESS")

    def _stats(vals: list[float]) -> tuple:
        if not vals:
            return ("-", "-", "-", "-", "-")
        best_v = min(vals)
        worst_v = max(vals)
        mean_v = sum(vals) / len(vals)
        med_v = median(vals)
        std_v = stdev(vals) if len(vals) > 1 else 0.0
        return (best_v, worst_v, mean_v, med_v, std_v)

    failed_runs = run_count - successful_runs
    result_stats = (
        f"{successful_runs} OK",
        f"{failed_runs} FAIL",
        "-",
        "-",
        "-",
    )

    col = 14

    def _stat_row(key: str, stats: tuple) -> None:
        best_v, worst_v, mean_v, med_v, std_v = stats
        line = f"{key:<{16}}"
        for v in (best_v, worst_v, mean_v, med_v, std_v):
            line += f"| {_fmt(v):<{col}}"
        print(line)

    print("=" * 120)
    print("[BATCH] RESULTS:")
    print(f"[BATCH] Algorithm   : {algo_name}")
    print(f"[BATCH] Map         : {map_name}")
    print(f"[BATCH] Total runs  : {run_count}")
    print(f"[BATCH] Successful  : {successful_runs}/{run_count}")
    print(f"[BATCH] Start time  : {batch_start_time}")
    print(f"[BATCH] End time    : {batch_end_time}")
    print(f"[BATCH] Total time  : {total_time:.4f}s")
    print(f"[BATCH] Excel       : {excel_path}")

    if best_run:
        print(
            f"[BATCH] Best run    : {best_run['Run_ID']} "
            f"| Fitness = {best_run['TOTAL_FITNESS']:.4f}"
        )
    print("-" * 120)

    header = f"{'Metrics':<{16}}"
    for col_name in ("Best", "Worst", "Mean", "Median", "Std Dev"):
        header += f"| {col_name:<{col}}"
    print(header)
    print("-" * 120)

    _stat_row("Result", result_stats)
    _stat_row("Total distance", _stats(dist_vals))
    _stat_row("Average angle", _stats(angle_vals))
    _stat_row("Min clearance", _stats(clear_vals))
    _stat_row("Execution time", _stats(time_vals))
    _stat_row("TOTAL FITNESS", _stats(fit_vals))

    print("=" * 120)


def print_batch_header(
    algo_name: str,
    map_name: str,
    batch_start_time: str,
    run_count: int,
) -> None:
    print("=" * 120)
    print("[BATCH] ALGORITHM BATCH TEST REPORT")
    print("=" * 120)
    print(f"{'Algorithm':<16}: {algo_name}")
    print(f"{'Map':<16}: {map_name}")
    print(f"{'Start time':<16}: {batch_start_time}")
    print(f"{'Total runs':<16}: {run_count}")
    print("=" * 120)
