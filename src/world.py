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
    """Convert a pixel position to a zero-based grid cell."""
    return position[0] // grid_size, position[1] // grid_size


def cell_to_pixel(cell, grid_size):
    """Return the top-left pixel position of a grid cell."""
    return cell[0] * grid_size, cell[1] * grid_size


def cell_rect(cell, grid_size):
    """Return a cell rectangle as ``(left, top, width, height)``."""
    left, top = cell_to_pixel(cell, grid_size)
    return left, top, grid_size, grid_size


def rect_cells(rect, grid_size):
    """Yield every cell touched by a rectangle footprint."""
    if rect.width <= 0 or rect.height <= 0:
        return

    left = rect.left // grid_size
    top = rect.top // grid_size
    right = (rect.right - 1) // grid_size
    bottom = (rect.bottom - 1) // grid_size
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

        for building in buildings:
            for x, y in rect_cells(building.rect, self.grid_size):
                if self.in_bounds((x, y)):
                    terrain_kind = new_grid[y][x][0]
                    new_grid[y][x] = (terrain_kind, 1)

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
