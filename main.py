from astar import Astar
from config.colors import (
    BLACK,
    MEDIUM,
    LIGHT,
    WHITE,
    RED,
    ORANGE,
    YELLOW,
    GREEN,
    BLUE,
    INDIGO,
    VIOLET,
)
from config.ui import (
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    NAV_HEIGHT,
    NAV_WIDTH,
    NAV_MENU,
    NAV_OFFSET_X,
    NAV_OFFSET_Y,
    MODE_HEIGHT,
    MODE_OFFSET_X,
    MODE_OFFSET_Y,
    GRID_CELL_SIZE,
    TEXT_FONT,
    SMALL_TEXT_SIZE,
    NORMAL_TEXT_SIZE,
    LARGE_TEXT_SIZE,
    TKINTER_ALGOR_WINDOW_SIZE,
    TKINTER_BATCH_WINDOW_SIZE,
    TKINTER_TEXT_FONT,
    TKINTER_TEXT_SIZE,
)
from config.parameter import (
    GRID_MAP_HEIGHT,
    GRID_MAP_WIDTH,
    MIN_CLEARANCE,
    COLLISION_PENALTY,
)
from datetime import datetime
from grid_map import GridMap
from hapso import HAPSO
from openpyxl import Workbook
from pathlib import Path
from prm import PRM
from rrt_star import RRTStar
from tkinter import filedialog, messagebox, Tk
from utils import (
    compute_path_metrics,
    print_all_path_metrics,
    print_batch_header,
    print_batch_summary_report,
    print_path_metrics,
    save_run_results,
)

import json
import pygame
import time
import tkinter as tk


class Text:
    def __init__(
        self,
        screen: pygame.Surface,
        x: int,
        y: int,
        color: tuple[int, int, int],
        text: str,
        font_name: str = TEXT_FONT,
        size: int = NORMAL_TEXT_SIZE,
    ) -> None:
        self.screen = screen
        self.x = x
        self.y = y

        self.color = color

        self.text = text
        self.font_name = font_name
        self.size = size

        self.font = pygame.font.SysFont(self.font_name, self.size)

    def draw_text(self) -> None:
        text_surface = self.font.render(self.text, True, self.color)

        self.screen.blit(text_surface, (self.x, self.y))


class AlgorithmSelectDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc, current_idx: int, options: list[str]) -> None:
        super().__init__(parent)

        self.title("Select Algorithm")
        self.geometry(TKINTER_ALGOR_WINDOW_SIZE)
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(
            self, text="Choose Solver:", font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE)
        ).pack(pady=10)
        self.selected_algo_var = tk.IntVar(value=current_idx)

        for i, name in enumerate(options):
            tk.Radiobutton(
                self,
                text=name,
                variable=self.selected_algo_var,
                value=i,
                font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
            ).pack(anchor="w", padx=40)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Select",
            command=self.on_select,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)

        self._center_window()

    def on_select(self) -> None:
        self.result = self.selected_algo_var.get()
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()

        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")


class BatchTestDialog(tk.Toplevel):
    def __init__(self, parent: tk.Misc) -> None:
        super().__init__(parent)

        self.title("Batch Test Configuration")
        self.geometry(TKINTER_BATCH_WINDOW_SIZE)
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(
            self,
            text="Number of Test Runs (1-100):",
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(pady=10)
        self.run_count_var = tk.IntVar(value=10)
        tk.Entry(
            self,
            textvariable=self.run_count_var,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Start Testing",
            command=self.on_start,
            width=15,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
            font=(TKINTER_TEXT_FONT, TKINTER_TEXT_SIZE),
        ).pack(side=tk.LEFT, padx=5)

        self._center_window()

    def on_start(self) -> None:
        try:
            runs = self.run_count_var.get()

        except tk.TclError:
            messagebox.showerror("Error", "Invalid number.")
            return

        if not isinstance(runs, int) or not (1 <= runs <= 100):
            messagebox.showerror("Error", "Enter 1-100.")
            return

        self.result = runs
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()

        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")


class SettingsDialog(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Misc,
        current_width: int,
        current_height: int,
        current_cell_size: int,
    ) -> None:
        super().__init__(parent)

        self.title("Map Settings")
        self.geometry("300x250")
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(self, text="Width (5-100):").pack(pady=(10, 0))
        self.width_var = tk.IntVar(value=current_width)
        tk.Entry(self, textvariable=self.width_var).pack()

        tk.Label(self, text="Height (5-100):").pack(pady=(10, 0))
        self.height_var = tk.IntVar(value=current_height)
        tk.Entry(self, textvariable=self.height_var).pack()

        tk.Label(self, text="Cell Size (5-50 px):").pack(pady=(10, 0))
        self.cell_size_var = tk.IntVar(value=current_cell_size)
        tk.Entry(self, textvariable=self.cell_size_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Apply", command=self.on_apply, width=10).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(
            side=tk.LEFT, padx=5
        )

        self._center_window()

    def on_apply(self) -> None:
        try:
            width = self.width_var.get()
            height = self.height_var.get()
            cell_size = self.cell_size_var.get()

        except tk.TclError:
            messagebox.showerror("Error", "Invalid input.")
            return

        if not (5 <= width <= 100 and 5 <= height <= 100 and 5 <= cell_size <= 50):
            messagebox.showerror("Error", "Values out of range.")
            return

        self.result = (width, height, cell_size)
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()

        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)

        self.geometry(f"{w}x{h}+{x}+{y}")


