from __future__ import annotations
from config.colors import (
    CHART_COLORS,
    CHART_HATCHES,
    DARK_GRAY,
    CHART_BLUE,
    CHART_ORANGE,
    CHART_GREEN,
    CHART_DARK_GREEN,
    CHART_MAGENTA,
    CHART_PURPLE,
    CHART_GOLD,
    HEX_MEDIUM,
)
from typing import Dict, List, Optional, Tuple

import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]

# MAP_NAME = "KB02-MZ"
# ...
MAP_NAME = "KB03-OD"
COMPARISON_TABLE = """Thuật toán	RRT*	PRM	A*	HAPSO
Tỷ lệ thành công	100.0	10.0	100.0	100.0
Độ dài đường đi	53.1532	48.8074	49.3137	50.123
Góc quay trung bình	14.9267	42.3634	9	4.3502
Khoảng cách an toàn 	1.3097	0.7071	0.7071	1.1729
Thời gian tính toán	0.2157	0.2009	0.0021	1.1606
Hàm đánh giá	0.6695	5	5	0.634
"""

METRIC_FILENAME_MAP: Dict[str, str] = {
    "Tỷ lệ thành công": "success_rate",
    "Độ dài đường đi": "path_length",
    "Góc quay trung bình": "average_turning_angle",
    "Khoảng cách an toàn": "safety_clearance",
    "Thời gian tính toán": "computation_time",
    "Hàm đánh giá": "evaluation_function",
}


