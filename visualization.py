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
    BLACK,
)
from typing import Dict, List, Optional, Tuple

import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

# ---------------------------------------------------------------------------
# Report-friendly global font settings: Arial, sized to sit comfortably next
# to 10pt body text. Matplotlib falls back to Liberation Sans / DejaVu Sans
# if Arial isn't installed on the rendering machine (Liberation Sans is
# metric-compatible with Arial, so it's a safe fallback), so this still
# renders sensibly outside Windows/Office environments.
# ---------------------------------------------------------------------------
plt.rcParams["font.family"] = ["Arial", "Liberation Sans", "DejaVu Sans", "sans-serif"]

# Centralized font sizes (pt), tuned to sit next to 10pt body text in a report:
#   - subplot titles slightly above body text
#   - axis labels roughly at body text size
#   - tick labels / legend / in-chart annotations slightly below body text
FS_TITLE = 11  # subplot titles (e.g. "Early stage", "With SOBL")
FS_AXIS_LABEL = 10  # axis labels (xlabel/ylabel)
FS_TICK = 9  # tick labels
FS_LEGEND = 9  # legend text
FS_ANNOT = 8  # in-chart value annotations / point labels

plt.rcParams["axes.titlesize"] = FS_TITLE
plt.rcParams["axes.labelsize"] = FS_AXIS_LABEL
plt.rcParams["xtick.labelsize"] = FS_TICK
plt.rcParams["ytick.labelsize"] = FS_TICK
plt.rcParams["legend.fontsize"] = FS_LEGEND
plt.rcParams["font.size"] = FS_AXIS_LABEL

# Each entry: map name -> raw comparison table (tab-separated, Vietnamese metric
# names kept as keys since _parse_comparison_table matches on them, but display
# labels are translated to English via METRIC_LABEL_MAP / ALGO no translation needed).
COMPARISON_TABLES: Dict[str, str] = {
    "KB02-MZ": """Thuật toán\tRRT*\tPRM\tA*\tHAPSO
Tỷ lệ thành công\t70.0\t10.0\t100.0\t100.0
Độ dài đường đi\t100.0793\t87.5287\t84.527\t85.9735
Góc quay trung bình\t30.9597\t47.2212\t15.203\t6.6081
Khoảng cách an toàn \t1.2205\t0.7071\t0.7071\t1.0011
Thời gian tính toán\t0.1943\t0.2518\t0.0048\t1.9978
Hàm đánh giá\t1.0622\t5.0000\t5\t0.9366
""",
    "KB02-CL": """Thuật toán\tRRT*\tPRM\tA*\tHAPSO
Tỷ lệ thành công\t90.0\t0.0\t100.0\t100.0
Độ dài đường đi\t57.3003\t–\t43.3553\t50.7023
Góc quay trung bình\t31.5568\t–\t9.8438\t6.9699
Khoảng cách an toàn \t1.1267\t–\t0.7071\t1.0453
Thời gian tính toán\t0.133\t0.2013\t0.0096\t1.2786
Hàm đánh giá\t0.7756\t–\t5\t0.6734
""",
    "KB03-ID": """Thuật toán\tRRT*\tPRM\tA*\tHAPSO
Tỷ lệ thành công\t90.0\t10.0\t100.0\t100.0
Độ dài đường đi\t33.7909\t27.4441\t28.3137\t32.2559
Góc quay trung bình\t27.4363\t29.8106\t18.75\t8.4228
Khoảng cách an toàn \t1.1712\t0.7593\t0.7071\t1.1232
Thời gian tính toán\t0.2366\t0.2325\t0.0015\t0.6411
Hàm đánh giá\t0.5793\t5\t5\t0.525
""",
    "KB03-OD": """Thuật toán\tRRT*\tPRM\tA*\tHAPSO
Tỷ lệ thành công\t100.0\t10.0\t100.0\t100.0
Độ dài đường đi\t53.1532\t48.8074\t49.3137\t50.123
Góc quay trung bình\t14.9267\t42.3634\t9\t4.3502
Khoảng cách an toàn \t1.3097\t0.7071\t0.7071\t1.1729
Thời gian tính toán\t0.2157\t0.2009\t0.0021\t1.1606
Hàm đánh giá\t0.6695\t5\t5\t0.634
""",
}

