from .parameter import GRID_MAP_HEIGHT, GRID_MAP_WIDTH

GRID_CELL_SIZE = 13
TEXT_FONT = "Consolas"

SMALL_TEXT_SIZE = 16
NORMAL_TEXT_SIZE = 20
LARGE_TEXT_SIZE = 24

TKINTER_ALGOR_WINDOW_SIZE = "300x300"
TKINTER_BATCH_WINDOW_SIZE = "300x150"
TKINTER_TEXT_SIZE = 13
TKINTER_TEXT_FONT = "Arial"

WINDOW_HEIGHT = 700
WINDOW_WIDTH = 1260

NAV_HEIGHT = WINDOW_HEIGHT
NAV_WIDTH = 250
NAV_OFFSET_X = 10
NAV_OFFSET_Y = 20
NAV_MENU = [
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
    "[V] Toggle Animate",
    "[B] Batch test",
    "[<] Speed -",
    "[>] Speed +",
    "",
    "[P] Setting",
    "[ESC] Quit",
]

MODE_HEIGHT = 50
MODE_WIDTH = WINDOW_WIDTH - NAV_WIDTH
MODE_OFFSET_X = NAV_WIDTH + 20
MODE_OFFSET_Y = 20

GRID_SIDE_HEIGHT = WINDOW_HEIGHT - MODE_HEIGHT
GRID_SIDE_WIDTH = WINDOW_WIDTH - NAV_WIDTH

GRID_OFFSET_X = (GRID_SIDE_WIDTH - (GRID_CELL_SIZE * GRID_MAP_WIDTH)) // 2 + NAV_WIDTH
GRID_OFFSET_Y = (
    GRID_SIDE_HEIGHT - (GRID_CELL_SIZE * GRID_MAP_HEIGHT)
) // 2 + MODE_HEIGHT