def _save_fig(fig: plt.Figure, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def _parse_comparison_table(
    raw: str,
) -> Tuple[List[str], Dict[str, List[Optional[float]]]]:
    lines = [ln.rstrip() for ln in raw.strip().splitlines() if ln.strip()]

    header_idx, algorithms = 0, []
    for i, line in enumerate(lines):
        parts = line.split("\t")
        if len(parts) >= 3:
            algorithms = [p.strip() for p in parts[1:] if p.strip()]
            header_idx = i
            break

    data: Dict[str, List[Optional[float]]] = {}
    for line in lines[header_idx + 1 :]:
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        metric = parts[0].strip()
        values = [None if v.strip() in ("", "-", "–") else float(v) for v in parts[1:]]
        if metric and len(values) == len(algorithms):
            data[metric] = values

    return algorithms, data


def plot_algorithm_comparison(
    raw_table: str = COMPARISON_TABLE,
    map_name: str = MAP_NAME,
    out_base_dir: str = "data/results/charts",
    figsize: Tuple[float, float] = (7.0, 5.5),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    if not map_name:
        print("[VISUALIZATION] MAP_NAME is not defined — skipping.")
        return

    algorithms, data = _parse_comparison_table(raw_table)
    if not algorithms or not data:
        print("[VISUALIZATION] Failed to parse data from the table.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(out_base_dir, f"{map_name}_{timestamp}")
    os.makedirs(out_dir, exist_ok=True)

    x = np.arange(len(algorithms))
    bar_width = min(0.55 / max(len(algorithms) - 1, 1) * len(algorithms), 0.65)
    colors = CHART_COLORS[: len(algorithms)]
    hatches = CHART_HATCHES[: len(algorithms)]
    success_rates = data["Tỷ lệ thành công"]

    for metric, values in data.items():
        if metric == "Tỷ lệ thành công":
            continue

        fig, ax1 = plt.subplots(figsize=figsize, dpi=dpi)
        ax2 = ax1.twinx()

        valid = [
            (x[i], v, colors[i], hatches[i])
            for i, v in enumerate(values)
            if v is not None
        ]
        valid_x, valid_values, valid_colors, valid_hatches = zip(*valid)

        bars = ax1.bar(
            valid_x,
            valid_values,
            width=bar_width,
            color=valid_colors,
            edgecolor="black",
            linewidth=0.8,
        )
        for bar, hatch in zip(bars, valid_hatches):
            bar.set_hatch(hatch)

        max_val = max(valid_values)
        for bar, val in zip(bars, valid_values):
            ax1.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_val * 0.015,
                f"{val:.4g}",
                ha="center",
                va="bottom",
                fontsize=16,
            )

        ax2.plot(
            x,
            success_rates,
            marker="o",
            linewidth=2.5,
            color="red",
            label="Tỷ lệ thành công",
        )

        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms, fontsize=20)
        ax1.set_ylabel(metric, fontsize=20)
        ax2.set_ylabel("Tỷ lệ thành công (%)", fontsize=20)
        ax1.set_ylim(0, max_val * 1.18)
        ax2.set_ylim(0, 105)
        ax1.tick_params(axis="y", labelsize=18)
        ax2.tick_params(axis="y", labelsize=18)
        ax1.grid(True, axis="y", linestyle=grid_style, alpha=0.6)
        ax1.set_axisbelow(True)
        fig.tight_layout()

        file_stem = METRIC_FILENAME_MAP.get(metric, metric.lower().replace(" ", "_"))
        _save_fig(fig, os.path.join(out_dir, f"{file_stem}.png"))

    print(f"[VISUALIZATION] Completed — {len(data)} charts saved to '{out_dir}'")


def plot_stochastic_inertia_weight(
    max_iterations: int = 50,
    weight_max: float = 0.9,
    weight_min: float = 0.4,
    noise_scale: float = 0.1,
    seed: int = 42,
    out_path: str = "data/results/improved/stochastic_inertia.png",
    figsize: Tuple[float, float] = (8.0, 4.5),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    iterations = np.arange(max_iterations)
    linear_weight = weight_max - (weight_max - weight_min) * iterations / max_iterations
    rng = np.random.default_rng(seed)
    stochastic_weight = linear_weight * (
        1 + noise_scale * (rng.random(max_iterations) - 0.5)
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.plot(iterations, stochastic_weight, "b-", label="Giá trị trọng số quán tính")
    ax.set_xlabel("Vòng lặp (t)", fontsize=12)
    ax.set_ylabel("Trọng số quán tính (w)", fontsize=12)
    ax.legend(fontsize=12)
    ax.grid(True, linestyle=grid_style)
    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] SIW saved to '{out_path}'")


def plot_tvac(
    particle_count: int = 40,
    space_min_value: float = 0.0,
    space_max_value: float = 100.0,
    global_best: Tuple[float, float] = (50.0, 50.0),
    seed: int = 10,
    out_path: str = "data/results/improved/tvac.png",
    figsize: Tuple[float, float] = (11.0, 4.8),
    dpi: int = 150,
) -> None:
    rng = np.random.default_rng(seed)
    gbx, gby = global_best

    early_x = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)
    early_y = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)
    late_x = rng.normal(gbx, 4, particle_count)
    late_y = rng.normal(gby, 4, particle_count)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)

    ax1.quiver(
        early_x,
        early_y,
        rng.uniform(-15, 15, particle_count),
        rng.uniform(-15, 15, particle_count),
        color=CHART_GREEN,
        alpha=0.7,
    )
    ax1.scatter(early_x, early_y, color=CHART_DARK_GREEN, s=100, label="Cá thể")
    ax1.set_title("Giai đoạn đầu", fontsize=18)

    ax2.quiver(
        late_x,
        late_y,
        (gbx - late_x) * 0.5 + rng.normal(0, 0.5, particle_count),
        (gby - late_y) * 0.5 + rng.normal(0, 0.5, particle_count),
        color=CHART_MAGENTA,
        alpha=0.7,
    )
    ax2.scatter(late_x, late_y, color=CHART_PURPLE, s=30)
    ax2.scatter(
        gbx,
        gby,
        color=CHART_GOLD,
        marker="*",
        s=200,
        edgecolors="black",
        label="Tối ưu toàn cục (Gbest)",
    )
    ax2.set_title("Giai đoạn cuối", fontsize=18)

    for _ax in (ax1, ax2):
        _ax.set_xlim(space_min_value, space_max_value)
        _ax.set_ylim(space_min_value, space_max_value)
        _ax.set_xlabel("Không gian X₁", fontsize=16)
        _ax.set_ylabel("Không gian X₂", fontsize=16)
        _ax.grid(True, linestyle=":")
        _ax.legend(fontsize=14)

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] TVAC saved to '{out_path}'")


