import os
import subprocess
import sys

import pygame

from src.assets import AssetLoader
from src.game import FixedStepRunner, GameState
from src import rts


PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))


def test_importing_rts_does_not_initialize_pygame():
    code = "import pygame; import src.rts; assert not pygame.get_init()"
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        check=True,
        env=os.environ.copy(),
    )


def test_asset_loader_uses_repository_root_and_placeholder(caplog):
    pygame.init()
    pygame.display.set_mode((1, 1))
    try:
        loader = AssetLoader(project_root=PROJECT_ROOT)
        castle = loader.image("building.castle", (32, 32))
        missing = loader.image("missing.example", (16, 16))
        font = loader.font(12)

        assert castle.get_size() == (32, 32)
        assert missing.get_size() == (16, 16)
        assert font.get_height() > 0
        assert any("missing.example" in message for message in loader.diagnostics)
        assert loader.path_for("building.castle").is_file()
    finally:
        pygame.quit()


def test_new_match_state_does_not_share_mutable_values():
    class TerrainFixture:
        screen_width = 32
        screen_height = 16
        grid_size = 16
        terrain = [[0, 0]]

    first = GameState.new_match(TerrainFixture())
    second = GameState.new_match(TerrainFixture())
    first.resources["wood"] = 0
    first.buildings.append(object())

    assert second.resources["wood"] == 200
    assert second.buildings == []
    assert first.grid is not second.grid


def test_fixed_step_runner_caps_catch_up_and_uses_constant_dt():
    class Clock:
        def tick(self, fps):
            return 1000

    runner = FixedStepRunner(Clock(), fps=30, max_catch_up_steps=5)
    steps = []
    runner.begin_frame()
    assert runner.run_updates(steps.append) == 5
    assert steps == [1000 / 30] * 5


def test_main_can_start_a_match_and_quit(monkeypatch):
    start = pygame.event.Event(
        pygame.MOUSEBUTTONDOWN,
        {"button": 1, "pos": (384, 360)},
    )
    quit_event = pygame.event.Event(pygame.QUIT, {})
    batches = iter([[start], [quit_event]])

    class Clock:
        def tick(self, fps):
            return 33

        def get_fps(self):
            return 30

    monkeypatch.setattr(pygame.event, "get", lambda: next(batches, []))
    monkeypatch.setattr(pygame.time, "Clock", Clock)

    assert rts.main() == 0
    assert not pygame.get_init()
