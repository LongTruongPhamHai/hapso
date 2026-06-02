from astar import Astar
from config.colors import (
    BLACK,
    DARK,
    DARKEST,
    DARKER,
    DARK,
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
from config.parameter import (
    GRID_MAP_HEIGHT,
    GRID_MAP_WIDTH,
    MIN_CLEARANCE,
    PSO_COLLISION_PENALTY,
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
from datetime import datetime
from grid_map import GridMap
from hapso import HAPSO
from openpyxl import Workbook
from pathlib import Path
from tkinter import filedialog, messagebox, Tk
from utils import calculator_path_metrics, print_path_metrics

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
        self.selected_algorithm_index_var = tk.IntVar(value=current_idx)

        for index, name in enumerate(options):
            tk.Radiobutton(
                self,
                text=name,
                variable=self.selected_algorithm_index_var,
                value=index,
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

        self.center_window()

    def on_select(self) -> None:
        self.result = self.selected_algorithm_index_var.get()
        self.destroy()

    def center_window(self) -> None:
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


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

        self.center_window()

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

    def center_window(self) -> None:
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


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

        self.center_window()

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

    def center_window(self) -> None:
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


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

        self.grid_map = GridMap(
            width=self.width,
            height=self.height,
        )
        self.min_clearance = MIN_CLEARANCE
        self.collision_penalty = PSO_COLLISION_PENALTY

        self.running = True

        self.mode = "Free"
        self.selected_algorithm = "A-Star"

        self.is_dragging = False
        self.start_point: tuple[float, float] | None = None
        self.end_point: tuple[float, float] | None = None
        self.current_path: list[tuple[float, float]] | None = None

        self.algorithm_names = [
            "RRT",
            "RRT-Star",
            "PRM",
            "Dijkstra",
            "A-Star",
            "HAPSO",
            "All",
        ]

        colors_for_algos = [BLUE, ORANGE, GREEN, VIOLET, INDIGO, YELLOW, RED]
        self.algorithm_colors: dict[str, tuple[int, int, int]] = {}
        color_idx = 0
        for name in self.algorithm_names:
            if name == "All":
                continue
            self.algorithm_colors[name] = colors_for_algos[
                color_idx % len(colors_for_algos)
            ]
            color_idx += 1

        self.all_paths: dict[str, list[tuple[float, float]]] = {}

        self.recalc_layout()

        print(
            f"[INIT] Grid initialized: {self.width}x{self.height} (cell size: {self.cell_size}px)"
        )
        print(f"[INIT] Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"[INIT] Ready. Press [?] or check menu for commands.\n")

    def run(self) -> None:
        while self.running:
            self.handle_events()

            self.draw_ui()

            self.clock.tick(60)

        print("\n[EXIT] Shutting down application...")
        pygame.quit()
        self.tk_root.destroy()
        print("[EXIT] Application closed.")

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        if not self.is_dragging:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        self.end_point = grid_pos

    def screen_to_grid(self, pos: tuple[float, float]) -> tuple[float, float] | None:
        x, y = pos
        grid_width = self.grid_map.width * self.cell_size
        grid_height = self.grid_map.height * self.cell_size

        if (
            x < self.grid_offset_x
            or y < self.grid_offset_y
            or x >= self.grid_offset_x + grid_width
            or y >= self.grid_offset_y + grid_height
        ):
            return None

        grid_x = (x - self.grid_offset_x) // self.cell_size
        grid_y = (y - self.grid_offset_y) // self.cell_size

        return (grid_x, grid_y)

    def handle_mouse_up(self, event: pygame.event.Event) -> None:
        if event.button != 1:
            return

        if (
            self.is_dragging
            and self.start_point is not None
            and self.end_point is not None
        ):
            points = self.bresenham_line(self.start_point, self.end_point)
            self.apply_line(points)

        self.is_dragging = False
        self.start_point = None
        self.end_point = None

    def bresenham_line(
        self,
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> list[tuple[float, float]]:
        x_start, y_start = start
        x_end, y_end = end
        points = []

        delta_x = abs(x_end - x_start)
        delta_y = abs(y_end - y_start)
        err = delta_x - delta_y

        step_x = 1 if x_start < x_end else -1
        step_y = 1 if y_start < y_end else -1

        x, y = x_start, y_start
        while True:
            points.append((x, y))

            if x == x_end and y == y_end:
                break

            e2 = 2 * err
            if e2 > -delta_y:
                err -= delta_y
                x += step_x

            if e2 < delta_x:
                err += delta_x
                y += step_y

        return points

    def apply_line(self, points: list[tuple[float, float]]) -> None:
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

    def handle_mouse_down(self, event: pygame.event.Event) -> None:
        if event.button != 1:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        if self.mode == "Free":
            pass

        elif self.mode in ("Obstacle", "Erase"):
            self.is_dragging = True
            self.start_point = grid_pos
            self.end_point = grid_pos

        elif self.mode == "Start":
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None
                self.stop_simulation()

        elif self.mode == "Goal":
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None
                self.stop_simulation()

    def handle_keydown(self, event: pygame.event.Event) -> None:
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
            self.clear_map()

        elif event.key == pygame.K_i:
            self.import_map()

        elif event.key == pygame.K_e:
            self.export_map()

        elif event.key == pygame.K_a:
            self.open_algo_dialog()

        elif event.key == pygame.K_SPACE:
            self.run_selected_algorithm()

        elif event.key == pygame.K_r:
            self.reset_result()

        elif event.key == pygame.K_b:
            self.open_batch_test_dialog()

        elif event.key == pygame.K_p:
            self.open_settings_dialog()

    def clear_map(self) -> None:
        self.grid_map.grid = [
            [GridMap.FREE for _ in range(self.grid_map.width)]
            for _ in range(self.grid_map.height)
        ]
        self.grid_map.rebuild_obstacle_set()
        self.grid_map.start = None
        self.grid_map.goal = None
        self.current_path = None
        self.stop_simulation()
        print("[MAP] Map cleared")

    def reset_result(self) -> None:
        self.current_path = None
        self.stop_simulation()
        print("[RUN] Result reset")

    def import_map(self) -> None:
        path = self.ask_open_path()
        if not path:
            print("[IMPORT] Cancelled")
            return

        file_path = Path(path)
        if not file_path.exists():
            print(f"[IMPORT] ERROR - File not found: {path}")
            return

        try:
            with file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)

            loaded = self.grid_map_from_dict(data)
            if loaded is None:
                print("[IMPORT] ERROR - Invalid map data")
                return

            self.grid_map = loaded
            self.current_path = None
            self.all_paths = {}
            self.stop_simulation()
            self.recalc_layout()

            print(
                f"[IMPORT] SUCCESS - Map loaded: {self.grid_map.width}x{self.grid_map.height}"
            )

            if self.grid_map.start:
                print(f"[IMPORT] Start position: {self.grid_map.start}")
            if self.grid_map.goal:
                print(f"[IMPORT] Goal position: {self.grid_map.goal}")

        except Exception as e:
            print(f"[IMPORT] ERROR - {str(e)}")

    def ask_open_path(self) -> str:
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

    def grid_map_from_dict(self, data: dict) -> GridMap | None:
        if not isinstance(data, dict):
            return None

        if "width" not in data or "height" not in data or "grid" not in data:
            return None

        try:
            grid_map = GridMap(data["width"], data["height"])
            grid_map.grid = data["grid"]
            grid_map.rebuild_obstacle_set()
            grid_map.start = tuple(data["start"]) if data.get("start") else None
            grid_map.goal = tuple(data["goal"]) if data.get("goal") else None

            return grid_map

        except (TypeError, ValueError):
            return None

    def export_map(self) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[EXPORT] ERROR - Start and goal positions must be set")
            return

        try:
            base_dir = Path("data/maps")
            base_dir.mkdir(parents=True, exist_ok=True)

            filename = self.ask_save_path(str(base_dir))
            if not filename:
                print("[EXPORT] Cancelled")
                return

            with open(filename, "w", encoding="utf-8") as file:
                json.dump(self.grid_map_to_dict(self.grid_map), file, indent=2)

            print(f"[EXPORT] SUCCESS - Map saved to: {filename}")
            print(f"[EXPORT] Map size: {self.grid_map.width}x{self.grid_map.height}")

        except Exception as e:
            print(f"[EXPORT] ERROR - {str(e)}")

    def ask_save_path(self, initial_dir: str = "") -> str:
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

    def grid_map_to_dict(self, grid_map: GridMap) -> dict:
        return {
            "width": grid_map.width,
            "height": grid_map.height,
            "grid": grid_map.grid,
            "start": grid_map.start,
            "goal": grid_map.goal,
        }

    def open_algo_dialog(self) -> None:
        dialog = AlgorithmSelectDialog(
            self.tk_root,
            self.algorithm_names.index(self.selected_algorithm),
            self.algorithm_names,
        )

        self.tk_root.wait_window(dialog)
        if dialog.result is not None:
            self.selected_algorithm = self.algorithm_names[dialog.result]
            print(f"[MENU] Algorithm selected: {self.selected_algorithm}")

    def run_selected_algorithm(self) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[ALGORITHM] ERROR - Start and goal positions must be set")
            return

        print("-" * 120)
        print(f"[ALGORITHM] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[ALGORITHM] Running: {self.selected_algorithm}")
        print(f"[ALGORITHM] Start: {self.grid_map.start}, Goal: {self.grid_map.goal}")

        start_time = time.perf_counter()

        if self.selected_algorithm != "All":
            self.all_paths = {}

        match self.selected_algorithm:
            case "A-Star":
                planner = Astar(self.grid_map)
                self.current_path = planner.plan()
                self.stop_simulation()

            case "HAPSO":
                planner = HAPSO(self.grid_map)
                self.current_path = planner.plan()
                self.stop_simulation()

            case "All":
                self.all_paths = {}
                self.all_path_metrics = {}
                for name in self.algorithm_names:
                    if name == "All":
                        continue

                    print(f"[ALGORITHM:All] Running: {name}")

                    if name == "A-Star":
                        planner = Astar(self.grid_map)
                        algo_start_time = time.perf_counter()
                        path = planner.plan()
                    elif name == "HAPSO":
                        planner = HAPSO(self.grid_map)
                        algo_start_time = time.perf_counter()
                        path = planner.plan()
                    else:
                        path = None
                        algo_start_time = time.perf_counter()

                    algo_elapsed_time = time.perf_counter() - algo_start_time

                    self.all_paths[name] = path or []
                    if not hasattr(self, "all_path_metrics"):
                        self.all_path_metrics = {}
                    self.all_path_metrics[name] = {
                        **calculator_path_metrics(
                            path or [],
                            name,
                            self.grid_map,
                            self.min_clearance,
                            self.collision_penalty,
                        )[name],
                        "Execution time": algo_elapsed_time,
                    }

                self.current_path = None
                self.stop_simulation()

        elapsed_time = time.perf_counter() - start_time
        if self.selected_algorithm == "All":
            print_path_metrics(self.all_path_metrics)
            print("[ALGORITHM:All] Completed all planners")

        else:
            if self.current_path:
                print(
                    f"[ALGORITHM] SUCCESS | Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )

                print(f"[ALGORITHM] PATH: {self.current_path}")

                path_metrics = calculator_path_metrics(
                    self.current_path,
                    self.selected_algorithm,
                    self.grid_map,
                    self.min_clearance,
                    self.collision_penalty,
                )[self.selected_algorithm]
                path_metrics["Execution time"] = elapsed_time

                print_path_metrics({self.selected_algorithm: path_metrics})

            else:
                print(
                    f"[ALGORITHM] FAILED - No path found | Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print(f"[ALGORITHM] Execution time: {elapsed_time:.4f}s")

    def start_simulation(self, trace: list[tuple]) -> None:
        return

    def stop_simulation(self) -> None:
        return

    def update_simulation(self) -> None:
        return

    def open_batch_test_dialog(self) -> None:
        dialog = BatchTestDialog(self.tk_root)
        self.tk_root.wait_window(dialog)

        if dialog.result is not None:
            self.batch_test(dialog.result)

    def batch_test(self, run_count: int = 10) -> None:
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

        print(f"\n{'='*60}")
        print(f"[BATCH] Starting batch test: {run_count} runs")
        print(f"[BATCH] Algorithm: {self.selected_algorithm}")
        print(f"{'='*60}")

        successful_runs = 0
        total_time = 0.0
        path_lengths = []
        fitness_values = []
        run_records: list[dict[str, object]] = []
        best_run: dict[str, object] | None = None
        output_dir = Path(__file__).resolve().parent / "data" / "result_batch_test"
        output_dir.mkdir(parents=True, exist_ok=True)

        for i in range(run_count):
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested during batch test. Stopping.")
                    self.running = False
                    break
                elif ev.type == pygame.KEYDOWN:
                    try:
                        self.handle_keydown(ev)
                    except Exception:
                        pass
            if not self.running:
                break

            print(f"[BATCH] Run {i+1}/{run_count}...", end=" ", flush=True)
            start_time = time.perf_counter()
            self.run_selected_algorithm()
            run_time = time.perf_counter() - start_time
            total_time += run_time

            current_path = list(self.current_path) if self.current_path else []
            is_success = bool(current_path) and current_path[-1] == self.grid_map.goal

            if is_success:
                successful_runs += 1
                path_length = len(current_path)
                path_lengths.append(path_length)

                path_metrics = calculator_path_metrics(
                    current_path,
                    self.selected_algorithm,
                    self.grid_map,
                    self.min_clearance,
                    self.collision_penalty,
                )[self.selected_algorithm]
                fitness = path_metrics["TOTAL FITNESS"]
                fitness_values.append(fitness)

                run_record = {
                    "Run_ID": i + 1,
                    "Success": True,
                    "Path_Length": path_length,
                    "Total_Distance": path_metrics["Total distance"],
                    "Total_Waypoint": path_metrics["Total waypoint"],
                    "Total_Angle": path_metrics["Total angle"],
                    "Min_Angle": path_metrics["Min angle"],
                    "Max_Angle": path_metrics["Max angle"],
                    "Average_Angle": path_metrics["Average angle"],
                    "Min_Clearance": path_metrics["Min clearance"],
                    "TOTAL_FITNESS": fitness,
                    "Execution_Time_s": run_time,
                    "Path": json.dumps(current_path),
                }

                if (
                    best_run is None
                    or fitness < best_run["TOTAL_FITNESS"]
                    or (
                        fitness == best_run["TOTAL_FITNESS"]
                        and path_length < best_run["Path_Length"]
                    )
                ):
                    best_run = {**run_record, "path": current_path}

            else:
                run_record = {
                    "Run_ID": i + 1,
                    "Success": False,
                    "Path_Length": 0,
                    "Total_Distance": None,
                    "Total_Waypoint": None,
                    "Total_Angle": None,
                    "Min_Angle": None,
                    "Max_Angle": None,
                    "Average_Angle": None,
                    "Min_Clearance": None,
                    "TOTAL_FITNESS": None,
                    "Execution_Time": run_time,
                    "Path": "",
                }
                print(f"No valid path found ({run_time:.4f}s)")

            run_records.append(run_record)

            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    print("[BATCH] Quit requested after run. Stopping.")
                    self.running = False
                    break
                elif ev.type == pygame.KEYDOWN:
                    try:
                        self.handle_keydown(ev)
                    except Exception:
                        pass
            if not self.running:
                break

        avg_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
        avg_time = total_time / run_count if run_count else 0.0
        avg_fitness = (
            sum(fitness_values) / len(fitness_values) if fitness_values else 0.0
        )

        if best_run is not None:
            self.current_path = list(best_run["path"])
        else:
            self.current_path = None

        workbook = Workbook()
        results_sheet = workbook.active
        results_sheet.title = "Results"

        results_headers = [
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
            "Execution_Time",
            "Path",
        ]

        results_sheet.append(results_headers)
        for record in run_records:
            results_sheet.append([record.get(column) for column in results_headers])

        summary_sheet = workbook.create_sheet("Summary")
        summary_rows = [
            ("Algorithm", self.selected_algorithm),
            ("Total runs", run_count),
            ("Successful runs", successful_runs),
            ("Success rate", successful_runs / run_count if run_count else 0.0),
            ("Average path length", avg_length),
            ("Average fitness", avg_fitness),
            ("Average time (s)", avg_time),
            ("Total time (s)", total_time),
            (
                "Best run",
                best_run["Run_ID"] if best_run is not None else "N/A",
            ),
            (
                "Best fitness",
                best_run["TOTAL_FITNESS"] if best_run is not None else "N/A",
            ),
            (
                "Best path length",
                best_run["Path_Length"] if best_run is not None else "N/A",
            ),
        ]
        summary_sheet.append(["Metric", "Value"])
        for metric_name, metric_value in summary_rows:
            summary_sheet.append([metric_name, metric_value])

        algo_safe = "".join(
            [
                c if (c.isalnum() or c in (" ", "_")) else "_"
                for c in self.selected_algorithm
            ]
        ).replace(" ", "_")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"{timestamp}_{algo_safe}.xlsx"
        workbook.save(output_file)

        print(f"{'='*60}")
        print(f"[BATCH] Results:")
        print(f"[BATCH]   Total runs: {run_count}")
        print(f"[BATCH]   Successful: {successful_runs}/{run_count}")
        print(f"[BATCH]   Success rate: {successful_runs/run_count*100:.1f}%")
        print(f"[BATCH]   Avg path length: {avg_length:.2f} waypoints")
        print(f"[BATCH]   Avg fitness: {avg_fitness:.4f}")
        print(f"[BATCH]   Avg time: {avg_time:.4f}s")
        print(f"[BATCH]   Total time: {total_time:.4f}s")
        print(f"[BATCH]   Excel: {output_file}")
        if best_run is not None:
            print(
                f"[BATCH]   Best run: {best_run['Run_ID']} | Fitness = {best_run['TOTAL_FITNESS']:.4f}"
            )
        print(f"{'='*60}\n")

        if best_run is not None:
            message_text = (
                f"Runs: {run_count}\n"
                f"Success: {successful_runs}/{run_count}\n"
                f"Avg path length: {avg_length:.2f}\n"
                f"Avg fitness: {avg_fitness:.4f}\n"
                f"Avg time: {avg_time:.4f} s\n"
                f"Best run: {best_run['Run_ID']}\n"
                f"Excel: {output_file}"
            )
        else:
            message_text = (
                f"Runs: {run_count}\n"
                f"No valid path was found.\n"
                f"Excel: {output_file}"
            )

        messagebox.showinfo("Batch Test", message_text)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                print("[BATCH] Quit requested after dialog. Exiting.")
                self.running = False
            elif ev.type == pygame.KEYDOWN:
                try:
                    self.handle_keydown(ev)
                except Exception:
                    pass

    def open_settings_dialog(self) -> None:
        dialog = SettingsDialog(
            self.tk_root,
            GRID_MAP_WIDTH,
            GRID_MAP_HEIGHT,
            GRID_CELL_SIZE,
        )

        self.tk_root.wait_window(dialog)
        if dialog.result:
            width, height, cell_size = dialog.result
            self.resize_grid(width, height, cell_size)

    def recalc_layout(self) -> None:
        map_width = self.grid_map.width * self.cell_size
        map_height = self.grid_map.height * self.cell_size

        available_width = WINDOW_WIDTH - NAV_WIDTH
        available_height = WINDOW_HEIGHT - MODE_HEIGHT

        y_axis_label_width, x_axis_label_height = self._get_coordinate_axis_margins()
        axis_gap = 8

        total_content_width = map_width + y_axis_label_width + axis_gap
        total_content_height = map_height + x_axis_label_height + axis_gap

        start_x = NAV_WIDTH + max(0, (available_width - total_content_width) // 2)
        start_y = MODE_HEIGHT + max(0, (available_height - total_content_height) // 2)

        self.grid_offset_x = start_x + y_axis_label_width + axis_gap
        self.grid_offset_y = start_y + x_axis_label_height + axis_gap

    def resize_grid(self, width: int, height: int, cell_size: int) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.grid_map.resize(width=self.width, height=self.height)
        self.current_path = None
        self.all_paths = {}
        self.stop_simulation()

        self.recalc_layout()

    def draw_ui(self) -> None:
        self.screen.fill(WHITE)

        self.draw_nav_side()
        self.draw_status_bar()
        self.draw_grid_map()

        pygame.display.flip()

    def draw_nav_side(self) -> None:
        nav_side = (0, 0, NAV_WIDTH, NAV_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, nav_side)
        pygame.draw.line(self.screen, BLACK, (NAV_WIDTH, 0), (NAV_WIDTH, NAV_HEIGHT), 2)

        nav_title = Text(
            self.screen, NAV_OFFSET_X, NAV_OFFSET_Y, BLACK, "MENU", size=LARGE_TEXT_SIZE
        )
        nav_title.draw_text()

        nav_menu = NAV_MENU
        y_offset = NAV_OFFSET_Y + 40
        for menu in nav_menu:
            text = Text(self.screen, NAV_OFFSET_X, y_offset, BLACK, menu)
            text.draw_text()

            y_offset += 30

    def draw_status_bar(self) -> None:
        mode_text = Text(
            self.screen,
            MODE_OFFSET_X,
            MODE_OFFSET_Y,
            BLACK,
            f"Mode: {self.mode} | Alg: {self.selected_algorithm}",
        )
        mode_text.draw_text()
        pygame.draw.line(
            self.screen, BLACK, (NAV_WIDTH, MODE_HEIGHT), (WINDOW_WIDTH, MODE_HEIGHT), 2
        )

        try:
            legend_items = [
                (name, self.algorithm_colors[name])
                for name in self.algorithm_names
                if name in self.algorithm_colors
            ]

            if legend_items:
                padding = 4
                legend_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)
                box_size = SMALL_TEXT_SIZE - 4
                item_h = SMALL_TEXT_SIZE

                total_w = padding
                for name, _ in legend_items:
                    total_w += box_size + 4 + legend_font.size(name)[0] + padding

                legend_h = box_size + padding * 2
                legend_top = (MODE_HEIGHT - legend_h) // 2
                legend_left = WINDOW_WIDTH - total_w - 10

                legend_surf = pygame.Surface((total_w, legend_h), pygame.SRCALPHA)
                legend_surf.fill((255, 255, 255, 180))
                self.screen.blit(legend_surf, (legend_left, legend_top))

                x_cursor = legend_left + padding
                y_item = legend_top + padding
                for name, color in legend_items:
                    pygame.draw.rect(
                        self.screen, color, (x_cursor, y_item, box_size, box_size)
                    )
                    label_surf = legend_font.render(name, True, BLACK)
                    self.screen.blit(label_surf, (x_cursor + box_size + 4, y_item))
                    x_cursor += box_size + 4 + legend_font.size(name)[0] + padding

        except Exception:
            pass

    def draw_grid_map(self) -> None:
        for row in range(self.grid_map.height):
            for col in range(self.grid_map.width):
                rect = (
                    self.grid_offset_x + col * self.cell_size,
                    self.grid_offset_y + row * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                value = self.grid_map.grid[row][col]

                if value == self.grid_map.OBSTACLE:
                    pygame.draw.rect(self.screen, BLACK, rect)

                elif value == self.grid_map.START:
                    pygame.draw.rect(self.screen, GREEN, rect)
                    # pygame.draw.circle(
                    #     self.screen,
                    #     WHITE,
                    #     (rect[0] + self.cell_size // 2, rect[1] + self.cell_size // 2),
                    #     self.cell_size // 5,
                    # )

                elif value == self.grid_map.GOAL:
                    pygame.draw.rect(self.screen, RED, rect)
                    # pygame.draw.circle(
                    #     self.screen,
                    #     WHITE,
                    #     (rect[0] + self.cell_size // 2, rect[1] + self.cell_size // 2),
                    #     self.cell_size // 5,
                    # )

                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

                pygame.draw.rect(self.screen, LIGHT, rect, 1)

        if self.selected_algorithm == "All" and self.all_paths:
            for name, path_points in self.all_paths.items():
                if not path_points or len(path_points) <= 1:
                    continue

                color = self.algorithm_colors.get(name, BLUE)
                for index in range(len(path_points) - 1):
                    x_start, y_start = path_points[index]
                    x_end, y_end = path_points[index + 1]

                    start_x = (
                        self.grid_offset_x
                        + x_start * self.cell_size
                        + self.cell_size // 2
                    )
                    start_y = (
                        self.grid_offset_y
                        + y_start * self.cell_size
                        + self.cell_size // 2
                    )

                    end_x = (
                        self.grid_offset_x
                        + x_end * self.cell_size
                        + self.cell_size // 2
                    )
                    end_y = (
                        self.grid_offset_y
                        + y_end * self.cell_size
                        + self.cell_size // 2
                    )

                    pygame.draw.line(
                        self.screen, color, (start_x, start_y), (end_x, end_y), 2
                    )

        else:
            path_points = self.current_path or []

            if path_points and len(path_points) > 1:
                for index in range(len(path_points) - 1):
                    x_start, y_start = path_points[index]
                    x_end, y_end = path_points[index + 1]

                    start_x = (
                        self.grid_offset_x
                        + x_start * self.cell_size
                        + self.cell_size // 2
                    )
                    start_y = (
                        self.grid_offset_y
                        + y_start * self.cell_size
                        + self.cell_size // 2
                    )

                    end_x = (
                        self.grid_offset_x
                        + x_end * self.cell_size
                        + self.cell_size // 2
                    )
                    end_y = (
                        self.grid_offset_y
                        + y_end * self.cell_size
                        + self.cell_size // 2
                    )

                    pygame.draw.line(
                        self.screen, BLUE, (start_x, start_y), (end_x, end_y), 2
                    )

            node_radius = max(3, self.cell_size // 6)
            for x, y in path_points:
                center_x = self.grid_offset_x + x * self.cell_size + self.cell_size // 2
                center_y = self.grid_offset_y + y * self.cell_size + self.cell_size // 2

                pygame.draw.circle(self.screen, BLUE, (center_x, center_y), node_radius)

                pygame.draw.circle(
                    self.screen,
                    WHITE,
                    (center_x, center_y),
                    max(1, node_radius - 2),
                )

        if (
            self.is_dragging
            and self.start_point is not None
            and self.end_point is not None
        ):
            for x, y in self.bresenham_line(self.start_point, self.end_point):
                preview_rect = (
                    self.grid_offset_x + x * self.cell_size,
                    self.grid_offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                pygame.draw.rect(self.screen, MEDIUM, preview_rect, 2)

        self.draw_coordinate_axes()
        # self.draw_cell_values()

    def draw_coordinate_axes(self) -> None:
        map_width = self.grid_map.width * self.cell_size
        map_height = self.grid_map.height * self.cell_size
        y_axis_label_width, _ = self._get_coordinate_axis_margins()
        axis_tick_length = 6
        axis_label_gap = 6
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        grid_left = self.grid_offset_x
        grid_top = self.grid_offset_y
        grid_right = grid_left + map_width
        grid_bottom = grid_top + map_height

        pygame.draw.line(
            self.screen, BLACK, (grid_left, grid_top), (grid_left, grid_bottom), 2
        )
        pygame.draw.line(
            self.screen, BLACK, (grid_left, grid_top), (grid_right, grid_top), 2
        )

        max_x_tick = self.grid_map.width - (self.grid_map.width % 5)
        for coord in range(0, max_x_tick + 1, 5):
            x_pos = grid_left + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (x_pos, grid_top - axis_tick_length),
                (x_pos, grid_top),
                1,
            )

            label_surface = label_font.render(str(coord), True, BLACK)
            label_x = x_pos - label_surface.get_width() // 2
            label_y = (
                grid_top
                - axis_tick_length
                - axis_label_gap
                - label_surface.get_height()
            )
            self.screen.blit(label_surface, (label_x, label_y))

        max_y_tick = self.grid_map.height - (self.grid_map.height % 5)
        for coord in range(0, max_y_tick + 1, 5):
            y_pos = grid_top + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (grid_left - axis_tick_length, y_pos),
                (grid_left, y_pos),
                1,
            )

            label_surface = label_font.render(str(coord), True, BLACK)
            label_x = (
                grid_left - y_axis_label_width + axis_tick_length + axis_label_gap - 10
            )
            label_y = y_pos - label_surface.get_height() // 2
            self.screen.blit(label_surface, (label_x, label_y))

    def _get_coordinate_axis_margins(self) -> tuple[float, float]:
        label_font = pygame.font.SysFont(TEXT_FONT, SMALL_TEXT_SIZE)

        max_x_label = self.grid_map.width - (self.grid_map.width % 5)
        max_y_label = self.grid_map.height - (self.grid_map.height % 5)
        max_label_width = max(
            label_font.size(str(max_x_label))[0],
            label_font.size(str(max_y_label))[0],
        )

        axis_tick_length = 6
        axis_label_gap = 6
        y_axis_label_width = max_label_width + axis_tick_length + axis_label_gap + 2
        x_axis_label_height = (
            label_font.get_height() + axis_tick_length + axis_label_gap
        )

        return y_axis_label_width, x_axis_label_height

    def draw_cell_values(self) -> None:
        font_size = max(15, self.cell_size // 2)
        font = pygame.font.SysFont("monospace", font_size, bold=True)

        value_colors = {
            self.grid_map.FREE: BLACK,  # 0 → màu nhạt
            self.grid_map.OBSTACLE: WHITE,  # 1 → trắng (nền đen)
            self.grid_map.START: BLACK,  # 2 → trắng (nền xanh lá)
            self.grid_map.GOAL: BLACK,  # 3 → trắng (nền đỏ)
        }

        for row in range(self.grid_map.height):
            for col in range(self.grid_map.width):
                value = self.grid_map.grid[row][col]

                color = value_colors.get(value, LIGHT)
                text_surface = font.render(str(value), True, color)

                cell_center_x = (
                    self.grid_offset_x + col * self.cell_size + self.cell_size // 2
                )
                cell_center_y = (
                    self.grid_offset_y + row * self.cell_size + self.cell_size // 2
                )

                text_rect = text_surface.get_rect(center=(cell_center_x, cell_center_y))
                self.screen.blit(text_surface, text_rect)


if __name__ == "__main__":
    app = App()
    app.run()
