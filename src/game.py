from dataclasses import dataclass, field

from .constants import FPS
from .world import World


def _starting_resources():
    return {"wood": 200, "stone": 200, "food": 200, "people": 3}


def _resource_increase_rates():
    return {
        "gold": 1.5,
        "wood": 0.5,
        "stone": 0.5,
        "food": 0.25,
        "people": 0.1,
    }


def can_afford(cost, resources, gold):
    """Return whether every cost entry has enough available balance."""
    return all(
        (gold if resource == "gold" else resources.get(resource, 0)) >= amount
        for resource, amount in cost.items()
    )


def deduct_cost(cost, resources, gold):
    """Deduct a cost atomically and return the updated gold balance."""
    if not can_afford(cost, resources, gold):
        raise ValueError("insufficient resources")

    for resource, amount in cost.items():
        if resource == "gold":
            gold -= amount
        else:
            resources[resource] = resources.get(resource, 0) - amount
    return gold


@dataclass
class GameState:
    """All mutable state that belongs to one match."""

    terrain_generator: object
    world: World
    gold: float = 150.0
    resources: dict = field(default_factory=_starting_resources)
    resource_increase_rates: dict = field(default_factory=_resource_increase_rates)
    buildings: list = field(default_factory=list)
    units: list = field(default_factory=list)
    enemies: list = field(default_factory=list)
    game_messages: list = field(default_factory=list)
    current_building_type: str | None = "Castle"
    building_cooldown: float = 0
    selected_unit: object | None = None
    wave_timer: float = 0
    current_wave: int = 1
    show_debug: bool = True

    @classmethod
    def new_match(cls, terrain_generator):
        """Create isolated mutable state for a new match."""
        world = terrain_generator.generate_world()
        return cls(
            terrain_generator=terrain_generator,
            world=world,
        )


class FixedStepRunner:
    """Accumulate wall-clock time and update the simulation in fixed steps."""

    def __init__(self, clock, fps=FPS, max_catch_up_steps=5):
        self.clock = clock
        self.fps = fps
        self.fixed_dt = 1.0 / fps
        self.fixed_dt_ms = 1000.0 / fps
        self.max_catch_up_steps = max_catch_up_steps
        self.accumulator = 0.0

    def begin_frame(self):
        """Read wall time and cap catch-up work after a long frame."""
        elapsed_ms = max(0, self.clock.tick(self.fps))
        elapsed_seconds = elapsed_ms / 1000.0
        elapsed_seconds = min(
            elapsed_seconds,
            self.fixed_dt * self.max_catch_up_steps,
        )
        self.accumulator += elapsed_seconds

    def run_updates(self, update):
        """Call ``update(fixed_dt_ms)`` for each pending simulation step."""
        steps = 0
        while (
            self.accumulator >= self.fixed_dt
            and steps < self.max_catch_up_steps
        ):
            update(self.fixed_dt_ms)
            self.accumulator -= self.fixed_dt
            steps += 1

        # Drop excess backlog instead of freezing the render loop in catch-up.
        if steps == self.max_catch_up_steps and self.accumulator >= self.fixed_dt:
            self.accumulator = 0.0
        return steps

    def reset(self):
        """Discard time accumulated before a menu transition or pause."""
        self.accumulator = 0.0
