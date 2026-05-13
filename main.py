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
    TEXT_FONT,
    SMALL_TEXT_SIZE,
    NORMAL_TEXT_SIZE,
    LARGE_TEXT_SIZE,
    GRID_CELL_SIZE,
)
from grid_map import GridMap

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

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            self.draw_ui()
            self.clock.tick(60)

    # def get_mouse_input(self):

    def draw_ui(self):
        self.screen.fill(WHITE)

        self.draw_nav_side()

        pygame.display.flip()

    def draw_nav_side(self):
        nav_side = (0, 0, NAV_WIDTH, NAV_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, nav_side)
        pygame.draw.line(self.screen, BLACK, (NAV_WIDTH, 0), (NAV_WIDTH, NAV_HEIGHT), 2)

        nav_title = Text(self.screen, 10, 20, BLACK, "MENU", size=LARGE_TEXT_SIZE)
        nav_title.draw_text()

        nav_menu = NAV_MENU
        y_offset = 60
        for menu in nav_menu:
            text = Text(self.screen, 10, y_offset, BLACK, menu)
            text.draw_text()

            y_offset += 30


if __name__ == "__main__":
    app = App()
    app.run()
