import pygame

from src.spawning import generate_spawn_point
from src.world import FootprintStatus, TerrainKind, TerrainTile, World


class ObjectWithRect:
    def __init__(self, rect):
        self.rect = rect


def grass_world(width=4, height=4):
    return World(
        16,
        [
            [TerrainTile(TerrainKind.GRASS) for _ in range(width)]
            for _ in range(height)
        ],
    )


def test_validate_footprint_checks_bounds_water_and_occupancy():
    world = grass_world()
    world.terrain[1][1] = TerrainTile(TerrainKind.WATER)
    world.rebuild_navigation()
    building = ObjectWithRect(pygame.Rect(2 * 16, 2 * 16, 16, 16))

    assert world.validate_footprint((0, 0), (1, 1)).status is FootprintStatus.VALID
    assert world.validate_footprint((3, 3), (2, 2)).status is FootprintStatus.OUT_OF_BOUNDS
    assert world.validate_footprint((1, 1), (1, 1)).status is FootprintStatus.WATER
    assert world.validate_footprint((2, 2), (1, 1), [building]).status is FootprintStatus.OCCUPIED


def test_training_exit_is_free_and_adjacent_to_the_footprint():
    world = grass_world()
    building = ObjectWithRect(pygame.Rect(16, 16, 16, 16))
    world.rebuild_navigation([building])

    exit_cell = world.find_free_exit((1, 1), (1, 1), [building])

    assert exit_cell in {(1, 0), (1, 2), (0, 1), (2, 1)}
    assert world.is_cell_free(exit_cell, [building])


def test_spawn_point_uses_free_edge_land():
    world = grass_world()
    edge_buildings = [
        ObjectWithRect(pygame.Rect(0, 0, 16, 16)),
        ObjectWithRect(pygame.Rect(16, 0, 16, 16)),
    ]
    world.rebuild_navigation(edge_buildings)

    point = generate_spawn_point(world, edge_buildings)

    assert point is not None
    cell = (point[0] // 16, point[1] // 16)
    assert cell[0] in {0, 3} or cell[1] in {0, 3}
    assert world.is_cell_free(cell, edge_buildings)
