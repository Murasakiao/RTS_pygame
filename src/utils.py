import pygame

from .constants import (
    BLACK,
    BUILDING_DATA,
    GREEN,
    GRID_SIZE,
    MESSAGE_DURATION,
    RED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .world import cell_to_pixel, pixel_to_cell


def draw_grid(screen, color=BLACK, line_width=1, opacity=150):
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(
                surface,
                (*color, opacity),
                (x, 0),
                (x, SCREEN_HEIGHT),
                line_width,
            )
            pygame.draw.line(
                surface,
                (*color, opacity),
                (0, y),
                (SCREEN_WIDTH, y),
                line_width,
            )
    screen.blit(surface, (0, 0))


def add_game_message(message, game_messages, duration=MESSAGE_DURATION):
    current_time = pygame.time.get_ticks()
    game_messages[:] = [
        msg
        for msg in game_messages
        if current_time - msg["start_time"] < msg["duration"]
    ]

    if not any(msg["text"] == message for msg in game_messages):
        game_messages.append(
            {
                "text": message,
                "start_time": current_time,
                "duration": duration,
            }
        )


def update_preview_rect(mouse_pos, current_building_type):
    cell = pixel_to_cell(mouse_pos, GRID_SIZE)
    grid_x, grid_y = cell_to_pixel(cell, GRID_SIZE)
    size_multiplier = BUILDING_DATA.get(current_building_type, {}).get(
        "size_multiplier", 1
    )
    size = GRID_SIZE * size_multiplier
    return pygame.Rect(grid_x, grid_y, size, size)


def draw_resources(screen, font, resources, gold):
    resource_text = f"Gold: {int(gold)}"
    for resource, amount in resources.items():
        resource_text += f", {resource.capitalize()}: {int(amount)}"
    gold_text = font.render(resource_text, True, BLACK)
    screen.blit(gold_text, (10, 10))


def draw_building_preview(
    screen, preview_rect, collision, resources, gold, current_building_type
):
    if preview_rect:
        building_resources = BUILDING_DATA.get(current_building_type, {}).get(
            "resources", {}
        )
        affordable = all(
            resources.get(resource, gold) >= amount
            for resource, amount in building_resources.items()
        )
        color = GREEN if not collision and affordable else RED
        pygame.draw.rect(screen, color, preview_rect, 2)


def draw_messages(screen, font, game_messages):
    current_time = pygame.time.get_ticks()
    active_messages = [
        msg
        for msg in game_messages
        if current_time - msg["start_time"] < msg["duration"]
    ]
    for i, msg in enumerate(active_messages):
        message_text = font.render(msg["text"], True, RED)
        screen.blit(message_text, (10, 30 + i * 20))


def draw_key_bindings(
    screen, font, building_map, screen_width, screen_height, grid_size, building_data
):
    x = screen_width - 10 * grid_size
    y = 10
    for key, building_type in building_map.items():
        text = f"{pygame.key.name(key)}: {building_type}"
        requirements = building_data.get(building_type, {}).get("resources", {})
        if requirements:
            text += f" ({', '.join(f'{resource}: {amount}' for resource, amount in requirements.items())})"
        text_surface = font.render(text, True, RED)
        screen.blit(text_surface, (x, y))
        y += 20


def check_collision(preview_rect, buildings, units):
    for building in buildings:
        if preview_rect.colliderect(building.rect):
            return True
    for unit in units:
        if preview_rect.colliderect(unit.rect):
            return True
    return False


def draw_debug_info(screen, font, debug_info, x=10, y=40):
    for i, line in enumerate(debug_info):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (x, y + i * 20))


def check_collision_with_building(unit_rect, buildings):
    for building in buildings:
        if unit_rect.colliderect(building.rect):
            return True
    return False


def check_collision_with_unit(unit_rect, units, exclude_unit=None):
    for other_unit in units:
        if other_unit is not exclude_unit and unit_rect.colliderect(other_unit.rect):
            return True
    return False


def check_collision_with_enemy(unit_rect, enemies):
    for enemy in enemies:
        if unit_rect.colliderect(enemy.rect):
            return True
    return False