# Pick which maps go into the combined comparison figure.
COMPARISON_MAP_GROUP: List[str] = ["KB02-MZ", "KB02-CL"]

# Wide-format table pasted directly from Word/Excel: several maps side by
# side, one column per algorithm per map. Parsed with
# `parse_wide_comparison_table`. Metric names here are already in English,
# so they are used as-is (see METRIC_LABEL_MAP fallback behavior below).
WIDE_COMPARISON_TABLE = """Map name\tKB02-MZ\tKB02-CL
Metric\tRRT*\tPRM\tA*\tHAPSO\tRRT*\tPRM\tA*\tHAPSO
Success Rate (%)\t70%\t100%\t100%\t100%\t100%\t100%\t100%\t100%
Path length (Cell)\t101.73\t91.96\t84.52\t86.32\t58.77\t52.41\t43.35\t50.58
Avg turning angle (Degree)\t30.80\t55.53\t15.20\t6.73\t31.88\t46.78\t9.84\t6.76
Minimum clearance (Cell)\t1.24\t1.04\t0.70\t1.00\t1.13\t1.06\t0.70\t1.02
Computation time (Second)\t0.21\t1.10\t0.01\t1.75\t0.21\t1.65\t0.01\t1.26
Composite fitness\t1.06\t1.09\t5.00\t0.93\t0.78\t0.78\t5.00\t0.67
"""

# Metrics (as they literally appear in WIDE_COMPARISON_TABLE) to plot as
# subplots in the combined figure, in order.
WIDE_COMBINED_METRICS: List[str] = [
    "Path length (Cell)",
    "Avg turning angle (Degree)",
    "Composite fitness",
]

# English display labels for the (Vietnamese-keyed) metrics parsed from the tables.
METRIC_LABEL_MAP: Dict[str, str] = {
    "Tỷ lệ thành công": "Success Rate (%)",
    "Độ dài đường đi": "Path Length",
    "Góc quay trung bình": "Average Turning Angle (°)",
    "Khoảng cách an toàn": "Minimum Clearance",
    "Thời gian tính toán": "Computation Time (s)",
    "Hàm đánh giá": "Fitness Value",
}

METRIC_FILENAME_MAP: Dict[str, str] = {
    "Tỷ lệ thành công": "success_rate",
    "Độ dài đường đi": "path_length",
    "Góc quay trung bình": "average_turning_angle",
    "Khoảng cách an toàn": "safety_clearance",
    "Thời gian tính toán": "computation_time",
    "Hàm đánh giá": "evaluation_function",
}

# Metrics to include as subplots in the combined comparison figure, in order.
COMBINED_METRICS: List[str] = [
    "Độ dài đường đi",
    "Góc quay trung bình",
    "Hàm đánh giá",
]


def _metric_label(metric: str) -> str:
    return METRIC_LABEL_MAP.get(metric, metric)


