import math
import random
import pygame
from constants import *

pygame.init()
font = pygame.font.Font(None, 20)

def draw_grid(screen, color=BLACK, line_width=1):
    # ... (same code as before)

def add_game_message(message, game_messages, duration=MESSAGE_DURATION):
    # ... (same code as before)

def update_preview_rect(mouse_pos, current_building_type):
    # ... (same code as before)

def draw_resources(screen, font, resources, gold):
    # ... (same code as before)

def draw_building_preview(screen, preview_rect, collision, resources, gold, current_building_type):
    # ... (same code as before)

def draw_messages(screen, font, game_messages):
    # ... (same code as before)

def draw_key_bindings(screen, font, building_map, screen_width, screen_height, grid_size, building_data):
    # ... (same code as before)

def check_collision(preview_rect, buildings, units):
    # ... (same code as before)

def generate_spawn_point():
    # ... (same code as before)

def spawn_enemies(current_wave, enemy_spawn_rate): # Simplified enemy spawning
    enemies = []
    for _ in range(current_wave * enemy_spawn_rate):
        x, y = generate_spawn_point()
        enemy_type = random.choice(list(ENEMY_DATA.keys()))
        enemy = EnemyUnit(ENEMY_DATA[enemy_type], x, y, [], []) # No initial targets
        enemies.append(enemy)
    return enemies

def draw_debug_info(screen, font, debug_info, x=10, y=40):
    # ... (same code as before)

def can_afford(resources, gold, cost): # Helper function to check affordability
    for resource, amount in cost.items():
        if resource == "gold":
            if gold < amount:
                return False
        elif resources.get(resource, 0) < amount:
            return False
    return True

def deduct_cost(resources, gold, cost): # Helper function to deduct cost
    for resource, amount in cost.items():
        if resource == "gold":
            gold -= amount
        else:
            resources[resource] -= amount

