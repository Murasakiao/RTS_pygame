import pygame

from src.entities import Building, EnemyUnit
from src.world import (
    TerrainKind,
    TerrainTile,
    World,
    cell_rect,
    rectangle_gap,
    rect_cells,
)


def make_world(width=8, height=8):
    return World(
        16,
        [
            [TerrainTile(TerrainKind.GRASS) for _ in range(width)]
            for _ in range(height)
        ],
    )


def make_assets():
    pygame.init()
    return (
        pygame.Surface((16, 16)),
        pygame.Surface((32, 32)),
        pygame.font.Font(None, 12),
    )


def test_rectangle_gap_treats_touching_edges_as_in_range():
    assert rectangle_gap((0, 0, 16, 16), (16, 0, 16, 16)) == 0
    assert rectangle_gap((0, 0, 16, 16), (32, 0, 16, 16)) == 16


def test_world_line_of_sight_passes_water_but_stops_at_buildings():
    world = make_world(6, 3)
    first = (0, 16, 16, 16)
    target = (80, 16, 16, 16)

    assert world.has_line_of_sight(first, target)

    world.terrain[1][2] = TerrainTile(TerrainKind.WATER)
    world.rebuild_navigation()
    assert world.has_line_of_sight(first, target)

    world.terrain[1][2] = TerrainTile(TerrainKind.GRASS)
    _, building_image, font = make_assets()
    blocker = Building(32, 16, "House", building_image, font)
    world.rebuild_navigation([blocker])
    assert not world.has_line_of_sight(first, target)
    pygame.quit()


def test_world_provides_reachable_attack_cells_around_a_building():
    world = make_world()
    _, building_image, font = make_assets()
    building = Building(32, 32, "Castle", building_image, font)
    world.rebuild_navigation([building])

    candidates = world.attack_cells(building.rect, (16, 16), 15)

    assert candidates
    assert all(cell not in set(rect_cells(building.rect, 16)) for cell in candidates)
    assert all(
        rectangle_gap(cell_rect(cell, 16), building.rect) <= 15
        for cell in candidates
    )
    pygame.quit()


def test_enemy_routes_around_hidden_target_instead_of_staying_idle():
    unit_image, building_image, font = make_assets()
    try:
        world = make_world(12, 8)
        for y in range(world.height):
            if y != 6:
                world.terrain[y][5] = TerrainTile(TerrainKind.WATER)
        building = Building(144, 48, "Castle", building_image, font)
        world.rebuild_navigation([building])
        enemy = EnemyUnit(
            "Goblin",
            0,
            48,
            [building],
            [],
            unit_image,
            font,
        )

        enemy.update(33, world, [])

        assert enemy.target is building
        assert enemy.path
    finally:
        pygame.quit()


def test_enemy_routes_to_a_reachable_building_attack_position():
    unit_image, building_image, font = make_assets()
    try:
        world = make_world()
        building = Building(32, 32, "Castle", building_image, font)
        world.rebuild_navigation([building])
        enemy = EnemyUnit(
            "Goblin",
            0,
            32,
            [building],
            [],
            unit_image,
            font,
        )

        enemy.update(33, world, [])

        assert enemy.target is building
        assert enemy.path
        assert enemy.route_revision == world.navigation_revision
    finally:
        pygame.quit()


def test_unreachable_attack_position_uses_bounded_retry():
    unit_image, building_image, font = make_assets()
    try:
        world = make_world(7, 7)
        building = Building(48, 48, "Castle", building_image, font)
        enemy_cell = (0, 3)
        target_cells = set(rect_cells(building.rect, 16))
        for y in range(world.height):
            for x in range(world.width):
                if (x, y) not in target_cells and (x, y) != enemy_cell:
                    world.terrain[y][x] = TerrainTile(TerrainKind.WATER)
        world.rebuild_navigation([building])
        enemy = EnemyUnit(
            "Goblin",
            0,
            48,
            [building],
            [],
            unit_image,
            font,
        )

        enemy.issue_attack(building)
        enemy.update(33, world, [])

        assert enemy.path == []
        assert enemy.path_retry_timer > 0
        assert enemy.destination is None
    finally:
        pygame.quit()