class App:
    def __init__(self) -> None:
        print("=" * 60)
        print("HAPSO: Hybrid A-Star Particle Swarm Optimizer")
        print("=" * 60)
        print("[INIT] Initializing application...")

        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("HAPSO: Simulator Application")

        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(TEXT_FONT, NORMAL_TEXT_SIZE)

        self.height = GRID_MAP_HEIGHT
        self.width = GRID_MAP_WIDTH
        self.cell_size = GRID_CELL_SIZE

        self.grid_map = GridMap(width=self.width, height=self.height)

        self.min_clearance = MIN_CLEARANCE
        self.collision_penalty = COLLISION_PENALTY

        self.running = True
        self.mode = "Free"
        self.selected_algorithm = "A-Star"

        self.is_dragging = False
        self.drag_start: tuple[float, float] | None = None
        self.drag_end: tuple[float, float] | None = None
        self.current_path: list[tuple[float, float]] | None = None

        self.map_name: str = "N/A"

        self.algorithm_names = [
            "RRT-Star",
            "PRM",
            "A-Star",
            "HAPSO",
            "All",
        ]

        colors_for_algos = [BLUE, ORANGE, GREEN, VIOLET, INDIGO, YELLOW, RED]
        self.algorithm_colors: dict[str, tuple[int, int, int]] = {
            name: colors_for_algos[i % len(colors_for_algos)]
            for i, name in enumerate(self.algorithm_names)
            if name != "All"
        }

        self.all_paths: dict[str, list[tuple[float, float]]] = {}

        self._recalc_layout()

        print(
            f"[INIT] Grid initialized: {self.width}x{self.height} (cell size: {self.cell_size}px)"
        )
        print(f"[INIT] Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"[INIT] Ready. Press [?] or check menu for commands.\n")

    @staticmethod
    def _now_str() -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def run(self) -> None:
        while self.running:
            self._handle_events()
            self._draw_ui()
            self.clock.tick(60)

        print("\n[EXIT] Shutting down application...")
        pygame.quit()
        self.tk_root.destroy()
        print("[EXIT] Application closed.")

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                self._on_mouse_motion(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self._on_mouse_up(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._on_mouse_down(event)

            elif event.type == pygame.KEYDOWN:
                self._on_keydown(event)

    def _on_mouse_motion(self, event: pygame.event.Event) -> None:
        if not self.is_dragging:
            return

        grid_pos = self._screen_to_grid(event.pos)
        if grid_pos is not None:
            self.drag_end = grid_pos

    def _on_mouse_up(self, event: pygame.event.Event) -> None:
        if event.button != 1:
            return
        if (
            self.is_dragging
            and self.drag_start is not None
            and self.drag_end is not None
        ):
            pts = self._bresenham_line(self.drag_start, self.drag_end)
            self._apply_line(pts)

        self.is_dragging = False
        self.drag_start = None
        self.drag_end = None

    def _on_mouse_down(self, event: pygame.event.Event) -> None:
        if event.button != 1:
            return

        grid_pos = self._screen_to_grid(event.pos)
        if grid_pos is None:
            return

        if self.mode == "Free":
            pass

        elif self.mode in ("Obstacle", "Erase"):
            self.is_dragging = True
            self.drag_start = grid_pos
            self.drag_end = grid_pos

        elif self.mode == "Start":
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None
                self._stop_simulation()

        elif self.mode == "Goal":
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None
                self._stop_simulation()

    def _on_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            self.running = False

        elif event.key == pygame.K_0:
            self.mode = "Free"

        elif event.key == pygame.K_1:
            self.mode = "Obstacle"

        elif event.key == pygame.K_2:
            self.mode = "Erase"

        elif event.key == pygame.K_s:
            self.mode = "Start"

        elif event.key == pygame.K_g:
            self.mode = "Goal"

        elif event.key == pygame.K_c:
            self._clear_map()

        elif event.key == pygame.K_i:
            self._import_map()

        elif event.key == pygame.K_e:
            self._export_map()

        elif event.key == pygame.K_a:
            self._open_algo_dialog()

        elif event.key == pygame.K_SPACE:
            result = self._run_selected_algorithm()

            if result is not None:
                algo_elapsed, metrics = result

                try:
                    run_dir = save_run_results(
                        algorithm_name=self.selected_algorithm,
                        path=self.current_path or [],
                        metrics=metrics,
                        map_name=self.map_name,
                    )

                    print(f"[SAVE] Results saved → {run_dir}")

                except Exception as exc:
                    print(f"[SAVE] WARNING – could not save results: {exc}")

        elif event.key == pygame.K_r:
            self._reset_result()

        elif event.key == pygame.K_b:
            self._open_batch_test_dialog()

        elif event.key == pygame.K_p:
            self._open_settings_dialog()

    def _screen_to_grid(
        self, screen_pos: tuple[float, float]
    ) -> tuple[float, float] | None:
        sx, sy = screen_pos
        grid_w = self.grid_map.width * self.cell_size
        grid_h = self.grid_map.height * self.cell_size

        if (
            sx < self.grid_offset_x
            or sy < self.grid_offset_y
            or sx >= self.grid_offset_x + grid_w
            or sy >= self.grid_offset_y + grid_h
        ):
            return None

        grid_x = (sx - self.grid_offset_x) // self.cell_size
        grid_y = (sy - self.grid_offset_y) // self.cell_size

        return (grid_x, grid_y)

    def _bresenham_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> list[tuple[float, float]]:
        x0, y0 = start
        x1, y1 = end
        points = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        err = dx - dy

        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1

        x, y = x0, y0
        while True:
            points.append((x, y))
            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += step_x

            if e2 < dx:
                err += dx
                y += step_y

        return points

    def _apply_line(self, points: list[tuple[float, float]]) -> None:
        if self.mode == "Free":
            return

        changed = False
        for x, y in points:
            if self.mode == "Obstacle":
                changed = self.grid_map.set_obstacle(x, y, True) or changed

            elif self.mode == "Erase":
                changed = self.grid_map.set_obstacle(x, y, False) or changed

        if changed:
            self.current_path = None

    def _clear_map(self) -> None:
        self.grid_map.grid = [
            [GridMap.FREE for _ in range(self.grid_map.width)]
            for _ in range(self.grid_map.height)
        ]
        self.grid_map.rebuild_obstacle_set()
        self.grid_map.start = None
        self.grid_map.goal = None
        self.current_path = None
        self.map_name = "N/A"

        self._stop_simulation()
        print("[MAP] Map cleared")

    def _reset_result(self) -> None:
        self.current_path = None
        self._stop_simulation()
        print("[RUN] Result reset")

    def _import_map(self) -> None:
        path = self._ask_open_path()
        if not path:
            print("[IMPORT] Cancelled")
            return

        file_path = Path(path)
        if not file_path.exists():
            print(f"[IMPORT] ERROR - File not found: {path}")
            return

        try:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            loaded = self._dict_to_grid_map(data)
            if loaded is None:
                print("[IMPORT] ERROR - Invalid map data")
                return

            self.grid_map = loaded
            self.map_name = file_path.stem
            self.current_path = None
            self.all_paths = {}
            self._stop_simulation()
            self._recalc_layout()

            print(
                f"[IMPORT] SUCCESS - Map loaded: {self.grid_map.width}x{self.grid_map.height}"
            )

            if self.grid_map.start:
                print(f"[IMPORT] Start position: {self.grid_map.start}")
            if self.grid_map.goal:
                print(f"[IMPORT] Goal position: {self.grid_map.goal}")

            obstacle_count = self.grid_map.get_obstacle_count()
            total_cells = self.grid_map.width * self.grid_map.height
            obstacle_ratio = round(obstacle_count / total_cells * 100)
            print(
                f"[IMPORT] Obstacle count: {obstacle_count} / {total_cells} ({obstacle_ratio}%)"
            )

        except Exception as e:
            print(f"[IMPORT] ERROR - {str(e)}")

    def _export_map(self) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[EXPORT] ERROR - Start and goal positions must be set")
            return

        try:
            base_dir = Path("data/maps")
            base_dir.mkdir(parents=True, exist_ok=True)

            filename = self._ask_save_path(str(base_dir))
            if not filename:
                print("[EXPORT] Cancelled")
                return

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self._grid_map_to_dict(self.grid_map), f, indent=2)

            self.map_name = Path(filename).stem
            print(f"[EXPORT] SUCCESS - Map saved to: {filename}")
            print(f"[EXPORT] Map size: {self.grid_map.width}x{self.grid_map.height}")

        except Exception as e:
            print(f"[EXPORT] ERROR - {str(e)}")

    def _ask_open_path(self) -> str:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return filedialog.askopenfilename(
                parent=root,
                title="Import map JSON",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            )

        finally:
            root.destroy()

    def _ask_save_path(self, initial_dir: str = "") -> str:
        root = Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            return filedialog.asksaveasfilename(
                parent=root,
                title="Export map JSON",
                initialdir=initial_dir,
                defaultextension=".json",
                filetypes=(("JSON files", "*.json"), ("All files", "*.*")),
            )

        finally:
            root.destroy()

    def _dict_to_grid_map(self, data: dict) -> GridMap | None:
        if not isinstance(data, dict):
            return None

        if "width" not in data or "height" not in data or "grid" not in data:
            return None

        try:
            gm = GridMap(data["width"], data["height"])
            gm.grid = data["grid"]
            gm.rebuild_obstacle_set()
            gm.start = tuple(data["start"]) if data.get("start") else None
            gm.goal = tuple(data["goal"]) if data.get("goal") else None
            return gm

        except (TypeError, ValueError):
            return None

    def _grid_map_to_dict(self, grid_map: GridMap) -> dict:
        return {
            "width": grid_map.width,
            "height": grid_map.height,
            "grid": grid_map.grid,
            "start": grid_map.start,
            "goal": grid_map.goal,
        }

    def _open_algo_dialog(self) -> None:
        dialog = AlgorithmSelectDialog(
            self.tk_root,
            self.algorithm_names.index(self.selected_algorithm),
            self.algorithm_names,
        )

        self.tk_root.wait_window(dialog)
        if dialog.result is not None:
            self.selected_algorithm = self.algorithm_names[dialog.result]
            print(f"[MENU] Algorithm selected: {self.selected_algorithm}")

    def _run_selected_algorithm(self) -> tuple[float, dict] | None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[ALGORITHM] ERROR - Start and goal positions must be set")
            return

        run_start_time = self._now_str()

        if self.selected_algorithm != "All":
            self.all_paths = {}

        match self.selected_algorithm:
            case "RRT-Star":
                planner = RRTStar(self.grid_map)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "PRM":
                planner = PRM(self.grid_map)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "A-Star":
                planner = Astar(self.grid_map, min_clearance=0.0)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "HAPSO":
                planner = HAPSO(self.grid_map)

                algo_t0 = time.perf_counter()
                self.current_path = planner.plan()
                algo_elapsed = time.perf_counter() - algo_t0

                self._stop_simulation()

            case "All":
                self.all_paths = {}
                self.all_path_metrics = {}
                algo_start_times: dict[str, str] = {}
                algo_end_times: dict[str, str] = {}

                for name in self.algorithm_names:
                    if name == "All":
                        continue

                    if name == "RRT-Star":
                        planner = RRTStar(self.grid_map)

                    elif name == "PRM":
                        planner = PRM(self.grid_map)

                    elif name == "A-Star":
                        planner = Astar(self.grid_map, min_clearance=0.0)

                    elif name == "HAPSO":
                        planner = HAPSO(self.grid_map)

                    else:
                        self.all_paths[name] = []
                        continue

                    algo_start_times[name] = self._now_str()
                    algo_t_start = time.perf_counter()
                    path = planner.plan()
                    algo_elapsed = time.perf_counter() - algo_t_start
                    algo_end_times[name] = self._now_str()

                    self.all_paths[name] = path or []
                    self.all_path_metrics[name] = {
                        **compute_path_metrics(
                            path=path or [],
                            algorithm_name=name,
                            grid_map=self.grid_map,
                        )[name],
                        "Execution time": algo_elapsed,
                    }

                    try:
                        run_dir = save_run_results(
                            algorithm_name=name,
                            path=path or [],
                            metrics=self.all_path_metrics[name],
                            map_name=self.map_name,
                            start_time=algo_start_times[name],
                            end_time=algo_end_times[name],
                        )
                        print(f"[SAVE] {name} results saved → {run_dir}")

                    except Exception as exc:
                        print(f"[SAVE] WARNING – could not save {name} results: {exc}")

                self.current_path = None
                self._stop_simulation()

        run_end_time = self._now_str()

        if self.selected_algorithm == "All":
            print_all_path_metrics(
                self.all_path_metrics,
                self.all_paths,
                map_name=self.map_name,
                start_time=run_start_time,
                end_time=run_end_time,
                algo_start_times=algo_start_times,
                algo_end_times=algo_end_times,
            )
            return None

        metrics = compute_path_metrics(
            path=self.current_path or [],
            algorithm_name=self.selected_algorithm,
            grid_map=self.grid_map,
        )[self.selected_algorithm]
        metrics["Execution time"] = algo_elapsed

        print_path_metrics(
            {self.selected_algorithm: metrics},
            map_name=self.map_name,
            start_time=run_start_time,
            end_time=run_end_time,
            path=self.current_path,
        )

        return algo_elapsed, metrics

    def _open_batch_test_dialog(self) -> None:
        dialog = BatchTestDialog(self.tk_root)
        self.tk_root.wait_window(dialog)
        if dialog.result is not None:
            self._batch_test(dialog.result)

    def _batch_test(self, run_count: int = 10) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[BATCH] ERROR - Start and goal positions must be set")
            messagebox.showwarning("Batch Test", "Please set start and goal first.")
            return

        if self.selected_algorithm == "All":
            messagebox.showwarning(
                "Batch Test",
                "Please select a single algorithm before running batch test.",
            )
            return

        if run_count < 1:
            return

        batch_start_time = self._now_str()
        print_batch_header(
            self.selected_algorithm,
            self.map_name,
            batch_start_time,
            run_count,
        )

        successful_runs = 0
        total_time = 0.0
        path_lengths = []
        fitness_values = []
        run_records: list[dict] = []
        best_success_run = None
        best_failed_run = None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_algo = "".join(
            c if (c.isalnum() or c in " _") else "_" for c in self.selected_algorithm
        ).replace(" ", "_")
        batch_root = (
            Path(__file__).resolve().parent
            / "data"
            / "results"
            / "batch_tests"
            / f"{safe_algo}_{timestamp}_batch"
        )
        batch_root.mkdir(parents=True, exist_ok=True)

        output_dir = batch_root

        for run_idx in range(run_count):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested during batch test. Stopping.")
                    self.running = False
                    break

                elif ev.type == pygame.KEYDOWN:
                    try:
                        self._on_keydown(ev)

                    except Exception:
                        pass

            if not self.running:
                break

            print(f"[BATCH] ALGORITHM REPORT ({run_idx + 1}/{run_count})")

            run_start_time = self._now_str()
            result = self._run_selected_algorithm()
            run_end_time = self._now_str()

            if result is None:
                continue

            run_time, metrics = result

            total_time += run_time

            curr_path = list(self.current_path) if self.current_path else []

            is_success = metrics["Result"]

            if is_success:
                successful_runs += 1
                path_len = len(curr_path)
                path_lengths.append(path_len)

                fitness = metrics["TOTAL FITNESS"]

                if fitness is not None:
                    fitness_values.append(fitness)

                record = {
                    "Run_ID": run_idx + 1,
                    "Found_Path": bool(curr_path),
                    "Success": is_success,
                    "Path_Length": path_len,
                    "Total_Distance": metrics["Total distance"],
                    "Total_Waypoint": metrics["Total waypoint"],
                    "Total_Angle": metrics["Total angle"],
                    "Min_Angle": metrics["Min angle"],
                    "Max_Angle": metrics["Max angle"],
                    "Average_Angle": metrics["Average angle"],
                    "Min_Clearance": metrics["Min clearance"],
                    "TOTAL_FITNESS": fitness,
                    "Execution_Time_s": run_time,
                    "Path": json.dumps(curr_path),
                    "_start": run_start_time,
                    "_end": run_end_time,
                }

                if (
                    best_success_run is None
                    or fitness < best_success_run["TOTAL_FITNESS"]
                    or (
                        fitness == best_success_run["TOTAL_FITNESS"]
                        and path_len < best_success_run["Path_Length"]
                    )
                    or (
                        fitness == best_success_run["TOTAL_FITNESS"]
                        and path_len == best_success_run["Path_Length"]
                        and run_time < best_success_run["Execution_Time_s"]
                    )
                ):
                    best_success_run = {
                        **record,
                        "path": curr_path,
                    }

            else:
                record = {
                    "Run_ID": run_idx + 1,
                    "Found_Path": bool(curr_path),
                    "Success": False,
                    "Path_Length": len(curr_path),
                    "Total_Distance": metrics["Total distance"],
                    "Total_Waypoint": metrics["Total waypoint"],
                    "Total_Angle": metrics["Total angle"],
                    "Min_Angle": metrics["Min angle"],
                    "Max_Angle": metrics["Max angle"],
                    "Average_Angle": metrics["Average angle"],
                    "Min_Clearance": metrics["Min clearance"],
                    "TOTAL_FITNESS": metrics["TOTAL FITNESS"],
                    "Execution_Time_s": run_time,
                    "Path": json.dumps(curr_path),
                    "_start": run_start_time,
                    "_end": run_end_time,
                }

                if curr_path:
                    curr_clearance = metrics["Min clearance"] or 0

                    if (
                        best_failed_run is None
                        or curr_clearance > (best_failed_run["Min_Clearance"] or 0)
                        or (
                            curr_clearance == (best_failed_run["Min_Clearance"] or 0)
                            and len(curr_path) < best_failed_run["Path_Length"]
                        )
                    ):
                        best_failed_run = {
                            **record,
                            "path": curr_path,
                        }

            run_records.append(record)

            try:
                run_dir = save_run_results(
                    algorithm_name=self.selected_algorithm,
                    path=curr_path,
                    metrics=metrics,
                    map_name=self.map_name,
                    start_time=run_start_time,
                    end_time=run_end_time,
                    base_dir=str(batch_root / f"run_{run_idx + 1:03d}"),
                )
                print(f"[SAVE] Run {run_idx + 1} saved → {run_dir}")

            except Exception as exc:
                print(f"[SAVE] WARNING – run {run_idx + 1} save failed: {exc}")

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested after run. Stopping.")
                    self.running = False
                    break

                elif ev.type == pygame.KEYDOWN:
                    try:
                        self._on_keydown(ev)

                    except Exception:
                        pass

            if not self.running:
                break

        best_run = best_success_run if best_success_run is not None else best_failed_run

        avg_len = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0

        actual_runs = len(run_records)
        avg_time = total_time / actual_runs if actual_runs > 0 else 0.0

        avg_fitness = (
            sum(fitness_values) / len(fitness_values) if fitness_values else 0.0
        )

        self.current_path = list(best_run["path"]) if best_run else None

        wb = Workbook()
        ws_results = wb.active
        ws_results.title = "Results"

        result_cols = [
            "Run_ID",
            "Success",
            "Path_Length",
            "Total_Distance",
            "Total_Waypoint",
            "Total_Angle",
            "Min_Angle",
            "Max_Angle",
            "Average_Angle",
            "Min_Clearance",
            "TOTAL_FITNESS",
            "Execution_Time_s",
            "Path",
        ]
        ws_results.append(result_cols)
        for rec in run_records:
            ws_results.append([rec.get(col) for col in result_cols])

        ws_summary = wb.create_sheet("Summary")
        ws_summary.append(["Metric", "Value"])
        for row in [
            ("Algorithm", self.selected_algorithm),
            ("Total runs", run_count),
            ("Successful runs", successful_runs),
            ("Success rate", successful_runs / run_count if run_count else 0.0),
            ("Average path length", avg_len),
            ("Average fitness", avg_fitness),
            ("Average time (s)", avg_time),
            ("Total time (s)", total_time),
            ("Best run", best_run["Run_ID"] if best_run else "N/A"),
            ("Best fitness", best_run["TOTAL_FITNESS"] if best_run else "N/A"),
            ("Best path length", best_run["Path_Length"] if best_run else "N/A"),
        ]:
            ws_summary.append(list(row))

        algo_safe = "".join(
            c if (c.isalnum() or c in " _") else "_" for c in self.selected_algorithm
        ).replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = output_dir / f"{timestamp}_{algo_safe}.xlsx"
        wb.save(out_file)

        batch_end_time = self._now_str()

        print_batch_summary_report(
            algo_name=self.selected_algorithm,
            map_name=self.map_name,
            batch_start_time=batch_start_time,
            batch_end_time=batch_end_time,
            run_count=run_count,
            successful_runs=successful_runs,
            total_time=total_time,
            excel_path=str(out_file),
            best_run=best_run,
            run_records=run_records,
        )

        if successful_runs > 0:
            msg = (
                f"Runs: {run_count}\n"
                f"Success: {successful_runs}/{run_count}\n"
                f"Avg path length: {avg_len:.2f}\n"
                f"Avg fitness: {avg_fitness:.4f}\n"
                f"Avg time: {avg_time:.4f} s\n"
                f"Best run: {best_run['Run_ID']}\n"
                f"Excel: {out_file}"
            )
        else:
            msg = (
                f"Runs: {run_count}\n"
                f"Success: 0/{run_count}\n"
                f"No successful path was found.\n"
                f"Displaying the best failed path.\n"
                f"Best run: {best_run['Run_ID'] if best_run else 'N/A'}\n"
                f"Excel: {out_file}"
            )

        messagebox.showinfo("Batch Test", msg)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self.running = False

            elif ev.type == pygame.KEYDOWN:
                try:
                    self._on_keydown(ev)

                except Exception:
                    pass

    def _stop_simulation(self) -> None:
        return

    def _open_settings_dialog(self) -> None:
        dialog = SettingsDialog(
            self.tk_root, GRID_MAP_WIDTH, GRID_MAP_HEIGHT, GRID_CELL_SIZE
        )

        self.tk_root.wait_window(dialog)
        if dialog.result:
            width, height, cell_size = dialog.result
            self._resize_grid(width, height, cell_size)

    def _recalc_layout(self) -> None:
        map_w = self.grid_map.width * self.cell_size
        map_h = self.grid_map.height * self.cell_size

        avail_w = WINDOW_WIDTH - NAV_WIDTH
        avail_h = WINDOW_HEIGHT - MODE_HEIGHT

        axis_label_w, axis_label_h = self._axis_label_margins()
        gap = 8

        content_w = map_w + axis_label_w + gap
        content_h = map_h + axis_label_h + gap

        origin_x = NAV_WIDTH + max(0, (avail_w - content_w) // 2)
        origin_y = MODE_HEIGHT + max(0, (avail_h - content_h) // 2)

        self.grid_offset_x = origin_x + axis_label_w + gap
        self.grid_offset_y = origin_y + axis_label_h + gap

    def _resize_grid(self, width: int, height: int, cell_size: int) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid_map.resize(width=self.width, height=self.height)
        self.current_path = None
        self.all_paths = {}
        self._stop_simulation()
        self._recalc_layout()

    def _draw_ui(self) -> None:
        self.screen.fill(WHITE)
        self._draw_nav_panel()
        self._draw_status_bar()
        self._draw_grid()
        pygame.display.flip()

    def _draw_nav_panel(self) -> None:
        pygame.draw.rect(self.screen, WHITE, (0, 0, NAV_WIDTH, NAV_HEIGHT))
        pygame.draw.line(self.screen, BLACK, (NAV_WIDTH, 0), (NAV_WIDTH, NAV_HEIGHT), 2)

        Text(
            self.screen, NAV_OFFSET_X, NAV_OFFSET_Y, BLACK, "MENU", size=LARGE_TEXT_SIZE
        ).draw_text()

        y = NAV_OFFSET_Y + 40
        for item in NAV_MENU:
            Text(self.screen, NAV_OFFSET_X, y, BLACK, item).draw_text()
            y += 30

    def _draw_status_bar(self) -> None:
        Text(
            self.screen,
            MODE_OFFSET_X,
            MODE_OFFSET_Y,
            BLACK,
            f"Mode: {self.mode} | Alg: {self.selected_algorithm}",
        ).draw_text()
        pygame.draw.line(
            self.screen,
            BLACK,
            (NAV_WIDTH, MODE_HEIGHT),
            (WINDOW_WIDTH, MODE_HEIGHT),
            2,
        )

        try:
            legend_items = [
                (name, self.algorithm_colors[name])
                for name in self.algorithm_names
                if name in self.algorithm_colors
            ]
            if not legend_items:
                return

            pad = 4
            lgd_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)
            box_sz = SMALL_TEXT_SIZE - 4

            total_w = pad
            for name, _ in legend_items:
                total_w += box_sz + 4 + lgd_font.size(name)[0] + pad

            lgd_h = box_sz + pad * 2
            lgd_top = (MODE_HEIGHT - lgd_h) // 2
            lgd_left = WINDOW_WIDTH - total_w - 10

            surf = pygame.Surface((total_w, lgd_h), pygame.SRCALPHA)
            surf.fill((255, 255, 255, 180))
            self.screen.blit(surf, (lgd_left, lgd_top))

            cx = lgd_left + pad
            cy = lgd_top + pad
            for name, color in legend_items:
                pygame.draw.rect(self.screen, color, (cx, cy, box_sz, box_sz))
                label = lgd_font.render(name, True, BLACK)
                self.screen.blit(label, (cx + box_sz + 4, cy))
                cx += box_sz + 4 + lgd_font.size(name)[0] + pad

        except Exception:
            pass

    def _draw_grid(self) -> None:
        for row in range(self.grid_map.height):
            for col in range(self.grid_map.width):
                rect = (
                    self.grid_offset_x + col * self.cell_size,
                    self.grid_offset_y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                val = self.grid_map.grid[row][col]

                if val == GridMap.OBSTACLE:
                    pygame.draw.rect(self.screen, BLACK, rect)

                elif val == GridMap.START:
                    pygame.draw.rect(self.screen, GREEN, rect)

                elif val == GridMap.GOAL:
                    pygame.draw.rect(self.screen, RED, rect)

                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

                pygame.draw.rect(self.screen, LIGHT, rect, 1)

        if self.selected_algorithm == "All" and self.all_paths:
            for name, pts in self.all_paths.items():
                if not pts or len(pts) <= 1:
                    continue

                color = self.algorithm_colors.get(name, BLUE)
                self._draw_path_lines(pts, color)

        else:
            pts = self.current_path or []
            if pts and len(pts) > 1:
                self._draw_path_lines(pts, BLUE)

            # self._draw_path_nodes(pts, BLUE)

        if (
            self.is_dragging
            and self.drag_start is not None
            and self.drag_end is not None
        ):
            for x, y in self._bresenham_line(self.drag_start, self.drag_end):
                pygame.draw.rect(
                    self.screen,
                    MEDIUM,
                    (
                        self.grid_offset_x + x * self.cell_size,
                        self.grid_offset_y + y * self.cell_size,
                        self.cell_size,
                        self.cell_size,
                    ),
                    2,
                )

        self._draw_axes()

    def _draw_path_lines(
        self,
        pts: list[tuple[float, float]],
        color: tuple[int, int, int],
    ) -> None:
        for i in range(len(pts) - 1):
            sx = self.grid_offset_x + pts[i][0] * self.cell_size + self.cell_size // 2
            sy = self.grid_offset_y + pts[i][1] * self.cell_size + self.cell_size // 2
            ex = (
                self.grid_offset_x
                + pts[i + 1][0] * self.cell_size
                + self.cell_size // 2
            )
            ey = (
                self.grid_offset_y
                + pts[i + 1][1] * self.cell_size
                + self.cell_size // 2
            )

            pygame.draw.line(self.screen, color, (sx, sy), (ex, ey), 2)

    def _draw_path_nodes(
        self,
        pts: list[tuple[float, float]],
        color: tuple[int, int, int],
    ) -> None:
        r = max(3, self.cell_size // 6)

        for x, y in pts:
            cx = self.grid_offset_x + x * self.cell_size + self.cell_size // 2
            cy = self.grid_offset_y + y * self.cell_size + self.cell_size // 2
            pygame.draw.circle(self.screen, color, (cx, cy), r)
            pygame.draw.circle(self.screen, WHITE, (cx, cy), max(1, r - 2))

    def _draw_axes(self) -> None:
        map_w = self.grid_map.width * self.cell_size
        map_h = self.grid_map.height * self.cell_size
        axis_label_w, _ = self._axis_label_margins()
        tick_len = 6
        label_gap = 6
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        gx = self.grid_offset_x
        gy = self.grid_offset_y
        gr = gx + map_w
        gb = gy + map_h

        pygame.draw.line(self.screen, BLACK, (gx, gy), (gx, gb), 2)
        pygame.draw.line(self.screen, BLACK, (gx, gy), (gr, gy), 2)

        max_x_tick = self.grid_map.width - (self.grid_map.width % 5)
        for coord in range(0, max_x_tick + 1, 5):
            tick_x = gx + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (tick_x, gy - tick_len),
                (tick_x, gy),
                1,
            )
            lbl = label_font.render(str(coord), True, BLACK)
            self.screen.blit(
                lbl,
                (
                    tick_x - lbl.get_width() // 2,
                    gy - tick_len - label_gap - lbl.get_height(),
                ),
            )

        max_y_tick = self.grid_map.height - (self.grid_map.height % 5)
        for coord in range(0, max_y_tick + 1, 5):
            tick_y = gy + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (gx - tick_len, tick_y),
                (gx, tick_y),
                1,
            )
            lbl = label_font.render(str(coord), True, BLACK)
            self.screen.blit(
                lbl,
                (
                    gx - axis_label_w + tick_len + label_gap - 10,
                    tick_y - lbl.get_height() // 2,
                ),
            )

    def _axis_label_margins(self) -> tuple[float, float]:
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        max_x_label = self.grid_map.width - (self.grid_map.width % 5)
        max_y_label = self.grid_map.height - (self.grid_map.height % 5)
        max_lbl_w = max(
            label_font.size(str(max_x_label))[0],
            label_font.size(str(max_y_label))[0],
        )

        tick_len = 6
        label_gap = 6
        margin_w = max_lbl_w + tick_len + label_gap + 2
        margin_h = label_font.get_height() + tick_len + label_gap

        return margin_w, margin_h


if __name__ == "__main__":
    app = App()
    app.run()
