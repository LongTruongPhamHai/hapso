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
)
from grid_map import GridMap
from random import uniform
from typing import Optional
from utils import (
    compute_fitness,
    euclidean_distance,
    round_pos,
)

import numpy as np

PSO_N_WAYPOINTS: int = 5
PSO_MAX_SPEED: float = 3.0  # velocity clamp (grid units / iter)
PSO_SMOOTH_ALPHA: float = 0.15  # laplacian smooth strength (0 = off)
PSO_SMOOTH_ROUNDS: int = 1
PSO_PATIENCE: int = 20  # early-stopping: iter tanpa improvement
PSO_PATIENCE_TOL: float = 1e-6


# ──────────────────────────────────────────────
# Path utilities (grid-space equivalents)
# ──────────────────────────────────────────────


def _catmull_rom_segment(
    p0: np.ndarray,
    p1: np.ndarray,
    p2: np.ndarray,
    p3: np.ndarray,
    n_samples: int = 20,
) -> np.ndarray:
    """Nội suy Catmull-Rom từ p1 → p2 với n_samples điểm."""
    ts = np.linspace(0.0, 1.0, n_samples, endpoint=False)
    pts = []
    for t in ts:
        t2, t3 = t * t, t * t * t
        pt = 0.5 * (
            2.0 * p1
            + (-p0 + p2) * t
            + (2.0 * p0 - 5.0 * p1 + 4.0 * p2 - p3) * t2
            + (-p0 + 3.0 * p1 - 3.0 * p2 + p3) * t3
        )
        pts.append(pt)
    return np.array(pts)


def _catmull_rom_chain(ctrl: np.ndarray, samples_per_seg: int = 20) -> np.ndarray:
    """Nối tất cả đoạn Catmull-Rom, thêm điểm ảo ở 2 đầu."""
    ghost_start = 2.0 * ctrl[0] - ctrl[1]
    ghost_end = 2.0 * ctrl[-1] - ctrl[-2]
    ext = np.vstack([ghost_start, ctrl, ghost_end])

    segments = []
    for i in range(1, len(ext) - 2):
        seg = _catmull_rom_segment(
            ext[i - 1], ext[i], ext[i + 1], ext[i + 2], samples_per_seg
        )
        segments.append(seg)
    segments.append(ctrl[[-1]])  # thêm điểm cuối
    return np.vstack(segments)


def _resample_by_arclength(pts: np.ndarray, n: int) -> np.ndarray:
    """Resample đường cong về đúng n điểm cách đều theo arclength."""
    diffs = np.diff(pts, axis=0)
    segs = np.linalg.norm(diffs, axis=1)
    cum = np.concatenate([[0.0], np.cumsum(segs)])
    total = cum[-1]
    if total < 1e-9:
        return np.tile(pts[0], (n, 1))
    targets = np.linspace(0.0, total, n)
    xs = np.interp(targets, cum, pts[:, 0])
    ys = np.interp(targets, cum, pts[:, 1])
    return np.stack([xs, ys], axis=1)


def _smooth_path(path: np.ndarray, alpha: float = 0.15, rounds: int = 1) -> np.ndarray:
    """Laplacian smooth giữ 2 đầu cố định."""
    p = path.copy()
    for _ in range(rounds):
        mid = 0.5 * (p[:-2] + p[2:])
        p[1:-1] = (1.0 - alpha) * p[1:-1] + alpha * mid
    return p


