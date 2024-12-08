import pygame
import noise
import os
from constants import *

class TerrainGenerator:
    def __init__(self, screen_width, screen_height, grid_size, noise_seed):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.noise_seed = noise_seed        
        self.grass_tiles = []
        self.water_tiles = []
        self.load_plains_tiles()
        self.terrain = self.generate_terrain()

    def load_plains_tiles(self):
        for i in range(1, 7):
            try:
                tile = pygame.image.load(f'assets/tiles/plains/grass_{i}.png')
                tile = pygame.transform.scale(tile, (self.grid_size, self.grid_size))
                self.grass_tiles.append(tile)
            except Exception as e:
                print(f"Error loading grass_{i}.png: {e}")

        try:
            tile = pygame.image.load(f'assets/tiles/plains/water_1.png')
            tile = pygame.transform.scale(tile, (self.grid_size, self.grid_size))
            self.water_tiles.append(tile)
        except Exception as e:
            print(f"Error loading water_1.png: {e}")

        if not self.grass_tiles:  # Fallback if no grass tiles loaded
            default_grass = pygame.Surface((self.grid_size, self.grid_size))
            default_grass.fill(GREEN)
            self.grass_tiles.append(default_grass)

        if not self.water_tiles:  # Fallback if no water tiles loaded
            default_water = pygame.Surface((self.grid_size, self.grid_size))
            default_water.fill(BLUE)
            self.water_tiles.append(default_water)

    def generate_terrain(self):
        terrain = []
        scale = 100.0
        octaves = 3
        persistence = 0.5
        lacunarity = 2.0

        for y in range(0, self.screen_height, self.grid_size):
            row = []
            for x in range(0, self.screen_width, self.grid_size):
                noise_value = noise.pnoise2((x + self.noise_seed) / scale,
                                            (y + self.noise_seed) / scale,
                                            octaves=octaves,
                                            persistence=persistence,
                                            lacunarity=lacunarity,
                                            repeatx=self.screen_width,
                                            repeaty=self.screen_height,
                                            base=0)

                # Simple threshold to determine water or grass
                if noise_value < -0.2:
                    tile_index = len(self.grass_tiles)  # Water tile index
                else:
                    tile_index = int((noise_value + 1) / 2 * len(self.grass_tiles))
                    tile_index = max(0, min(tile_index, len(self.grass_tiles) - 1))

                row.append(tile_index)
            terrain.append(row)
        return terrain

    def draw_terrain(self, screen):
        for y, row in enumerate(self.terrain):
            for x, tile_index in enumerate(row):
                if tile_index == len(self.grass_tiles):  # Water tile
                    tile = self.water_tiles[0]
                else:
                    tile = self.grass_tiles[tile_index]
                screen.blit(tile, (x * self.grid_size, y * self.grid_size))
