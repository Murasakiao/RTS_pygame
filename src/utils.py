# utils.py

import math
import random
import sys
import os
import pygame

# Add the rts_pygame directory to the sys.path list
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.entities import EnemyUnit
from src.entities import AlliedUnit
from constants import *

pygame.init()
font = pygame.font.Font(None, 20)

# --- Functions ---
def draw_grid(screen, color=BLACK, line_width=1, opacity=150):
    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(s, (*color, opacity), (x, 0), (x, SCREEN_HEIGHT), line_width)
            pygame.draw.line(s, (*color, opacity), (0, y), (SCREEN_WIDTH, y), line_width)
    screen.blit(s, (0, 0))

def add_game_message(message, game_messages, duration=MESSAGE_DURATION):
    current_time = pygame.time.get_ticks()
    game_messages[:] = [msg for msg in game_messages if current_time - msg["start_time"] < msg["duration"]]  # Remove expired messages

    if not any(msg["text"] == message for msg in game_messages):  # Add new message if not a duplicate
        game_messages.append({"text": message, "start_time": current_time, "duration": duration})

def update_preview_rect(mouse_pos, current_building_type):
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size_multiplier = BUILDING_DATA.get(current_building_type, {}).get("size_multiplier", 1)
    size = GRID_SIZE * size_multiplier
    return pygame.Rect(grid_x, grid_y, size, size)

def draw_resources(screen, font, resources, gold):
    resource_text = f"Gold: {int(gold)}"
    for resource, amount in resources.items():
        resource_text += f", {resource.capitalize()}: {int(amount)}"
    gold_text = font.render(resource_text, True, BLACK)
    screen.blit(gold_text, (10, 10))

def draw_building_preview(screen, preview_rect, collision, resources, gold, current_building_type):
    if preview_rect:  # Only draw if preview_rect exists
        building_resources = BUILDING_DATA.get(current_building_type, {}).get("resources", {})
        affordable = all(resources.get(resource, gold) >= amount for resource, amount in building_resources.items())
        color = GREEN if not collision and affordable else RED
        pygame.draw.rect(screen, color, preview_rect, 2)

def draw_messages(screen, font, game_messages):
    current_time = pygame.time.get_ticks()
    active_messages = [msg for msg in game_messages if current_time - msg["start_time"] < msg["duration"]]
    for i, msg in enumerate(active_messages):
        message_text = font.render(msg["text"], True, RED)
        screen.blit(message_text, (10, 30 + i * 20))

def draw_key_bindings(screen, font, building_map, screen_width, screen_height, grid_size, building_data):
    x = screen_width - 10 * grid_size  # Adjusted x position
    y = 10
    for key, building_type in building_map.items():
        text = f"{pygame.key.name(key)}: {building_type}"
        requirements = building_data.get(building_type, {}).get("resources", {})
        if requirements:
            text += f" ({', '.join(f'{resource}: {amount}' for resource, amount in requirements.items())})"
        text_surface = font.render(text, True, RED)
        screen.blit(text_surface, (x, y))
        y += 20

def check_collision(preview_rect, buildings, units):
    for building in buildings:
        if preview_rect.colliderect(building.rect):
            return True
    for unit in units:
        if preview_rect.colliderect(unit.rect):
            return True
    return False

def generate_spawn_point():
    side = random.choice(["left", "right", "top", "bottom"])
    if side == "left":
        return -GRID_SIZE, random.randint(0, SCREEN_HEIGHT - GRID_SIZE)
    elif side == "right":
        return SCREEN_WIDTH, random.randint(0, SCREEN_HEIGHT - GRID_SIZE)
    elif side == "top":
        return random.randint(0, SCREEN_WIDTH - GRID_SIZE), -GRID_SIZE
    else:  # bottom
        return random.randint(0, SCREEN_WIDTH - GRID_SIZE), SCREEN_HEIGHT

