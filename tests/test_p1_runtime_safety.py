import pygame

from src.rts import handle_game_event


class State:
    def __init__(self):
        self.world = object()
        self.terrain_generator = object()
        self.buildings = []
        self.units = []
        self.enemies = []
        self.game_messages = []
        self.current_building_type = None
        self.selected_unit = None
        self.show_debug = False


def test_terrain_regeneration_is_not_allowed_during_a_match():
    pygame.init()
    try:
        state = State()
        original_world = state.world
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_t)

        assert handle_game_event(state, event, None, None, {}) is True
        assert state.world is original_world
        assert state.game_messages[-1]["text"] == (
            "Map regeneration is disabled during a match."
        )
    finally:
        pygame.quit()
