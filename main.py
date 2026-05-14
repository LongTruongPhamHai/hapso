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
    MODE_WIDTH,
    MODE_OFFSET_X,
    MODE_OFFSET_Y,
    GRID_CELL_SIZE,
    GRID_OFFSET_X,
    GRID_OFFSET_Y,
    TEXT_FONT,
    SMALL_TEXT_SIZE,
    NORMAL_TEXT_SIZE,
    LARGE_TEXT_SIZE,
)
from config.parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH
from datetime import datetime
from grid_map import GridMap
from pathlib import Path
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
    ):
        self.screen = screen
        self.x = x
        self.y = y

        self.color = color

        self.text = text
        self.font_name = font_name
        self.size = size

        self.font = pygame.font.SysFont(self.font_name, self.size)

    def draw_text(self):
        text_surface = self.font.render(self.text, True, self.color)

        self.screen.blit(text_surface, (self.x, self.y))


class AlgorithmSelectDialog(tk.Toplevel):
    def __init__(self, parent, current_idx, options):
        super().__init__(parent)

        self.title("Select Algorithm")
        self.geometry("320x320")
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(self, text="Choose Solver:", font=(TEXT_FONT, NORMAL_TEXT_SIZE)).pack(
            pady=10
        )
        self.var = tk.IntVar(value=current_idx)

        for index, name in enumerate(options):
            tk.Radiobutton(
                self,
                text=name,
                variable=self.var,
                value=index,
                font=(TEXT_FONT, NORMAL_TEXT_SIZE),
            ).pack(anchor="w", padx=40)

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Select", command=self.on_select, width=10).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(
            side=tk.LEFT, padx=5
        )

        self.center_window()

    def on_select(self):
        self.result = self.var.get()
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


class BatchTestDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.title("Batch Test Configuration")
        self.geometry("300x160")
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(self, text="Number of Test Runs (1-100):").pack(pady=10)
        self.runs_var = tk.IntVar(value=10)
        tk.Entry(self, textvariable=self.runs_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame, text="Start Testing", command=self.on_start, width=15
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(
            side=tk.LEFT, padx=5
        )

        self.center_window()

    def on_start(self):
        try:
            runs = self.runs_var.get()
        except tk.TclError:
            messagebox.showerror("Error", "Invalid number.")
            return

        if not (1 <= runs <= 100):
            messagebox.showerror("Error", "Enter 1-100.")
            return

        self.result = runs
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


class SettingsDialog(tk.Toplevel):

    def __init__(self, parent, current_rows, current_cols, current_size):
        super().__init__(parent)
        self.title("Map Settings")
        self.geometry("300x250")
        self.result = None
        self.lift()
        self.focus_force()
        self.grab_set()

        tk.Label(self, text="Rows (5-100):").pack(pady=(10, 0))
        self.rows_var = tk.IntVar(value=current_rows)
        tk.Entry(self, textvariable=self.rows_var).pack()

        tk.Label(self, text="Cols (5-100):").pack(pady=(10, 0))
        self.cols_var = tk.IntVar(value=current_cols)
        tk.Entry(self, textvariable=self.cols_var).pack()

        tk.Label(self, text="Cell Size (5-50 px):").pack(pady=(10, 0))
        self.size_var = tk.IntVar(value=current_size)
        tk.Entry(self, textvariable=self.size_var).pack()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Apply", command=self.on_apply, width=10).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="Cancel", command=self.destroy, width=10).pack(
            side=tk.LEFT, padx=5
        )
        self.center_window()

    def on_apply(self):
        try:
            rows = self.rows_var.get()
            cols = self.cols_var.get()
            size = self.size_var.get()
        except tk.TclError:
            messagebox.showerror("Error", "Invalid input.")
            return

        if not (5 <= rows <= 100 and 5 <= cols <= 100 and 5 <= size <= 50):
            messagebox.showerror("Error", "Values out of range.")
            return

        self.result = (rows, cols, size)
        self.destroy()

    def center_window(self):
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()

        pos_x = (self.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (self.winfo_screenheight() // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("HAPSO: Simulator Application")

        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(TEXT_FONT, NORMAL_TEXT_SIZE)

        self.grid_height = GRID_MAP_HEIGHT
        self.grid_width = GRID_MAP_WIDTH
        self.cell_size = GRID_CELL_SIZE

        self.grid_map = GridMap(width=self.grid_width, height=self.grid_height)

        self.running = True

        self.mode = "Free"
        self.selected_algorithm = "Astar"
        self.debug = False
        self.speed = 1
        self.settings_open = False

        self.is_mouse_pressed = False
        self.line_start: tuple[int, int] | None = None
        self.line_end: tuple[int, int] | None = None
        self.current_path: list[tuple[int, int]] | None = None

        self.algorithm_names = ["Astar"]

        self.recalc_layout()

    def run(self):
        while self.running:
            self.handle_events()

            self.draw_ui()

            self.clock.tick(60)

        pygame.quit()
        self.tk_root.destroy()

    def handle_events(self):
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

    def handle_mouse_motion(self, event):
        if not self.is_mouse_pressed:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        self.line_end = grid_pos

    def screen_to_grid(self, pos):
        x, y = pos
        grid_width = self.grid_map.width * GRID_CELL_SIZE
        grid_height = self.grid_map.height * GRID_CELL_SIZE

        if (
            x < GRID_OFFSET_X
            or y < GRID_OFFSET_Y
            or x >= GRID_OFFSET_X + grid_width
            or y >= GRID_OFFSET_Y + grid_height
        ):
            return None

        grid_x = (x - GRID_OFFSET_X) // GRID_CELL_SIZE
        grid_y = (y - GRID_OFFSET_Y) // GRID_CELL_SIZE

        return (grid_x, grid_y)

    def handle_mouse_up(self, event):
        if event.button != 1:
            return

        if (
            self.is_mouse_pressed
            and self.line_start is not None
            and self.line_end is not None
        ):
            points = self.bresenham_line(self.line_start, self.line_end)
            self.apply_line(points)

        self.is_mouse_pressed = False
        self.line_start = None
        self.line_end = None

    def bresenham_line(self, start, end):
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
            self.is_mouse_pressed = True
            self.line_start = grid_pos
            self.line_end = grid_pos

        elif self.mode == "Start":
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None

        elif self.mode == "Goal":
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None

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

        elif event.key == pygame.K_b:
            self.open_batch_test_dialog()

        elif event.key == pygame.K_d:
            self.debug = not self.debug

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

    def import_map(self):
        path = self.ask_open_path()
        if not path:
            return

        file_path = Path(path)
        if not file_path.exists():
            print(f"File not found - {path}")
            return

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        loaded = self.grid_map_from_dict(data)
        if loaded is None:
            return

        self.grid_map = loaded
        self.rows = self.grid_map.height
        self.cols = self.grid_map.width
        self.current_path = None
        self.recalc_layout()

    def ask_open_path(self):
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
        try:
            grid_map = GridMap(data["width"], data["height"])
            grid_map.grid = data["grid"]
            grid_map.start = tuple(data["start"]) if data.get("start") else None
            grid_map.goal = tuple(data["goal"]) if data.get("goal") else None

            return grid_map

        except (KeyError, TypeError, ValueError):
            return None

    def export_map(self):
        if self.grid_map.start is None or self.grid_map.goal is None:
            return

        base_dir = Path("data/maps")
        base_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        map_path = base_dir / timestamp
        map_path.mkdir(parents=True, exist_ok=True)

        json_path = map_path / "map.json"
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(self.grid_map_to_dict(self.grid_map), file, indent=2)

    def grid_map_to_dict(self, grid_map: GridMap) -> dict:
        return {
            "width": grid_map.width,
            "height": grid_map.height,
            "grid": grid_map.grid,
            "start": grid_map.start,
            "goal": grid_map.goal,
        }

    def open_algo_dialog(self):
        dialog = AlgorithmSelectDialog(
            self.tk_root,
            self.algorithm_names.index(self.selected_algorithm),
            self.algorithm_names,
        )

        self.tk_root.wait_window(dialog)
        if dialog.result is not None:
            self.selected_algorithm = self.algorithm_names[dialog.result]

    def run_selected_algorithm(self):
        if self.grid_map.start is None or self.grid_map.goal is None:
            return

        algorithm = self.selected_algorithm

        match self.selected_algorithm:
            case "Astar":
                planner = Astar(self.grid_map)
                self.current_path = planner.plan()

    def open_batch_test_dialog(self):
        dialog = BatchTestDialog(self.tk_root)
        self.tk_root.wait_window(dialog)

        if dialog.result is not None:
            self.batch_test(dialog.result)

    def batch_test(self, run_count: int = 10):
        if self.grid_map.start is None or self.grid_map.goal is None:
            messagebox.showwarning("Batch Test", "Please set start and goal first.")
            return

        if run_count < 1:
            return

        successful_runs = 0
        total_time = 0.0
        path_lengths = []

        for _ in range(run_count):
            start_time = time.perf_counter()
            self.run_selected_algorithm()
            total_time += time.perf_counter() - start_time

            if self.current_path:
                successful_runs += 1
                path_lengths.append(len(self.current_path))

        avg_length = sum(path_lengths) / len(path_lengths) if path_lengths else 0.0
        avg_time = total_time / run_count if run_count else 0.0
        messagebox.showinfo(
            "Batch Test",
            (
                f"Runs: {run_count}\n"
                f"Success: {successful_runs}/{run_count}\n"
                f"Avg path length: {avg_length:.2f}\n"
                f"Avg time: {avg_time:.4f} s"
            ),
        )

    def change_speed(self, delta: int):
        self.speed = max(1, min(10, self.speed + delta))

    def open_settings_dialog(self):
        dialog = SettingsDialog(
            self.tk_root,
            GRID_MAP_HEIGHT,
            GRID_MAP_WIDTH,
            GRID_CELL_SIZE,
        )

        self.tk_root.wait_window(dialog)
        if dialog.result:
            rows, cols, cell_size = dialog.result
            self.resize_grid(rows, cols, cell_size)

    def recalc_layout(self):
        map_width = self.grid_map.width * self.cell_size
        map_height = self.grid_map.height * self.cell_size

        available_width = WINDOW_WIDTH - NAV_WIDTH
        available_height = WINDOW_HEIGHT - MODE_HEIGHT

        self.grid_offset_x = NAV_WIDTH + max(0, (available_width - map_width) // 2)
        self.grid_offset_y = MODE_HEIGHT + max(0, (available_height - map_height) // 2)

    def resize_grid(self, height: int, width: int, cell_size: int):
        self.grid_height = height
        self.grid_width = width
        self.cell_size = cell_size

        self.grid_map.resize(width=self.grid_width, height=self.grid_height)
        self.current_path = None

        self.recalc_layout()

    def draw_ui(self):
        self.screen.fill(WHITE)

        self.draw_nav_side()
        self.draw_active_mode()
        self.draw_grid_map()

        pygame.display.flip()

    def draw_nav_side(self):
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

    def draw_active_mode(self, mode: str = "Set obstacle"):
        mode_text = Text(
            self.screen,
            MODE_OFFSET_X,
            MODE_OFFSET_Y,
            BLACK,
            f"Mode: {self.mode} | Alg: {self.selected_algorithm} | Speed: {self.speed} | Debug: {'On' if self.debug else 'Off'}",
        )
        mode_text.draw_text()
        pygame.draw.line(
            self.screen, BLACK, (NAV_WIDTH, MODE_HEIGHT), (WINDOW_WIDTH, MODE_HEIGHT), 2
        )

    def draw_grid_map(self):
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

                pygame.draw.rect(self.screen, MEDIUM, rect, 1)

        if self.current_path and len(self.current_path) > 1:
            for index in range(len(self.current_path) - 1):
                x1, y1 = self.current_path[index]
                x2, y2 = self.current_path[index + 1]

                start_x = self.grid_offset_x + x1 * self.cell_size + self.cell_size // 2
                start_y = self.grid_offset_y + y1 * self.cell_size + self.cell_size // 2

                end_x = self.grid_offset_x + x2 * self.cell_size + self.cell_size // 2
                end_y = self.grid_offset_y + y2 * self.cell_size + self.cell_size // 2

                pygame.draw.line(
                    self.screen, BLUE, (start_x, start_y), (end_x, end_y), 2
                )

        if (
            self.is_mouse_pressed
            and self.line_start is not None
            and self.line_end is not None
        ):
            for x, y in self.bresenham_line(self.line_start, self.line_end):
                preview_rect = (
                    self.grid_offset_x + x * self.cell_size,
                    self.grid_offset_y + y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )

                pygame.draw.rect(self.screen, MEDIUM, preview_rect, 2)


if __name__ == "__main__":
    app = App()
    app.run()
