import pygame

from src.astar import a_star
from src.entities import Building, EnemyUnit
from src.game import GameState
from src.rts import handle_game_event
from src.spawning import generate_spawn_point
from src.world import (
    ConnectivityRoute,
    ConnectivityStatus,
    FootprintStatus,
    TerrainKind,
    TerrainTile,
    TrainerExitRequirement,
    World,
)


class ObjectWithRect:
    def __init__(self, rect):
        self.rect = rect


class SurfaceAssets:
    def image(self, asset_key, size):
        return pygame.Surface(size)


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


def test_connectivity_rejects_a_building_that_seals_the_castle_route():
    world = grass_world(10, 3)
    castle = ObjectWithRect(pygame.Rect(8 * 16, 16, 32, 32))
    upper_wall = ObjectWithRect(pygame.Rect(3 * 16, 0, 16, 16))
    lower_wall = ObjectWithRect(pygame.Rect(3 * 16, 2 * 16, 16, 16))
    sealing_building = ObjectWithRect(pygame.Rect(3 * 16, 16, 16, 16))
    route = ConnectivityRoute(
        (0, 1),
        castle.rect,
        (16, 16),
        15,
    )

    world.rebuild_navigation([castle, upper_wall, lower_wall])

    result = world.validate_connectivity(
        [route],
        [castle, upper_wall, lower_wall, sealing_building],
    )

    assert result.status is ConnectivityStatus.BLOCKED_ROUTE
    assert result.reason == "blocked_route"


def test_connectivity_accepts_a_route_with_an_open_detour():
    world = grass_world(10, 4)
    castle = ObjectWithRect(pygame.Rect(8 * 16, 16, 32, 32))
    wall = ObjectWithRect(pygame.Rect(3 * 16, 16, 16, 16))
    route = ConnectivityRoute((0, 1), castle.rect, (16, 16), 15)

    result = world.validate_connectivity(
        [route],
        [castle, wall],
    )

    assert result.status is ConnectivityStatus.VALID


def test_trainer_exit_validation_rejects_a_surrounded_trainer():
    world = grass_world(5, 5)
    trainer = ObjectWithRect(pygame.Rect(2 * 16, 2 * 16, 16, 16))
    blockers = [
        ObjectWithRect(pygame.Rect(2 * 16, 1 * 16, 16, 16)),
        ObjectWithRect(pygame.Rect(2 * 16, 3 * 16, 16, 16)),
        ObjectWithRect(pygame.Rect(1 * 16, 2 * 16, 16, 16)),
        ObjectWithRect(pygame.Rect(3 * 16, 2 * 16, 16, 16)),
    ]
    buildings = [trainer, *blockers]
    world.rebuild_navigation(buildings)
    requirement = TrainerExitRequirement(
        origin=(2, 2),
        size=(1, 1),
        actor_size=(16, 16),
        attack_range=15,
        actor=trainer,
    )

    result = world.validate_trainer_exits([requirement], buildings)

    assert result.status is ConnectivityStatus.EXIT_BLOCKED
    assert result.actor is trainer


def test_spawn_lane_validation_requires_two_reachable_edges():
    world = World(
        16,
        [
            [TerrainTile(TerrainKind.WATER) for _ in range(10)]
            for _ in range(6)
        ],
    )
    for x in range(6):
        world.terrain[2][x] = TerrainTile(TerrainKind.GRASS)
        world.terrain[3][x] = TerrainTile(TerrainKind.GRASS)
    castle = ObjectWithRect(pygame.Rect(4 * 16, 2 * 16, 32, 32))
    world.rebuild_navigation([castle])

    result = world.validate_spawn_lanes(
        castle.rect,
        (16, 16),
        5,
        [castle],
        minimum_lanes=2,
    )

    assert result.status is ConnectivityStatus.INSUFFICIENT_SPAWN_LANES
    assert result.lanes == ("left",)


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


def test_placement_rejects_a_building_that_seals_a_living_enemy_route():
    pygame.init()
    try:
        assets = SurfaceAssets()
        font = pygame.font.Font(None, 12)
        world = grass_world(10, 3)
        castle = Building(8 * 16, 16, "Castle", assets.image("castle", (32, 32)), font)
        upper_wall = Building(3 * 16, 0, "House", assets.image("house", (16, 16)), font)
        lower_wall = Building(3 * 16, 2 * 16, "House", assets.image("house", (16, 16)), font)
        world.rebuild_navigation([castle, upper_wall, lower_wall])
        enemy = EnemyUnit(
            "Goblin",
            0,
            16,
            [castle],
            [],
            assets.image("goblin", (16, 16)),
            font,
        )
        state = GameState(object(), world)
        state.buildings = [castle, upper_wall, lower_wall]
        state.enemies = [enemy]
        state.current_building_type = "House"
        state.gold = 100
        state.resources = {"wood": 100}

        handled = handle_game_event(
            state,
            pygame.event.Event(
                pygame.MOUSEBUTTONDOWN,
                button=1,
                pos=(3 * 16, 1 * 16),
            ),
            assets,
            font,
            {},
        )

        assert handled is True
        assert len(state.buildings) == 3
        assert state.gold == 100
        assert state.game_messages[-1]["text"] == "Cannot build: blocked route."
    finally:
        pygame.quit()


def test_spawn_point_prefers_an_edge_that_can_reach_the_target():
    world = World(
        16,
        [
            [TerrainTile(TerrainKind.GRASS) for _ in range(10)]
            for _ in range(6)
        ],
    )
    for y in range(world.height):
        if y != 5:
            world.terrain[y][5] = TerrainTile(TerrainKind.WATER)
    target = ObjectWithRect(pygame.Rect(32, 32, 32, 32))
    world.rebuild_navigation([target])

    point = generate_spawn_point(
        world,
        [target],
        target=target,
        attack_range=15,
    )

    assert point is not None
    cell = (point[0] // 16, point[1] // 16)
    assert any(
        a_star(world.navigation_grid, cell, candidate).succeeded
        for candidate in world.attack_cells(target.rect, (16, 16), 15)
    )
