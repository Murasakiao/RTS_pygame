import pygame
import sys
import random
import math
import noise

from constants import *
from entities import *
from src.procedural import TerrainGenerator

from pygame.locals import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kingdom Conquer")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)

# --- Game Initialization ---
gold = 150
resources = {"wood": 200, "stone": 200, "food": 200, "people": 3}
resource_increase_rates = {
    "gold": 3, "wood": 2, "stone": 1, "food": 1, "people": 0.1
}

# --- Grid Setup ---
grid_width = SCREEN_WIDTH // GRID_SIZE
grid_height = SCREEN_HEIGHT // GRID_SIZE
grid = [[0 for _ in range(grid_width)] for _ in range(grid_height)]

def update_grid(buildings):
    """Updates the grid based on building positions."""
    for y in range(grid_height):
        for x in range(grid_width):
            grid[y][x] = 0  # Clear the grid
    for building in buildings:
        for x in range(building.rect.left // GRID_SIZE, building.rect.right // GRID_SIZE):
            for y in range(building.rect.top // GRID_SIZE, building.rect.bottom // GRID_SIZE):
                if 0 <= x < grid_width and 0 <= y < grid_height:
                    grid[y][x] = 1  # Mark cells occupied by buildings

buildings = []
units = []
enemies = []
game_messages = [] # Initialize game_messages list

current_building_type = "Castle"
building_cooldown = 0
selected_unit = None

terrain_generator = TerrainGenerator(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, noise)
terrain = terrain_generator.generate_terrain()

wave_timer = 0
current_wave = 1

building_map = {
    K_1: "Castle", K_2: "House", K_3: "Market", K_4: "Barracks",
    K_5: "Stable", K_6: "Farm", K_7: "LumberMill", K_8: "Quarry",
}

# --- Menu ---

def draw_button(screen, text, color, rect, border_color=BLACK, border_width=2, opacity=255):
    pygame.draw.rect(screen, border_color, rect, border_width)  # Draw border directly on screen
    button_surface = pygame.Surface((rect[2] - 2 * border_width, rect[3] - 2 * border_width), pygame.SRCALPHA) # Create a surface with per-pixel alpha, adjusted for border
    pygame.draw.rect(button_surface, color, (0, 0, rect[2] - 2 * border_width, rect[3] - 2 * border_width))  # Button background
    button_surface.set_alpha(opacity) # Set opacity of the button surface
    screen.blit(button_surface, (rect[0] + border_width, rect[1] + border_width)) # Blit the button surface onto the screen, offset by border width
    button_text = font.render(text, True, BLACK)
    text_rect = button_text.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
    screen.blit(button_text, text_rect)

# Create terrain background
terrain_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
terrain_generator.draw_terrain(terrain_background)

# Load and scale logo
logo = pygame.transform.scale(pygame.image.load("buildings/castle.png"), (150, 150))

title_font = pygame.font.Font(None, 50)  # Larger font for title
title_text = title_font.render("KINGDOM CONQUER", True, BLACK)
title_text_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

while menu_running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            menu_running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if start_button.collidepoint(event.pos):
                game_running = True
                menu_running = False  # Exit menu loop
            elif exit_button.collidepoint(event.pos):
                menu_running = False


    screen.blit(terrain_background, (0, 0))
    screen.blit(logo, logo_rect)  # Draw logo
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 60, 120, 30)
    exit_button = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 100, 120, 30)
    screen.blit(title_text, title_text_rect)  # Draw title


    # Draw menu elements with styling
    draw_button(screen, "Start New Game", GREEN, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 60, 120, 30), opacity=50) # Example opacity value
    draw_button(screen, "Exit", RED, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 + 100, 120, 30), opacity=150) # Example opacity value

    pygame.display.flip()

# --- Game Loop ---

