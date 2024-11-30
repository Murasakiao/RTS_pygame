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
ENEMY_SPAWN_RATE = 2
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
# ... (Building, Unit, and Enemy Data remain unchanged)

# --- Classes ---
# ... (GameObject and Building classes remain unchanged)

class Unit(GameObject):
    # ... (Existing code remains unchanged)

    def update(self, dt, enemies):
        if self.target and self.target.hp > 0:  # Check if target is alive
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)

            if distance <= UNIT_ATTACK_RANGE:
                self.attack(dt, enemies)
            elif self.moving:  # Only move if not attacking
                travel_distance = self.speed * (dt / 1000)
                self.x += (dx / distance) * travel_distance
                self.y += (dy / distance) * travel_distance
                self.rect.topleft = (self.x, self.y)

                if math.hypot(dx, dy) <= travel_distance:
                    self.moving = False
                    self.destination = None
        elif self.moving and self.destination:  # Move towards destination if no target
            # ... (Existing movement code remains unchanged)

    def attack(self, dt, enemies):
        now = pygame.time.get_ticks()
        if now - self.last_attack >= UNIT_ATTACK_COOLDOWN:
            self.target.hp -= self.atk
            add_game_message(f"{self.type} attacked {self.target.type}", game_messages)
            if self.target.hp <= 0:
                add_game_message(f"{self.type} killed {self.target.type}", game_messages)
                enemies.remove(self.target)  # Remove the enemy from the list
                self.target = None  # Reset target
            self.last_attack = now

    def find_nearest_target(self, targets):
        valid_targets = [target for target in targets if target.hp > 0]
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        return None

    def draw(self, screen):
        # ... (Existing drawing code remains unchanged)

# ... (Enemy, TerrainGenerator classes remain unchanged)

# --- Functions ---
# ... (Existing functions remain unchanged)

# --- Game Initialization ---
# ... (Existing initialization code remains unchanged)

# Add last_attack attribute to Unit class
for unit in units:
    unit.last_attack = 0

# --- Game Loop ---
running = True
show_debug = True
while running:
    # ... (Existing game loop code remains unchanged)

    # --- Game Updates ---
    for unit in units:
        unit.update(dt, enemies)  # Pass enemies list to unit update

    for enemy in enemies:
        game_messages = enemy.update(dt, game_messages)

    # ... (Rest of the game loop code remains unchanged)
