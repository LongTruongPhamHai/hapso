BLACK: tuple[int, int, int] = (0, 0, 0)
MEDIUM: tuple[int, int, int] = (140, 140, 140)
LIGHT: tuple[int, int, int] = (200, 200, 200)
WHITE: tuple[int, int, int] = (255, 255, 255)

HEX_MEDIUM = f"#{MEDIUM[0]:02x}{MEDIUM[1]:02x}{MEDIUM[2]:02x}"

RED: tuple[int, int, int] = (255, 0, 0)
ORANGE: tuple[int, int, int] = (255, 127, 0)
YELLOW: tuple[int, int, int] = (255, 255, 0)
GREEN: tuple[int, int, int] = (0, 255, 0)
BLUE: tuple[int, int, int] = (0, 127, 255)
INDIGO: tuple[int, int, int] = (75, 0, 130)
VIOLET: tuple[int, int, int] = (148, 0, 211)

# ── Màu bổ sung cho visualization ──
DARK_GRAY: str = "#444441"  # Điểm đang xét (SOBL), trục x tick
CHART_BLUE: str = "#378ADD"  # Hạt gốc (SOBL)
CHART_ORANGE: str = "#D85A30"  # Điểm đối lập (SOBL)
CHART_GREEN: str = "#639922"  # Quỹ đạo A* (SOBL), màu quiver giai đoạn đầu
CHART_DARK_GREEN: str = "#1B6B1B"  # darkgreen (TVAC giai đoạn đầu)
CHART_MAGENTA: str = "#FF00FF"  # Điểm P_in / P_out (Bezier), quiver giai đoạn cuối
CHART_PURPLE: str = "#6A0DAD"  # Scatter giai đoạn cuối (TVAC)
CHART_GOLD: str = "#FFD700"  # Gbest marker (TVAC)

# CHART_COLORS = ["#1f77b4", "#17becf", "#2ca02c", "#9467bd"]
CHART_COLORS = ["#f0f0f0", "#f0f0f0", "#f0f0f0", "#f0f0f0"]
CHART_HATCHES = ["", "/", "x", "-"]
