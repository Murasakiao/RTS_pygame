import pygame

from src.astar import a_star
from src.entities import AlliedUnit
from src.orders import OrderKind, UnitOrder


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
