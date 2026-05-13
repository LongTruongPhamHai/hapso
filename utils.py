from grid_map import GridMap
from math import sqrt


def dis_line_to_obs(
    start: tuple[int, int], end: tuple[int, int], obs: tuple[float, float]
) -> float:
    start_x, start_y = start[0] + 0.5, start[1] + 0.5
    end_x, end_y = end[0] + 0.5, end[1] + 0.5
    obs_x, obs_y = obs[0] + 0.5, obs[1] + 0.5

    dx = end_x - start_x
    dy = end_y - start_y

    if dx == 0 and dy == 0:
        return sqrt((obs_x - start_x) ** 2 + (obs_y - start_y) ** 2)

    t = ((obs_x - start_x) * dx + (obs_y - start_y) * dy) / (dx * dx + dy * dy)

    t = max(0, min(1, t))

    nearest_x = start_x + t * dx
    nearest_y = start_y + t * dy

    return sqrt((obs_x - nearest_x) ** 2 + (obs_y - nearest_y) ** 2)


def min_dis_to_obs(
    start: tuple[int, int],
    end: tuple[int, int],
    grid_map: GridMap,
    margin: int = 3,
):
    all_obstacles = grid_map.get_obstacles()

    start_x, start_y = start[0] + 0.5, start[1] + 0.5
    end_x, end_y = end[0] + 0.5, end[1] + 0.5

    min_obs_x = min(start_x, end_x) - margin
    max_obs_x = max(start_x, end_x) + margin

    min_obs_y = min(start_y, end_y) - margin
    max_obs_y = max(start_y, end_y) + margin

    obstacles = [
        (x, y)
        for x, y in all_obstacles
        if min_obs_x <= x <= max_obs_x and min_obs_y <= y <= max_obs_y
    ]

    min_distance = grid_map.height * grid_map.width
    for obs in obstacles:
        distance = dis_line_to_obs(start, end, obs)

        if distance < min_distance:
            min_distance = distance

    return min_distance
