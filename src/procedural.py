import noise

from .world import TerrainKind, TerrainTile, World


class TerrainGenerator:
    def __init__(
        self,
        screen_width,
        screen_height,
        grid_size,
        noise_seed,
        grass_tiles,
        water_tiles,
    ):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.noise_seed = noise_seed
        self.grass_tiles = tuple(grass_tiles)
        self.water_tiles = tuple(water_tiles)
        if not self.grass_tiles or not self.water_tiles:
            raise ValueError("TerrainGenerator needs at least one grass and water tile")

    @property
    def grid_width(self):
        return self.screen_width // self.grid_size

    @property
    def grid_height(self):
        return self.screen_height // self.grid_size

    def generate_terrain(self):
        terrain = []
        scale = 150.0
        octaves = 4
        persistence = 0.5
        lacunarity = 1.5

        for y in range(0, self.screen_height, self.grid_size):
            row = []
            for x in range(0, self.screen_width, self.grid_size):
                noise_value = noise.pnoise2(
                    (x + self.noise_seed) / scale,
                    (y + self.noise_seed) / scale,
                    octaves=octaves,
                    persistence=persistence,
                    lacunarity=lacunarity,
                    repeatx=self.screen_width,
                    repeaty=self.screen_height,
                    base=0,
                )

                water_threshold = -0.1
                if noise_value < water_threshold:
                    row.append(TerrainTile(TerrainKind.WATER))
                else:
                    variant = int(
                        (noise_value - water_threshold)
                        / (1 - water_threshold)
                        * len(self.grass_tiles)
                    )
                    variant = max(0, min(variant, len(self.grass_tiles) - 1))
                    row.append(TerrainTile(TerrainKind.GRASS, variant))
            terrain.append(row)

        return terrain

    def generate_world(self):
        """Create one authoritative world from the current seed and settings."""
        return World(
            self.grid_size,
            self.generate_terrain(),
            self.grass_tiles,
            self.water_tiles,
        )
