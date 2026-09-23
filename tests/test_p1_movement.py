import pygame

from src.astar import a_star
from src.entities import AlliedUnit, Building, EnemyUnit
from src.orders import OrderKind, UnitOrder
from src.world import TerrainKind, TerrainTile, World


def make_unit():
    pygame.init()
    return AlliedUnit(
        "Swordsman",
        0,
        0,
        [],
        pygame.Surface((16, 16)),
        pygame.font.Font(None, 12),
    )


def test_route_consumes_remaining_distance_across_waypoints():
    unit = make_unit()
    try:
        grid = [[(0, 0), (0, 0), (0, 0)]]
        result = a_star(grid, (0, 0), (2, 0))
        unit.apply_path_result(result, (2, 0), 1)

        unit.move_towards_target(2000, grid, 1)

        assert (unit.x, unit.y) == (32, 0)
        assert unit.path == []
        assert unit.destination is None
        assert unit.destination_cell is None
    finally:
        pygame.quit()


def test_navigation_revision_invalidates_a_route_before_movement():
    unit = make_unit()
    try:
        open_grid = [[(0, 0), (0, 0), (0, 0)]]
        result = a_star(open_grid, (0, 0), (2, 0))
        unit.order = UnitOrder(OrderKind.MOVE, destination=(2, 0))
        unit.apply_path_result(result, (2, 0), 1)

        blocked_grid = [[(0, 0), (0, 1), (0, 0)]]
        unit.move_towards_target(1000, blocked_grid, 2)

        assert (unit.x, unit.y) == (0, 0)
        assert unit.path == []
        assert unit.destination is None
        assert unit.destination_cell == (2, 0)
    finally:
        pygame.quit()


def test_failed_destination_retries_after_a_bounded_delay_without_direct_motion():
    unit = make_unit()
    try:
        blocked_grid = [[(0, 0), (0, 1), (0, 0)]]
        unit.order = UnitOrder(OrderKind.MOVE, destination=(2, 0))
        unit.destination_cell = (2, 0)
        unit.route_revision = 1

        unit.update(100, blocked_grid, [], 1)
        first_retry_timer = unit.path_retry_timer
        unit.update(100, blocked_grid, [], 1)

        assert first_retry_timer > 0
        assert unit.path_retry_timer < first_retry_timer
        assert (unit.x, unit.y) == (0, 0)
        assert unit.destination_cell == (2, 0)
    finally:
        pygame.quit()


def test_fractional_enemy_position_can_replan_after_building_placement():
    pygame.init()
    try:
        world = World(
            16,
            [
                [TerrainTile(TerrainKind.GRASS) for _ in range(20)]
                for _ in range(10)
            ],
        )
        font = pygame.font.Font(None, 12)
        castle = Building(16 * 16, 16 * 5, "Castle", pygame.Surface((32, 32)), font)
        world.rebuild_navigation([castle])
        enemy = EnemyUnit(
            "Goblin",
            0,
            16 * 5,
            [castle],
            [],
            pygame.Surface((16, 16)),
            font,
        )

        for _ in range(100):
            enemy.update(1000 / 30, world, [])
        assert enemy.x % 1 != 0

        blocker = Building(16 * 5, 16 * 5, "House", pygame.Surface((16, 16)), font)
        world.rebuild_navigation([castle, blocker])
        enemy.update(1000 / 30, world, [])

        assert enemy.route_revision == world.navigation_revision
        assert enemy.path
        assert enemy.path_retry_timer == 0
    finally:
        pygame.quit()
