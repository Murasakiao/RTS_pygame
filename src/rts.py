import random

import pygame

from .assets import AssetLoader
from .astar import a_star
from .constants import (
    ALLY_DATA,
    BLACK,
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
from .game import FixedStepRunner, GameState
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


def update_grid(state):
    """Build a navigation grid from the current match terrain and buildings."""
    grid = [
        [(0, 0) for _ in range(state.grid_width)]
        for _ in range(state.grid_height)
    ]

    for y in range(state.grid_height):
        for x in range(state.grid_width):
            is_water = state.terrain[y][x] == len(
                state.terrain_generator.grass_tiles
            )
            grid[y][x] = (state.terrain[y][x], 1 if is_water else 0)

    for building in state.buildings:
        for x in range(
            building.rect.left // GRID_SIZE,
            building.rect.right // GRID_SIZE,
        ):
            for y in range(
                building.rect.top // GRID_SIZE,
                building.rect.bottom // GRID_SIZE,
            ):
                if 0 <= x < state.grid_width and 0 <= y < state.grid_height:
                    grid[y][x] = (grid[y][x][0], 1)

    return grid


def create_terrain_generator(assets, noise_seed):
    grass_tiles = [
        assets.image(
            f"tile.grass_{index}",
            (GRID_SIZE, GRID_SIZE),
        )
        for index in range(1, 7)
    ]
    water_tiles = [
        assets.image("tile.water_1", (GRID_SIZE, GRID_SIZE))
    ]
    return TerrainGenerator(
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        GRID_SIZE,
        noise_seed,
        grass_tiles,
        water_tiles,
    )


def create_match(assets):
    """Create a new terrain generator and a fresh, isolated match state."""
    terrain_generator = create_terrain_generator(
        assets,
        random.randint(0, 1000),
    )
    state = GameState.new_match(terrain_generator)
    state.grid = update_grid(state)
    return state


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


def building_image(assets, building_type):
    data = BUILDING_DATA[building_type]
    size_multiplier = data.get("size_multiplier", 1)
    size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
    return assets.image(data["asset_key"], size)


def unit_image(assets, unit_type):
    return assets.image(
        ALLY_DATA[unit_type]["asset_key"],
        (GRID_SIZE, GRID_SIZE),
    )


def handle_game_event(state, event, assets, entity_font, building_map):
    """Apply one input event to the current match state."""
    if event.type == pygame.QUIT:
        return False

    if event.type == pygame.KEYDOWN:
        if event.key in building_map:
            state.current_building_type = building_map[event.key]
            state.selected_unit = None
        elif event.key == pygame.K_ESCAPE:
            state.current_building_type = None
        elif event.key == pygame.K_t:
            state.terrain = state.terrain_generator.generate_terrain()
        elif event.key == pygame.K_d:
            state.show_debug = not state.show_debug
            print(state.grid)
        return True

    if event.type != pygame.MOUSEBUTTONDOWN:
        return True

    mouse_pos = event.pos
    if event.button == 1:
        clicked_unit = next(
            (
                unit
                for unit in state.units
                if unit.rect.collidepoint(mouse_pos)
            ),
            None,
        )

        if clicked_unit:
            state.selected_unit = clicked_unit
            add_game_message(
                f"Selected {clicked_unit.type}",
                state.game_messages,
            )
            state.current_building_type = None
            return True

        grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
        grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
        terrain_index = state.terrain[
            grid_y // GRID_SIZE
        ][grid_x // GRID_SIZE]
        is_water = terrain_index == len(state.terrain_generator.grass_tiles)

        if is_water:
            add_game_message("Cannot build in water!", state.game_messages)
            return True

        clicked_building = next(
            (
                building
                for building in state.buildings
                if building.rect.collidepoint(mouse_pos)
            ),
            None,
        )

        if clicked_building and "unit" in BUILDING_DATA[clicked_building.type]:
            unit_type = BUILDING_DATA[clicked_building.type]["unit"]
            unit_cost = ALLY_DATA[unit_type]["cost"]
            if all(
                state.resources.get(resource, state.gold) >= amount
                for resource, amount in unit_cost.items()
            ):
                new_unit = AlliedUnit(
                    unit_type,
                    clicked_building.x,
                    clicked_building.y + GRID_SIZE,
                    state.enemies,
                    unit_image(assets, unit_type),
                    entity_font,
                )
                state.units.append(new_unit)
                for resource, amount in unit_cost.items():
                    if resource == "gold":
                        state.gold -= amount
                    else:
                        state.resources[resource] -= amount
                add_game_message(
                    f"Trained {unit_type}",
                    state.game_messages,
                )
            else:
                add_game_message(
                    f"Not enough resources to train {unit_type}",
                    state.game_messages,
                )
            return True

        if state.current_building_type and state.building_cooldown <= 0:
            preview_rect = update_preview_rect(
                mouse_pos,
                state.current_building_type,
            )
            collision = check_collision(
                preview_rect,
                state.buildings,
                state.units,
            )
            if collision:
                return True

            castle_exists = any(
                building.type == "Castle" for building in state.buildings
            )
            if state.current_building_type == "Castle" and castle_exists:
                add_game_message(
                    "Only one castle can be built.",
                    state.game_messages,
                )
                return True

            cost = BUILDING_DATA[state.current_building_type].get(
                "resources",
                {},
            )
            affordable = all(
                state.resources.get(resource, state.gold) >= amount
                for resource, amount in cost.items()
            )
            if affordable:
                new_building = Building(
                    grid_x,
                    grid_y,
                    state.current_building_type,
                    building_image(assets, state.current_building_type),
                    entity_font,
                )
                state.buildings.append(new_building)
                for resource, amount in cost.items():
                    if resource == "gold":
                        state.gold -= amount
                    else:
                        state.resources[resource] -= amount
                state.building_cooldown = BUILDING_COOLDOWN_TIME
                add_game_message(
                    f"Built {state.current_building_type}",
                    state.game_messages,
                )
            else:
                add_game_message(
                    f"Not enough resources to build {state.current_building_type}",
                    state.game_messages,
                )
        return True

    if event.button == 3 and state.selected_unit:
        grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
        grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
        state.selected_unit.destination = (grid_x, grid_y)
        state.selected_unit.moving = True

        start_grid_x = int(state.selected_unit.x // GRID_SIZE)
        start_grid_y = int(state.selected_unit.y // GRID_SIZE)
        end_grid_x = grid_x // GRID_SIZE
        end_grid_y = grid_y // GRID_SIZE

        state.selected_unit.path = []
        path = a_star(
            state.grid,
            (start_grid_x, start_grid_y),
            (end_grid_x, end_grid_y),
        )

        if path:
            state.selected_unit.path = path
            add_game_message(
                f"Moving {state.selected_unit.type}",
                state.game_messages,
            )
        else:
            add_game_message(
                f"No path found for {state.selected_unit.type}",
                state.game_messages,
            )

        state.selected_unit.target = state.selected_unit.find_nearest_target()
        print(path)

    return True


def update_match(state, dt_ms, assets, entity_font):
    """Advance one fixed simulation step."""
    state.grid = update_grid(state)

    building_counts = {}
    for building in state.buildings:
        building_counts[building.type] = building_counts.get(building.type, 0) + 1

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

    for resource, rate in state.resource_increase_rates.items():
        multiplier = resource_multipliers.get(resource, 1)
        increase = rate * multiplier * (dt_ms / 1000)
        if resource == "gold":
            state.gold += increase
        else:
            state.resources[resource] += increase

    state.building_cooldown = max(0, state.building_cooldown - dt_ms)

    for unit in list(state.units):
        unit.targets = state.enemies
        unit.update(dt_ms, state.grid, state.game_messages)

    for enemy in list(state.enemies):
        enemy.targets = state.units + state.buildings
        state.game_messages = enemy.update(
            dt_ms,
            state.grid,
            state.game_messages,
        )

    if state.wave_timer >= WAVE_INTERVAL * state.current_wave:
        state.enemies.extend(
            spawn_enemies(
                state.buildings,
                state.units,
                state.current_wave,
                ENEMY_SPAWN_RATE,
                assets,
                entity_font,
            )
        )
        state.wave_timer = 0
        state.current_wave += 1
    else:
        state.wave_timer += dt_ms

    state.enemies[:] = [enemy for enemy in state.enemies if enemy.hp > 0]
    state.units[:] = [unit for unit in state.units if unit.hp > 0]
    state.buildings[:] = [
        building for building in state.buildings if building.hp > 0
    ]
    if state.selected_unit and state.selected_unit.hp <= 0:
        state.selected_unit = None


def draw_match(
    screen,
    state,
    hud_font,
    building_map,
    preview_rect,
    collision,
    fps,
):
    debug_info = [
        f"FPS: {int(fps)}",
        f"Buildings: {len(state.buildings)}",
        f"Units: {len(state.units)}",
        f"Enemies: {len(state.enemies)}",
        f"Mouse Position: {pygame.mouse.get_pos()}",
        f"Selected Unit: {state.selected_unit.type if state.selected_unit else 'None'}",
        f"Current Wave: {state.current_wave}",
    ]

    screen.fill(WHITE)
    state.terrain_generator.draw_terrain(screen)
    draw_resources(screen, hud_font, state.resources, state.gold)

    for building in state.buildings:
        building.draw(screen)

    for unit in state.units:
        unit.draw(
            screen,
            state.units,
            state.buildings,
            state.enemies,
            state.show_debug,
        )
        if unit == state.selected_unit:
            pygame.draw.rect(screen, GREEN, unit.rect, 2)

    for enemy in state.enemies:
        enemy.draw(
            screen,
            state.units,
            state.buildings,
            state.enemies,
            state.show_debug,
        )

    draw_building_preview(
        screen,
        preview_rect,
        collision,
        state.resources,
        state.gold,
        state.current_building_type,
    )
    draw_messages(screen, hud_font, state.game_messages)
    draw_key_bindings(
        screen,
        hud_font,
        building_map,
        SCREEN_WIDTH,
        SCREEN_HEIGHT,
        GRID_SIZE,
        BUILDING_DATA,
    )

    if state.show_debug:
        draw_debug_info(screen, hud_font, debug_info)
        draw_grid(screen)


def main():
    """Initialize Pygame, run one match, then shut Pygame down."""
    pygame.init()

    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Kingdom Conquer")
        assets = AssetLoader()
        menu_font = assets.font(20)
        title_font = assets.font(50)
        entity_font = assets.font(12)
        menu_clock = pygame.time.Clock()

        menu_terrain = create_terrain_generator(
            assets,
            random.randint(0, 1000),
        )
        terrain_background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        menu_terrain.draw_terrain(terrain_background)

        logo = assets.image("building.castle", (150, 150))
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

        menu_running = True
        game_running = False
        state = None

        while menu_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if start_button.collidepoint(event.pos):
                        state = create_match(assets)
                        game_running = True
                        menu_running = False
                    elif exit_button.collidepoint(event.pos):
                        menu_running = False

            screen.blit(terrain_background, (0, 0))
            screen.blit(logo, logo_rect)
            screen.blit(title_text, title_text_rect)
            draw_button(
                screen,
                menu_font,
                "Start New Game",
                GREEN,
                start_button,
                opacity=50,
            )
            draw_button(
                screen,
                menu_font,
                "Exit",
                RED,
                exit_button,
                opacity=150,
            )
            pygame.display.flip()
            menu_clock.tick(FPS)

        if not game_running or state is None:
            return 0

        runner = FixedStepRunner(pygame.time.Clock())
        while game_running:
            runner.begin_frame()

            for event in pygame.event.get():
                if not handle_game_event(
                    state,
                    event,
                    assets,
                    entity_font,
                    building_map,
                ):
                    game_running = False
                    break

            if not game_running:
                break

            runner.run_updates(
                lambda fixed_dt_ms: update_match(
                    state,
                    fixed_dt_ms,
                    assets,
                    entity_font,
                )
            )

            mouse_pos = pygame.mouse.get_pos()
            if not state.selected_unit:
                preview_rect = update_preview_rect(
                    mouse_pos,
                    state.current_building_type,
                )
                collision = check_collision(
                    preview_rect,
                    state.buildings,
                    state.units,
                )
            else:
                preview_rect = None
                collision = False

            draw_match(
                screen,
                state,
                menu_font,
                building_map,
                preview_rect,
                collision,
                runner.clock.get_fps(),
            )
            pygame.display.flip()

        return 0
    finally:
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main())
