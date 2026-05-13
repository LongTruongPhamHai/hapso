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
from datetime import datetime
from grid_map import GridMap
from pathlib import Path
from tkinter import Tk, filedialog

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


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("HAPSO: Simulator Application")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(TEXT_FONT, NORMAL_TEXT_SIZE)

        self.grid_map = GridMap()

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

        self.status_message = ""

    def run(self):
        while self.running:
            self.handle_events()

            self.draw_ui()

            self.clock.tick(60)

        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mouse_down(event)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mouse_motion(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mouse_up(event)

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
            self.grid_map.clear_map()
            self.current_path = None
            self.status_message = "Map cleared"

        elif event.key == pygame.K_i:
            self.import_map()

        elif event.key == pygame.K_e:
            self.export_map()

        elif event.key == pygame.K_a:
            pass

        elif event.key == pygame.K_SPACE:
            self.run_selected_algorithm()

        elif event.key == pygame.K_b:
            self.batch_test()

        elif event.key == pygame.K_d:
            self.debug = not self.debug
            self.status_message = f"Debug {'on' if self.debug else 'off'}"

        elif event.key in (pygame.K_COMMA, pygame.K_LEFT):
            self.change_speed(-1)

        elif event.key in (pygame.K_PERIOD, pygame.K_RIGHT):
            self.change_speed(1)

        elif event.key == pygame.K_p:
            self.settings_open = not self.settings_open
            self.status_message = (
                "Settings opened" if self.settings_open else "Settings closed"
            )

    def handle_mouse_down(self, event):
        if event.button != 1:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        if self.mode in ("Obstacle", "Erase"):
            self.is_mouse_pressed = True
            self.line_start = grid_pos
            self.line_end = grid_pos
        elif self.mode == "Start":
            if self.grid_map.set_start(*grid_pos):
                self.current_path = None
        elif self.mode == "Goal":
            if self.grid_map.set_goal(*grid_pos):
                self.current_path = None

    def handle_mouse_motion(self, event):
        if not self.is_mouse_pressed:
            return

        grid_pos = self.screen_to_grid(event.pos)
        if grid_pos is None:
            return

        self.line_end = grid_pos

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

    def apply_line(self, points):
        changed = False
        for x, y in points:
            if self.mode == "Obstacle":
                changed = self.grid_map.set_obstacle(x, y, True) or changed
            elif self.mode == "Erase":
                changed = self.grid_map.set_obstacle(x, y, False) or changed

        if changed:
            self.current_path = None

    def import_map(self):
        path = self.ask_open_path()
        if not path:
            return

        file_path = Path(path)
        if not file_path.exists():
            print(f"[MAP_SERIALIZER]: File not found - {path}")
            self.status_message = f"Failed to load: {path}"
            return

        with file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        loaded = GridMap.from_dict(data)
        if loaded is None:
            self.status_message = f"Failed to load: {path}"
            return

        self.grid_map = loaded
        self.current_path = None
        self.status_message = f"Loaded map: {Path(path).name}"

    def export_map(self):
        if self.grid_map.start is None or self.grid_map.goal is None:
            self.status_message = "Start and goal are required before export"
            return

        base_dir = Path("data/maps")
        base_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        map_path = base_dir / timestamp
        map_path.mkdir(parents=True, exist_ok=True)

        json_path = map_path / "map.json"
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(self.grid_map.to_dict(), file, indent=2)

        self.status_message = f"Exported map: {json_path}"

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
            self.screen, MODE_OFFSET_X, MODE_OFFSET_Y, BLACK, f"Mode: " + mode
        )
        mode_text.draw_text()
        pygame.draw.line(
            self.screen, BLACK, (NAV_WIDTH, MODE_HEIGHT), (WINDOW_WIDTH, MODE_HEIGHT), 2
        )

    def draw_grid_map(self):
        for row in range(self.grid_map.height):
            for col in range(self.grid_map.width):
                rect = (
                    GRID_OFFSET_X + col * GRID_CELL_SIZE,
                    GRID_OFFSET_Y + row * GRID_CELL_SIZE,
                    GRID_CELL_SIZE,
                    GRID_CELL_SIZE,
                )

                pygame.draw.rect(self.screen, WHITE, rect)
                pygame.draw.rect(self.screen, MEDIUM, rect, 1)


if __name__ == "__main__":
    app = App()
    app.run()