def _repair_path(
    path: np.ndarray,
    grid_map: GridMap,
    min_clearance: float,
) -> np.ndarray:
    """Đẩy các waypoint nằm trong obstacle / ngoài grid về vị trí hợp lệ gần nhất."""
    w, h = float(grid_map.width - 1), float(grid_map.height - 1)
    path[:, 0] = np.clip(path[:, 0], 0.0, w)
    path[:, 1] = np.clip(path[:, 1], 0.0, h)

    obs_set = grid_map.get_obstacle_set()
    if not obs_set:
        return path

    obs = np.array([[x + 0.5, y + 0.5] for x, y in obs_set])  # obstacle centers

    for i in range(1, len(path) - 1):  # 2 đầu không chạm
        px, py = path[i]
        ix, iy = int(px), int(py)

        if not grid_map.is_obstacle(ix, iy):
            continue

        # vector từ obstacle gần nhất → điểm hiện tại, đẩy ra ngoài
        diffs = path[i] - obs
        dists = np.linalg.norm(diffs, axis=1)
        nearest_idx = int(np.argmin(dists))
        d = dists[nearest_idx]

        if d < 1e-9:
            # trùng tâm obstacle → đẩy thẳng ra theo hướng về goal
            direction = path[-1] - path[i]
            norm = np.linalg.norm(direction)
            direction = direction / (norm + 1e-9)
        else:
            direction = diffs[nearest_idx] / d

        push = min_clearance + 0.5 - d + 1e-3
        if push > 0:
            path[i] = path[i] + direction * push

        path[i, 0] = np.clip(path[i, 0], 0.0, w)
        path[i, 1] = np.clip(path[i, 1], 0.0, h)

    return path


def _init_spline_particle(
    start: np.ndarray,
    goal: np.ndarray,
    grid_map: GridMap,
    min_clearance: float,
    M: int,
    K: int = 5,
    jitter: float = 3.0,
    max_attempts: int = 20,
) -> np.ndarray:
    """
    Khởi tạo particle bằng Catmull-Rom spline:
      K control points dọc line start→goal + nhiễu mềm,
      resample về M waypoints, rồi repair.
    jitter tính theo grid units (khác code mẫu dùng pixel).
    """
    t_vals = np.linspace(0, 1, K).reshape(-1, 1)
    ctrl = (1.0 - t_vals) * start + t_vals * goal

    d = goal - start
    dn = d / (np.linalg.norm(d) + 1e-9)
    perp = np.array([-dn[1], dn[0]])

    noise_perp = np.random.randn(K, 1) * jitter
    noise_along = np.random.randn(K, 1) * (0.25 * jitter)
    ctrl = ctrl + noise_perp * perp + noise_along * dn
    ctrl[0] = start
    ctrl[-1] = goal

    dense = _catmull_rom_chain(ctrl, samples_per_seg=30)
    path = _resample_by_arclength(dense, M)
    path = _repair_path(path, grid_map, min_clearance)
    path[0] = start
    path[-1] = goal
    return path


# ──────────────────────────────────────────────
# PSO
# ──────────────────────────────────────────────


