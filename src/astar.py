from dataclasses import dataclass
from enum import Enum
import heapq
import itertools
import math
from collections.abc import Sequence


Cell = tuple[int, int]
SQRT_TWO = math.sqrt(2.0)


class PathStatus(str, Enum):
    FOUND = "found"
    ALREADY_THERE = "already_there"
    UNREACHABLE = "unreachable"
    INVALID_INPUT = "invalid_input"


@dataclass(frozen=True)
class PathResult:
    """Explicit result for a grid route request."""

    status: PathStatus
    path: tuple[Cell, ...] = ()
    reason: str | None = None

    @property
    def succeeded(self):
        return self.status in {
            PathStatus.FOUND,
            PathStatus.ALREADY_THERE,
        }

    def __bool__(self):
        return self.succeeded


def _coordinate(value):
    if (
        not isinstance(value, Sequence)
        or isinstance(value, (str, bytes))
        or len(value) != 2
        or any(isinstance(part, bool) or not isinstance(part, int) for part in value)
    ):
        return None
    return int(value[0]), int(value[1])


def _validate_grid(grid):
    if (
        not isinstance(grid, Sequence)
        or isinstance(grid, (str, bytes))
        or not grid
    ):
        return None, "grid_empty"

    if any(
        not isinstance(row, Sequence)
        or isinstance(row, (str, bytes))
        or not row
        for row in grid
    ):
        return None, "grid_not_rectangular"

    width = len(grid[0])
    if any(len(row) != width for row in grid):
        return None, "grid_not_rectangular"

    for row in grid:
        for cell in row:
            if (
                not isinstance(cell, Sequence)
                or len(cell) < 2
                or cell[1] not in (0, 1, False, True)
            ):
                return None, "grid_cell_invalid"

    return (width, len(grid)), None


def _walkable(grid, cell):
    x, y = cell
    return grid[y][x][1] == 0


def _neighbors(grid, cell, width, height):
    x, y = cell
    directions = (
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 1),
        (1, -1),
        (-1, -1),
        (-1, 1),
    )
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < width and 0 <= ny < height):
            continue
        if not _walkable(grid, (nx, ny)):
            continue
        if dx and dy:
            # Do not squeeze through a blocked diagonal corner.
            if not _walkable(grid, (x + dx, y)):
                continue
            if not _walkable(grid, (x, y + dy)):
                continue
        yield nx, ny


def distance(first, second):
    """Return the cost of an optimal eight-direction grid displacement."""
    first_cell = _coordinate(first)
    second_cell = _coordinate(second)
    if first_cell is None or second_cell is None:
        raise ValueError("distance() expects two (x, y) cells")
    dx = abs(second_cell[0] - first_cell[0])
    dy = abs(second_cell[1] - first_cell[1])
    return max(dx, dy) + (SQRT_TWO - 1) * min(dx, dy)


def h_score(start, end):
    """Use the admissible octile heuristic for eight-direction movement."""
    return distance(start, end)


def _reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return tuple(path)


def a_star(grid, start_coords, end_coords):
    """Find a route through a validated, eight-direction grid.

    The returned path contains immutable ``(x, y)`` cells. A blocked goal is
    reported as unreachable; callers that need an attack position should
    choose and validate a reachable candidate goal explicitly.
    """
    dimensions, grid_error = _validate_grid(grid)
    if grid_error:
        return PathResult(PathStatus.INVALID_INPUT, reason=grid_error)

    start = _coordinate(start_coords)
    end = _coordinate(end_coords)
    if start is None or end is None:
        return PathResult(PathStatus.INVALID_INPUT, reason="coordinate_invalid")

    width, height = dimensions
    if not (0 <= start[0] < width and 0 <= start[1] < height):
        return PathResult(PathStatus.INVALID_INPUT, reason="start_out_of_bounds")
    if not (0 <= end[0] < width and 0 <= end[1] < height):
        return PathResult(PathStatus.INVALID_INPUT, reason="goal_out_of_bounds")
    if not _walkable(grid, start):
        return PathResult(PathStatus.INVALID_INPUT, reason="start_blocked")
    if not _walkable(grid, end):
        return PathResult(PathStatus.UNREACHABLE, reason="goal_blocked")
    if start == end:
        return PathResult(PathStatus.ALREADY_THERE, (start,))

    counter = itertools.count()
    open_set = []
    came_from = {}
    g_score = {start: 0.0}
    heapq.heappush(
        open_set,
        (h_score(start, end), 0.0, next(counter), start),
    )

    while open_set:
        _, current_g, _, current = heapq.heappop(open_set)
        # A better route may have pushed a newer entry for this cell.
        if current_g > g_score.get(current, math.inf):
            continue

        if current == end:
            return PathResult(
                PathStatus.FOUND,
                _reconstruct_path(came_from, current),
            )

        for neighbor in _neighbors(grid, current, width, height):
            step_cost = SQRT_TWO if neighbor[0] != current[0] and neighbor[1] != current[1] else 1.0
            tentative_g = current_g + step_cost
            if tentative_g >= g_score.get(neighbor, math.inf):
                continue

            came_from[neighbor] = current
            g_score[neighbor] = tentative_g
            f_score = tentative_g + h_score(neighbor, end)
            heapq.heappush(
                open_set,
                (f_score, tentative_g, next(counter), neighbor),
            )

    return PathResult(PathStatus.UNREACHABLE, reason="no_route")
