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
    PSO_USE_VISIBILITY_SHORTCUTTING,
    PSO_USE_BEZIER,
    PSO_BEZIER_THRESHOLD,
    PSO_BEZIER_BLEND_RATIO,
    PSO_BEZIER_N_POINTS,
    PSO_USE_LAPLACIAN,
    PSO_LAPLACIAN_ALPHA,
    PSO_LAPLACIAN_ROUND,
)
from grid_map import GridMap
from math import exp, sqrt
from random import gauss, uniform
from typing import Optional
from utils import (
    euclidean_distance,
    min_distance_line_to_obstacle,
    round_pos,
    total_fitness,
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
        use_visibility_shortcutting: bool = PSO_USE_VISIBILITY_SHORTCUTTING,
        use_bezier: bool = PSO_USE_BEZIER,
        bezier_threshold: float = PSO_BEZIER_THRESHOLD,
        bezier_blend_ratio: float = PSO_BEZIER_BLEND_RATIO,
        bezier_n_points: int = PSO_BEZIER_N_POINTS,
        use_laplacian: bool = PSO_USE_LAPLACIAN,
        laplacian_alpha: float = PSO_LAPLACIAN_ALPHA,
        laplacian_round: int = PSO_LAPLACIAN_ROUND,
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

        self.use_visibility_shortcutting = use_visibility_shortcutting

        self.use_bezier = use_bezier
        self.bezier_threshold = bezier_threshold
        self.bezier_blend_ratio = bezier_blend_ratio
        self.bezier_n_points = bezier_n_points

        self.use_laplacian = use_laplacian
        self.laplacian_alpha = laplacian_alpha
        self.laplacian_round = laplacian_round

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

        initial_path = self._astar_planning()
        if initial_path is None:
            return None

        pso_optimized_path = self._pso_optimize_path(initial_path)

        pso_improved_path = self._improve_pso_path(pso_optimized_path)

        pso_improved_path.append(goal)

        return pso_improved_path

    def _astar_planning(self) -> Optional[list[tuple[float, float]]]:
        astar = Astar(grid_map=self.grid_map)
        return astar.plan()

    def _pso_optimize_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        if len(path) <= 2:
            return path

        optimized_path = [path[0]]

        for i in range(1, len(path) - 1):
            prev_point = optimized_path[-1]
            next_point = path[i + 1]

            particles = self._initialize_pso_particles(prev_point, next_point)

            best_particles = self._pso_optimize_segment(
                particles, prev_point, next_point
            )

            optimized_path.append(round_pos(best_particles))

        return optimized_path

    def _initialize_pso_particles(
        self, prev_point: tuple[float, float], next_point: tuple[float, float]
    ) -> list[dict]:
        particles = []

        for i in range(self.n_particles):
            valid = False

            for attempt in range(self.max_init_attempts):
                particle_x = prev_point[0] + (
                    (next_point[0] - prev_point[0]) * uniform(0.0, 1.0)
                )
                particle_y = prev_point[1] + (
                    (next_point[1] - prev_point[1]) * uniform(0.0, 1.0)
                )

                particle_pos = round_pos((particle_x, particle_y))

                if not self.grid_map.is_inside(particle_x, particle_y):
                    continue

                if self.grid_map.is_obstacle(int(particle_x), int(particle_y)):
                    continue

                if (
                    min_distance_line_to_obstacle(
                        particle_pos, particle_pos, self.grid_map
                    )
                    < self.min_clearance
                ):
                    continue

                valid = True
                break

            if not valid:
                particle_x = round((prev_point[0] + next_point[0]) / 2.0, 2)
                particle_y = round((prev_point[1] + next_point[1]) / 2.0, 2)

            max_velocity = self.vmax_k * sqrt(
                (next_point[0] - prev_point[0]) ** 2
                + (next_point[1] - prev_point[1]) ** 2
            )

            velocity_x = uniform(-max_velocity, max_velocity)
            velocity_y = uniform(-max_velocity, max_velocity)

            fitness = self._pso_fitness(
                (particle_x, particle_y), prev_point, next_point
            )

            particle = {
                "position": (particle_x, particle_y),
                "velocity": (velocity_x, velocity_y),
                "best_position": (particle_x, particle_y),
                "best_fitness": fitness,
                "fitness": fitness,
            }
            particles.append(particle)

        return particles

    def _pso_optimize_segment(
        self,
        particles: list[dict],
        prev_point: tuple[float, float],
        next_point: tuple[float, float],
    ) -> tuple[float, float]:
        gbest_particle = min(particles, key=lambda p: p["best_fitness"])

        gbest_position = gbest_particle["best_position"]
        gbest_fitness = gbest_particle["best_fitness"]

        if self.use_sobl:
            local_lb_x = min(prev_point[0], next_point[0]) - self.sobl_margin
            local_ub_x = max(prev_point[0], next_point[0]) + self.sobl_margin
            local_lb_y = min(prev_point[1], next_point[1]) - self.sobl_margin
            local_ub_y = max(prev_point[1], next_point[1]) + self.sobl_margin

        for iteration in range(self.max_iter):
            for particle in particles:
                weight = self._stochastic_inertia_weight(iteration)
                cog_coeff, soc_coeff = self._time_varying_acceleration_coefficients(
                    iteration
                )

                curr_velocity = particle["velocity"]
                curr_position = particle["position"]
                curr_pbest = particle["best_position"]

                new_velocity_x = (
                    weight * curr_velocity[0]
                    + cog_coeff * uniform(0.0, 1.0) * (curr_pbest[0] - curr_position[0])
                    + soc_coeff
                    * uniform(0.0, 1.0)
                    * (gbest_position[0] - curr_position[0])
                )
                new_velocity_y = (
                    weight * curr_velocity[1]
                    + cog_coeff * uniform(0.0, 1.0) * (curr_pbest[1] - curr_position[1])
                    + soc_coeff
                    * uniform(0.0, 1.0)
                    * (gbest_position[1] - curr_position[1])
                )

                new_position = round_pos(
                    (
                        curr_position[0] + new_velocity_x,
                        curr_position[1] + new_velocity_y,
                    )
                )

                if self.use_sobl:
                    r = gauss(self.sobl_mu, self.sobl_sigma)

                    opposite_x = round(local_lb_x + local_ub_x - new_position[0] * r, 2)
                    opposite_y = round(local_lb_y + local_ub_y - new_position[1] * r, 2)

                    opposite_x = max(local_lb_x, min(local_ub_x, opposite_x))
                    opposite_y = max(local_lb_y, min(local_ub_y, opposite_y))

                    new_position_fitness = self._pso_fitness(
                        new_position,
                        prev_point,
                        next_point,
                    )
                    opposite_position_fitness = self._pso_fitness(
                        (opposite_x, opposite_y),
                        prev_point,
                        next_point,
                    )

                    if opposite_position_fitness < new_position_fitness:
                        particle["position"] = (opposite_x, opposite_y)
                        particle["fitness"] = opposite_position_fitness

                    else:
                        particle["position"] = new_position
                        particle["fitness"] = new_position_fitness

                else:
                    particle["position"] = new_position
                    particle["fitness"] = self._pso_fitness(
                        new_position, prev_point, next_point
                    )

                particle["velocity"] = (
                    new_velocity_x,
                    new_velocity_y,
                )

                if particle["fitness"] < particle["best_fitness"]:
                    particle["best_fitness"] = particle["fitness"]
                    particle["best_position"] = particle["position"]

                new_gbest_particle = min(particles, key=lambda p: p["best_fitness"])
                new_gbest_fitness = new_gbest_particle["best_fitness"]

                if new_gbest_fitness < gbest_fitness:
                    gbest_fitness = new_gbest_fitness
                    gbest_position = new_gbest_particle["best_position"]

        return gbest_position

    def _stochastic_inertia_weight(self, iter: int) -> float:
        if self.use_siw:
            return self.w_max - (self.w_max - self.w_min) * (
                iter / self.max_iter
            ) * exp(uniform(-0.1, 0.1))

        return self.weight

    def _time_varying_acceleration_coefficients(self, iter: int) -> tuple[float, float]:
        if self.use_tvac:
            cog_val = (self.cog_final - self.cog_init) * (
                iter / self.max_iter
            ) + self.cog_init
            soc_val = (self.soc_final - self.soc_init) * (
                iter / self.max_iter
            ) + self.soc_init

            return cog_val, soc_val

        return self.cognitive_coeff, self.social_coeff

    def _improve_pso_path(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        current_path = path

        if self.use_visibility_shortcutting and len(current_path) > 2:
            current_path = self._visibility_shortcut(current_path)

        if self.use_bezier and len(current_path) > 2:
            current_path = self._bezier_corner_smoothing(current_path)

        if self.use_laplacian and len(current_path) > 2:
            current_path = self._laplacian_smoothing(current_path)

        return current_path

    def _safe(
        self,
        start_point: tuple[float, float],
        end_point: tuple[float, float],
    ) -> bool:
        return (
            min_distance_line_to_obstacle(start_point, end_point, self.grid_map)
            > self.min_clearance
        )

    def _visibility_shortcut(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        if len(path) <= 2:
            return path

        result = [path[0]]
        i = 0

        while i < len(path) - 1:
            j = len(path) - 1

            while j > i + 1:
                if self._safe(result[-1], path[j]):
                    break

                j -= 1

            result.append(path[j])
            i = j

        return result

    def _bezier_corner_smoothing(
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

            distance_prev = euclidean_distance(prev_point, curr_point)
            distance_next = euclidean_distance(curr_point, next_point)

            if distance_prev < 1e-6 or distance_next < 1e-6:
                smoothed.append(curr_point)
                continue

            prev_blend_ratio = min(self.bezier_blend_ratio, 0.5)
            next_blend_ratio = min(self.bezier_blend_ratio, 0.5)

            entry_point = (
                curr_point[0] + prev_blend_ratio * (prev_point[0] - curr_point[0]),
                curr_point[1] + prev_blend_ratio * (prev_point[1] - curr_point[1]),
            )

            exit_point = (
                curr_point[0] + next_blend_ratio * (next_point[0] - curr_point[0]),
                curr_point[1] + next_blend_ratio * (next_point[1] - curr_point[1]),
            )

            bezier_points = []
            for k in range(self.bezier_n_points + 1):
                blend_t = k / self.bezier_n_points
                bezier_x = (
                    (1 - blend_t) ** 2 * entry_point[0]
                    + 2 * (1 - blend_t) * blend_t * curr_point[0]
                    + blend_t**2 * exit_point[0]
                )
                bezier_y = (
                    (1 - blend_t) ** 2 * entry_point[1]
                    + 2 * (blend_t) * blend_t * curr_point[1]
                    + blend_t**2 * exit_point[1]
                )
                bezier_points.append(round_pos((bezier_x, bezier_y)))

            bezier_safe = self._safe(smoothed[-1], bezier_points[0])
            if bezier_safe:
                for k in range(len(bezier_points) - 1):
                    if not self._safe(bezier_points[k], bezier_points[k + 1]):
                        bezier_safe = False
                        break

            if bezier_safe:
                smoothed.extend(bezier_points)

            else:
                smoothed.append(curr_point)

        smoothed.append(path[-1])
        return smoothed

    def _laplacian_smoothing(
        self, path: list[tuple[float, float]]
    ) -> list[tuple[float, float]]:
        if len(path) <= 2:
            return path

        for _ in range(self.laplacian_round):
            smoothed_path = path.copy()

            for i in range(1, len(path) - 1):
                prev_point = path[i - 1]
                curr_point = path[i]
                next_point = path[i + 1]

                candidate = (
                    (1 - self.laplacian_alpha) * curr_point[0]
                    + self.laplacian_alpha * 0.5 * (prev_point[0] + next_point[0]),
                    (1 - self.laplacian_alpha) * curr_point[1]
                    + self.laplacian_alpha * 0.5 * (prev_point[1] + next_point[1]),
                )

                if self._safe(prev_point, candidate) and self._safe(
                    candidate, next_point
                ):
                    smoothed_path[i] = candidate

            smoothed_path[0] = path[0]
            smoothed_path[-1] = path[-1]
            path = smoothed_path

        return [round_pos(point) for point in path]
