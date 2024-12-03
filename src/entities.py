# entities.py

import math
import pygame
from constants import *
from constants import add_game_message
from utils import astar, EnemyUnit  # Import astar and EnemyUnit

pygame.init()

# --- Classes ---
class GameObject: # Keep GameObject in entities.py
    def __init__(self, x, y, image_path, size=(GRID_SIZE, GRID_SIZE)):
        self.x = x
        self.y = y
        # Use a default image path if not provided
        default_image = 'default_unit.png'  # Make sure this exists
        try:
            self.image = pygame.transform.scale(
                pygame.image.load(image_path or default_image), 
                size
            )
        except pygame.error:
            # Fallback to a simple surface if image loading fails
            self.image = pygame.Surface(size)
            self.image.fill(BLACK)  # Fallback image
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font(None, 15)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        hp = self.font.render(f"HP: {self.hp}", True, BLACK)
        screen.blit(hp, (self.rect.centerx - hp.get_width() // 2, self.rect.top + self.rect.height + 5))

class Building(GameObject):
    def __init__(self, x, y, building_type):
        self.type = building_type
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(x, y, data["image"], size)
        self.hp = data["hp"]

class Unit(GameObject):
    def __init__(self, unit_type, x, y, targets, font=None):
        # Get unit data based on type
        unit_data = ALLY_DATA.get(unit_type) or ENEMY_DATA.get(unit_type)
        if unit_data is None:
            raise ValueError(f"Invalid unit_type: {unit_type}")
        
        super().__init__(x, y, unit_data["image"])
        
        self.name = unit_data['name']  # Store the name separately
        self.type = unit_type  # Store the unit type as a string
        self.destination = None
        self.speed = unit_data.get("speed")
        self.hp = unit_data.get("hp", 100)
        self.attack = unit_data.get("atk", 10)  # Renamed to 'attack'
        
        self.font = font or pygame.font.Font(None, 15)
        
        # Ensure targets is a list
        if targets is None:
            self.targets = []
        elif isinstance(targets, list):
            self.targets = targets
        else:
            # If a single target is passed, convert to a list
            self.targets = [targets]
        
        self.target = None
        self.attack_cooldown = 0
        self.path = []  # Initialize path

    def update(self, dt, game_messages=None, grid=None, buildings=None):  # Add grid and buildings parameters
        """
        Update method to be implemented by subclasses
        Handles target selection, movement, and attacking
        """
        self.handle_target_selection()
        self.move_towards_target(dt, grid, buildings)  # Pass grid and buildings to move_towards_target
        self.handle_attack(dt, game_messages, grid, buildings)  # Pass grid and buildings to handle_attack
        return game_messages

    def handle_target_selection(self):
        """
        Select the nearest target if current target is invalid
        """
        if not self.target or self.target.hp <= 0:
            self.target = self.find_nearest_target()

    def move_towards_target(self, dt, grid, buildings):
        if self.destination and not self.path:  # Only calculate path if destination exists and path is empty
            start = (self.x // GRID_SIZE, self.y // GRID_SIZE)
            end = (self.destination[0] // GRID_SIZE, self.destination[1] // GRID_SIZE)
            self.path = astar(grid, start, end, buildings)
            if not self.path:
                self.destination = None  # No path found, clear destination
                return

        if self.path:
            next_cell = self.path[0]
            target_x = next_cell[0] * GRID_SIZE
            target_y = next_cell[1] * GRID_SIZE
            dx = target_x - self.x
            dy = target_y - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                travel_distance = self.speed * (dt / 1000)
                new_x = self.x + (dx / distance) * travel_distance
                new_y = self.y + (dy / distance) * travel_distance

                self.x = new_x
                self.y = new_y
                self.rect.topleft = (self.x, self.y)

                if distance <= travel_distance:
                    self.path.pop(0)  # Move to the next cell in the path
                    if not self.path:
                        self.destination = None  # Reached destination


    def handle_attack(self, dt, game_messages, grid, buildings):
        """
        Handle attack cooldown and attacking
        """
        if self.target and self.attack_cooldown <= 0:
            if self.should_attack():
                self.attack_target(game_messages)
                self.attack_cooldown = self.get_attack_cooldown()
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def attack_target(self, game_messages):
        """
        Attack the current target and generate game messages
        """
        if self.target:
            # Use the unit type name instead of the entire dictionary
            unit_name = self.name  # Use the stored name
            # Use the unit type name instead of the entire dictionary
            unit_name = self.name  # Use the stored name
            if hasattr(self.target, 'name'):
                target_name = self.target.name
            else:
                target_name = self.target.type  # Use type if no name attribute
            self.target.hp -= self.attack
            message = f"{unit_name} attacked {target_name} for {self.attack} damage."

            if self.target and self.target.hp <= 0:  # Check if target still exists
                message = f"{unit_name} destroyed {target_name}"
                # Automatically find a new target after destroying current one
                self.target = None
            
            if game_messages is not None:
                add_game_message(message, game_messages)

    def find_nearest_target(self):
        """
        Find the nearest valid target
        """
        # More robust target filtering
        valid_targets = [
            target for target in self.targets 
            if (hasattr(target, 'hp') and 
                hasattr(target, 'x') and 
                hasattr(target, 'y') and 
                target.hp > 0)
        ]
        
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        return None

    def draw(self, screen):
        """
        Draw the unit with additional information
        """
        super().draw(screen)
        
        # Draw target information if a target exists
        if self.target and self.target.hp > 0:
            target_text = self.font.render(str(self.target.type), True, RED)
            screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, 
                                      self.rect.top - target_text.get_height() - 5))

class AlliedUnit(Unit):
    def __init__(self, unit_type, x, y, targets, font=None):
        super().__init__(unit_type, x, y, targets, font)

    def should_attack(self):
        """
        Determine if the unit should attack based on attack range
        """
        if not self.target:
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)
        unit_range = ALLY_DATA[self.type].get("range", UNIT_ATTACK_RANGE)  # Get range, default to UNIT_ATTACK_RANGE
        return distance <= unit_range

    def get_attack_range(self):
        """
        Get the attack range for this unit.
        """
        return ALLY_DATA.get(self.type, {}).get("range", UNIT_ATTACK_RANGE)

    def get_attack_cooldown(self):
        """
        Get the attack cooldown for allied units
        """
        return UNIT_ATTACK_COOLDOWN

    def __init__(self, screen_width, screen_height, grid_size, noise):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.grass_tiles = self.load_grass_tiles()
        self.scale = 100.0
        self.octaves = 12
        self.persistence = 0.01
        self.lacunarity = 2.0
        self.noise = noise

    def load_grass_tiles(self):
        grass_tiles = []
        for i in range(1, 7):
            try:
                tile = pygame.image.load(f'buildings/tile_{i}.png')
                tile = pygame.transform.scale(tile, (self.grid_size, self.grid_size))
                grass_tiles.append(tile)
            except Exception as e:
                print(f"Error loading tile_{i}.png: {e}")

        if not grass_tiles:  # Fallback if no tiles loaded 
            grass_tiles.append(pygame.Surface((self.grid_size, self.grid_size)))
            grass_tiles[0].fill((0, 255, 0))
        return grass_tiles

    def generate_terrain(self):
        terrain = []
        for y in range(0, self.screen_height, self.grid_size):
            row = []
            for x in range(0, self.screen_width, self.grid_size):
                noise_value = self.noise.pnoise2(x / self.scale, y / self.scale,
                                            octaves=self.octaves, persistence=self.persistence,
                                            lacunarity=self.lacunarity, repeatx=self.screen_width,
                                            repeaty=self.screen_height, base=0)
                normalized_noise = (noise_value + 1) / 2
                tile_index = int(normalized_noise * (len(self.grass_tiles) - 1))
                row.append(tile_index)
            terrain.append(row)
        return terrain

    def draw_terrain(self, screen, terrain):
        for y, row in enumerate(terrain):
            for x, tile_index in enumerate(row):
                tile = self.grass_tiles[tile_index]
                screen.blit(tile, (x * self.grid_size, y * self.grid_size))