def plot_bezier_corner_smoothing(
    blend_ratio: float = 0.3,
    out_path: str = "data/results/improved/bezier_corner_smoothing.png",
    figsize: Tuple[float, float] = (7.2, 4.5),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    prev_point = np.array([2.0, 2.0])
    corner_point = np.array([6.0, 8.0])
    next_point = np.array([10.0, 3.0])
    entry_point = corner_point + blend_ratio * (prev_point - corner_point)
    exit_point = corner_point + blend_ratio * (next_point - corner_point)

    t = np.linspace(0.0, 1.0, 100)
    bezier_points = (
        np.outer((1 - t) ** 2, entry_point)
        + np.outer(2 * (1 - t) * t, corner_point)
        + np.outer(t**2, exit_point)
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.set_xticks(np.arange(0, 13, 1))
    ax.set_yticks(np.arange(0, 11, 1))
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.7)

    ax.plot(
        [prev_point[0], corner_point[0], next_point[0]],
        [prev_point[1], corner_point[1], next_point[1]],
        "r--o",
        label="Quỹ đạo gốc",
    )
    ax.plot(
        bezier_points[:, 0],
        bezier_points[:, 1],
        "b-",
        linewidth=2.5,
        label="Đường cong Bezier nội suy",
    )
    ax.scatter(
        [entry_point[0], exit_point[0]],
        [entry_point[1], exit_point[1]],
        color=CHART_MAGENTA,
        s=80,
        zorder=5,
    )
    ax.text(entry_point[0] - 0.8, entry_point[1] + 0.2, "$P_{in}$")
    ax.text(exit_point[0] + 0.3, exit_point[1] + 0.2, "$P_{out}$")
    ax.text(corner_point[0] - 0.5, corner_point[1] + 0.3, "$P_{curr}$")

    ax.set_xlabel("Trục X")
    ax.set_ylabel("Trục Y")
    ax.legend()
    ax.grid(True, linestyle=grid_style)
    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] Bezier saved to '{out_path}'")


def plot_sobl(
    n_particles: int = 20,
    seed: int = 42,
    out_path: str = "data/results/improved/sobl.png",
    figsize: Tuple[float, float] = (11.0, 4.8),
    dpi: int = 150,
) -> None:
    rng = np.random.default_rng(seed)

    focus = np.array([0.50, 0.50])
    lb, ub = focus - 0.30, focus + 0.30

    raw = np.clip(rng.normal(focus, 0.13, (n_particles, 2)), 0.06, 0.94)
    opp = np.clip(
        lb + ub - raw * rng.normal(1.0, 0.15, n_particles)[:, None], 0.06, 0.94
    )

    path_pts = np.array(
        [
            [0.08, 0.88],
            [0.22, 0.72],
            [0.40, 0.58],
            [0.50, 0.50],
            [0.62, 0.38],
            [0.78, 0.24],
            [0.92, 0.10],
        ]
    )

    fig, (ax_without, ax_with) = plt.subplots(1, 2, figsize=figsize, dpi=dpi)

    for ax, show_sobl in [(ax_without, False), (ax_with, True)]:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.set_xlabel("Không gian X₁", fontsize=16)
        ax.set_ylabel("Không gian X₂", fontsize=16)
        ax.grid(True, linestyle=":")

        ax.plot(
            path_pts[:, 0],
            path_pts[:, 1],
            color=CHART_GREEN,
            lw=2.0,
            linestyle=(0, (6, 4)),
            label="Quỹ đạo",
            zorder=2,
        )
        ax.scatter(
            [focus[0]],
            [focus[1]],
            marker="D",
            s=80,
            color=DARK_GRAY,
            zorder=6,
            label="Điểm đang xét",
        )

        if show_sobl:
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (lb[0], lb[1]),
                    ub[0] - lb[0],
                    ub[1] - lb[1],
                    boxstyle="square,pad=0",
                    linewidth=0.9,
                    edgecolor=HEX_MEDIUM,
                    facecolor="none",
                    linestyle=(0, (4, 3)),
                    alpha=0.6,
                )
            )
            for i in range(n_particles):
                ax.plot(
                    [raw[i, 0], opp[i, 0]],
                    [raw[i, 1], opp[i, 1]],
                    color=CHART_ORANGE,
                    lw=0.7,
                    alpha=0.3,
                    linestyle=(0, (2, 3)),
                )
            ax.scatter(
                opp[:, 0],
                opp[:, 1],
                s=40,
                color=CHART_ORANGE,
                marker="^",
                alpha=0.75,
                zorder=4,
                label="Điểm đối lập",
            )

        ax.scatter(
            raw[:, 0],
            raw[:, 1],
            s=55,
            color=CHART_BLUE,
            alpha=0.85,
            zorder=5,
            label="Cá thể gốc",
        )
        ax.set_title("Áp dụng SOBL" if show_sobl else "Không áp dụng SOBL", fontsize=18)
        ax.legend(fontsize=12, loc="upper right")

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] SOBL saved to '{out_path}'")


if __name__ == "__main__":

    # plot_stochastic_inertia_weight()
    # plot_tvac()
    plot_sobl()
    # plot_bezier_corner_smoothing()
    # plot_algorithm_comparison()

    pass
