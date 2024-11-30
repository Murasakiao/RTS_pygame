import pygame
import sys
import random
import math
import noise

from pygame.locals import *

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25
FPS = 30
BUILDING_COOLDOWN_TIME = 1000
MESSAGE_DURATION = 3000
WAVE_INTERVAL = 25000
ENEMY_SPAWN_RATE = 1
UNIT_ATTACK_RANGE = 50
UNIT_ATTACK_COOLDOWN = 1000  # 1 second cooldown

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("City Builder")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)

# --- Data ---
# Building data
BUILDING_DATA = {
    "Castle": {"hp": 2750, "image": "buildings/castle.png", "cost": 75, "resources": {"gold": 75, "wood": 50, "stone": 100}, "size_multiplier": 2},
    "House": {"hp": 2000, "image": "buildings/house.png", "cost": 20, "resources": {"gold": 20, "wood": 15}},
    "Market": {"hp": 2300, "image": "buildings/market.png", "cost": 30, "resources": {"gold": 30, "wood": 20, "stone": 25}},
    "Barracks": {"hp": 2400, "image": "buildings/barracks.png", "cost": 40, "resources": {"gold": 40, "wood": 20, "stone": 15}, "unit": "Swordsman"},
    "Stable": {"hp": 2250, "image": "buildings/stable.png", "cost": 25, "resources": {"gold": 35, "wood": 20, "stone": 15}, "unit": "Archer"},
    "Farm": {"hp": 2500, "image": "buildings/farm.png", "cost": 25, "resources": {"gold": 25, "wood": 10}},
    "LumberMill": {"hp": 2000, "image": "buildings/lumber.png", "cost": 40, "resources": {"gold": 40, "wood": 30, "stone": 10}},
    "Quarry": {"hp": 2500, "image": "buildings/quarry.png", "cost": 50, "resources": {"gold": 20, "wood": 30, "stone": 10}},
}

# Unit data
UNIT_DATA = {
    "Swordsman": {"image": "characters/swordsman.png", "cost": {"gold": 50, "food": 30, "people": 1}, "speed": 50, "hp": 10, "atk": 1},
    "Archer": {"image": "characters/bowman.png", "cost": {"gold": 60, "food": 40, "people": 1}, "speed": 40, "hp": 8, "atk": 2},
}

# Enemy data
ENEMY_DATA = {
    "Goblin": {"image": "characters/goblin.png", "speed": 20, "hp": 8, "atk": 1},
    "Orc": {"image": "characters/orc.png", "speed": 10, "hp": 12, "atk": 2},
}

# --- Classes ---
class GameObject:
    def __init__(self, x, y, image_path, size=(GRID_SIZE, GRID_SIZE)):
        self.x = x
        self.y = y
        try:
            self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        except pygame.error:
            self.image = pygame.Surface(size)
            self.image.fill(BLACK)  # Fallback image
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Building(GameObject):
    def __init__(self, x, y, building_type):
        self.type = building_type
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(x, y, data["image"], size)
        self.hp = data["hp"]

class Unit(GameObject):
    def __init__(self, unit_type, x, y):
        super().__init__(x, y, UNIT_DATA[unit_type]["image"])
        self.type = unit_type
        self.moving = False
        self.destination = None
        self.speed = UNIT_DATA[unit_type]["speed"]
        self.hp = UNIT_DATA[unit_type]["hp"]
        self.atk = UNIT_DATA[unit_type]["atk"]
        self.target = None
        self.attack_cooldown = 0

    def update(self, dt, game_messages, buildings):
        if self.moving and self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                travel_distance = self.speed * (dt / 1000)
                
                # Calculate potential new position
                new_x = self.x + (dx / distance) * travel_distance
                new_y = self.y + (dy / distance) * travel_distance
                
                # Create a temporary rect for the potential new position
                temp_rect = self.image.get_rect(topleft=(new_x, new_y))
                
                # Check for collision with buildings
                collision = False
                for building in buildings:
                    if temp_rect.colliderect(building.rect):
                        collision = True
                        break
                
                if not collision:
                    # No collision, move to the new position
                    self.x = new_x
                    self.y = new_y
                    self.rect.topleft = (self.x, self.y)
                else:
                    # Collision detected, move as close as possible without colliding
                    # Calculate the direction vector
                    direction_x = dx / distance
                    direction_y = dy / distance
                    
                    # Move step by step until collision or reaching destination
                    step_size = 1
                    while distance > step_size:
                        temp_x = self.x + direction_x * step_size
                        temp_y = self.y + direction_y * step_size
                        temp_rect = self.image.get_rect(topleft=(temp_x, temp_y))
                        
                        collision = False
                        for building in buildings:
                            if temp_rect.colliderect(building.rect):
                                collision = True
                                break
                        
                        if collision:
                            break  # Stop if collision occurs
                        
                        self.x = temp_x
                        self.y = temp_y
                        self.rect.topleft = (self.x, self.y)
                        distance = math.hypot(self.destination[0] - self.x, self.y - self.destination[1])
