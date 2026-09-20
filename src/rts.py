import random

import pygame

from .astar import a_star
from .constants import (
    ALLY_DATA,
    BLACK,
    BLUE,
    BUILDING_COOLDOWN_TIME,
    BUILDING_DATA,
    ENEMY_SPAWN_RATE,
    FPS,
    GREEN,
    GRID_SIZE,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    WAVE_INTERVAL,
    WHITE,
)
from .entities import AlliedUnit, Building
from .procedural import TerrainGenerator
from .spawning import spawn_enemies
from .utils import (
    add_game_message,
    check_collision,
    draw_building_preview,
    draw_debug_info,
    draw_grid,
    draw_key_bindings,
    draw_messages,
    draw_resources,
    update_preview_rect,
)


def update_grid(terrain, buildings, terrain_generator, grid_width, grid_height):
    """Build a navigation grid from terrain and building occupancy."""
    grid = [[(0, 0) for _ in range(grid_width)] for _ in range(grid_height)]

    for y in range(grid_height):
        for x in range(grid_width):
            is_water = terrain[y][x] == len(terrain_generator.grass_tiles)
            grid[y][x] = (terrain[y][x], 1 if is_water else 0)

    for building in buildings:
        for x in range(
            building.rect.left // GRID_SIZE,
            building.rect.right // GRID_SIZE,
        ):
            for y in range(
                building.rect.top // GRID_SIZE,
                building.rect.bottom // GRID_SIZE,
            ):
                if 0 <= x < grid_width and 0 <= y < grid_height:
                    grid[y][x] = (grid[y][x][0], 1)

    return grid


def draw_button(
    screen,
    font,
    text,
    color,
    rect,
    border_color=BLACK,
    border_width=2,
    opacity=255,
):
    rect = pygame.Rect(rect)
    pygame.draw.rect(screen, border_color, rect, border_width)
    button_surface = pygame.Surface(
        (rect.width - 2 * border_width, rect.height - 2 * border_width),
        pygame.SRCALPHA,
    )
    pygame.draw.rect(button_surface, color, button_surface.get_rect())
    button_surface.set_alpha(opacity)
    screen.blit(button_surface, (rect.left + border_width, rect.top + border_width))

    button_text = font.render(text, True, BLACK)
    text_rect = button_text.get_rect(center=rect.center)
    screen.blit(button_text, text_rect)


