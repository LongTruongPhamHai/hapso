from astar import Astar
from config.parameter import (
    MIN_CLEARANCE,
    PSO_N_PARTICLES,
    PSO_MAX_INIT_ATTEMPTS,
    PSO_MAX_ITER,
    PSO_WEIGHT,
    PSO_COGNITIVE_COEFF,
    PSO_SOCIAL_COEFF,
    PSO_COLLISION_PENALTY,
    PSO_VMAX_K,
    PSO_USE_SIW,
    PSO_W_MAX,
    PSO_W_MIN,
    PSO_USE_TVAC,
    PSO_COG_INIT,
    PSO_COG_FINAL,
    PSO_SOC_INIT,
    PSO_SOC_FINAL,
    PSO_USE_SOBL,
    PSO_SOBL_MARGIN,
    PSO_SOBL_MU,
    PSO_SOBL_SIGMA,
    PSO_USE_BEZIER,
    PSO_BEZIER_THRESHOLD,
    PSO_BEZIER_BLEND_RATIO,
    PSO_BEZIER_N_POINTS,
)
from grid_map import GridMap
from math import exp, sqrt
from random import gauss, uniform
from typing import Optional
from utils import (
    compute_fitness,
    euclidean_distance,
    min_distance_line_to_obstacle,
    round_pos,
    turning_angle,
)


