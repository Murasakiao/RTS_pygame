import random

from .constants import ENEMY_DATA, GRID_SIZE, SCREEN_HEIGHT, SCREEN_WIDTH
from .entities import EnemyUnit


def generate_spawn_point():
    """Return a random grid-aligned point on one map edge."""
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


def spawn_enemies(buildings, units, current_wave, enemy_spawn_rate):
    """Create the current wave's enemies at grid-aligned map-edge points."""
    grid_width = SCREEN_WIDTH // GRID_SIZE
    grid_height = SCREEN_HEIGHT // GRID_SIZE

    spawned_enemies = []
    for _ in range(current_wave * enemy_spawn_rate):
        spawn_x, spawn_y = generate_spawn_point()

        spawn_x = max(0, min(spawn_x, (grid_width - 1) * GRID_SIZE))
        spawn_y = max(0, min(spawn_y, (grid_height - 1) * GRID_SIZE))

        enemy_type = random.choice(list(ENEMY_DATA))
        spawned_enemies.append(
            EnemyUnit(enemy_type, spawn_x, spawn_y, buildings, units)
        )

    return spawned_enemies