def main():
    """Initialize Pygame, run one match, then shut Pygame down."""
    pygame.init()

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Kingdom Conquer")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 20)

        gold = 150
        resources = {"wood": 200, "stone": 200, "food": 200, "people": 3}
        resource_increase_rates = {
            "gold": 1.5,
            "wood": 0.5,
            "stone": 0.5,
            "food": 0.25,
            "people": 0.1,
        }

        grid_width = SCREEN_WIDTH // GRID_SIZE
        grid_height = SCREEN_HEIGHT // GRID_SIZE

        buildings = []
        units = []
        enemies = []
        game_messages = []

        current_building_type = "Castle"
        building_cooldown = 0
        selected_unit = None

        noise_seed = random.randint(0, 1000)
        terrain_generator = TerrainGenerator(
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            GRID_SIZE,
            noise_seed,
        )
        terrain = terrain_generator.terrain
        grid = update_grid(
            terrain,
            buildings,
            terrain_generator,
            grid_width,
            grid_height,
        )

        wave_timer = 0
        current_wave = 1

        building_map = {
            pygame.K_1: "Castle",
            pygame.K_2: "House",
            pygame.K_3: "Market",
            pygame.K_4: "Barracks",
            pygame.K_5: "Stable",
            pygame.K_6: "Farm",
            pygame.K_7: "LumberMill",
            pygame.K_8: "Quarry",
        }

        terrain_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        terrain_generator.draw_terrain(terrain_background)

        logo = pygame.transform.scale(
            pygame.image.load("assets/buildings/castle.png"),
            (150, 150),
        )
        title_font = pygame.font.Font(None, 50)
        title_text = title_font.render("KINGDOM CONQUER", True, BLACK)
        title_text_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
        )
        logo_rect = logo.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
        )
        start_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 60,
            SCREEN_HEIGHT // 2 + 60,
            120,
            30,
        )
        exit_button = pygame.Rect(
            SCREEN_WIDTH // 2 - 60,
            SCREEN_HEIGHT // 2 + 100,
            120,
            30,
        )

        menu_running = True
        game_running = False
        show_debug = True

        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        game_running = True
                        menu_running = False
                    elif exit_button.collidepoint(event.pos):
                        menu_running = False

            screen.blit(terrain_background, (0, 0))
            screen.blit(logo, logo_rect)
            screen.blit(title_text, title_text_rect)
            draw_button(
                screen,
                font,
                "Start New Game",
                GREEN,
                start_button,
                opacity=50,
            )
            draw_button(
                screen,
                font,
                "Exit",
                RED,
                exit_button,
                opacity=150,
            )
            pygame.display.flip()
            clock.tick(FPS)

        if not game_running:
            return 0

        # Do not carry time spent in the menu into the first gameplay frame.
        clock = pygame.time.Clock()

        while game_running:
            grid = update_grid(
                terrain,
                buildings,
                terrain_generator,
                grid_width,
                grid_height,
            )

            dt = clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            debug_info = [
                f"FPS: {int(clock.get_fps())}",
                f"Buildings: {len(buildings)}",
                f"Units: {len(units)}",
                f"Enemies: {len(enemies)}",
                f"Mouse Position: {mouse_pos}",
                f"Selected Unit: {selected_unit.type if selected_unit else 'None'}",
                f"Current Wave: {current_wave}",
            ]

            building_counts = {}
            for building in buildings:
                building_counts[building.type] = (
                    building_counts.get(building.type, 0) + 1
                )

            resource_multipliers = {
                "gold": 1
                + (building_counts.get("Market", 0) * 0.1)
                + (building_counts.get("Castle", 0) * 0.2),
                "wood": 1
                + (building_counts.get("LumberMill", 0) * 0.15)
                + (building_counts.get("Castle", 0) * 0.1),
                "stone": 1
                + (building_counts.get("Quarry", 0) * 0.12)
                + (building_counts.get("Castle", 0) * 0.15),
                "food": 1
                + (building_counts.get("Farm", 0) * 0.2)
                + (building_counts.get("Castle", 0) * 0.1),
                "people": 1
                + (building_counts.get("House", 0) * 0.0005)
                + (building_counts.get("Castle", 0) * 0.001),
            }

            for resource, rate in resource_increase_rates.items():
                multiplier = resource_multipliers.get(resource, 1)
                increase = rate * multiplier * (dt / 1000)
                if resource == "gold":
                    gold += increase
                else:
                    resources[resource] += increase

            building_cooldown = max(0, building_cooldown - dt)

            if not selected_unit:
                preview_rect = update_preview_rect(
                    mouse_pos,
                    current_building_type,
                )
                collision = (
                    check_collision(preview_rect, buildings, units)
                    if preview_rect
                    else False
                )
            else:
                preview_rect = None
                collision = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in building_map:
                        current_building_type = building_map[event.key]
                        selected_unit = None
                    elif event.key == pygame.K_ESCAPE:
                        current_building_type = None
                    elif event.key == pygame.K_t:
                        terrain = terrain_generator.generate_terrain()
                    elif event.key == pygame.K_d:
                        show_debug = not show_debug
                        print(grid)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    if event.button == 1:
                        clicked_unit = next(
                            (
                                unit
                                for unit in units
                                if unit.rect.collidepoint(mouse_pos)
                            ),
                            None,
                        )

                        if clicked_unit:
                            selected_unit = clicked_unit
                            add_game_message(
                                f"Selected {clicked_unit.type}",
                                game_messages,
                            )
                            current_building_type = None
                            continue

                        grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                        grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                        terrain_index = terrain[
                            grid_y // GRID_SIZE
                        ][grid_x // GRID_SIZE]
                        is_water = terrain_index == len(
                            terrain_generator.grass_tiles
                        )

                        if is_water:
                            add_game_message(
                                "Cannot build in water!",
                                game_messages,
                            )
                            continue

                        clicked_building = next(
                            (
                                building
                                for building in buildings
                                if building.rect.collidepoint(mouse_pos)
                            ),
                            None,
                        )

                        if clicked_building and "unit" in BUILDING_DATA[
                            clicked_building.type
                        ]:
                            unit_type = BUILDING_DATA[clicked_building.type][
                                "unit"
                            ]
                            unit_cost = ALLY_DATA[unit_type]["cost"]
                            if all(
                                resources.get(resource, gold) >= amount
                                for resource, amount in unit_cost.items()
                            ):
                                new_unit = AlliedUnit(
                                    unit_type,
                                    clicked_building.x,
                                    clicked_building.y + GRID_SIZE,
                                    enemies,
                                )
                                units.append(new_unit)
                                for resource, amount in unit_cost.items():
                                    if resource == "gold":
                                        gold -= amount
                                    else:
                                        resources[resource] -= amount
                                add_game_message(
                                    f"Trained {unit_type}",
                                    game_messages,
                                )
                            else:
                                add_game_message(
                                    f"Not enough resources to train {unit_type}",
                                    game_messages,
                                )

                        elif (
                            current_building_type
                            and not collision
                            and building_cooldown <= 0
                        ):
                            castle_exists = any(
                                building.type == "Castle"
                                for building in buildings
                            )
                            if (
                                current_building_type == "Castle"
                                and castle_exists
                            ):
                                add_game_message(
                                    "Only one castle can be built.",
                                    game_messages,
                                )
                            else:
                                cost = BUILDING_DATA[
                                    current_building_type
                                ].get("resources", {})
                                affordable = all(
                                    resources.get(resource, gold) >= amount
                                    for resource, amount in cost.items()
                                )
                                if affordable:
                                    new_building = Building(
                                        grid_x,
                                        grid_y,
                                        current_building_type,
                                    )
                                    buildings.append(new_building)
                                    for resource, amount in cost.items():
                                        if resource == "gold":
                                            gold -= amount
                                        else:
                                            resources[resource] -= amount
                                    building_cooldown = BUILDING_COOLDOWN_TIME
                                    add_game_message(
                                        f"Built {current_building_type}",
                                        game_messages,
                                    )
                                else:
                                    add_game_message(
                                        f"Not enough resources to build {current_building_type}",
                                        game_messages,
                                    )

                    elif event.button == 3 and selected_unit:
                        grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                        grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                        selected_unit.destination = (grid_x, grid_y)
                        selected_unit.moving = True

                        start_grid_x = int(selected_unit.x // GRID_SIZE)
                        start_grid_y = int(selected_unit.y // GRID_SIZE)
                        end_grid_x = grid_x // GRID_SIZE
                        end_grid_y = grid_y // GRID_SIZE

                        selected_unit.path = []
                        path = a_star(
                            grid,
                            (start_grid_x, start_grid_y),
                            (end_grid_x, end_grid_y),
                        )

                        if path:
                            selected_unit.path = path
                            add_game_message(
                                f"Moving {selected_unit.type}",
                                game_messages,
                            )
                        else:
                            selected_unit.path = []
                            add_game_message(
                                f"No path found for {selected_unit.type}",
                                game_messages,
                            )

                        selected_unit.target = selected_unit.find_nearest_target()
                        print(path)

            for unit in units:
                unit.targets = enemies
                unit.update(dt, grid, game_messages)

            for enemy in enemies:
                enemy.targets = units + buildings
                game_messages = enemy.update(dt, grid, game_messages)

            if wave_timer >= WAVE_INTERVAL * current_wave:
                new_enemies = spawn_enemies(
                    buildings,
                    units,
                    current_wave,
                    ENEMY_SPAWN_RATE,
                )
                enemies.extend(new_enemies)
                wave_timer = 0
                current_wave += 1
            else:
                wave_timer += dt

            enemies[:] = [enemy for enemy in enemies if enemy.hp > 0]
            units[:] = [unit for unit in units if unit.hp > 0]

            screen.fill(WHITE)
            terrain_generator.draw_terrain(screen)
            draw_resources(screen, font, resources, gold)

            for building in buildings:
                building.draw(screen)
                if building.hp <= 0:
                    buildings.remove(building)

            for unit in units:
                unit.draw(
                    screen,
                    units,
                    buildings,
                    enemies,
                    show_debug,
                )
                if unit == selected_unit:
                    pygame.draw.rect(screen, GREEN, unit.rect, 2)

            for enemy in enemies:
                enemy.draw(
                    screen,
                    units,
                    buildings,
                    enemies,
                    show_debug,
                )

            draw_building_preview(
                screen,
                preview_rect,
                collision,
                resources,
                gold,
                current_building_type,
            )
            draw_messages(screen, font, game_messages)
            draw_key_bindings(
                screen,
                font,
                building_map,
                SCREEN_WIDTH,
                SCREEN_HEIGHT,
                GRID_SIZE,
                BUILDING_DATA,
            )

            if show_debug:
                draw_debug_info(screen, font, debug_info)
                draw_grid(screen)

            pygame.display.flip()

        return 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