game_messages = []
while game_running:
    # Update the grid at the beginning of the game loop
    update_grid(buildings)

    dt = clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    mouse_pos = pygame.mouse.get_pos()
    debug_info = [
        f"FPS: {int(clock.get_fps())}",
        f"Buildings: {len(buildings)}",
        f"Units: {len(units)}",
        f"Enemies: {len(enemies)}",
        f"Mouse Position: {mouse_pos}",
        f"Selected Unit: {selected_unit.type if selected_unit else 'None'}",
        f"Current Wave: {current_wave}",
        # f"Gold: {int(gold)}",
        # f"Resources: {int(resources['gold'])}, {int(resources['wood'])}, {int(resources['stone'])}, {int(resources['food'])}, {int(resources['people'])}",
        # Add more debug variables as needed
    ]

    # --- Resource Management ---
    building_counts = {}
    for building in buildings:
        building_counts[building.type] = building_counts.get(building.type, 0) + 1

    resource_multipliers = {
        "gold": 1 + (building_counts.get("Market", 0) * 0.1) + (building_counts.get("Castle", 0) * 0.2),
        "wood": 1 + (building_counts.get("LumberMill", 0) * 0.15) + (building_counts.get("Castle", 0) * 0.1),
        "stone": 1 + (building_counts.get("Quarry", 0) * 0.12) + (building_counts.get("Castle", 0) * 0.15),
        "food": 1 + (building_counts.get("Farm", 0) * 0.2) + (building_counts.get("Castle", 0) * 0.1),
        "people": 1 + (building_counts.get("House", 0) * 0.0005) + (building_counts.get("Castle", 0) * 0.001),
    }

    for resource, rate in resource_increase_rates.items():
        multiplier = resource_multipliers.get(resource, 1)
        increase = rate * multiplier * (dt / 1000)
        if resource == "gold":
            gold += increase
        else:
            resources[resource] += increase

    # --- Building Cooldown ---
    building_cooldown = max(0, building_cooldown - dt)

    # --- Preview Rect ---
    if not selected_unit:
        preview_rect = update_preview_rect(mouse_pos, current_building_type)
        collision = check_collision(preview_rect, buildings, units) if preview_rect else False
    else:
        preview_rect = None  # No preview while unit is selected
        collision = False

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == QUIT:
            game_running = False
        elif event.type == KEYDOWN:
            if event.key in building_map:
                current_building_type = building_map[event.key]
                selected_unit = None  # Deselect unit when switching building
            elif event.key == pygame.K_ESCAPE:
                current_building_type = None
            elif event.key == K_t:
                terrain = terrain_generator.generate_terrain()
            elif event.key == K_d:  # 'D' key to toggle debug info display
                show_debug = not show_debug
                print(grid)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Unit Selection
                clicked_unit = None
                for unit in units:
                    if unit.rect.collidepoint(mouse_pos):
                        clicked_unit = unit
                        break

                if clicked_unit:
                    selected_unit = clicked_unit
                    add_game_message(f"Selected {clicked_unit.type}", game_messages)
                    current_building_type = None
                    continue  # Skip building placement

                # Building Placement / Unit Training
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE

                clicked_building = next((building for building in buildings if building.rect.collidepoint(mouse_pos)), None)

                if clicked_building and "unit" in BUILDING_DATA[clicked_building.type]:
                    unit_type = BUILDING_DATA[clicked_building.type]["unit"]
                    unit_cost = ALLY_DATA[unit_type]["cost"]
                    speed = 50
                    if all(resources.get(resource, gold) >= amount for resource, amount in unit_cost.items()):
                        new_unit = AlliedUnit(unit_type, clicked_building.x, clicked_building.y + GRID_SIZE, enemies)
                        units.append(new_unit)
                        for resource, amount in unit_cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                        add_game_message(f"Trained {unit_type}", game_messages)
                    else:
                        add_game_message(f"Not enough resources to train {unit_type}", game_messages)

                elif current_building_type and not collision and building_cooldown <= 0:
                    castle_exists = any(building.type == "Castle" for building in buildings)
                    if current_building_type == "Castle" and castle_exists:
                        add_game_message("Only one castle can be built.", game_messages)
                    else:
                        cost = BUILDING_DATA[current_building_type].get("resources", {})
                        affordable = all(resources.get(resource, gold) >= amount for resource, amount in cost.items())
                        if affordable:
                            new_building = Building(grid_x, grid_y, current_building_type)
                            buildings.append(new_building)
                            for resource, amount in cost.items():
                                if resource == "gold":
                                    gold -= amount
                                else:
                                    resources[resource] -= amount
                            building_cooldown = BUILDING_COOLDOWN_TIME
                            add_game_message(f"Built {current_building_type}", game_messages)
                        else:
                            add_game_message(f"Not enough resources to build {current_building_type}", game_messages)

            elif event.button == 3 and selected_unit:  # Move selected unit
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                selected_unit.destination = (grid_x, grid_y)
                selected_unit.moving = True

                # --- A* Grid Update ---
                start_grid_x = int(selected_unit.x // GRID_SIZE)
                start_grid_y = int(selected_unit.y // GRID_SIZE)
                end_grid_x = grid_x // GRID_SIZE
                end_grid_y = grid_y // GRID_SIZE

                # Update grid with start and end points (2)
                if 0 <= start_grid_x < grid_width and 0 <= start_grid_y < grid_height:
                    grid[start_grid_y][start_grid_x] = 2

                if 0 <= end_grid_x < grid_width and 0 <= end_grid_y < grid_height:
                    grid[end_grid_y][end_grid_x] = 2
                # --- End A* Grid Update ---

                print(selected_unit.destination)
                print(grid)

                # Find nearest target for the selected unit
                selected_unit.target = selected_unit.find_nearest_target()

                add_game_message(f"Moving {selected_unit.type}", game_messages)

    # --- Game Updates ---
    for unit in units:
        unit.targets = enemies  # Update targets for allied units
        unit.update(dt, game_messages)

    for enemy in enemies:
        enemy.targets = units + buildings  # Update targets for enemy units
        game_messages = enemy.update(dt, game_messages)

    if wave_timer >= WAVE_INTERVAL:
        new_enemies = spawn_enemies(buildings, units, current_wave, ENEMY_SPAWN_RATE)
        enemies.extend(new_enemies)
        wave_timer = 0
        current_wave += 1
    else:
        wave_timer += dt

    # Remove dead units and enemies
    enemies[:] = [enemy for enemy in enemies if enemy.hp > 0]
    units[:] = [unit for unit in units if unit.hp > 0]

    # --- Drawing ---
    screen.fill(WHITE)
    terrain_generator.draw_terrain(screen)

    draw_resources(screen, font, resources, gold)

    for building in buildings:
        building.draw(screen)
        # Update the building's HP here...
        if building.hp <= 0:
            buildings.remove(building)

    for unit in units:
        unit.draw(screen, units, buildings, enemies, show_debug)  # Pass show_debug here
        if unit == selected_unit:
            pygame.draw.rect(screen, GREEN, unit.rect, 2)

    for enemy in enemies:
        enemy.draw(screen, units, buildings, enemies, show_debug)  # Pass show_debug here as well

    draw_building_preview(screen, preview_rect, collision, resources, gold, current_building_type)
    draw_messages(screen, font, game_messages)
    draw_key_bindings(screen, font, building_map, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BUILDING_DATA)

    # print(wave_timer, current_wave)
    # Draw debug information if enabled
    if show_debug:
        draw_debug_info(screen, font, debug_info)
        draw_grid(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
