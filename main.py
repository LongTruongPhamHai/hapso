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
    GRID_SIDE_HEIGHT,
    GRID_SIDE_WIDTH,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
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
from config.parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH
from datetime import datetime
from pathlib import Path
from grid_map import GridMap
from tkinter import filedialog, messagebox, Tk

import csv
import json
import pandas as pd
import pygame
import sys
import time
import tkinter as tk


class Text:
    def __init__(
        self,
        screen,
        x,
        y,
        color,
        text,
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
    def __init__(self, parent, current_idx, options) -> None:
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
    def __init__(self, parent) -> None:
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
        self, parent, current_width, current_height, current_cell_size
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
        print("HAPSO: Hybrid A* Particle Swarm Optimizer")
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

        self.running = True

        self.mode = "Free"
        self.selected_algorithm = "Astar"
        self.speed = 1

        self.is_dragging = False
        self.start_cell: tuple[int, int] | None = None
        self.end_cell: tuple[int, int] | None = None

        self.current_path: list[tuple[int, int]] | None = None

        self.simulation_active = False
        self.simulation_trace: list[tuple] = []
        self.simulation_index = 0
        self.simulation_visited: list[tuple[int, int]] = []
        self.simulation_path: list[tuple[int, int]] = []
        self.simulation_step = 0
        self.simulation_last_update = 0.0
        self.animate_toggle = True

        self.algorithm_names = ["Astar"]

        self.recalc_layout()

        print(
            f"[INIT] Grid initialized: {self.width}x{self.height} (cell size: {self.cell_size}px)"
        )
        print(f"[INIT] Window size: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        print(f"[INIT] Ready. Press [?] or check menu for commands.\n")

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update_simulation()

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

    def handle_mouse_motion(self, event) -> None:
        if not self.is_dragging:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        self.end_cell = grid_pos

    def screen_to_grid(self, pos) -> tuple[int, int] | None:
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

    def handle_mouse_up(self, event) -> None:
        if event.button != 1:
            return

        if (
            self.is_dragging
            and self.start_cell is not None
            and self.end_cell is not None
        ):
            points = self.bresenham_line(self.start_cell, self.end_cell)
            self.apply_line(points)

        self.is_dragging = False
        self.start_cell = None
        self.end_cell = None

    def bresenham_line(self, start, end) -> list[tuple[int, int]]:
        x0, y0 = start
        x1, y1 = end
        points = []

        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        err = dx - dy

        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1

        x, y = x0, y0
        while True:
            points.append((x, y))

            if x == x1 and y == y1:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx

            if e2 < dx:
                err += dx
                y += sy

        return points

    def apply_line(self, points):
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

    def handle_mouse_down(self, event):
        if event.button != 1:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        if self.mode == "Free":
            pass

        elif self.mode in ("Obstacle", "Erase"):
            self.is_dragging = True
            self.start_cell = grid_pos
            self.end_cell = grid_pos

        elif self.mode == "Start":
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None
                self.stop_simulation()

        elif self.mode == "Goal":
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None
                self.stop_simulation()

    def handle_keydown(self, event):
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

        elif event.key == pygame.K_v:
            self.animate_toggle = not self.animate_toggle
            print(f"[UI] Animate mode (show path immediately): {self.animate_toggle}")

        elif event.key == pygame.K_r:
            self.reset_result()

        elif event.key == pygame.K_b:
            self.open_batch_test_dialog()

        elif event.key in (pygame.K_COMMA, pygame.K_LEFT):
            self.change_speed(-1)

        elif event.key in (pygame.K_PERIOD, pygame.K_RIGHT):
            self.change_speed(1)

        elif event.key == pygame.K_p:
            self.open_settings_dialog()

    def clear_map(self) -> None:
        self.grid_map.grid = [
            [GridMap.FREE for _ in range(self.grid_map.width)]
            for _ in range(self.grid_map.height)
        ]
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

    def run_selected_algorithm(self, animate: bool = True) -> None:
        if self.grid_map.start is None or self.grid_map.goal is None:
            print("[ALGORITHM] ERROR - Start and goal positions must be set")
            return

        print(f"[ALGORITHM] Running: {self.selected_algorithm}")
        print(f"[ALGORITHM] Start: {self.grid_map.start}, Goal: {self.grid_map.goal}")

        start_time = time.perf_counter()

        match self.selected_algorithm:
            case "Astar":
                should_animate = animate and self.animate_toggle
                planner = Astar(self.grid_map, animate=should_animate)
                self.current_path = planner.plan()

                trace = getattr(planner, "visual_trace", [])
                if should_animate and trace:
                    self.start_simulation(trace)
                else:
                    self.stop_simulation()

        elapsed_time = time.perf_counter() - start_time

        if self.current_path:
            print(
                f"[ALGORITHM] SUCCESS - Path found: {len(self.current_path)} waypoints"
            )
            print(f"[ALGORITHM] Execution time: {elapsed_time:.4f}s")
        else:
            print(f"[ALGORITHM] FAILED - No path found")
            print(f"[ALGORITHM] Execution time: {elapsed_time:.4f}s")

    def start_simulation(self, trace: list[tuple]) -> None:
        self.current_path = None

        self.simulation_trace = list(trace)
        self.simulation_index = 0
        self.simulation_visited = []
        self.simulation_path = []
        self.simulation_step = 0
        self.simulation_last_update = time.perf_counter()
        self.simulation_active = bool(self.simulation_trace)

    def stop_simulation(self) -> None:
        self.simulation_active = False
        self.simulation_trace = []
        self.simulation_index = 0
        self.simulation_visited = []
        self.simulation_path = []
        self.simulation_step = 0
        self.simulation_last_update = 0.0

    def update_simulation(self) -> None:
        if not self.simulation_active:
            return

        if self.simulation_index >= len(self.simulation_trace):
            self.stop_simulation()
            return

        effective_speed = max(1.0, self.speed / 2.0)
        step_interval = max(0.03, 0.18 / effective_speed)
        now = time.perf_counter()

        if now - self.simulation_last_update < step_interval:
            return

        self.simulation_last_update = now
        event = self.simulation_trace[self.simulation_index]
        self.simulation_index += 1
        self.simulation_step = self.simulation_index

        if not isinstance(event, tuple) or not event:
            return

        kind = event[0]
        if kind == "visit" and len(event) >= 2:
            coord = event[1]
            self.simulation_visited.append(coord)

        elif kind == "path" and len(event) >= 2:
            path = event[1] or []
            self.simulation_path = list(path)
            self.current_path = list(path)
            self.simulation_active = False
            self.simulation_trace = []
            self.simulation_index = 0

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

        if run_count < 1:
            return

        print(f"\n{'='*60}")
        print(f"[BATCH] Starting batch test: {run_count} runs")
        print(f"[BATCH] Algorithm: {self.selected_algorithm}")
        print(f"{'='*60}")

        successful_runs = 0
        total_time = 0.0
        path_lengths = []

        for i in range(run_count):
            print(f"[BATCH] Run {i+1}/{run_count}...", end=" ", flush=True)

            start_time = time.perf_counter()
            self.run_selected_algorithm(animate=False)
            run_time = time.perf_counter() - start_time
            total_time += run_time

            if self.current_path:
                successful_runs += 1
                path_lengths.append(len(self.current_path))
                print(f"Path: {len(self.current_path)} waypoints ({run_time:.4f}s)")

            else:
                print(f"No path found ({run_time:.4f}s)")

        avg_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
        avg_time = total_time / run_count if run_count else 0.0

        print(f"{'='*60}")
        print(f"[BATCH] Results:")
        print(f"[BATCH]   Total runs: {run_count}")
        print(f"[BATCH]   Successful: {successful_runs}/{run_count}")
        print(f"[BATCH]   Success rate: {successful_runs/run_count*100:.1f}%")
        print(f"[BATCH]   Avg path length: {avg_length:.2f} waypoints")
        print(f"[BATCH]   Avg time: {avg_time:.4f}s")
        print(f"[BATCH]   Total time: {total_time:.4f}s")
        print(f"{'='*60}\n")

        messagebox.showinfo(
            "Batch Test",
            (
                f"Runs: {run_count}\n"
                f"Success: {successful_runs}/{run_count}\n"
                f"Avg path length: {avg_length:.2f}\n"
                f"Avg time: {avg_time:.4f} s"
            ),
        )

    def change_speed(self, delta: int) -> None:
        old_speed = self.speed
        self.speed = max(1, min(10, self.speed + delta))

        if old_speed != self.speed:
            print(f"[MENU] Speed changed: {old_speed} -> {self.speed}")

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

        content_width = map_width + y_axis_label_width + axis_gap
        content_height = map_height + x_axis_label_height + axis_gap

        self.grid_offset_x = (
            NAV_WIDTH
            + max(0, (available_width - content_width) // 2)
            + y_axis_label_width
            + axis_gap
        )
        self.grid_offset_y = MODE_HEIGHT + max(
            0, (available_height - content_height) // 2
        )

    def resize_grid(self, width: int, height: int, cell_size: int) -> None:
        self.width = width
        self.height = height
        self.cell_size = cell_size

        self.grid_map.resize(width=self.width, height=self.height)
        self.current_path = None
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
        animate_text = f" | Animate: {'ON' if self.animate_toggle else 'OFF'}"
        mode_text = Text(
            self.screen,
            MODE_OFFSET_X,
            MODE_OFFSET_Y,
            BLACK,
            f"Mode: {self.mode} | Alg: {self.selected_algorithm}{animate_text} | Speed: {self.speed}",
        )
        mode_text.draw_text()

        pygame.draw.line(
            self.screen, BLACK, (NAV_WIDTH, MODE_HEIGHT), (WINDOW_WIDTH, MODE_HEIGHT), 2
        )

    def draw_grid_map(self) -> None:
        visited_limit = min(self.simulation_step, len(self.simulation_visited))
        visited_set = set(self.simulation_visited[:visited_limit])
        path_limit = max(0, self.simulation_step - len(self.simulation_visited))
        visited_overlay = None

        if visited_set:
            visited_overlay = pygame.Surface(
                (self.cell_size, self.cell_size), pygame.SRCALPHA
            )
            visited_overlay.fill((180, 220, 255, 120))

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

                elif value == self.grid_map.GOAL:
                    pygame.draw.rect(self.screen, RED, rect)

                else:
                    pygame.draw.rect(self.screen, WHITE, rect)

                if visited_overlay is not None and (col, row) in visited_set:
                    self.screen.blit(visited_overlay, (rect[0], rect[1]))

                pygame.draw.rect(self.screen, MEDIUM, rect, 1)

        path_points = self.current_path or []
        if self.simulation_active and self.simulation_path:
            if path_limit <= 0:
                path_points = self.simulation_path[:1]

            else:
                path_points = self.simulation_path[
                    : min(len(self.simulation_path), path_limit + 1)
                ]

        if path_points and len(path_points) > 1:
            for index in range(len(path_points) - 1):
                x1, y1 = path_points[index]
                x2, y2 = path_points[index + 1]

                start_x = self.grid_offset_x + x1 * self.cell_size + self.cell_size // 2
                start_y = self.grid_offset_y + y1 * self.cell_size + self.cell_size // 2

                end_x = self.grid_offset_x + x2 * self.cell_size + self.cell_size // 2
                end_y = self.grid_offset_y + y2 * self.cell_size + self.cell_size // 2

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
            and self.start_cell is not None
            and self.end_cell is not None
        ):
            for x, y in self.bresenham_line(self.start_cell, self.end_cell):
                preview_rect = (
                    self.grid_offset_x + x * self.cell_size,
                    self.grid_offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                pygame.draw.rect(self.screen, MEDIUM, preview_rect, 2)

        self.draw_coordinate_axes()

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
            self.screen, BLACK, (grid_left, grid_bottom), (grid_right, grid_bottom), 2
        )

        max_x_tick = self.grid_map.width - (self.grid_map.width % 5)
        for coord in range(0, max_x_tick + 1, 5):
            x_pos = grid_left + coord * self.cell_size
            pygame.draw.line(
                self.screen,
                BLACK,
                (x_pos, grid_bottom),
                (x_pos, grid_bottom + axis_tick_length),
                1,
            )

            label_surface = label_font.render(str(coord), True, BLACK)
            label_x = x_pos - label_surface.get_width() // 2
            label_y = grid_bottom + axis_tick_length + axis_label_gap

            self.screen.blit(label_surface, (label_x, label_y))

        max_y_tick = self.grid_map.height - (self.grid_map.height % 5)
        for coord in range(0, max_y_tick + 1, 5):
            y_pos = grid_bottom - coord * self.cell_size
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

    def _get_coordinate_axis_margins(self) -> tuple[int, int]:
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


if __name__ == "__main__":
    app = App()
    app.run()