def _save_fig(fig: plt.Figure, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def plot_stochastic_inertia_weight(
    max_iterations: int = 50,
    weight_max: float = 0.9,
    weight_min: float = 0.4,
    noise_scale: float = 0.1,
    seed: int = 42,
    out_path: str = "data/results/improved/stochastic_inertia.png",
    figsize: Tuple[float, float] = (6.0, 2.0),
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
    ax.plot(iterations, stochastic_weight, "b-", label="Inertia weight value")
    ax.set_xlabel("Iteration (t)", fontsize=FS_AXIS_LABEL, color=BLACK)
    ax.set_ylabel("Inertia weight (w)", fontsize=FS_AXIS_LABEL, color=BLACK)
    ax.legend(fontsize=FS_LEGEND, labelcolor=BLACK)
    ax.grid(True, linestyle=grid_style)
    ax.tick_params(axis="both", labelsize=FS_TICK)

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
    figsize: Tuple[float, float] = (6.0, 2.0),
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
    ax1.scatter(early_x, early_y, color=CHART_DARK_GREEN, s=60, label="Particle")
    ax1.set_title("Early stage", fontsize=FS_TITLE, color=BLACK)

    ax2.quiver(
        late_x,
        late_y,
        (gbx - late_x) * 0.5 + rng.normal(0, 0.5, particle_count),
        (gby - late_y) * 0.5 + rng.normal(0, 0.5, particle_count),
        color=CHART_MAGENTA,
        alpha=0.7,
    )
    ax2.scatter(late_x, late_y, color=CHART_PURPLE, s=20)
    ax2.scatter(
        gbx,
        gby,
        color=CHART_GOLD,
        marker="*",
        s=140,
        edgecolors="black",
        label="Global best (Gbest)",
    )
    ax2.set_title("Late stage", fontsize=FS_TITLE, color=BLACK)

    for _ax in (ax1, ax2):
        _ax.set_xlim(space_min_value, space_max_value)
        _ax.set_ylim(space_min_value, space_max_value)
        _ax.set_xlabel("Space X₁", fontsize=FS_AXIS_LABEL, color=BLACK)
        _ax.set_ylabel("Space X₂", fontsize=FS_AXIS_LABEL, color=BLACK)
        _ax.grid(True, linestyle=":")
        _ax.legend(fontsize=FS_LEGEND, loc="upper right")
        _ax.tick_params(axis="both", labelsize=FS_TICK)

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] TVAC saved to '{out_path}'")


def plot_sobl(
    n_particles: int = 20,
    seed: int = 42,
    out_path: str = "data/results/improved/sobl.png",
    figsize: Tuple[float, float] = (6.0, 3.0),
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
        ax.set_xlabel("Space X₁", fontsize=FS_AXIS_LABEL, color=BLACK)
        ax.set_ylabel("Space X₂", fontsize=FS_AXIS_LABEL, color=BLACK)
        ax.grid(True, linestyle=":")

        ax.plot(
            path_pts[:, 0],
            path_pts[:, 1],
            color=CHART_GREEN,
            lw=2.0,
            linestyle=(0, (6, 4)),
            label="Trajectory",
            zorder=2,
        )
        ax.scatter(
            [focus[0]],
            [focus[1]],
            marker="D",
            s=50,
            color=DARK_GRAY,
            zorder=6,
            label="Point under consideration",
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
                s=28,
                color=CHART_ORANGE,
                marker="^",
                alpha=0.75,
                zorder=4,
                label="Opposite point",
            )

        ax.scatter(
            raw[:, 0],
            raw[:, 1],
            s=35,
            color=CHART_BLUE,
            alpha=0.85,
            zorder=5,
            label="Original particle",
        )
        ax.set_title(
            "With SOBL" if show_sobl else "Without SOBL",
            fontsize=FS_TITLE,
            color=BLACK,
        )
        ax.tick_params(axis="both", labelsize=FS_TICK)
        # ax.legend(fontsize=FS_LEGEND, loc="upper right")

    # handles, labels = ax_with.get_legend_handles_labels()
    # fig.legend(
    #     handles,
    #     labels,
    #     loc="center",
    #     bbox_to_anchor=(0.48, 0.5),
    #     fontsize=FS_LEGEND,
    #     framealpha=0.9,
    # )

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] SOBL saved to '{out_path}'")


def plot_bezier_corner_smoothing(
    blend_ratio: float = 0.3,
    out_path: str = "data/results/improved/bezier_corner_smoothing.png",
    figsize: Tuple[float, float] = (6.0, 2.0),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    prev_point = np.array([2.0, 2.0])
    corner_point = np.array([4.0, 8.0])
    next_point = np.array([6.0, 3.0])
    entry_point = corner_point + blend_ratio * (prev_point - corner_point)
    exit_point = corner_point + blend_ratio * (next_point - corner_point)

    t = np.linspace(0.0, 1.0, 100)
    bezier_points = (
        np.outer((1 - t) ** 2, entry_point)
        + np.outer(2 * (1 - t) * t, corner_point)
        + np.outer(t**2, exit_point)
    )

    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.set_aspect("auto", adjustable="box")
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 10)
    ax.set_xticks(np.arange(0, 9, 1))
    ax.set_yticks(np.arange(0, 11, 1))
    ax.grid(True, linestyle=":", linewidth=0.8, alpha=0.7)

    ax.plot(
        [prev_point[0], corner_point[0], next_point[0]],
        [prev_point[1], corner_point[1], next_point[1]],
        "r--o",
        label="Original trajectory",
    )
    ax.plot(
        bezier_points[:, 0],
        bezier_points[:, 1],
        "b-",
        linewidth=2.5,
        label="Interpolated Bezier curve",
    )
    ax.scatter(
        [entry_point[0], exit_point[0]],
        [entry_point[1], exit_point[1]],
        color=CHART_MAGENTA,
        s=50,
        zorder=5,
    )
    ax.text(
        entry_point[0] - 0.7, entry_point[1] + 0.2, "$P_{entry}$", fontsize=FS_ANNOT
    )
    ax.text(exit_point[0] + 0.2, exit_point[1] + 0.2, "$P_{exit}$", fontsize=FS_ANNOT)
    ax.text(
        corner_point[0] - 0.5, corner_point[1] + 0.3, "$P_{curr}$", fontsize=FS_ANNOT
    )

    ax.set_xlabel("X axis", fontsize=FS_AXIS_LABEL, color=BLACK)
    ax.set_ylabel("Y axis", fontsize=FS_AXIS_LABEL, color=BLACK)
    ax.legend(fontsize=FS_LEGEND)
    ax.tick_params(axis="both", labelsize=FS_TICK)
    ax.grid(True, linestyle=grid_style)

    fig.tight_layout()
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] Bezier saved to '{out_path}'")


