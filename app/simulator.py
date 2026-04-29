import pygame
import math
from typing import List, Optional, Tuple

from algorithms.astar import Astar
from algorithms.pso import PSOPlanner
from algorithms.apso import APSO
from algorithms.hapso import HAPSO
from algorithms.hapso import HAPSO
from config import (
    COLOR_FREE,
    COLOR_OBSTACLE,
    DEFAULT_GRID_HEIGHT,
    DEFAULT_GRID_WIDTH,
    FONT_NORMAL,
    RESULTS_DIR,
    SIMULATION_WINDOW_HEIGHT,
    SIMULATION_WINDOW_WIDTH,
)
from environment.grid_map import GridMap
from .grid_editor import GridEditor
from .menu import MapMenu, StartMenu
from utils.message_handler import MessageHandler
from utils.layout_calculator import calculate_layout
from utils.geometry import calculate_path_metrics
from utils.results_saver import save_all_results
from utils.visualization import draw_grid, draw_path


class PathfindingSimulator:
    def __init__(self):
        pygame.init()
        self.running = True
        self.grid: Optional[GridMap] = None
        self.current_path: Optional[List[Tuple[int, int]]] = None
        self.current_algorithm = 1
        self.algorithm_name = "A*"
        self.message_handler = MessageHandler()
        self.simulation_screen: Optional[pygame.Surface] = None
        self.path_metrics: Optional[dict] = None
        self.prune_collinear = False
        self.prune_transitions = False
        self.avoid_corner_cutting = False

    def run(self):
        while self.running:
            start_menu = StartMenu()
            choice = start_menu.run()

            if choice is None:
                print("Exiting application...")
                self.running = False
                break

            if choice == "new":
                print("Creating new map...")
                self._create_new_map()
            else:
                print("Loading map...")
                if not self._load_map():
                    continue

            if not self.running or self.grid is None:
                break

            if not self._edit_map():
                continue

            self._run_simulation()

        pygame.quit()
        print("Application closed.")

    def _create_new_map(self):
        self.grid = GridMap(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)

    def _load_map(self) -> bool:
        map_menu = MapMenu()
        map_path = map_menu.run()

        if map_path is None:
            print("Map loading cancelled.")
            return False

        self.grid = GridMap.load_from_path(map_path)
        if self.grid is None:
            print(f"Failed to load map from {map_path}")
            return False

        print(f"Map loaded successfully!")
        return True

    def _edit_map(self):
        if self.grid is None:
            self.grid = GridMap(DEFAULT_GRID_WIDTH, DEFAULT_GRID_HEIGHT)

        print("Opening grid editor...\nInstructions:")
        print("  - Click to toggle obstacles")
        print("  - Drag to draw obstacle lines")
        print("  - S: Set start position")
        print("  - G: Set goal position")
        print("  - ENTER or SPACE: Save and run simulation")
        print("  - C: Clear map")
        print("  - ESC: Return to menu")

        editor = GridEditor(self.grid)
        proceed_to_simulation = editor.run()

        if not proceed_to_simulation:
            print("Returning to menu...")
            return False

        print("Map ready! Starting simulation...")
        return True

    def _run_simulation(self):
        if self.grid is None or self.grid.start is None or self.grid.goal is None:
            print("Invalid grid. Returning to map creation.")
            return

        layout = calculate_layout(
            self.grid.width,
            self.grid.height,
            SIMULATION_WINDOW_WIDTH,
            SIMULATION_WINDOW_HEIGHT,
        )
        screen = pygame.display.set_mode((layout.window_width, layout.window_height))
        pygame.display.set_caption("Pathfinding Simulator")
        clock = pygame.time.Clock()
        font_normal = pygame.font.Font(None, FONT_NORMAL)

        self.simulation_screen = screen
        self.current_path = None
        self.path_metrics = None
        running = True

        print(f"\n{'='*60}")
        print(f"Algorithm: {self.algorithm_name}")
        print(f"Start: {self.grid.start}, Goal: {self.grid.goal}")
        print(f"{'='*60}")
        print("Controls:")
        print("  SPACE: Run algorithm")
        print("  1: A* |  2: PSO |  3: APSO |  4: HAPSO")
        print("  S: Save results | ESC: Exit")

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self._find_path()
                    elif event.key == pygame.K_1:
                        self.current_algorithm = 1
                        self.algorithm_name = "A*"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message("Algorithm switched to A*")
                        print("\nAlgorithm switched to A*")
                    elif event.key == pygame.K_2:
                        self.current_algorithm = 2
                        self.algorithm_name = "PSO"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message("Algorithm switched to PSO")
                        print("\nAlgorithm switched to PSO")
                    elif event.key == pygame.K_3:
                        self.current_algorithm = 3
                        self.algorithm_name = "APSO"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message("Algorithm switched to APSO")
                        print("\nAlgorithm switched to APSO")
                    elif event.key == pygame.K_4:
                        self.current_algorithm = 4
                        self.algorithm_name = "HAPSO"
                        self.current_path = None
                        self.path_metrics = None
                        self.message_handler.set_message("Algorithm switched to HAPSO")
                        print("\nAlgorithm switched to HAPSO")
                    elif event.key == pygame.K_s:
                        self._save_results()
                    elif event.key == pygame.K_c:
                        self.prune_collinear = not self.prune_collinear
                        status = "ON" if self.prune_collinear else "OFF"
                        self.message_handler.set_message(f"Prune collinear: {status}")
                        print(f"Prune collinear toggled to {status}")
                    elif event.key == pygame.K_t:
                        self.prune_transitions = not self.prune_transitions
                        status = "ON" if self.prune_transitions else "OFF"
                        self.message_handler.set_message(f"Prune transitions: {status}")
                        print(f"Prune transitions toggled to {status}")
                    elif event.key == pygame.K_n:
                        self.avoid_corner_cutting = not self.avoid_corner_cutting
                        status = "ON" if self.avoid_corner_cutting else "OFF"
                        self.message_handler.set_message(f"Corner cut guard: {status}")
                        print(f"Corner cut guard toggled to {status}")
                    elif event.key == pygame.K_i:
                        self._print_path_info()

            screen.fill(COLOR_FREE)
            draw_grid(screen, self.grid, layout.left_x, layout.left_y)
            if self.current_path:
                draw_path(
                    screen, self.current_path, layout.left_x, layout.left_y, thickness=3
                )
            y_offset = layout.right_y
            message = self.message_handler.get_message()
            if message:
                msg_surface = font_normal.render(message, True, COLOR_OBSTACLE)
                screen.blit(msg_surface, (layout.right_x, y_offset))
                y_offset += 30
            y_offset += 10
            algo_line = font_normal.render(
                f"Algorithm: {self.algorithm_name}", True, COLOR_OBSTACLE
            )
            screen.blit(algo_line, (layout.right_x, y_offset))
            y_offset += 40
            status_label = font_normal.render("Status:", True, COLOR_OBSTACLE)
            screen.blit(status_label, (layout.right_x, y_offset))
            y_offset += 25

            start_goal_text = font_normal.render(
                f"Start: {self.grid.start}   |   Goal: {self.grid.goal}",
                True,
                COLOR_OBSTACLE,
            )
            screen.blit(start_goal_text, (layout.right_x, y_offset))
            y_offset += 40
            path_label = font_normal.render("Path Info:", True, COLOR_OBSTACLE)
            screen.blit(path_label, (layout.right_x, y_offset))
            y_offset += 25

            collinear_text = font_normal.render(
                f"Prune collinear A* (C): {'ON' if self.prune_collinear else 'OFF'}",
                True,
                COLOR_OBSTACLE,
            )
            screen.blit(collinear_text, (layout.right_x, y_offset))
            y_offset += 20

            transition_text = font_normal.render(
                f"Prune transitions A* (T): {'ON' if self.prune_transitions else 'OFF'}",
                True,
                COLOR_OBSTACLE,
            )
            screen.blit(transition_text, (layout.right_x, y_offset))
            y_offset += 20

            corner_text = font_normal.render(
                f"Corner-cut guard A* (N): {'ON' if self.avoid_corner_cutting else 'OFF'}",
                True,
                COLOR_OBSTACLE,
            )
            screen.blit(corner_text, (layout.right_x, y_offset))
            y_offset += 20

            if self.current_path and self.path_metrics:
                length_text = font_normal.render(
                    f"Length: {self.path_metrics['length']:.1f}", True, COLOR_OBSTACLE
                )
                screen.blit(length_text, (layout.right_x, y_offset))
                y_offset += 20
                waypoint_text = font_normal.render(
                    f"Waypoints: {self.path_metrics['waypoint_count']}",
                    True,
                    COLOR_OBSTACLE,
                )
                screen.blit(waypoint_text, (layout.right_x, y_offset))
                y_offset += 20
            else:
                no_path_text = font_normal.render("No path yet", True, COLOR_OBSTACLE)
                screen.blit(no_path_text, (layout.right_x, y_offset))
            y_offset += 40
            instr_label = font_normal.render("Controls:", True, COLOR_OBSTACLE)
            screen.blit(instr_label, (layout.right_x, y_offset))
            y_offset += 25

            instructions = [
                "1: A* | 2: PSO | 3: APSO | 4: HAPSO",
                "SPACE: Run | S: Save",
                "I: Path Info | ESC: Exit",
                "C: Toggle prune collinear",
                "T: Toggle prune transitions",
                "N: Toggle corner cut guard",
            ]
            for instr in instructions:
                instr_text = font_normal.render(instr, True, COLOR_OBSTACLE)
                screen.blit(instr_text, (layout.right_x, y_offset))
                y_offset += 20

            pygame.display.flip()
            clock.tick(60)

    def _find_path(self):
        if self.grid is None or self.grid.start is None or self.grid.goal is None:
            self.message_handler.set_message("Invalid start or goal")
            return

        print(f"\nFinding path using {self.algorithm_name}...")

        try:
            if self.current_algorithm == 1:
                astar = Astar(
                    self.grid,
                    prune_collinear=self.prune_collinear,
                    prune_transitions=self.prune_transitions,
                    avoid_corner_cutting=self.avoid_corner_cutting,
                )
                self.current_path = astar.plan()
            elif self.current_algorithm == 2:
                pso = PSOPlanner(self.grid, num_waypoints=20)
                self.current_path = pso.plan()
            elif self.current_algorithm == 3:
                apso = APSO(
                    self.grid,
                    # APSO uses defaults: prune_collinear=True, prune_transitions=True, avoid_corner_cutting=False
                    # Toggle does NOT affect APSO
                    pso_swarm_size=30,
                    pso_max_iter=100,
                )
                self.current_path = apso.plan()
            elif self.current_algorithm == 4:
                hapso = HAPSO(
                    self.grid,
                    # HAPSO uses defaults: prune_collinear=True, prune_transitions=True, avoid_corner_cutting=True
                    # Toggle does NOT affect HAPSO
                    pso_swarm_size=30,
                    pso_max_iter=100,
                )
                self.current_path = hapso.plan()

            if self.current_path:
                self.path_metrics = calculate_path_metrics(self.grid, self.current_path)
                print(f"Path found! Length: {self.path_metrics['length']:.1f}")
                self.message_handler.set_message(
                    f"Path found! Length: {self.path_metrics['length']:.1f}"
                )
            else:
                print(f"No path found")
                self.message_handler.set_message("No path found!")
                self.path_metrics = None
        except Exception as e:
            print(f"Error during pathfinding: {e}")
            self.message_handler.set_message(f"Error: {str(e)[:50]}")
            self.path_metrics = None

    def _print_path_info(self):
        if self.current_path is None or self.path_metrics is None:
            print("\n⚠ No path found yet. Run algorithm first (press SPACE)")
            return

        print(f"\n{'='*60}")
        print(f"PATH INFORMATION - {self.algorithm_name}")
        print(f"{'='*60}")

        # Basic metrics
        print(f"\n📊 BASIC METRICS:")
        print(f"  Path length:      {self.path_metrics['length']:.2f} units")
        print(f"  Waypoint count:   {self.path_metrics['waypoint_count']}")
        print(f"  Start position:   {self.grid.start}")
        print(f"  Goal position:    {self.grid.goal}")

        # List all waypoints
        print(f"\n📍 WAYPOINTS LIST:")
        for idx, (x, y) in enumerate(self.current_path):
            if idx == 0:
                print(f"  [{idx}] ({x}, {y}) - START")
            elif idx == len(self.current_path) - 1:
                print(f"  [{idx}] ({x}, {y}) - GOAL")
            else:
                print(f"  [{idx}] ({x}, {y})")

        # Calculate turning angles if we have enough waypoints
        if len(self.current_path) > 2:
            angles = self._calculate_turning_angles()
            if angles:
                print(f"\n📐 TURNING ANGLES:")
                print(f"  Max turning angle:    {max(angles):.2f}°")
                print(f"  Min turning angle:    {min(angles):.2f}°")
                print(f"  Average turning:      {sum(angles)/len(angles):.2f}°")
                print(f"  Total turns:          {len(angles)}")

        # Path safety check
        collision_free = self._check_path_safety()
        print(f"\n✓ SAFETY CHECK:")
        print(f"  Collision-free:   {'Yes ✓' if collision_free else 'No ✗'}")

        print(f"{'='*60}\n")

    def _calculate_turning_angles(self) -> List[float]:
        """Calculate turning angles between consecutive path segments."""
        if self.current_path is None or len(self.current_path) < 3:
            return []

        angles = []
        for i in range(1, len(self.current_path) - 1):
            p1 = self.current_path[i - 1]
            p2 = self.current_path[i]
            p3 = self.current_path[i + 1]

            angle = self._angle_between_vectors(
                (p2[0] - p1[0], p2[1] - p1[1]), (p3[0] - p2[0], p3[1] - p2[1])
            )
            angles.append(angle)

        return angles

    def _angle_between_vectors(
        self, v1: Tuple[float, float], v2: Tuple[float, float]
    ) -> float:
        """Calculate angle between two vectors in degrees."""
        dot_product = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if mag1 == 0 or mag2 == 0:
            return 0.0

        cos_angle = dot_product / (mag1 * mag2)
        cos_angle = max(-1.0, min(1.0, cos_angle))
        angle_rad = math.acos(cos_angle)
        angle_deg = math.degrees(angle_rad)

        return angle_deg

    def _check_path_safety(self) -> bool:
        """Check if the path is free from collisions."""
        if self.grid is None or self.current_path is None:
            return False

        for x, y in self.current_path:
            if self.grid.grid[y][x] == 1:  # 1 means obstacle
                return False

        return True

    def _save_results(self):
        if self.grid is None or self.simulation_screen is None:
            self.message_handler.set_message("Cannot save - no simulation active")
            print("Cannot save results - no simulation active")
            return

        print(f"\nSaving results...")
        success, results_dir = save_all_results(
            self.simulation_screen,
            RESULTS_DIR,
            self.grid,
            self.current_path,
            self.algorithm_name,
        )

        if success:
            self.message_handler.set_message(f"Results saved to: results/<timestamp>")
            print(f"Results successfully saved!")
        else:
            self.message_handler.set_message("Failed to save results")
            print(f"Failed to save results")
