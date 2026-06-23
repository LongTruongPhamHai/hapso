from __future__ import annotations
from config.colors import CHART_COLORS, CHART_HATCHES
from dataclasses import dataclass
from typing import Dict, List, Tuple

import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

plt.rcParams["font.family"] = ["DejaVu Sans", "sans-serif"]

# MAP_NAME = "KB02-MZ"
# COMPARISON_TABLE = """Thuật toán	RRT*	PRM	A*	HAPSO
# Tỷ lệ thành công	70.0	10.0	100.0	100.0
# Độ dài đường đi	100.0793	87.5287	84.527	85.9735
# Góc quay trung bình	30.9597	47.2212	15.203	6.6081
# Khoảng cách an toàn 	1.2205	0.7071	0.7071	1.0011
# Thời gian tính toán	0.1943	0.2518	0.0048	1.9978
# Hàm đánh giá	1.0622	5.0000	5	0.9366
# """
# MAP_NAME = "KB02-CL"
# COMPARISON_TABLE = """Thuật toán	RRT*	PRM	A*	HAPSO
# Tỷ lệ thành công	90.0	0.0	100.0	100.0
# Độ dài đường đi	57.3003	–	43.3553	50.7023
# Góc quay trung bình	31.5568	–	9.8438	6.9699
# Khoảng cách an toàn 	1.1267	–	0.7071	1.0453
# Thời gian tính toán	0.133	0.2013	0.0096	1.2786
# Hàm đánh giá	0.7756	–	5	0.6734
# """
# MAP_NAME = "KB03-ID"
# COMPARISON_TABLE = """Thuật toán	RRT*	PRM	A*	HAPSO
# Tỷ lệ thành công	90.0	10.0	100.0	100.0
# Độ dài đường đi	33.7909	27.4441	28.3137	32.2559
# Góc quay trung bình	27.4363	29.8106	18.75	8.4228
# Khoảng cách an toàn 	1.1712	0.7593	0.7071	1.1232
# Thời gian tính toán	0.2366	0.2325	0.0015	0.6411
# Hàm đánh giá	0.5793	5	5	0.525
# """
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


@dataclass
class PlotStyle:
    figsize: Tuple[float, float] = (8.0, 4.5)
    grid_style: str = "--"
    dpi: int = 150


def _parse_comparison_table(raw: str) -> Tuple[List[str], Dict[str, List[float]]]:
    lines = [ln.rstrip() for ln in raw.strip().splitlines() if ln.strip()]

    header_idx = 0
    algorithms: List[str] = []

    for i, line in enumerate(lines):
        parts = line.split("\t")

        if len(parts) >= 3:
            algorithms = [p.strip() for p in parts[1:] if p.strip()]
            header_idx = i
            break

    data: Dict[str, List[float]] = {}
    for line in lines[header_idx + 1 :]:
        parts = line.split("\t")

        if len(parts) < 2:
            continue

        metric = parts[0].strip()
        values: List[float | None] = []

        for v in parts[1:]:
            v = v.strip()

            if not v:
                values.append(None)

            elif v == "-" or v == "–":
                values.append(None)

            else:
                values.append(float(v))

        if metric and len(values) == len(algorithms):
            data[metric] = values

    return algorithms, data