def _clean_value(raw_value: str) -> Optional[float]:
    v = raw_value.strip()
    if v in ("", "-", "–", "—", "N/A", "n/a"):
        return None
    v = v.replace("%", "").replace(",", "").strip()
    try:
        return float(v)
    except ValueError:
        return None


def _parse_comparison_table(
    raw: str,
) -> Tuple[List[str], Dict[str, List[Optional[float]]]]:
    """Parse a single-map comparison table.

    Expected shape (tab-separated), e.g.:
        Thuật toán    RRT*    PRM    A*    HAPSO
        Tỷ lệ thành công    70.0    10.0    100.0    100.0
        ...
    """
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
        values = [_clean_value(v) for v in parts[1:]]
        if metric and len(values) == len(algorithms):
            data[metric] = values

    return algorithms, data


def parse_wide_comparison_table(
    raw: str,
) -> Dict[str, Tuple[List[str], Dict[str, List[Optional[float]]]]]:
    """Parse a "wide" comparison table pasted directly from Word/Excel, where
    several maps are laid out side by side, each occupying a block of
    columns (one column per algorithm).

    Two paste styles are supported:

    1) Merged cells preserved as empty tab-separated placeholders:
        Map name\tKB02-MZ\t\t\t\tKB02-CL
        Metric\tRRT*\tPRM\tA*\tHAPSO\tRRT*\tPRM\tA*\tHAPSO

    2) Merged cells collapsed (common when pasting from Word into a plain
       text editor — the blank placeholder cells are simply dropped):
        Map name\tKB02-MZ\tKB02-CL
        Metric\tRRT*\tPRM\tA*\tHAPSO\tRRT*\tPRM\tA*\tHAPSO

    Both styles are handled by: reading the map names as the non-empty
    tokens on the map-name row (in order), then dividing the algorithm
    columns from the metric row evenly across that many maps (assumes every
    map has the same number of algorithm columns, which holds for this
    paper's tables).

    Returns a dict keyed by map name, each value being (algorithms, data)
    with the same shape as `_parse_comparison_table`, so it plugs directly
    into `plot_algorithm_comparison` / `plot_algorithm_comparison_combined`.
    """
    lines = [ln.rstrip("\n") for ln in raw.strip("\n").splitlines() if ln.strip()]
    if len(lines) < 3:
        raise ValueError(
            "Wide table needs at least a map-name row, a metric row, and one data row."
        )

    map_row = lines[0].split("\t")
    metric_header_row = lines[1].split("\t")

    # Map names: every non-empty token after the first (label) cell, in order.
    map_names = [c.strip() for c in map_row[1:] if c.strip()]
    if not map_names:
        raise ValueError("Could not find any map names on the first row.")

    # Algorithm columns: everything after the first (label) cell on the metric row.
    algo_tokens = [c.strip() for c in metric_header_row[1:]]
    # Trim trailing empty tokens (e.g. stray trailing tabs), but keep internal
    # ones in case a table genuinely has an empty algorithm name (unlikely).
    while algo_tokens and not algo_tokens[-1]:
        algo_tokens.pop()

    n_maps = len(map_names)
    if n_maps == 0 or len(algo_tokens) % n_maps != 0:
        raise ValueError(
            f"Cannot evenly split {len(algo_tokens)} algorithm columns across "
            f"{n_maps} maps — check that every map has the same number of "
            f"algorithm columns."
        )
    block_size = len(algo_tokens) // n_maps

    map_algorithms: Dict[str, List[str]] = {}
    for i, m in enumerate(map_names):
        map_algorithms[m] = algo_tokens[i * block_size : (i + 1) * block_size]

    map_data: Dict[str, Dict[str, List[Optional[float]]]] = {m: {} for m in map_names}

    for line in lines[2:]:
        parts = [p.strip() for p in line.split("\t")]
        metric = parts[0].strip() if parts else ""
        if not metric:
            continue
        values_all = parts[1:]
        # Pad in case a data row is short a trailing empty cell or two.
        if len(values_all) < len(algo_tokens):
            values_all = values_all + [""] * (len(algo_tokens) - len(values_all))
        for i, m in enumerate(map_names):
            block = values_all[i * block_size : (i + 1) * block_size]
            map_data[m][metric] = [_clean_value(v) for v in block]

    return {m: (map_algorithms[m], map_data[m]) for m in map_names}


