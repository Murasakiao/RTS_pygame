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
WAVE_INTERVAL = 10000
ENEMY_SPAWN_RATE = 5

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
    "Castle": {"hp": 275, "image": "buildings/castle.png", "cost": 75, "resources": {"gold": 75, "wood": 50, "stone": 100}, "size_multiplier": 2},
    "House": {"hp": 200, "image": "buildings/house.png", "cost": 20, "resources": {"gold": 20, "wood": 15}},
    "Market": {"hp": 230, "image": "buildings/market.png", "cost": 30, "resources": {"gold": 30, "wood": 20, "stone": 25}},
    "Barracks": {"hp": 240, "image": "buildings/barracks.png", "cost": 40, "resources": {"gold": 40, "wood": 20, "stone": 15}, "unit": "Swordsman"},
    "Stable": {"hp": 225, "image": "buildings/stable.png", "cost": 25, "resources": {"gold": 35, "wood": 20, "stone": 15}, "unit": "Archer"},
    "Farm": {"hp": 250, "image": "buildings/farm.png", "cost": 25, "resources": {"gold": 25, "wood": 10}},
    "LumberMill": {"hp": 200, "image": "buildings/lumber.png", "cost": 40, "resources": {"gold": 40, "wood": 30, "stone": 10}},
    "Quarry": {"hp": 250, "image": "buildings/quarry.png", "cost": 50, "resources": {"gold": 20, "wood": 30, "stone": 10}},
}

# Unit data
UNIT_DATA = {
    "Swordsman": {"image": "characters/swordsman.png", "cost": {"gold": 50, "food": 30, "people": 1}, "hp": 10, "atk": 1},
    "Archer": {"image": "characters/bowman.png", "cost": {"gold": 60, "food": 40, "people": 1}, "hp": 8, "atk": 2},
}

# Enemy data
ENEMY_DATA = {
    "Goblin": {"image": "characters/bowman.png", "speed": 50, "hp": 8, "atk": 1},
    "Orc": {"image": "characters/swordsman.png", "speed": 70, "hp": 12, "atk": 2},
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
        self.speed = 75
        self.hp = UNIT_DATA[unit_type]["hp"]
        self.atk = UNIT_DATA[unit_type]["atk"]

    def update(self, dt):
        if self.moving and self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                travel_distance = self.speed * (dt / 1000)
                self.x += (dx / distance) * travel_distance
                self.y += (dy / distance) * travel_distance
                self.rect.topleft = (self.x, self.y)

                if math.hypot(dx, dy) <= travel_distance:  # Check if close enough to destination
                    self.moving = False
                    self.destination = None

class Enemy(GameObject):
    def __init__(self, unit_type, x, y, initial_target):
        super().__init__(x, y, ENEMY_DATA[unit_type]["image"])
        self.type = unit_type
        self.target = initial_target
        self.speed = ENEMY_DATA[unit_type]["speed"]
        self.hp = ENEMY_DATA[unit_type]["hp"]
        self.atk = ENEMY_DATA[unit_type]["atk"]

    def update(self, dt, game_messages=None):
        if self.target and self.target.hp <= 0:
            self.target = self.find_nearest_target(buildings + units)  # Find new target

        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                travel_distance = self.speed * (dt / 1000)
                self.x += (dx / distance) * travel_distance
                self.y += (dy / distance) * travel_distance
                self.rect.topleft = (self.x, self.y)

                if self.rect.colliderect(self.target.rect):
                    game_messages = self.attack_target(game_messages)

        return game_messages

    def attack_target(self, game_messages=None):
        if self.target:
            self.target.hp -= self.atk
            message = f"Enemy {self.type} attacked {self.target.type}"

            if self.target.hp <= 0:
                message = f"Enemy {self.type} destroyed {self.target.type}"
                self.target = self.find_nearest_target(buildings + units)

            if game_messages is not None:  # Only add message if list is provided
                add_game_message(message, game_messages)

        return game_messages

    def find_nearest_target(self, targets):
        valid_targets = [target for target in targets if target.hp > 0]
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
