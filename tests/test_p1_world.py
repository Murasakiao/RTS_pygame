import pygame

from src.world import (
    TerrainKind,
    TerrainTile,
    World,
    cell_to_pixel,
    pixel_to_cell,
)


def test_world_uses_stable_terrain_kinds_and_revisioned_navigation():
    world = World(
        16,
        [[
            TerrainTile(TerrainKind.GRASS, 4),
            TerrainTile(TerrainKind.WATER),
        ]],
    )
    initial_revision = world.navigation_revision

    assert world.terrain_at((0, 0)).kind is TerrainKind.GRASS
    assert world.is_water((1, 0))
    assert not world.is_walkable((1, 0))

    world.rebuild_navigation()
    assert world.navigation_revision == initial_revision

    class BuildingFixture:
        rect = pygame.Rect(0, 0, 16, 16)

    world.rebuild_navigation([BuildingFixture()])
    assert world.navigation_revision == initial_revision + 1
    assert not world.is_walkable((0, 0))


def test_geometry_helpers_round_trip_cell_coordinates():
    cell = (7, 3)
    pixels = cell_to_pixel(cell, 16)
    assert pixels == (112, 48)
    assert pixel_to_cell((pixels[0] + 5, pixels[1] + 9), 16) == cell