def plot_algorithm_comparison(
    raw_table: str,
    map_name: str,
    out_base_dir: str = "data/results/charts",
    figsize: Tuple[float, float] = (5.5, 4.0),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    """Save one bar-chart image per metric for a single map.

    Kept for cases where a standalone, per-metric figure is still needed.
    For the standard paper figure comparing path length / turning angle /
    fitness across maps, prefer `plot_algorithm_comparison_combined`.
    """
    if not map_name:
        print("[VISUALIZATION] map_name is not defined — skipping.")
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
                fontsize=FS_ANNOT,
            )

        ax2.plot(
            x,
            success_rates,
            marker="o",
            linewidth=2.0,
            color="red",
            label="Success rate",
        )

        ax1.set_xticks(x)
        ax1.set_xticklabels(algorithms, fontsize=FS_TICK)
        ax1.set_ylabel(_metric_label(metric), fontsize=FS_AXIS_LABEL)
        ax2.set_ylabel("Success rate (%)", fontsize=FS_AXIS_LABEL)
        ax1.set_ylim(0, max_val * 1.18)
        ax2.set_ylim(0, 105)
        ax1.tick_params(axis="y", labelsize=FS_TICK)
        ax2.tick_params(axis="y", labelsize=FS_TICK)
        ax1.grid(True, axis="y", linestyle=grid_style, alpha=0.6)
        ax1.set_axisbelow(True)
        fig.tight_layout()

        file_stem = METRIC_FILENAME_MAP.get(metric, metric.lower().replace(" ", "_"))
        _save_fig(fig, os.path.join(out_dir, f"{file_stem}.png"))

    print(f"[VISUALIZATION] Completed — {len(data)} charts saved to '{out_dir}'")


