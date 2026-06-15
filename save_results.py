from __future__ import annotations
from datetime import datetime
from openpyxl import Workbook
from pathlib import Path
from typing import Optional

import json
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def save_run_results(
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    cost_history: Optional[list[float]] = None,
    map_name: str = "N/A",
    start_time: str = "N/A",
    end_time: str = "N/A",
    base_dir: str = "data/results",
) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = _safe(algorithm_name)
    run_dir = Path(base_dir) / f"{safe_name}_{timestamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    _save_path_json(
        run_dir, algorithm_name, path, metrics, map_name, start_time, end_time
    )
    _save_metrics_xlsx(
        run_dir, algorithm_name, path, metrics, map_name, start_time, end_time
    )

    if cost_history:
        _save_convergence_png(run_dir, algorithm_name, cost_history, map_name)

    return run_dir


def _safe(name: str) -> str:
    return "".join(c if (c.isalnum() or c == "_") else "_" for c in name)


def _save_path_json(
    run_dir: Path,
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    map_name: str,
    start_time: str,
    end_time: str,
) -> None:
    payload = {
        "algorithm": algorithm_name,
        "map": map_name,
        "start_time": start_time,
        "end_time": end_time,
        "success": bool(path),
        "waypoint_count": len(path) if path else 0,
        "path": [list(p) for p in path] if path else [],
        "metrics": {
            k: (v if not isinstance(v, float) else round(v, 4))
            for k, v in metrics.items()
        },
    }

    out = run_dir / "path.json"
    with out.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def _save_metrics_xlsx(
    run_dir: Path,
    algorithm_name: str,
    path: Optional[list[tuple[float, float]]],
    metrics: dict,
    map_name: str,
    start_time: str,
    end_time: str,
) -> None:
    wb = Workbook()

    ws_sum = wb.active
    ws_sum.title = "Summary"
    ws_sum.append(["Field", "Value"])

    for row in [
        ("Algorithm", algorithm_name),
        ("Map", map_name),
        ("Start time", start_time),
        ("End time", end_time),
        ("Result", "SUCCESS" if path else "FAILED"),
        ("Waypoint count", len(path) if path else 0),
    ]:
        ws_sum.append(list(row))

    ws_sum.append([])
    ws_sum.append(["Metric", "Value"])

    for k, v in metrics.items():
        ws_sum.append([k, round(v, 4) if isinstance(v, float) else v])

    wb.save(run_dir / "metrics.xlsx")


def _save_convergence_png(
    run_dir: Path,
    algorithm_name: str,
    cost_history: list[float],
    map_name: str,
) -> None:
    iterations = list(range(len(cost_history)))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(
        iterations,
        cost_history,
        linewidth=1.5,
        color="#2563EB",
        label="Giá trị hàm thích nghi toàn cục",
    )

    ax.set_title(
        f"Biểu đồ giá trị hàm mục tiêu {algorithm_name}\nBản đồ: {map_name}",
        fontsize=12,
    )
    ax.set_xlabel("Vòng lặp", fontsize=10)
    ax.set_ylabel("Giá trị", fontsize=10)
    ax.legend(fontsize=9)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()

    out = run_dir / "convergence.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
