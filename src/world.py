from dataclasses import dataclass, field
from enum import Enum


class TerrainKind(str, Enum):
    GRASS = "grass"
    WATER = "water"


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
