from config import (
    CELL_SIZE,
    COLOR_FREE,
    COLOR_GOAL,
    COLOR_GRID,
    COLOR_OBSTACLE,
    COLOR_PATH,
    COLOR_START,
    FONT_COORD,
)
from environment.grid_map import GridMap
from typing import List, Optional, Tuple

import pygame


def draw_text(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    color: Tuple[int, int, int],
    center: bool = False,
) -> None:
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)


def draw_grid(
    screen: pygame.Surface,
    grid: GridMap,
    offset_x: int = 0,
    offset_y: int = 0,
    show_coordinates: bool = False,
) -> None:
    for y in range(grid.height):
        for x in range(grid.width):
            rect = pygame.Rect(
                offset_x + x * CELL_SIZE,
                offset_y + y * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            cell_type = grid.grid[y][x]

            if cell_type == GridMap.OBSTACLE:
                color = COLOR_OBSTACLE
            elif cell_type == GridMap.START:
                color = COLOR_START
            elif cell_type == GridMap.GOAL:
                color = COLOR_GOAL
            elif cell_type == GridMap.PATH:
                color = COLOR_PATH
            else:
                color = COLOR_FREE

            pygame.draw.rect(screen, color, rect)

            pygame.draw.rect(screen, COLOR_GRID, rect, 1)

    if show_coordinates:
        draw_coordinate_axes(screen, grid, offset_x, offset_y)


def draw_coordinate_axes(
    screen: pygame.Surface,
    grid: GridMap,
    offset_x: int = 0,
    offset_y: int = 0,
) -> None:
    coord_font = pygame.font.Font(None, FONT_COORD)
    axis_color = (100, 100, 100)

    for x in range(grid.width):
        x_label = coord_font.render(str(x), True, axis_color)
        x_pos = offset_x + x * CELL_SIZE + (CELL_SIZE - x_label.get_width()) // 2
        y_pos = offset_y - 16
        if y_pos >= 0:
            screen.blit(x_label, (x_pos, y_pos))

    for y in range(grid.height):
        y_label = coord_font.render(str(y), True, axis_color)
        x_pos = offset_x - 20
        y_pos = offset_y + y * CELL_SIZE + (CELL_SIZE - y_label.get_height()) // 2
        if x_pos >= 0:
            screen.blit(y_label, (x_pos, y_pos))


def draw_path(
    screen: pygame.Surface,
    path: List[Tuple[int, int]],
    offset_x: int = 0,
    offset_y: int = 0,
    thickness: int = 2,
) -> None:
    if not path or len(path) < 2:
        return

    try:
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            px1 = offset_x + x1 * CELL_SIZE + CELL_SIZE // 2
            py1 = offset_y + y1 * CELL_SIZE + CELL_SIZE // 2
            px2 = offset_x + x2 * CELL_SIZE + CELL_SIZE // 2
            py2 = offset_y + y2 * CELL_SIZE + CELL_SIZE // 2

            pygame.draw.line(
                screen,
                COLOR_PATH,
                (int(px1), int(py1)),
                (int(px2), int(py2)),
                int(thickness),
            )
    except Exception as e:
        print(f"Error drawing line: {e}")


def draw_button(
    screen: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    x: int,
    y: int,
    size: Tuple[int, int],
    color: Tuple[int, int, int],
    hover_color: Tuple[int, int, int],
    text_color: Tuple[int, int, int],
) -> bool:
    mouse_pos = pygame.mouse.get_pos()
    clicked = False
    rect = pygame.Rect(x, y, size[0], size[1])

    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(screen, hover_color, rect)

        if pygame.mouse.get_pressed()[0]:
            clicked = True
    else:
        pygame.draw.rect(screen, color, rect)

    draw_text(screen, text, font, rect.centerx, rect.centery, text_color, center=True)

    return clicked


def get_cell_from_mouse(
    mouse_pos: Tuple[int, int],
    offset_x: int = 0,
    offset_y: int = 0,
) -> Optional[Tuple[int, int]]:
    x = (mouse_pos[0] - offset_x) // CELL_SIZE
    y = (mouse_pos[1] - offset_y) // CELL_SIZE

    return (x, y)


def save_screen(screen: pygame.Surface, filepath: str) -> bool:

    try:
        pygame.image.save(screen, filepath)
        return True
    except Exception as e:
        print(f"Error saving screen: {e}")
        return False