def plot_algorithm_comparison_combined(
    map_tables: Optional[Dict[str, str]] = None,
    parsed_tables: Optional[
        Dict[str, Tuple[List[str], Dict[str, List[Optional[float]]]]]
    ] = None,
    map_names: Optional[List[str]] = None,
    metrics: List[str] = COMBINED_METRICS,
    out_path: str = "data/results/charts/algorithm_comparison_combined.png",
    figsize_per_subplot: Tuple[float, float] = (3.6, 3.0),
    dpi: int = 150,
    grid_style: str = "--",
) -> None:
    """Build ONE figure with one subplot per metric.

    Each subplot is a grouped bar chart: groups = maps, bars within a group =
    algorithms. This replaces the earlier "one bar chart per metric per map"
    approach so the paper only needs a single combined figure, e.g.:

        Figure X: Comparison of path length, average turning angle, and
        composite fitness across algorithms on maps KB02-MZ and KB02-CL.

    Provide EITHER:
      - `map_tables`: Dict[map_name -> single-map raw table string] (old
        per-map format, parsed with `_parse_comparison_table`), OR
      - `parsed_tables`: Dict[map_name -> (algorithms, data)] already parsed
        (e.g. via `parse_wide_comparison_table`, which is the easiest way to
        feed in a table pasted straight from Word/Excel with several maps
        side by side).
    """
    if parsed_tables is not None:
        parsed_all = parsed_tables
    elif map_tables is not None:
        parsed_all = {}
        for name, raw in map_tables.items():
            algorithms, data = _parse_comparison_table(raw)
            if algorithms and data:
                parsed_all[name] = (algorithms, data)
    else:
        print("[VISUALIZATION] Provide either map_tables or parsed_tables — skipping.")
        return

    map_names = map_names or list(parsed_all.keys())
    if not map_names:
        print("[VISUALIZATION] No maps provided — skipping.")
        return

    parsed: Dict[str, Tuple[List[str], Dict[str, List[Optional[float]]]]] = {}
    for name in map_names:
        entry = parsed_all.get(name)
        if not entry or not entry[0] or not entry[1]:
            print(f"[VISUALIZATION] No usable data for map '{name}' — skipping it.")
            continue
        parsed[name] = entry

    if not parsed:
        print("[VISUALIZATION] Nothing to plot — no maps parsed successfully.")
        return

    valid_map_names = [n for n in map_names if n in parsed]
    # Assume the algorithm set/order is consistent across maps (typical for
    # this paper: RRT*, PRM, A*, HAPSO). Use the first map's order.
    algorithms = parsed[valid_map_names[0]][0]
    n_algo = len(algorithms)
    n_maps = len(valid_map_names)

    n_metrics = len(metrics)
    fig, axes = plt.subplots(
        1,
        n_metrics,
        figsize=(figsize_per_subplot[0] * n_metrics, figsize_per_subplot[1]),
        dpi=dpi,
    )
    if n_metrics == 1:
        axes = [axes]

    group_gap = 1.0
    x_group_centers = np.arange(n_maps) * (n_algo + group_gap)
    bar_width = 0.8
    colors = CHART_COLORS[:n_algo]
    hatches = CHART_HATCHES[:n_algo]

    for ax, metric in zip(axes, metrics):
        for algo_idx, algo in enumerate(algorithms):
            xs, ys = [], []
            for map_idx, map_name in enumerate(valid_map_names):
                _, data = parsed[map_name]
                values = data.get(metric)
                val = values[algo_idx] if values else None
                if val is None:
                    continue
                xs.append(x_group_centers[map_idx] + algo_idx * bar_width)
                ys.append(val)
            bars = ax.bar(
                xs,
                ys,
                width=bar_width * 0.95,
                color=colors[algo_idx],
                edgecolor="black",
                linewidth=0.5,
                hatch=hatches[algo_idx],
                label=algo,
            )
            for bar, val in zip(bars, ys):
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{val:.3g}",
                    ha="center",
                    va="bottom",
                    fontsize=FS_ANNOT,
                )

        tick_positions = x_group_centers + (n_algo - 1) * bar_width / 2
        ax.set_xticks(tick_positions)
        ax.set_xticklabels(valid_map_names, fontsize=FS_TICK)
        ax.set_ylabel(_metric_label(metric), fontsize=FS_AXIS_LABEL, color=BLACK)
        ax.grid(True, axis="y", linestyle=grid_style, alpha=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", labelsize=FS_TICK)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=n_algo,
        fontsize=FS_LEGEND,
        frameon=False,
    )

    fig.tight_layout(rect=[0, 0, 1, 0.94])
    _save_fig(fig, out_path)
    print(f"[VISUALIZATION] Combined comparison figure saved to '{out_path}'")


if __name__ == "__main__":

    # plot_stochastic_inertia_weight()
    # plot_tvac()
    plot_sobl()
    # plot_bezier_corner_smoothing()

    # Option A: several single-map tables (old format, Vietnamese metric keys).
    # plot_algorithm_comparison_combined(
    #     map_tables=COMPARISON_TABLES,
    #     map_names=COMPARISON_MAP_GROUP,
    # )

    # Option B: one "wide" table pasted straight from Word/Excel, with maps
    # laid out side by side (this matches the format you pasted).
    # parsed_wide = parse_wide_comparison_table(WIDE_COMPARISON_TABLE)
    # plot_algorithm_comparison_combined(
    #     parsed_tables=parsed_wide,
    #     metrics=WIDE_COMBINED_METRICS,
    #     out_path="data/results/charts/algorithm_comparison_combined_wide.png",
    # )

    pass
