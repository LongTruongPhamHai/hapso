from __future__ import annotations
from dataclasses import dataclass
from grid_map import GridMap
from typing import Iterable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import os

plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]


@dataclass
class PlotStyle:
    figsize: Tuple[float, float] = (8.0, 4.5)
    grid_style: str = "--"
    dpi: int = 150


def _ensure_out_dir(out_dir: str) -> None:
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)


def plot_stochastic_inertia_weight(
    max_iterations: int = 100,
    weight_max: float = 0.9,
    weight_min: float = 0.4,
    noise_scale: float = 0.1,
    seed: int = 42,
    out_path: str | None = None,
    style: PlotStyle | None = None,
) -> None:
    style = style or PlotStyle()
    iterations = np.arange(0, max_iterations)

    linear_weight = weight_max - (
        (weight_max - weight_min) * iterations / max_iterations
    )

    rng = np.random.default_rng(seed)
    stochastic_weight = linear_weight * (
        1 + noise_scale * (rng.random(max_iterations) - 0.5)
    )

    plt.figure(figsize=style.figsize, dpi=style.dpi)
    plt.plot(iterations, stochastic_weight, "b-", label="Giá trị trọng số quán tính")
    plt.xlabel("Vòng lặp (t)")
    plt.ylabel("Trọng số quán tính (w)")
    plt.legend()
    plt.grid(True, linestyle=style.grid_style)

    if out_path:
        _ensure_out_dir(os.path.dirname(out_path))
        plt.savefig(out_path, bbox_inches="tight")
    else:
        plt.show()
    plt.close()


def plot_tvac(
    max_iterations: int = 100,
    particle_count: int = 40,
    space_min_value: float = 0.0,
    space_max_value: float = 100.0,
    global_best: Tuple[float, float] = (50.0, 50.0),
    seed: int = 10,
    out_path: str | None = None,
    style: PlotStyle | None = None,
) -> None:
    style = style or PlotStyle(figsize=(11.0, 4.8))
    rng = np.random.default_rng(seed)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=style.figsize, dpi=style.dpi)

    early_x = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)
    early_y = rng.uniform(space_min_value + 10, space_max_value - 10, particle_count)
    early_u = rng.uniform(-15, 15, particle_count)
    early_v = rng.uniform(-15, 15, particle_count)

    ax1.quiver(early_x, early_y, early_u, early_v, color="green", alpha=0.7)
    ax1.scatter(early_x, early_y, color="darkgreen", s=100, label="Cá thể (Hạt)")
    ax1.set_title("Giai đoạn đầu", fontsize=18)
    ax1.set_xlim(space_min_value, space_max_value)
    ax1.set_ylim(space_min_value, space_max_value)
    ax1.set_xlabel("Không gian X₁", fontsize=16)
    ax1.set_ylabel("Không gian X₂", fontsize=16)
    ax1.grid(True, linestyle=":")
    ax1.legend()

    global_best_x, global_best_y = global_best
    late_x = rng.normal(global_best_x, 4, particle_count)
    late_y = rng.normal(global_best_y, 4, particle_count)
    late_u = (global_best_x - late_x) * 0.5 + rng.normal(0, 0.5, particle_count)
    late_v = (global_best_y - late_y) * 0.5 + rng.normal(0, 0.5, particle_count)

    ax2.quiver(late_x, late_y, late_u, late_v, color="magenta", alpha=0.7)
    ax2.scatter(late_x, late_y, color="purple", s=30)
    ax2.scatter(
        global_best_x,
        global_best_y,
        color="gold",
        marker="*",
        s=200,
        edgecolors="black",
        label="Tối ưu toàn cục (Gbest)",
    )
    ax2.set_title("Giai đoạn cuối", fontsize=18)
    ax2.set_xlim(space_min_value, space_max_value)
    ax2.set_ylim(space_min_value, space_max_value)
    ax2.set_xlabel("Không gian X₁", fontsize=16)
    ax2.set_ylabel("Không gian X₂", fontsize=16)
    ax2.grid(True, linestyle=":")
    ax2.legend()

    fig.tight_layout()
    if out_path:
        _ensure_out_dir(os.path.dirname(out_path))
        fig.savefig(out_path, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def plot_bezier_corner_smoothing(
    blend_ratio: float = 0.3,
    out_path: str | None = None,
    style: PlotStyle | None = None,
) -> None:
    style = style or PlotStyle(figsize=(7.2, 4.5))

    prev_point = np.array([2.0, 2.0])
    corner_point = np.array([6.0, 8.0])
    next_point = np.array([10.0, 3.0])

    entry_point = corner_point + blend_ratio * (prev_point - corner_point)
    exit_point = corner_point + blend_ratio * (next_point - corner_point)

    t_values = np.linspace(0.0, 1.0, 100)
    bezier_points = np.array(
        [
            (1 - t_val) ** 2 * entry_point
            + 2 * (1 - t_val) * t_val * corner_point
            + t_val**2 * exit_point
            for t_val in t_values
        ]
    )

    fig, ax = plt.subplots(figsize=style.figsize, dpi=style.dpi)
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
        label="Quỹ đạo gãy khúc gốc",
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
        color="magenta",
        s=80,
        zorder=5,
    )
    ax.text(entry_point[0] - 0.8, entry_point[1] + 0.2, "$P_{in}$")
    ax.text(exit_point[0] + 0.3, exit_point[1] + 0.2, "$P_{out}$")
    ax.text(corner_point[0] - 0.5, corner_point[1] + 0.3, "$P_{curr}$")

    ax.set_xlabel("Trục X")
    ax.set_ylabel("Trục Y")
    # ax.set_title("Đường cong Bezier")
    ax.legend()
    ax.grid(True, linestyle=style.grid_style)

    if out_path:
        _ensure_out_dir(os.path.dirname(out_path))
        fig.savefig(out_path, bbox_inches="tight")
    else:
        plt.show()
    plt.close(fig)


def generate_all_plots(out_dir: str = r"data/visualization") -> None:
    _ensure_out_dir(out_dir)
    plot_stochastic_inertia_weight(
        out_path=os.path.join(out_dir, "stochastic_inertia.png")
    )
    plot_tvac(out_path=os.path.join(out_dir, "tvac.png"))
    plot_bezier_corner_smoothing(
        out_path=os.path.join(out_dir, "bezier_corner_smoothing.png")
    )


if __name__ == "__main__":
    generate_all_plots()