def spawn_enemies(buildings, units, current_wave, enemy_spawn_rate, mini_bosses=None): # Updated to handle mini-bosses correctly
    spawned_enemies = []

    if current_wave % 2 == 0 and mini_bosses:  # Spawn a mini-boss every 10th wave
        enemy_type = random.choice(mini_bosses) # Choose a random mini-boss
        spawn_x, spawn_y = generate_spawn_point()
        mini_boss = EnemyUnit(enemy_type, spawn_x, spawn_y, buildings, units, enhanced_data=ENEMY_DATA.get(enemy_type)) # Pass enhanced_data
        spawned_enemies.append(mini_boss)
        print(f"Wave {current_wave}: Spawning mini-boss: {enemy_type}")
        return spawned_enemies # Return after spawning the mini-boss

    # Spawn regular enemies, excluding mini-bosses
    num_regular_enemies = current_wave * enemy_spawn_rate
    for _ in range(num_regular_enemies):
        spawn_x, spawn_y = generate_spawn_point()
        regular_enemies = [enemy for enemy in ENEMY_DATA if "mini-boss" not in ENEMY_DATA[enemy]["name"].lower()] # Exclude mini-bosses
        enemy_type = random.choice(regular_enemies)
        enemy = EnemyUnit(enemy_type, spawn_x, spawn_y, buildings, units)
        spawned_enemies.append(enemy)
        print(f"Wave {current_wave}: Spawning regular enemy: {enemy_type}")

    return spawned_enemies

def manage_waves(wave_timer, current_wave, dt, buildings, units, enemies, enemy_spawn_rate, wave_interval=WAVE_INTERVAL, mini_bosses=None): # Added mini_bosses parameter
    """Manages wave timing and enemy spawning with an interval between waves."""
    wave_in_progress = False

    if wave_timer >= wave_interval and not wave_in_progress:
        new_enemies = spawn_enemies(buildings, units, current_wave, enemy_spawn_rate)
        enemies.extend(new_enemies)
        wave_timer = 0
        current_wave += 1
        wave_in_progress = True # Set the flag when a wave starts
        print(f"Starting wave {current_wave}") # Debug message

    elif wave_in_progress and not enemies: # Check if wave is finished (no enemies left)
        wave_in_progress = False # Reset the flag
        wave_timer = 0 # Reset the timer to start the interval
        print(f"Wave {current_wave -1} finished. Next wave in {wave_interval/1000} seconds.") # Debug message

    elif not wave_in_progress: # Only increment timer if no wave is in progress
        wave_timer += dt

    return wave_timer, current_wave, wave_in_progress, enemies

def draw_debug_info(screen, font, debug_info, x=10, y=40):
    for i, line in enumerate(debug_info):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (x, y + i * 20))


def manage_waves(wave_timer, current_wave, dt, buildings, units, enemies, enemy_spawn_rate, wave_interval=WAVE_INTERVAL, mini_bosses=None): # Added mini_bosses parameter
    """Manages wave timing and enemy spawning with an interval between waves."""
    wave_in_progress = False

    if wave_timer >= wave_interval and not wave_in_progress:
        new_enemies = spawn_enemies(buildings, units, current_wave, enemy_spawn_rate, mini_bosses=mini_bosses) # Pass mini_bosses to spawn_enemies
        enemies.extend(new_enemies)
        wave_timer = 0
        current_wave += 1
        wave_in_progress = True # Set the flag when a wave starts
        print(f"Starting wave {current_wave}") # Debug message

    elif wave_in_progress and not enemies: # Check if wave is finished (no enemies left)
        wave_in_progress = False # Reset the flag
        wave_timer = 0 # Reset the timer to start the interval
        print(f"Wave {current_wave -1} finished. Next wave in {wave_interval/1000} seconds.") # Debug message

    elif not wave_in_progress: # Only increment timer if no wave is in progress
        wave_timer += dt

    return wave_timer, current_wave, wave_in_progress, enemies
