from config import (
    CELL_SIZE,
    COLOR_FREE,
    COLOR_OBSTACLE,
    COLOR_PATH,
    DEFAULT_GRID_HEIGHT,
    DEFAULT_GRID_WIDTH,
    EDITOR_WINDOW_HEIGHT,
    EDITOR_WINDOW_WIDTH,
    FONT_SMALL_SIZE,
    MAP_IMAGE_FILENAME,
)
from environment.grid_map import GridMap
from typing import Optional, Tuple
from utils.geometry import bresenham_line
from utils.layout_calculator import calculate_layout
from utils.message_handler import MessageHandler
from utils.visualization import (
    draw_grid,
    draw_text,
    get_cell_from_mouse,
    save_screen,
)

import os
import pygame


class GridEditor:

    def __init__(self, grid: Optional[GridMap] = None) -> None:
        self.grid = grid if grid else GridMap(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)

        self.font = pygame.font.Font(None, FONT_SMALL_SIZE)

        self.layout = calculate_layout(
            self.grid.width,
            self.grid.height,
            EDITOR_WINDOW_WIDTH,
            EDITOR_WINDOW_HEIGHT,
        )
        self.window_width = self.layout.window_width
        self.window_height = self.layout.window_height

        self.message_handler = MessageHandler()

        self.is_dragging = False
        self.drag_start: Optional[Tuple[int, int]] = None
        self.drag_end: Optional[Tuple[int, int]] = None

    def run(self) -> bool:
        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Pathfinding Simulator - Grid Editor")
        clock = pygame.time.Clock()

        running = True
        should_continue_to_simulation = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif event.key == pygame.K_s:
                        self._handle_set_start()

                    elif event.key == pygame.K_g:
                        self._handle_set_goal()

                    elif event.key == pygame.K_RETURN:
                        self._handle_save()

                    elif event.key == pygame.K_SPACE:
                        if self._handle_run():
                            should_continue_to_simulation = True
                            running = False

                    elif event.key == pygame.K_c:
                        self._handle_clear_map()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.is_dragging = True

                        cell = get_cell_from_mouse(
                            event.pos, self.layout.offset_x, self.layout.offset_y
                        )
                        if cell:
                            self.drag_start = cell
                            self.drag_end = cell

                if event.type == pygame.MOUSEMOTION:
                    if self.is_dragging and self.drag_start:
                        cell = get_cell_from_mouse(
                            event.pos, self.layout.offset_x, self.layout.offset_y
                        )
                        if cell:
                            self.drag_end = cell

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1 and self.is_dragging:
                        try:
                            if self.drag_start and self.drag_end:
                                if self.drag_start == self.drag_end:
                                    x, y = self.drag_start[0], self.drag_start[1]

                                    if (
                                        self.grid.is_inside(x, y)
                                        and (x, y) != self.grid.start
                                        and (x, y) != self.grid.goal
                                    ):
                                        if self.grid.grid[y][x] == GridMap.OBSTACLE:
                                            self.grid.grid[y][x] = GridMap.FREE
                                        else:
                                            self.grid.grid[y][x] = GridMap.OBSTACLE
                                        self._set_message("Obstacle toggled")
                                    elif not self.grid.is_inside(x, y):
                                        self._set_message("Click position outside map!")

                                else:
                                    self._draw_obstacle_line(
                                        self.drag_start, self.drag_end
                                    )
                                    self._set_message("Obstacle(s) added")

                        except (IndexError, KeyError) as e:
                            self._set_message("Error: Drag position invalid")

                        finally:
                            self.is_dragging = False
                            self.drag_start = None
                            self.drag_end = None

            self._draw_editor(screen)

            pygame.display.flip()

            clock.tick(60)

        return should_continue_to_simulation

    def _draw_editor(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_FREE)

        draw_grid(
            screen,
            self.grid,
            self.layout.offset_x,
            self.layout.offset_y,
            show_coordinates=True,
        )

        if self.is_dragging and self.drag_start and self.drag_end:
            preview_cells = bresenham_line(self.drag_start, self.drag_end)

            for cell_x, cell_y in preview_cells:
                if self.grid.is_inside(cell_x, cell_y):
                    rect = pygame.Rect(
                        self.layout.offset_x + cell_x * CELL_SIZE,
                        self.layout.offset_y + cell_y * CELL_SIZE,
                        CELL_SIZE,
                        CELL_SIZE,
                    )
                    pygame.draw.rect(screen, (100, 100, 100), rect)
                    pygame.draw.rect(screen, (200, 200, 200), rect, 2)

        right_x = self.layout.right_x + 10
        right_y = self.layout.right_y + 10

        msg_y = right_y
        message = self.message_handler.get_message()
        if message:
            draw_text(
                screen,
                message,
                self.font,
                right_x,
                msg_y,
                COLOR_PATH,
                center=False,
            )

        status_y = msg_y + 30
        status_text = f"Start: {self.grid.start} | Goal: {self.grid.goal}"
        draw_text(
            screen,
            status_text,
            self.font,
            right_x,
            status_y,
            COLOR_OBSTACLE,
        )

        instructions = [
            "Draw: Click to toggle",
            "| Drag to draw line",
            "S: Start  |  G: Goal",
            "",
            "SPACE: Run",
            "ENTER: Save maps",
            "C: Clear  |  ESC: Cancel",
        ]

        instr_start_y = status_y + 40
        instr_max_y = self.window_height - self.layout.margin - 10

        for i, instr in enumerate(instructions):
            if instr:
                y_position = instr_start_y + i * 18
                if y_position < instr_max_y:
                    draw_text(
                        screen,
                        instr,
                        self.font,
                        right_x,
                        y_position,
                        (100, 100, 100),
                        center=False,
                    )

    def _draw_obstacle_line(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        try:
            cells = bresenham_line(start, end)

            for x, y in cells:
                if (
                    self.grid.is_inside(x, y)
                    and (x, y) != self.grid.start
                    and (x, y) != self.grid.goal
                ):
                    self.grid.grid[y][x] = GridMap.OBSTACLE

        except (IndexError, KeyError) as e:
            self._set_message("Error: Obstacle line invalid")

    def _handle_set_start(self) -> None:
        self.message_handler.set_message("Click to set start position")

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cell = get_cell_from_mouse(
                        event.pos, self.layout.offset_x, self.layout.offset_y
                    )

                    if cell and self.grid.is_inside(cell[0], cell[1]):
                        if self.grid.set_start(cell[0], cell[1]):
                            self._set_message("Start set!")
                        else:
                            self._set_message("Cannot set start on obstacle")

                    waiting = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._set_message("Cancelled")
                    waiting = False

            self._draw_editor(pygame.display.get_surface())
            pygame.display.flip()
            pygame.time.delay(10)

    def _handle_set_goal(self) -> None:
        self.message_handler.set_message("Click to set goal position")

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    cell = get_cell_from_mouse(
                        event.pos, self.layout.offset_x, self.layout.offset_y
                    )

                    if cell and self.grid.is_inside(cell[0], cell[1]):
                        if self.grid.set_goal(cell[0], cell[1]):
                            self._set_message("Goal set!")
                        else:
                            self._set_message("Cannot set goal on obstacle")

                    waiting = False

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._set_message("Cancelled")
                    waiting = False

            self._draw_editor(pygame.display.get_surface())
            pygame.display.flip()
            pygame.time.delay(10)

    def _handle_save(self) -> None:
        if not self.grid.start or not self.grid.goal:
            self._set_message("Set both start and goal positions first!")
            return

        map_dir = self.grid.save_map()
        if not map_dir:
            self._set_message("Failed to save map")
            return

        print(f"Map saved to: {map_dir}")

        image_path = os.path.join(map_dir, MAP_IMAGE_FILENAME)
        screen = pygame.display.get_surface()

        if save_screen(screen, image_path):
            print(f"Map image saved to: {image_path}")
            self._set_message("Map saved! Press SPACE to run or keep editing")
        else:
            self._set_message("Map saved (image save failed)")

    def _handle_run(self) -> bool:
        if not self.grid.start or not self.grid.goal:
            self._set_message("Set both start and goal positions!")
            return False

        self._set_message("Launching simulator...")
        pygame.time.delay(500)
        return True

    def _handle_clear_map(self) -> None:
        self.grid = GridMap(self.grid.width, self.grid.height)
        self._set_message("Map cleared")

    def _set_message(self, message: str) -> None:
        self.message_handler.set_message(message)
