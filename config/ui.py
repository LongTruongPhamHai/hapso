from .parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH

GRID_CELL_SIZE: int = 18
TEXT_FONT: str = "Consolas"

SMALL_TEXT_SIZE: int = 16
NORMAL_TEXT_SIZE: int = 20
LARGE_TEXT_SIZE: int = 24

TKINTER_ALGOR_WINDOW_SIZE: str = "300x300"
TKINTER_BATCH_WINDOW_SIZE: str = "300x150"
TKINTER_TEXT_SIZE: int = 13
TKINTER_TEXT_FONT: str = "Arial"

WINDOW_HEIGHT: int = 700
WINDOW_WIDTH: int = 1260

NAV_HEIGHT: int = WINDOW_HEIGHT
NAV_WIDTH: int = 250
NAV_OFFSET_X: int = 10
NAV_OFFSET_Y: int = 20
NAV_MENU: list[str] = [
    "[0] Free",
    "[1] Set obstacle",
    "[2] Erase obstacle",
    "[C] Clear map",
    "[S] Set start",
    "[G] Set goal",
    "[I] Import JSON",
    "[E] Export JSON",
    "",
    "[A] Select algorithm",
    "[Space] Run",
    "[R] Reset result",
    "[B] Batch test",
    "",
    "[P] Setting",
    "[ESC] Quit",
]

MODE_HEIGHT: int = 50
MODE_WIDTH: int = WINDOW_WIDTH - NAV_WIDTH
MODE_OFFSET_X: int = NAV_WIDTH + 20
MODE_OFFSET_Y: int = 20

GRID_SIDE_HEIGHT: int = WINDOW_HEIGHT - MODE_HEIGHT
GRID_SIDE_WIDTH: int = WINDOW_WIDTH - NAV_WIDTH

GRID_OFFSET_X: int = (
    GRID_SIDE_WIDTH - (GRID_CELL_SIZE * GRID_MAP_WIDTH)
) // 2 + NAV_WIDTH
GRID_OFFSET_Y: int = (
    GRID_SIDE_HEIGHT - (GRID_CELL_SIZE * GRID_MAP_HEIGHT)
) // 2 + MODE_HEIGHT
