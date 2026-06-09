from config.parameter import (
    MIN_CLEARANCE,
    PSO_N_WAYPOINTS,
    PSO_N_PARTICLES,
    PSO_MAX_INIT_ATTEMPTS,
    PSO_MAX_ITER,
    PSO_WEIGHT,
    PSO_COGNITIVE_COEFF,
    PSO_SOCIAL_COEFF,
    PSO_COLLISION_PENALTY,
    PSO_VMAX_K,
)
from grid_map import GridMap
from random import uniform
from typing import Optional
from utils import (
    compute_fitness,
    euclidean_distance,
    round_pos,
)


class PSO:
    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
        n_waypoints: int = PSO_N_WAYPOINTS,
        n_particles: int = PSO_N_PARTICLES,
        max_init_attempts: int = PSO_MAX_INIT_ATTEMPTS,
        max_iter: int = PSO_MAX_ITER,
        weight: float = PSO_WEIGHT,
        cognitive_coeff: float = PSO_COGNITIVE_COEFF,
        social_coeff: float = PSO_SOCIAL_COEFF,
        collision_penalty: float = PSO_COLLISION_PENALTY,
        vmax_k: float = PSO_VMAX_K,
    ) -> None:
        self.grid_map = grid_map
        self.start = self.grid_map.start
        self.goal = self.grid_map.goal

        self.min_clearance = float(min_clearance)
        self.n_waypoints = n_waypoints
        self.n_particles = n_particles
        self.max_init_attempts = max_init_attempts
        self.max_iter = max_iter

        self.weight = weight
        self.cognitive_coeff = cognitive_coeff
        self.social_coeff = social_coeff
        self.collision_penalty = collision_penalty
        self.vmax_k = vmax_k

    def plan(self) -> Optional[list[tuple[float, float]]]:
        start = self.start
        goal = self.goal

        if start is None or goal is None:
            return None

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

        dim = self.n_waypoints * 2

        diag = euclidean_distance(
            (0.0, 0.0), (float(self.grid_map.width), float(self.grid_map.height))
        )
        vmax = self.vmax_k * diag

        lb, ub = self._build_bounds()

        particles = [
            self._init_particle(dim, lb, ub, vmax) for _ in range(self.n_particles)
        ]

        gbest_particle = min(particles, key=lambda p: p["best_fitness"])
        gbest_pos: list[float] = list(gbest_particle["best_pos"])
        gbest_fitness: float = gbest_particle["best_fitness"]

        for it in range(self.max_iter):
            for p in particles:
                pos = p["pos"]
                vel = p["vel"]
                pb = p["best_pos"]

                new_vel: list[float] = []
                new_pos: list[float] = []

                for d in range(dim):
                    v_d = (
                        self.weight * vel[d]
                        + self.cognitive_coeff * uniform(0.0, 1.0) * (pb[d] - pos[d])
                        + self.social_coeff
                        * uniform(0.0, 1.0)
                        * (gbest_pos[d] - pos[d])
                    )
                    v_d = max(-vmax, min(vmax, v_d))
                    new_vel.append(v_d)

                    x_d = max(lb[d], min(ub[d], pos[d] + v_d))
                    new_pos.append(x_d)

                p["pos"] = new_pos
                p["vel"] = new_vel
                p["fitness"] = self._eval_path_fitness(new_pos)

                if p["fitness"] < p["best_fitness"]:
                    p["best_fitness"] = p["fitness"]
                    p["best_pos"] = list(new_pos)

                if p["best_fitness"] < gbest_fitness:
                    gbest_fitness = p["best_fitness"]
                    gbest_pos = list(p["best_pos"])

        return self._decode_path(gbest_pos)

    def _build_bounds(self) -> tuple[list[float], list[float]]:
        lb: list[float] = []
        ub: list[float] = []
        for _ in range(self.n_waypoints):
            lb.extend([0.0, 0.0])
            ub.extend([float(self.grid_map.width - 1), float(self.grid_map.height - 1)])
        return lb, ub

    def _init_particle(
        self,
        dim: int,
        lb: list[float],
        ub: list[float],
        vmax: float,
    ) -> dict:
        pos: list[float] = []
        sx, sy = float(self.start[0]), float(self.start[1])
        gx, gy = float(self.goal[0]), float(self.goal[1])

        for i in range(self.n_waypoints):
            t = (i + 1) / (self.n_waypoints + 1)
            base_x = sx + t * (gx - sx)
            base_y = sy + t * (gy - sy)

            for _ in range(self.max_init_attempts):
                px = max(lb[i * 2], min(ub[i * 2], base_x + uniform(-2.0, 2.0)))
                py = max(lb[i * 2 + 1], min(ub[i * 2 + 1], base_y + uniform(-2.0, 2.0)))

                if self.grid_map.is_inside(
                    int(px), int(py)
                ) and not self.grid_map.is_obstacle(int(px), int(py)):
                    pos.extend([round(px, 2), round(py, 2)])
                    break
            else:
                pos.extend([round(base_x, 2), round(base_y, 2)])

        vel = [uniform(-vmax, vmax) for _ in range(dim)]
        fitness = self._eval_path_fitness(pos)

        return {
            "pos": pos,
            "vel": vel,
            "best_pos": list(pos),
            "best_fitness": fitness,
            "fitness": fitness,
        }

    def _decode_path(self, flat: list[float]) -> list[tuple[float, float]]:
        path: list[tuple[float, float]] = [self.start]
        for i in range(self.n_waypoints):
            path.append(round_pos((flat[i * 2], flat[i * 2 + 1])))
        path.append(self.goal)
        return path

    def _eval_path_fitness(self, flat: list[float]) -> float:
        return compute_fitness(
            self._decode_path(flat),
            self.grid_map,
            self.min_clearance,
            self.collision_penalty,
        )