class PSO:
    """Pure PSO path planner (grid-space).

    Mỗi particle là một mảng (M, 2) gồm M waypoints (bao gồm start & goal).
    Chỉ tối ưu M-2 waypoint giữa; start/goal được ghim cứng sau mỗi bước.

    Tính năng (từ code mẫu):
      - Khởi tạo bằng Catmull-Rom spline + resample
      - Velocity clamp theo max_speed
      - Laplacian smooth nhẹ sau mỗi bước
      - Early stopping theo patience
    """

    def __init__(
        self,
        grid_map: GridMap,
        min_clearance: float = MIN_CLEARANCE,
        n_particles: int = PSO_N_PARTICLES,
        max_init_attempts: int = PSO_MAX_INIT_ATTEMPTS,
        max_iter: int = PSO_MAX_ITER,
        n_waypoints: int = PSO_N_WAYPOINTS,
        weight: float = PSO_WEIGHT,
        cognitive_coeff: float = PSO_COGNITIVE_COEFF,
        social_coeff: float = PSO_SOCIAL_COEFF,
        collision_penalty: float = PSO_COLLISION_PENALTY,
        max_speed: float = PSO_MAX_SPEED,
        smooth_alpha: float = PSO_SMOOTH_ALPHA,
        smooth_rounds: int = PSO_SMOOTH_ROUNDS,
        patience: int = PSO_PATIENCE,
        patience_tol: float = PSO_PATIENCE_TOL,
    ) -> None:
        self.grid_map = grid_map
        self.start = grid_map.start
        self.goal = grid_map.goal
        self.min_clearance = float(min_clearance)

        self.n_particles = n_particles
        self.max_init_attempts = max_init_attempts
        self.max_iter = max_iter
        # M = tổng số điểm trong path (gồm cả start & goal)
        self.M = n_waypoints + 2

        self.weight = weight
        self.cognitive_coeff = cognitive_coeff
        self.social_coeff = social_coeff
        self.collision_penalty = collision_penalty
        self.max_speed = max_speed
        self.smooth_alpha = smooth_alpha
        self.smooth_rounds = smooth_rounds
        self.patience = patience
        self.patience_tol = patience_tol

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def plan(self) -> Optional[list[tuple[float, float]]]:
        if self.start is None or self.goal is None:
            return None

        for pos, name in [(self.start, "start"), (self.goal, "goal")]:
            if not self.grid_map.is_inside(*pos) or self.grid_map.is_obstacle(*pos):
                return None

        if self.start == self.goal:
            return [self.start, self.goal]

        np_start = np.array(self.start, dtype=float)
        np_goal = np.array(self.goal, dtype=float)
        M = self.M

        # ── Khởi tạo swarm ──────────────────────────────────────────
        positions = np.array(
            [
                _init_spline_particle(
                    np_start, np_goal, self.grid_map, self.min_clearance, M
                )
                for _ in range(self.n_particles)
            ]
        )  # (N, M, 2)
        velocities = np.zeros_like(positions)  # (N, M, 2)

        costs = np.array([self._eval(positions[i]) for i in range(self.n_particles)])

        pbest_pos = positions.copy()
        pbest_cost = costs.copy()

        gbest_idx = int(np.argmin(pbest_cost))
        gbest_pos = pbest_pos[gbest_idx].copy()  # (M, 2)
        gbest_cost = float(pbest_cost[gbest_idx])

        # ── Main loop ───────────────────────────────────────────────
        no_improve = 0
        prev_best = gbest_cost

        for it in range(self.max_iter):
            r1 = np.random.rand(self.n_particles, M, 2)
            r2 = np.random.rand(self.n_particles, M, 2)

            cognitive = self.cognitive_coeff * r1 * (pbest_pos - positions)
            social = self.social_coeff * r2 * (gbest_pos - positions)
            velocities = self.weight * velocities + cognitive + social

            # Velocity clamp
            speed = np.linalg.norm(velocities, axis=2, keepdims=True)  # (N,M,1)
            scale = np.minimum(1.0, self.max_speed / (speed + 1e-9))
            velocities *= scale

            positions += velocities

            # Repair + smooth + ghim 2 đầu
            for i in range(self.n_particles):
                positions[i] = _repair_path(
                    positions[i], self.grid_map, self.min_clearance
                )
                if self.smooth_alpha > 0:
                    positions[i] = _smooth_path(
                        positions[i], self.smooth_alpha, self.smooth_rounds
                    )
                positions[i][0] = np_start
                positions[i][-1] = np_goal

            # Đánh giá
            costs = np.array(
                [self._eval(positions[i]) for i in range(self.n_particles)]
            )

            improved = costs < pbest_cost
            pbest_pos[improved] = positions[improved].copy()
            pbest_cost[improved] = costs[improved]

            best_idx = int(np.argmin(pbest_cost))
            if pbest_cost[best_idx] < gbest_cost:
                gbest_cost = float(pbest_cost[best_idx])
                gbest_pos = pbest_pos[best_idx].copy()

            # Early stopping
            if gbest_cost < prev_best - self.patience_tol:
                prev_best = gbest_cost
                no_improve = 0
            else:
                no_improve += 1

            if no_improve >= self.patience:
                break

        return self._to_path(gbest_pos)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _eval(self, path_arr: np.ndarray) -> float:
        path = self._to_path(path_arr)
        return compute_fitness(
            path,
            self.grid_map,
            self.min_clearance,
            self.collision_penalty,
        )

    @staticmethod
    def _to_path(arr: np.ndarray) -> list[tuple[float, float]]:
        return [
            round_pos((float(arr[i, 0]), float(arr[i, 1]))) for i in range(len(arr))
        ]
