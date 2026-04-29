from typing import Tuple, NamedTuple

from config import CELL_SIZE


class LayoutConfig(NamedTuple):
    window_width: int
    window_height: int
    left_width: int
    right_width: int
    left_x: int
    left_y: int
    right_x: int
    right_y: int
    offset_x: int
    offset_y: int
    margin: int


def calculate_layout(
    grid_width: int,
    grid_height: int,
    target_width: int,
    target_height: int,
    margin: int = 10,
    axes_margin: int = 30,
    left_ratio: float = 0.6,
) -> LayoutConfig:
    content_width = grid_width * CELL_SIZE + axes_margin + 2 * margin
    dynamic_width = int(content_width / left_ratio)
    dynamic_height = grid_height * CELL_SIZE + axes_margin + 2 * margin

    window_width = max(dynamic_width, target_width)
    window_height = max(dynamic_height, target_height)

    content_width_actual = window_width - 2 * margin
    left_width = int(content_width_actual * left_ratio)
    right_width = int(content_width_actual * (1 - left_ratio))

    left_x = margin
    left_y = margin
    right_x = margin + left_width
    right_y = margin

    offset_x = left_x + axes_margin
    offset_y = left_y + axes_margin

    return LayoutConfig(
        window_width=window_width,
        window_height=window_height,
        left_width=left_width,
        right_width=right_width,
        left_x=left_x,
        left_y=left_y,
        right_x=right_x,
        right_y=right_y,
        offset_x=offset_x,
        offset_y=offset_y,
        margin=margin,
    )
