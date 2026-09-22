import random

from .constants import ENEMY_DATA, GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from .entities import EnemyUnit
from .world import cell_to_pixel


def _legacy_spawn_point():
    """Return an edge point for callers that do not yet have a World."""
    grid_width = SCREEN_WIDTH // GRID_SIZE
    grid_height = SCREEN_HEIGHT // GRID_SIZE
    side = random.choice(("top", "bottom", "left", "right"))
    if side == "top":
        return random.randint(0, grid_width - 1) * GRID_SIZE, 0
    if side == "bottom":
        return random.randint(0, grid_width - 1) * GRID_SIZE, (grid_height - 1) * GRID_SIZE
    if side == "left":
        return 0, random.randint(0, grid_height - 1) * GRID_SIZE
    return (grid_width - 1) * GRID_SIZE, random.randint(0, grid_height - 1) * GRID_SIZE


def generate_spawn_point(world=None, buildings=(), units=(), enemies=()):
    """Return a random valid, free map-edge point when a World is available."""
    if world is None:
        return _legacy_spawn_point()

    candidates = []
    for x in range(world.width):
        candidates.extend(((x, 0), (x, world.height - 1)))
    for y in range(1, world.height - 1):
        candidates.extend(((0, y), (world.width - 1, y)))
    random.shuffle(candidates)

    for cell in candidates:
        if world.is_cell_free(cell, buildings, units, enemies):
            return cell_to_pixel(cell, world.grid_size)
    return None


def spawn_enemies(
    world,
    buildings,
    units,
    enemies,
    current_wave,
    enemy_spawn_rate,
    asset_loader,
    entity_font,
):
    """Create enemies only at validated, free map-edge cells."""
    spawned_enemies = []
    occupied_enemies = list(enemies)
    for _ in range(current_wave * enemy_spawn_rate):
        spawn_point = generate_spawn_point(
            world,
            buildings,
            units,
            occupied_enemies,
        )
        if spawn_point is None:
            break

        spawn_x, spawn_y = spawn_point
        enemy_type = random.choice(list(ENEMY_DATA))
        image = asset_loader.image(
            ENEMY_DATA[enemy_type]["asset_key"],
            (GRID_SIZE, GRID_SIZE),
        )
        enemy = EnemyUnit(
            enemy_type,
            spawn_x,
            spawn_y,
            buildings,
            units,
            image,
            entity_font,
        )
        spawned_enemies.append(enemy)
        occupied_enemies.append(enemy)

    return spawned_enemies
