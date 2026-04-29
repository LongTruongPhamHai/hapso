from datetime import datetime
from environment.grid_map import GridMap
from typing import Any, Dict, List, Optional, Tuple

import json
import os
import pygame


def save_all_results(
    screen,
    results_base_dir: str,
    grid: GridMap,
    path: Optional[List[Tuple[int, int]]],
    algorithm: str,
) -> Tuple[bool, str]:
    try:
        results_dir = create_results_directory(results_base_dir)
        image_success = save_result_image(screen, results_dir)
        json_success = save_result_json(results_dir, grid, path or [], algorithm)
        success = image_success and json_success

        if success:
            print(f"\nAll results saved to: {results_dir}")
        else:
            print(f"\nSome files failed to save in: {results_dir}")

        return success, results_dir

    except Exception as e:
        print(f"Error in save_all_results: {e}")
        return False, ""


def create_results_directory(results_dir: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    timestamped_dir = os.path.join(results_dir, timestamp)
    os.makedirs(timestamped_dir, exist_ok=True)
    print(f"Created results directory: {timestamped_dir}")

    return timestamped_dir


def save_result_image(screen, results_dir: str, filename: str = "result.png") -> bool:
    try:
        filepath = os.path.join(results_dir, filename)

        pygame.image.save(screen, filepath)
        print(f"Saved image: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving image: {e}")
        return False


def save_result_json(
    results_dir: str,
    grid: GridMap,
    path: List[Tuple[int, int]],
    algorithm: str,
    filename: str = "result.json",
) -> bool:
    try:
        filepath = os.path.join(results_dir, filename)

        result_data: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "algorithm": algorithm,
            "grid": {
                "width": grid.width,
                "height": grid.height,
                "start": grid.start,
                "goal": grid.goal,
                "obstacles_count": sum(
                    1
                    for y in range(grid.height)
                    for x in range(grid.width)
                    if grid.grid[y][x] == GridMap.OBSTACLE
                ),
            },
            "path": {
                "found": path is not None and len(path) > 0,
                "length": len(path) if path else 0,
                "coordinates": path if path else [],
                "distance": len(path) - 1 if path and len(path) > 1 else 0,
            },
        }

        with open(filepath, "w") as f:
            json.dump(result_data, f, indent=2)

        print(f"Saved result JSON: {filepath}")
        return True
    except Exception as e:
        print(f"Error saving JSON: {e}")
        return False