def plot_algorithm_comparison(
    raw_table: str = COMPARISON_TABLE,
    map_name: str = MAP_NAME,
    out_base_dir: str = "data/results/charts",
    style: PlotStyle | None = None,
) -> None:
    if not map_name:
        print("[VISUALIZATION] MAP_NAME is not defined — skipping.")
        return

    style = style or PlotStyle(figsize=(7.0, 5.5))
    algorithms, data = _parse_comparison_table(raw_table)

    if not algorithms or not data:
        print("[VISUALIZATION] Failed to parse data from the table.")
        return

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = os.path.join(out_base_dir, f"{map_name}_{timestamp}")
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    x = np.arange(len(algorithms))
    bar_width = 0.55 / max(len(algorithms) - 1, 1) * len(algorithms)
    bar_width = min(bar_width, 0.65)

    colors = CHART_COLORS[: len(algorithms)]
    hatches = CHART_HATCHES[: len(algorithms)]

    success_rates = data["Tỷ lệ thành công"]

    for metric, values in data.items():
        # ======================================================
        # CHẾ ĐỘ 1: BIỂU ĐỒ CỘT THÔNG THƯỜNG
        # ======================================================

        # fig, ax1 = plt.subplots(figsize=style.figsize, dpi=style.dpi)

        # # Loại bỏ các giá trị None
        # valid_x = []
        # valid_values = []
        # valid_colors = []
        # valid_hatches = []
        # valid_algorithms = []

        # for i, val in enumerate(values):
        #     if val is not None:
        #         valid_x.append(x[i])
        #         valid_values.append(val)
        #         valid_colors.append(colors[i])
        #         valid_hatches.append(hatches[i])
        #         valid_algorithms.append(algorithms[i])

        # bars = ax1.bar(
        #     valid_x,
        #     valid_values,
        #     width=bar_width,
        #     color=valid_colors,
        #     edgecolor="black",
        #     linewidth=0.8,
        # )

        # for bar, hatch in zip(bars, valid_hatches):
        #     bar.set_hatch(hatch)

        # max_val = max(valid_values)

        # for bar, val in zip(bars, valid_values):
        #     ax1.text(
        #         bar.get_x() + bar.get_width() / 2,
        #         bar.get_height() + max_val * 0.015,
        #         f"{val:.4g}",
        #         ha="center",
        #         va="bottom",
        #         fontsize=20,
        #     )

        # ax1.set_xticks(valid_x)
        # ax1.set_xticklabels(valid_algorithms, fontsize=20)

        # ax1.set_ylabel("Giá trị trung bình", fontsize=20)
        # ax1.set_title(metric, fontsize=20, fontweight="bold")

        # ax1.set_ylim(0, max_val * 1.18)

        # ax1.grid(
        #     True,
        #     axis="y",
        #     linestyle=style.grid_style,
        #     alpha=0.6,
        # )
        # ax1.set_axisbelow(True)

        # fig.tight_layout()

        # ======================================================
        # CHẾ ĐỘ 2: BIỂU ĐỒ DUAL AXIS
        # ======================================================

        if metric == "Tỷ lệ thành công":
            continue

        fig, ax1 = plt.subplots(figsize=style.figsize, dpi=style.dpi)
        ax2 = ax1.twinx()

        # Chỉ giữ các giá trị hợp lệ cho biểu đồ cột
        valid_x = []
        valid_values = []
        valid_colors = []
        valid_hatches = []

        for i, val in enumerate(values):
            if val is not None:
                valid_x.append(x[i])
                valid_values.append(val)
                valid_colors.append(colors[i])
                valid_hatches.append(hatches[i])

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

        # Đường tỷ lệ thành công vẫn dùng tất cả thuật toán
        line = ax2.plot(
            x,
            success_rates,
            marker="o",
            linewidth=2.5,
            color="red",
            label="Tỷ lệ thành công",
        )

        # Trục x vẫn hiện đủ các thuật toán
        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms, fontsize=20)

        ax1.set_ylabel(metric, fontsize=20)
        ax2.set_ylabel("Tỷ lệ thành công (%)", fontsize=20)

        ax1.set_ylim(0, max_val * 1.18)
        ax2.set_ylim(0, 105)

        ax1.tick_params(axis="y", labelsize=18)
        ax2.tick_params(axis="y", labelsize=18)

        ax1.grid(
            True,
            axis="y",
            linestyle=style.grid_style,
            alpha=0.6,
        )
        ax1.set_axisbelow(True)

        fig.tight_layout()

        file_stem = METRIC_FILENAME_MAP.get(
            metric,
            metric.lower().replace(" ", "_"),
        )

        out_path = os.path.join(
            out_dir,
            f"{file_stem}.png",
        )

        fig.savefig(out_path, bbox_inches="tight")
        plt.close(fig)

    print(f"[VISUALIZATION] Completed — {len(data)} charts saved to '{out_dir}'")


def plot_stochastic_inertia_weight(
    max_iterations: int = 50,
    weight_max: float = 0.9,
    weight_min: float = 0.4,
    noise_scale: float = 0.1,
    seed: int = 42,
    out_path: str = r"data/results/improved",
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
    plt.xlabel("Vòng lặp (t)", fontsize=12)
    plt.ylabel("Trọng số quán tính (w)", fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle=style.grid_style)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    plt.savefig(out_path, bbox_inches="tight")

    plt.close()


def plot_tvac(
    particle_count: int = 40,
    space_min_value: float = 0.0,
    space_max_value: float = 100.0,
    global_best: Tuple[float, float] = (50.0, 50.0),
    seed: int = 10,
    out_path: str = r"data/results/improved",
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
    ax1.legend(fontsize=14)

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
    ax2.legend(fontsize=14)

    fig.tight_layout()

    if out_path and not os.path.isdir(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path, bbox_inches="tight")

    else:
        plt.show()

    plt.close(fig)


def plot_bezier_corner_smoothing(
    blend_ratio: float = 0.3,
    out_path: str = r"data/results/improved",
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
    ax.legend()
    ax.grid(True, linestyle=style.grid_style)

    if out_path and not os.path.isdir(out_path):
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        fig.savefig(out_path, bbox_inches="tight")

    else:
        plt.show()

    plt.close(fig)


if __name__ == "__main__":

    # plot_algorithm_comparison()

    # plot_stochastic_inertia_weight(
    #     out_path=("data/results/improved/stochastic_inertia.png")
    # )

    # plot_tvac(out_path=("data/results/improved/tvac.png"))

    # plot_bezier_corner_smoothing(out_path=("data/results/improved/bezier_corner_smoothing.png"))

    pass
