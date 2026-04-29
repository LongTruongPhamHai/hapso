from config import (
    COLOR_FREE,
    COLOR_HOVER,
    COLOR_OBSTACLE,
    FONT_LARGE,
    FONT_NORMAL,
    FONT_SMALL,
    MAPS_DIR,
)
from environment.grid_map import GridMap
from typing import Literal, Optional
from utils.visualization import draw_text

import os
import pygame


class StartMenu:
    def __init__(self) -> None:
        self.margin = 10
        self.button_gap = 10
        self.gap_title_button = 10

        self.button_width = 120
        self.button_height = 50
        self.button_border = 2
        self.title_height = 40

        self.window_width = (
            self.margin
            + self.button_width
            + self.button_gap
            + self.button_width
            + self.button_gap
            + self.button_width
            + self.margin
        )
        self.window_height = (
            self.margin
            + self.title_height
            + self.gap_title_button
            + self.button_height
            + self.margin
        )

        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_normal = pygame.font.Font(None, FONT_NORMAL)
        self.font_small = pygame.font.Font(None, FONT_SMALL)

        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)

    def run(self) -> Optional[Literal["new", "load"]]:
        screen = pygame.display.set_mode((self.window_width, self.window_height))

        pygame.display.set_caption("Pathfinding Simulator - Start Menu")

        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_n:
                        return "new"
                    elif event.key == pygame.K_l:
                        return "load"
                    elif event.key == pygame.K_ESCAPE:
                        return None

            self._draw_menu(screen)

            pygame.display.flip()

            clock.tick(60)

        return None

    def _draw_menu(self, screen: pygame.Surface) -> None:
        screen.fill(self.WHITE)

        title_y = self.margin + self.title_height // 2
        draw_text(
            screen,
            "UAV Pathfinding Simulator",
            self.font_large,
            self.window_width // 2,
            title_y,
            self.BLACK,
            center=True,
        )

        button_y = self.margin + self.title_height + self.gap_title_button

        button_1_x = self.margin
        button_1_rect = pygame.Rect(
            button_1_x, button_y, self.button_width, self.button_height
        )
        pygame.draw.rect(screen, self.BLACK, button_1_rect, self.button_border)
        draw_text(
            screen,
            "Press N",
            self.font_normal,
            button_1_rect.centerx,
            button_1_rect.centery - 8,
            self.BLACK,
            center=True,
        )
        draw_text(
            screen,
            "New Map",
            self.font_normal,
            button_1_rect.centerx,
            button_1_rect.centery + 10,
            self.BLACK,
            center=True,
        )

        button_2_x = self.margin + self.button_width + self.button_gap
        button_2_rect = pygame.Rect(
            button_2_x, button_y, self.button_width, self.button_height
        )
        pygame.draw.rect(screen, self.BLACK, button_2_rect, self.button_border)
        draw_text(
            screen,
            "Press L",
            self.font_normal,
            button_2_rect.centerx,
            button_2_rect.centery - 8,
            self.BLACK,
            center=True,
        )
        draw_text(
            screen,
            "Load Map",
            self.font_normal,
            button_2_rect.centerx,
            button_2_rect.centery + 10,
            self.BLACK,
            center=True,
        )

        button_3_x = self.margin + 2 * (self.button_width + self.button_gap)
        button_3_rect = pygame.Rect(
            button_3_x, button_y, self.button_width, self.button_height
        )
        pygame.draw.rect(screen, self.BLACK, button_3_rect, self.button_border)
        draw_text(
            screen,
            "Press ESC",
            self.font_normal,
            button_3_rect.centerx,
            button_3_rect.centery - 8,
            self.BLACK,
            center=True,
        )
        draw_text(
            screen,
            "Close",
            self.font_normal,
            button_3_rect.centerx,
            button_3_rect.centery + 10,
            self.BLACK,
            center=True,
        )


class MapMenu:
    def __init__(self) -> None:
        self.window_width = 400
        self.window_height = 350
        self.margin = 10
        self.font_large = pygame.font.Font(None, FONT_LARGE)
        self.font_normal = pygame.font.Font(None, FONT_NORMAL)
        self.font_small = pygame.font.Font(None, FONT_SMALL)

        self.maps_dir = MAPS_DIR
        self.all_maps = []
        self.selected_index = 0
        self.maps_per_page = 5
        self.current_page = 0

        self._load_maps()

    def _load_maps(self) -> None:
        self.all_maps = GridMap.list_saved_maps()

    def run(self) -> Optional[str]:
        if not self.all_maps:
            print("No saved maps found!")
            return None

        screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Pathfinding Simulator - Load Map")
        clock = pygame.time.Clock()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None

                    elif event.key == pygame.K_UP:
                        self.selected_index = max(0, self.selected_index - 1)

                    elif event.key == pygame.K_DOWN:
                        page_maps = self._get_current_page_maps()

                        self.selected_index = min(
                            len(page_maps) - 1, self.selected_index + 1
                        )

                    elif event.key == pygame.K_LEFT:
                        self.current_page = max(0, self.current_page - 1)
                        self.selected_index = 0

                    elif event.key == pygame.K_RIGHT:
                        self.current_page = min(
                            self._get_total_pages() - 1, self.current_page + 1
                        )
                        self.selected_index = 0

                    elif event.key == pygame.K_RETURN:
                        page_maps = self._get_current_page_maps()

                        if self.selected_index < len(page_maps):
                            return page_maps[self.selected_index]

            self._draw_menu(screen)
            pygame.display.flip()
            clock.tick(60)

        return None

    def _get_current_page_maps(self) -> list:
        start = self.current_page * self.maps_per_page
        end = start + self.maps_per_page
        return self.all_maps[start:end]

    def _get_total_pages(self) -> int:
        if not self.all_maps:
            return 1

        return (len(self.all_maps) + self.maps_per_page - 1) // self.maps_per_page

    def _draw_menu(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR_FREE)

        draw_text(
            screen,
            "Select Map to Load",
            self.font_large,
            self.window_width // 2,
            self.margin + 20,
            COLOR_OBSTACLE,
            center=True,
        )

        page_maps = self._get_current_page_maps()

        if not page_maps:
            draw_text(
                screen,
                "No maps found",
                self.font_normal,
                self.window_width // 2,
                self.window_height // 2,
                COLOR_OBSTACLE,
                center=True,
            )
        else:
            y_offset = self.margin + 70
            map_item_height = 35

            for i, map_path in enumerate(page_maps):
                map_name = os.path.basename(map_path)

                if i == self.selected_index:
                    color = COLOR_OBSTACLE
                    pygame.draw.rect(
                        screen,
                        COLOR_HOVER,
                        (
                            self.margin,
                            y_offset - 5,
                            self.window_width - 2 * self.margin,
                            25,
                        ),
                    )
                else:
                    color = COLOR_OBSTACLE

                draw_text(
                    screen,
                    map_name,
                    self.font_normal,
                    self.margin + 10,
                    y_offset,
                    color,
                )

                y_offset += map_item_height

        page_text = f"Page {self.current_page + 1}/{self._get_total_pages()}"
        draw_text(
            screen,
            page_text,
            self.font_normal,
            self.window_width // 2,
            self.window_height - 60,
            COLOR_OBSTACLE,
            center=True,
        )

        instructions = [
            "UP/DOWN: Select  |  LEFT/RIGHT: Page",
            "ENTER: Load  |  ESC: Cancel",
        ]

        for i, instr in enumerate(instructions):
            draw_text(
                screen,
                instr,
                self.font_normal,
                self.window_width // 2,
                self.window_height - 35 + i * 18,
                COLOR_OBSTACLE,
                center=True,
            )
