import pygame

from src.entities import AlliedUnit, Building
from src.game import GameState
from src.orders import OrderKind
from src.rts import cleanup_dead_entities


class Target:
    type = "Goblin"
    name = "Goblin"
    hp = 10
    x = 32
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


def test_dead_unit_does_not_take_an_update_turn():
    target = Target()
    unit = make_unit([target])
    try:
        unit.hp = 0
        unit.update(1000, [[(0, 0), (0, 0)]], [], 1)
        assert target.hp == 10
        assert unit.target is None
    finally:
        pygame.quit()


def test_cleanup_removes_dead_actors_and_clears_selection_and_targets():
    target = Target()
    unit = make_unit([target])
    try:
        unit.target = target
        unit.order = unit.order.__class__(OrderKind.ATTACK, target=target)
        target.hp = 0

        state = GameState(object(), object())
        state.units = [unit]
        state.enemies = [target]
        state.buildings = []
        state.selected_unit = target

        cleanup_dead_entities(state)

        assert state.enemies == []
        assert state.units == [unit]
        assert state.selected_unit is None
        assert unit.target is None
        assert unit.order.kind is OrderKind.IDLE
    finally:
        pygame.quit()
