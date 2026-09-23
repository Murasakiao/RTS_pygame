from dataclasses import dataclass, field
from enum import Enum


class TerrainKind(str, Enum):
    GRASS = "grass"
    WATER = "water"


class FootprintStatus(str, Enum):
    VALID = "valid"
    OUT_OF_BOUNDS = "out_of_bounds"
    WATER = "water"
    OCCUPIED = "occupied"


@dataclass(frozen=True)
class FootprintResult:
    status: FootprintStatus
    cells: tuple[tuple[int, int], ...] = ()

    @property
    def valid(self):
        return self.status is FootprintStatus.VALID

    @property
    def reason(self):
        return self.status.value


@dataclass(frozen=True)
class TerrainTile:
    """Stable terrain meaning plus a visual variant."""

    kind: TerrainKind
    variant: int = 0


def pixel_to_cell(position, grid_size):
    """Convert integer or floating pixel coordinates to integer cell indices."""
    return (
        int(position[0] // grid_size),
        int(position[1] // grid_size),
    )


def cell_to_pixel(cell, grid_size):
    """Return the top-left pixel position of a grid cell."""
    return cell[0] * grid_size, cell[1] * grid_size


def cell_rect(cell, grid_size, size=None):
    """Return a cell rectangle as ``(left, top, width, height)``."""
    left, top = cell_to_pixel(cell, grid_size)
    if size is None:
        width = height = grid_size
    else:
        width, height = size
    return left, top, width, height


def rectangle_bounds(rect):
    """Read rectangle edges from a Pygame Rect or a four-value tuple."""
    if hasattr(rect, "left"):
        return rect.left, rect.top, rect.right, rect.bottom
    left, top, width, height = rect
    return left, top, left + width, top + height


def rectangle_gap(first, second):
    """Return the shortest edge-to-edge distance between two rectangles."""
    first_left, first_top, first_right, first_bottom = rectangle_bounds(first)
    second_left, second_top, second_right, second_bottom = rectangle_bounds(second)
    horizontal = max(second_left - first_right, first_left - second_right, 0)
    vertical = max(second_top - first_bottom, first_top - second_bottom, 0)
    return (horizontal**2 + vertical**2) ** 0.5


def rect_cells(rect, grid_size):
    """Yield every cell touched by a rectangle footprint."""
    left_edge, top_edge, right_edge, bottom_edge = rectangle_bounds(rect)
    if right_edge <= left_edge or bottom_edge <= top_edge:
        return

    left = left_edge // grid_size
    top = top_edge // grid_size
    right = (right_edge - 1) // grid_size
    bottom = (bottom_edge - 1) // grid_size
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            yield x, y


@dataclass
class World:
    """Authoritative terrain and derived navigation data for a match."""

    grid_size: int
    terrain: list[list[TerrainTile]]
    grass_tiles: tuple = ()
    water_tiles: tuple = ()
    navigation_grid: list = field(init=False)
    navigation_revision: int = field(init=False, default=0)
    _navigation_signature: tuple | None = field(init=False, default=None, repr=False)
    _building_cells: frozenset = field(init=False, default_factory=frozenset, repr=False)

    def __post_init__(self):
        if not self.terrain or not self.terrain[0]:
            raise ValueError("World needs a non-empty terrain grid")
        width = len(self.terrain[0])
        if any(len(row) != width for row in self.terrain):
            raise ValueError("World terrain rows must have equal lengths")
        self.terrain = [list(row) for row in self.terrain]
        self.grass_tiles = tuple(self.grass_tiles)
        self.water_tiles = tuple(self.water_tiles)
        self.navigation_grid = []
        self.rebuild_navigation()

    @property
    def width(self):
        return len(self.terrain[0])

    @property
    def height(self):
        return len(self.terrain)

    def in_bounds(self, cell):
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def terrain_at(self, cell):
        if not self.in_bounds(cell):
            return None
        x, y = cell
        return self.terrain[y][x]

    def is_water(self, cell):
        tile = self.terrain_at(cell)
        return tile is None or tile.kind is TerrainKind.WATER

    def rebuild_navigation(self, buildings=()):
        """Rebuild walkability and increment the revision only when it changes."""
        new_grid = [
            [
                (tile.kind, 1 if tile.kind is TerrainKind.WATER else 0)
                for tile in row
            ]
            for row in self.terrain
        ]

        building_cells = set()
        for building in buildings:
            for x, y in rect_cells(building.rect, self.grid_size):
                if self.in_bounds((x, y)):
                    building_cells.add((x, y))
                    terrain_kind = new_grid[y][x][0]
                    new_grid[y][x] = (terrain_kind, 1)

        self._building_cells = frozenset(building_cells)
        signature = tuple(tuple(row) for row in new_grid)
        if signature != self._navigation_signature:
            self.navigation_grid = new_grid
            self._navigation_signature = signature
            self.navigation_revision += 1
        return self.navigation_grid

    def footprint_cells(self, origin, size):
        width, height = size
        if width <= 0 or height <= 0:
            return ()
        return tuple(
            (origin[0] + x, origin[1] + y)
            for y in range(height)
            for x in range(width)
        )

    def _occupied_cells(self, objects):
        occupied = set()
        for obj in objects:
            occupied.update(rect_cells(obj.rect, self.grid_size))
        return occupied

    def is_cell_free(self, cell, buildings=(), units=(), enemies=()):
        if not self.in_bounds(cell) or not self.is_walkable(cell):
            return False
        occupied = self._occupied_cells(
            (*buildings, *units, *enemies),
        )
        return cell not in occupied

    def validate_footprint(
        self,
        origin,
        size,
        buildings=(),
        units=(),
        enemies=(),
    ):
        """Validate every cell of a building or spawn footprint."""
        cells = self.footprint_cells(origin, size)
        if not cells or any(not self.in_bounds(cell) for cell in cells):
            return FootprintResult(FootprintStatus.OUT_OF_BOUNDS, cells)
        if any(self.is_water(cell) for cell in cells):
            return FootprintResult(FootprintStatus.WATER, cells)

        occupied = self._occupied_cells(
            (*buildings, *units, *enemies),
        )
        if any(cell in occupied for cell in cells):
            return FootprintResult(FootprintStatus.OCCUPIED, cells)
        return FootprintResult(FootprintStatus.VALID, cells)

    def find_free_exit(
        self,
        origin,
        size,
        buildings=(),
        units=(),
        enemies=(),
    ):
        """Return the nearest deterministic free cell around a footprint."""
        width, height = size
        candidates = []
        for x in range(width):
            candidates.extend(
                (
                    (origin[0] + x, origin[1] - 1),
                    (origin[0] + x, origin[1] + height),
                )
            )
        for y in range(height):
            candidates.extend(
                (
                    (origin[0] - 1, origin[1] + y),
                    (origin[0] + width, origin[1] + y),
                )
            )

        seen = set()
        for cell in candidates:
            if cell in seen:
                continue
            seen.add(cell)
            if self.is_cell_free(cell, buildings, units, enemies):
                return cell
        return None

    def has_line_of_sight(self, first_rect, target_rect):
        """Return whether terrain/buildings leave a clear cell ray to target."""
        first_left, first_top, first_right, first_bottom = rectangle_bounds(
            first_rect,
        )
        target_left, target_top, target_right, target_bottom = rectangle_bounds(
            target_rect,
        )
        start = pixel_to_cell(
            ((first_left + first_right - 1) // 2, (first_top + first_bottom - 1) // 2),
            self.grid_size,
        )
        goal = pixel_to_cell(
            ((target_left + target_right - 1) // 2, (target_top + target_bottom - 1) // 2),
            self.grid_size,
        )
        target_cells = set(rect_cells(target_rect, self.grid_size))

        x0, y0 = start
        x1, y1 = goal
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        step_x = 1 if x0 < x1 else -1
        step_y = 1 if y0 < y1 else -1
        error = dx - dy

        while True:
            cell = (x0, y0)
            if cell not in target_cells and cell in self._building_cells:
                return False
            if cell == goal:
                return True
            double_error = 2 * error
            if double_error > -dy:
                error -= dy
                x0 += step_x
            if double_error < dx:
                error += dx
                y0 += step_y

    def attack_cells(self, target_rect, attacker_size, attack_range):
        """Return visible walkable cells from which an attacker can reach target."""
        target_left, target_top, target_right, target_bottom = rectangle_bounds(
            target_rect,
        )
        target_cells = set(rect_cells(target_rect, self.grid_size))
        margin = int(attack_range + max(attacker_size)) + self.grid_size
        min_x = max(0, (target_left - margin) // self.grid_size)
        max_x = min(self.width - 1, (target_right + margin) // self.grid_size)
        min_y = max(0, (target_top - margin) // self.grid_size)
        max_y = min(self.height - 1, (target_bottom + margin) // self.grid_size)

        candidates = []
        for y in range(min_y, max_y + 1):
            for x in range(min_x, max_x + 1):
                cell = (x, y)
                if cell in target_cells or not self.is_walkable(cell):
                    continue
                attacker_rect = cell_rect(cell, self.grid_size, attacker_size)
                gap = rectangle_gap(attacker_rect, target_rect)
                if gap <= attack_range and self.has_line_of_sight(
                    attacker_rect,
                    target_rect,
                ):
                    candidates.append((gap, cell))

        candidates.sort(key=lambda item: (item[0], item[1][1], item[1][0]))
        return tuple(cell for _, cell in candidates)

    def is_walkable(self, cell):
        if not self.in_bounds(cell):
            return False
        return self.navigation_grid[cell[1]][cell[0]][1] == 0

    def draw_terrain(self, screen):
        if not self.grass_tiles or not self.water_tiles:
            raise ValueError("World needs grass and water surfaces to draw")

        for y, row in enumerate(self.terrain):
            for x, tile_data in enumerate(row):
                if tile_data.kind is TerrainKind.WATER:
                    tile = self.water_tiles[tile_data.variant % len(self.water_tiles)]
                else:
                    tile = self.grass_tiles[tile_data.variant % len(self.grass_tiles)]
                screen.blit(tile, cell_to_pixel((x, y), self.grid_size))
