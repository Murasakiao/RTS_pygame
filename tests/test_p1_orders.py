import pygame

from src.entities import AlliedUnit
from src.orders import OrderKind


class Target:
    type = "Goblin"
    name = "Goblin"
    hp = 10
    x = 16
    y = 0


def make_unit(targets=None):
    pygame.init()
    return AlliedUnit(
        "Swordsman",
        0,
        0,
        targets or [],
        pygame.Surface((16, 16)),
        pygame.font.Font(None, 12),
    )


def test_move_order_does_not_acquire_an_automatic_target():
    enemy = Target()
    unit = make_unit([enemy])
    try:
        grid = [[(0, 0), (0, 0), (0, 0)]]
        result = unit.issue_move((2, 0), grid, 1)
        unit.update(33, grid, [], 1)

        assert result.succeeded
        assert unit.order.kind is OrderKind.MOVE
        assert unit.target is None
    finally:
        pygame.quit()


def test_attack_and_stop_orders_are_explicit():
    enemy = Target()
    unit = make_unit()
    try:
        assert unit.issue_attack(enemy)
        assert unit.order.kind is OrderKind.ATTACK
        assert unit.order.target is enemy
        assert unit.target is enemy

        unit.stop()

        assert unit.order.kind is OrderKind.HOLD
        assert unit.target is None
        assert unit.path == []
        assert unit.destination is None
    finally:
        pygame.quit()


def test_hold_can_attack_a_target_already_in_range_without_chasing():
    enemy = Target()
    enemy.x = 10
    unit = make_unit([enemy])
    try:
        unit.stop()
        unit.update(33, [[(0, 0), (0, 0)]], [], 1)

        assert unit.order.kind is OrderKind.HOLD
        assert unit.target is enemy
        assert unit.path == []
    finally:
        pygame.quit()
