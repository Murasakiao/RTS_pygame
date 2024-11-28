import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25  # Smaller grid size

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("City Builder")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Building types
BUILDING_TYPES = {
    "Castle": "buildings/castle.png",
    "House": "buildings/house.png",
    "Market": "buildings/market.png",
    "Barracks": "buildings/barracks.png",
    "Stable": "buildings/stable.png",
    "Farm": "buildings/farm.png",
    "LumberMill": "buildings/lumber.png",  # Renamed for clarity
    "Quarry": "buildings/quarry.png",
}

# Building costs
BUILDING_COSTS = {
    "Farm": 25,
    "LumberMill": 40,
    "Quarry": 50,
    "Castle": 75,
    "House": 20,
    "Market": 30,
    "Barracks": 40,
    "Stable": 25,
}

# Unit types that can be trained in certain buildings
UNIT_TYPES = {
    "Barracks": "Swordsman",
    "Stable": "Knight",
}

# Unit data (images, costs, etc.)
UNITS = {
    "Swordsman": {
        "image": "characters/swordsman.png",
        "cost": {"gold": 25, "food": 10},
    },
    "Knight": {
        "image": "characters/knight.png",
        "cost": {"gold": 40, "food": 20},
    },
}

# Resource requirements
BUILDING_RESOURCES = {
    "Castle": {"gold": 75, "wood": 50, "stone": 100},
    "House": {"gold": 20, "wood": 15},
    "Market": {"gold": 30, "wood": 20, "stone": 25},
    "Barracks": {"gold": 40, "wood": 30, "stone": 40},
    "Stable": {"gold": 25, "wood": 20, "wood": 10},  # Corrected duplicate key
    "Farm": {"gold": 25, "wood": 10},
    "LumberMill": {"gold": 40, "wood": 20, "stone": 20},
    "Quarry": {"gold": 50, "wood": 25, "stone": 30},
}

class Building:
    def __init__(self, x, y, building_type):
        self.x = x
        self.y = y
        self.type = building_type
        self.size = (GRID_SIZE, GRID_SIZE)
        if building_type == "Castle":
            self.size = (GRID_SIZE * 2, GRID_SIZE * 2)  # Castle occupies 4 grids
        try:
            self.image = pygame.transform.scale(pygame.image.load(BUILDING_TYPES[building_type]), self.size)
        except pygame.error:
            # Fallback if image loading fails
            self.image = pygame.Surface(self.size)
            self.image.fill(BLACK)
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def draw(self):
        if self.image and self.rect:
            screen.blit(self.image, (self.x, self.y))

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

def add_game_message(message, messages, start_times):
    messages.append(message)
    start_times[message] = pygame.time.get_ticks()
    return messages, start_times

def update_preview_rect(mouse_pos, current_building_type):
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size = GRID_SIZE * 2 if current_building_type == "Castle" else GRID_SIZE
    return pygame.Rect(grid_x, grid_y, size, size)

def check_collision(preview_rect, buildings):
    for building in buildings:
        if building.rect.colliderect(preview_rect):
            return True
    return False

# Initialize game state
gold = 150
resources = {"wood": 100, "stone": 100, "food": 0}
resource_increase_rates = {
    "gold": 5,
    "wood": 2,
    "stone": 1,
    "food": 3,
}
buildings = []
current_building_type = "Castle"
font = pygame.font.Font(None, 20)
game_messages = []
message_start_times = {}
selected_building = None
building_cooldown = 0
BUILDING_COOLDOWN_TIME = 1000  # 1 second cooldown
message_duration = 5000  # 5 seconds

class Unit:
    def __init__(self, unit_type, x, y):
        self.type = unit_type
        self.x = x
        self.y = y
        try:
            self.image = pygame.transform.scale(pygame.image.load(UNITS[unit_type]["image"]), (GRID_SIZE, GRID_SIZE))
        except pygame.error as e:
            print(f"Error loading image for {unit_type}: {e}")
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))  # Fallback surface
            self.image.fill(RED) # Make it obvious there's a problem
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moving = False
        self.destination = None

    def update(self, dt):
        if self.moving:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            distance = (dx**2 + dy**2)**0.5

            if distance > 0:
                speed = 2  # Adjust for movement speed
                move_x = dx * speed * dt / 1000
                move_y = dy * speed * dt / 1000

                self.x += move_x
                self.y += move_y
                self.rect.topleft = (self.x, self.y)

            if abs(dx) < 1 and abs(dy) < 1:
                self.moving = False
                self.x = self.destination[0]
                self.y = self.destination[1]
                self.rect.topleft = (self.x, self.y)

    def draw(self):
        screen.blit(self.image, self.rect)

units = [] # List to store created Unit objects

# Define building map outside the loop using pygame key constants
building_