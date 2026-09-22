from dataclasses import dataclass
from enum import Enum


Cell = tuple[int, int]


class OrderKind(str, Enum):
    IDLE = "idle"
    MOVE = "move"
    ATTACK = "attack"
    HOLD = "hold"


@dataclass(frozen=True)
class UnitOrder:
    """The player's or AI's intent, separate from route and current target."""

    kind: OrderKind = OrderKind.IDLE
    destination: Cell | None = None
    target: object | None = None
