import noise


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
        self.grass_tiles = list(grass_tiles)
        self.water_tiles = list(water_tiles)
        if not self.grass_tiles or not self.water_tiles:
            raise ValueError("TerrainGenerator needs at least one grass and water tile")
        self.terrain = self.generate_terrain()

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
                    tile_index = len(self.grass_tiles)
                else:
                    tile_index = int(
                        (noise_value - water_threshold)
                        / (1 - water_threshold)
                        * len(self.grass_tiles)
                    )
                    tile_index = max(
                        0,
                        min(tile_index, len(self.grass_tiles) - 1),
                    )

                row.append(tile_index)
            terrain.append(row)

        self.terrain = terrain
        return terrain

    def draw_terrain(self, screen):
        for y, row in enumerate(self.terrain):
            for x, tile_index in enumerate(row):
                if tile_index == len(self.grass_tiles):
                    tile = self.water_tiles[0]
                else:
                    tile = self.grass_tiles[tile_index]
                screen.blit(tile, (x * self.grid_size, y * self.grid_size))
