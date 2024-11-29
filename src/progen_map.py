import pygame
import noise
import random

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25  # Smaller grid size

class TerrainGenerator:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Procedural Terrain Generator")
        
        # Load grass tiles
        self.grass_tiles = []
        for i in range(4, 7):
            try:
                tile = pygame.image.load(f"../buildings/tile_{i}.png")
                tile = pygame.transform.scale(tile, (GRID_SIZE, GRID_SIZE))
                self.grass_tiles.append(tile)
            except Exception as e:
                print(f"Error loading tile_{i}.png: {e}")
        
        # Check if tiles were loaded
        if not self.grass_tiles:
            raise Exception("No grass tiles found!")
        
        # Noise parameters
        self.scale = 100.0
        self.octaves = 6
        self.persistence = 0.5
        self.lacunarity = 2.0
        
    def generate_terrain(self):
        """Generate terrain using Perlin noise"""
        terrain = []
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            row = []
            for x in range(0, SCREEN_WIDTH, GRID_SIZE):
                # Generate Perlin noise value
                noise_value = noise.pnoise2(x / self.scale, 
                                            y / self.scale, 
                                            octaves=self.octaves, 
                                            persistence=self.persistence, 
                                            lacunarity=self.lacunarity, 
                                            repeatx=SCREEN_WIDTH, 
                                            repeaty=SCREEN_HEIGHT, 
                                            base=0)
                
                # Normalize noise value to 0-1 range
                normalized_noise = (noise_value + 1) / 2
                
                # Select tile based on noise value
                tile_index = int(normalized_noise * (len(self.grass_tiles) - 1))
                row.append(tile_index)
            terrain.append(row)
        return terrain
    
    def draw_terrain(self, terrain):
        """Draw the generated terrain"""
        self.screen.fill((0, 0, 0))  # Clear screen
        
        for y, row in enumerate(terrain):
            for x, tile_index in enumerate(row):
                tile = self.grass_tiles[tile_index]
                self.screen.blit(tile, (x * GRID_SIZE, y * GRID_SIZE))
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        # Generate initial terrain
        terrain = self.generate_terrain()
        
        # Draw initial terrain
        self.draw_terrain(terrain)
        
        # Main game loop
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # Regenerate terrain on spacebar press
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    terrain = self.generate_terrain()
                    self.draw_terrain(terrain)
        
        pygame.quit()

# Run the terrain generator
if __name__ == "__main__":
    generator = TerrainGenerator()
    generator.run()