class HAPSO:
    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
        n_particles: int = PSO_N_PARTICLES,
        max_init_attempts: int = PSO_MAX_INIT_ATTEMPTS,
        max_iter: int = PSO_MAX_ITER,
        weight: float = PSO_WEIGHT,
        cognitive_coeff: float = PSO_COGNITIVE_COEFF,
        social_coeff: float = PSO_SOCIAL_COEFF,
        collision_penalty: float = PSO_COLLISION_PENALTY,
        vmax_k: float = PSO_VMAX_K,
        use_siw: bool = PSO_USE_SIW,
        w_min: float = PSO_W_MIN,
        w_max: float = PSO_W_MAX,
        use_tvac: bool = PSO_USE_TVAC,
        cog_init: float = PSO_COG_INIT,
        cog_final: float = PSO_COG_FINAL,
        soc_init: float = PSO_SOC_INIT,
        soc_final: float = PSO_SOC_FINAL,
        use_sobl: bool = PSO_USE_SOBL,
        sobl_margin: float = PSO_SOBL_MARGIN,
        sobl_mu: float = PSO_SOBL_MU,
        sobl_sigma: float = PSO_SOBL_SIGMA,
        use_bezier: bool = PSO_USE_BEZIER,
        bezier_threshold: float = PSO_BEZIER_THRESHOLD,
        bezier_blend_ratio: float = PSO_BEZIER_BLEND_RATIO,
        bezier_n_points: int = PSO_BEZIER_N_POINTS,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.min_clearance = float(min_clearance)

        self.n_particles = n_particles
        self.max_init_attempts = max_init_attempts
        self.max_iter = max_iter
        self.weight = weight
        self.cognitive_coeff = cognitive_coeff
        self.social_coeff = social_coeff
        self.collision_penalty = collision_penalty
        self.vmax_k = vmax_k

        self.use_siw = use_siw
        self.w_min = w_min
        self.w_max = w_max

        self.use_tvac = use_tvac
        self.cog_init = cog_init
        self.cog_final = cog_final
        self.soc_init = soc_init
        self.soc_final = soc_final

        self.use_sobl = use_sobl
        self.sobl_margin = sobl_margin
        self.sobl_mu = sobl_mu
        self.sobl_sigma = sobl_sigma

        self.use_bezier = use_bezier
        self.bezier_threshold = bezier_threshold
        self.bezier_blend_ratio = bezier_blend_ratio
        self.bezier_n_points = bezier_n_points

    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.start
        goal = self.goal

        if not self.grid_map.is_inside(start[0], start[1]) or self.grid_map.is_obstacle(
            start[0], start[1]
        ):
            return None

        if not self.grid_map.is_inside(goal[0], goal[1]) or self.grid_map.is_obstacle(
            goal[0], goal[1]
        ):
            return None

        if start == goal:
            return [start, goal]

        initial_path = self._run_astar()
        if initial_path is None:
            return None

        pso_path = self._pso_optimize_path(initial_path)
        smooth_path = self._smooth_path(pso_path)
        smooth_path.append(goal)

        return smooth_path

    def _run_astar(self) -> Optional[list[tuple[float, float]]]:
        return Astar(grid_map=self.grid_map).plan()

    def _pso_optimize_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        if len(path) <= 2:
            return path

        optimized = [path[0]]

        for i in range(1, len(path) - 1):
            prev_point = optimized[-1]
            next_point = path[i + 1]

            particles = self._init_particles(prev_point, next_point)
            best_pos = self._run_pso_segment(particles, prev_point, next_point)
            optimized.append(round_pos(best_pos))

        return optimized

    def _init_particles(
        self, prev_point: tuple[float, float], next_point: tuple[float, float]
    ) -> list[dict]:
        particles = []

        max_vel = self.vmax_k * sqrt(
            (next_point[0] - prev_point[0]) ** 2 + (next_point[1] - prev_point[1]) ** 2
        )

        for _ in range(self.n_particles):
            px, py = self._sample_valid_position(prev_point, next_point)

            vel_x = uniform(-max_vel, max_vel)
            vel_y = uniform(-max_vel, max_vel)

            fitness = self._eval_fitness((px, py), prev_point, next_point)

            particles.append(
                {
                    "pos": (px, py),
                    "vel": (vel_x, vel_y),
                    "best_pos": (px, py),
                    "best_fitness": fitness,
                    "fitness": fitness,
                }
            )

        return particles

    def _sample_valid_position(
        self, prev_point: tuple[float, float], next_point: tuple[float, float]
    ) -> tuple[float, float]:
        for _ in range(self.max_init_attempts):
            t = uniform(0.0, 1.0)
            px = prev_point[0] + (next_point[0] - prev_point[0]) * t
            py = prev_point[1] + (next_point[1] - prev_point[1]) * t
            pos = round_pos((px, py))

            if not self.grid_map.is_inside(px, py):
                continue

            if self.grid_map.is_obstacle(int(px), int(py)):
                continue

            if (
                min_distance_line_to_obstacle(pos, pos, self.grid_map)
                < self.min_clearance
            ):
                continue

            return (px, py)

        return (
            round((prev_point[0] + next_point[0]) / 2.0, 2),
            round((prev_point[1] + next_point[1]) / 2.0, 2),
        )

    def _run_pso_segment(
        self,
        particles: list[dict],
        prev_point: tuple[float, float],
        next_point: tuple[float, float],
    ) -> tuple[float, float]:
        gbest = min(particles, key=lambda p: p["best_fitness"])
        gbest_pos = gbest["best_pos"]
        gbest_fitness = gbest["best_fitness"]

        if self.use_sobl:
            lb_x = min(prev_point[0], next_point[0]) - self.sobl_margin
            ub_x = max(prev_point[0], next_point[0]) + self.sobl_margin
            lb_y = min(prev_point[1], next_point[1]) - self.sobl_margin
            ub_y = max(prev_point[1], next_point[1]) + self.sobl_margin

        for it in range(self.max_iter):
            w = self._inertia_weight(it)
            cog_t, soc_t = self._acceleration_coeffs(it)

            for p in particles:
                vel_x, vel_y = p["vel"]
                pos_x, pos_y = p["pos"]
                pb_x, pb_y = p["best_pos"]

                new_vel_x = (
                    w * vel_x
                    + cog_t * uniform(0.0, 1.0) * (pb_x - pos_x)
                    + soc_t * uniform(0.0, 1.0) * (gbest_pos[0] - pos_x)
                )
                new_vel_y = (
                    w * vel_y
                    + cog_t * uniform(0.0, 1.0) * (pb_y - pos_y)
                    + soc_t * uniform(0.0, 1.0) * (gbest_pos[1] - pos_y)
                )

                new_pos = round_pos((pos_x + new_vel_x, pos_y + new_vel_y))

                if self.use_sobl:
                    r = gauss(self.sobl_mu, self.sobl_sigma)
                    opp_x = max(lb_x, min(ub_x, round(lb_x + ub_x - new_pos[0] * r, 2)))
                    opp_y = max(lb_y, min(ub_y, round(lb_y + ub_y - new_pos[1] * r, 2)))

                    fit_new = self._eval_fitness(new_pos, prev_point, next_point)
                    fit_opp = self._eval_fitness((opp_x, opp_y), prev_point, next_point)

                    if fit_opp < fit_new:
                        p["pos"] = (opp_x, opp_y)
                        p["fitness"] = fit_opp

                    else:
                        p["pos"] = new_pos
                        p["fitness"] = fit_new

                else:
                    p["pos"] = new_pos
                    p["fitness"] = self._eval_fitness(new_pos, prev_point, next_point)

                p["vel"] = (new_vel_x, new_vel_y)

                if p["fitness"] < p["best_fitness"]:
                    p["best_fitness"] = p["fitness"]
                    p["best_pos"] = p["pos"]

                candidate = min(particles, key=lambda p: p["best_fitness"])
                if candidate["best_fitness"] < gbest_fitness:
                    gbest_fitness = candidate["best_fitness"]
                    gbest_pos = candidate["best_pos"]

        return gbest_pos

    def _eval_fitness(
        self,
        particle_pos: tuple[float, float],
        prev_point: tuple[float, float],
        next_point: tuple[float, float],
    ) -> float:
        return compute_fitness(
            [prev_point, particle_pos, next_point],
            self.grid_map,
            self.min_clearance,
            self.collision_penalty,
        )

    def _inertia_weight(self, it: int) -> float:
        if self.use_siw:
            return self.w_max - (self.w_max - self.w_min) * (it / self.max_iter) * exp(
                uniform(-0.1, 0.1)
            )

        return self.weight

    def _acceleration_coeffs(self, it: int) -> tuple[float, float]:
        if self.use_tvac:
            t = it / self.max_iter
            cog_t = (self.cog_final - self.cog_init) * t + self.cog_init
            soc_t = (self.soc_final - self.soc_init) * t + self.soc_init

            return cog_t, soc_t

        return self.cognitive_coeff, self.social_coeff

    def _smooth_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        curr_path = path

        if self.use_bezier and len(curr_path) > 2:
            curr_path = self._bezier_corner_smooth(curr_path)

        return curr_path

    def _is_segment_safe(
        self,
        start_point: tuple[float, float],
        end_point: tuple[float, float],
    ) -> bool:
        return (
            min_distance_line_to_obstacle(start_point, end_point, self.grid_map)
            > self.min_clearance
        )

    def _bezier_corner_smooth(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        smoothed = [path[0]]

        for i in range(1, len(path) - 1):
            prev_point = smoothed[-1]
            curr_point = path[i]
            next_point = path[i + 1]

            angle = turning_angle(prev_point, curr_point, next_point)

            if angle < self.bezier_threshold:
                smoothed.append(curr_point)
                continue

            d_prev = euclidean_distance(prev_point, curr_point)
            d_next = euclidean_distance(curr_point, next_point)

            if d_prev < 1e-6 or d_next < 1e-6:
                smoothed.append(curr_point)
                continue

            blend = min(self.bezier_blend_ratio, 0.5)

            entry = (
                curr_point[0] + blend * (prev_point[0] - curr_point[0]),
                curr_point[1] + blend * (prev_point[1] - curr_point[1]),
            )
            exit_ = (
                curr_point[0] + blend * (next_point[0] - curr_point[0]),
                curr_point[1] + blend * (next_point[1] - curr_point[1]),
            )

            bezier_pts = []
            for k in range(self.bezier_n_points + 1):
                t = k / self.bezier_n_points
                bx = (
                    (1 - t) ** 2 * entry[0]
                    + 2 * (1 - t) * t * curr_point[0]
                    + t**2 * exit_[0]
                )
                by = (
                    (1 - t) ** 2 * entry[1]
                    + 2 * (1 - t) * t * curr_point[1]
                    + t**2 * exit_[1]
                )
                bezier_pts.append(round_pos((bx, by)))

            is_safe = self._is_segment_safe(smoothed[-1], bezier_pts[0])
            if is_safe:
                for k in range(len(bezier_pts) - 1):
                    if not self._is_segment_safe(bezier_pts[k], bezier_pts[k + 1]):
                        is_safe = False
                        break

            if is_safe:
                smoothed.extend(bezier_pts)

            else:
                smoothed.append(curr_point)

        smoothed.append(path[-1])
        return smoothed
