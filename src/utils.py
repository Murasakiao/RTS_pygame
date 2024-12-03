# utils.py

import math
import random
import sys
import os
import pygame

# Add the rts_pygame directory to the sys.path list
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from constants import *
# from entities import EnemyUnit  No longer needed

pygame.init()
font = pygame.font.Font(None, 20)

# --- Functions ---
def draw_grid(screen, color=BLACK, line_width=1):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect, line_width)

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

def check_collision_with_building(unit, buildings):
    for building in buildings:
        if unit.colliderect(building.rect):
            return True
    return False

def check_collision_with_unit(unit, units, exclude_unit=None):
    for other_unit in units:
        if other_unit is not exclude_unit and unit.colliderect(other_unit.rect):
            return True
    return False

def check_collision_with_enemy(unit, enemies):
    for enemy in enemies:
        if unit.colliderect(enemy.rect):
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

def spawn_enemies(buildings, units, current_wave, enemy_spawn_rate):
    spawned_enemies = []
    for _ in range(current_wave * enemy_spawn_rate):
        spawn_x, spawn_y = generate_spawn_point()
        enemy_type = random.choice(list(ENEMY_DATA.keys()))
        enemy = EnemyUnit(enemy_type, spawn_x, spawn_y, buildings, units)  # Pass buildings and units separately
        spawned_enemies.append(enemy)

    return spawned_enemies

import heapq

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, end, buildings):
    neighbors = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    close_set = set()
    came_from = {}
    gscore = {start: 0}
    fscore = {start: heuristic(start, end)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    grid_width = len(grid[0])
    grid_height = len(grid)

    while oheap:
        current = heapq.heappop(oheap)[1]

        if current == end:
            data = []
            while current in came_from:
                data.append(current)
                current = came_from[current]
            data.append(start)
            return data[::-1]  # Return reversed path

        close_set.add(current)
        for i, j in neighbors:
            neighbor = current[0] + i, current[1] + j
            tentative_g_score = gscore[current] + heuristic(current, neighbor)
            if 0 <= neighbor[0] < grid_width and 0 <= neighbor[1] < grid_height:
                if any(building.rect.collidepoint(neighbor[0] * GRID_SIZE, neighbor[1] * GRID_SIZE) for building in buildings):
                    continue  # Skip if cell is occupied by a building
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return False

class EnemyUnit(Unit):  # Moved from entities.py
    def __init__(self, unit_type, x, y, buildings, units, font=None):
        targets = buildings + units
        super().__init__(unit_type, x, y, targets, font)

    def should_attack(self):
        """
        Determine if the unit should attack based on rect collision
        """
        if not self.target:
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)
        unit_range = ENEMY_DATA[self.type].get("range", ENEMY_ATTACK_RANGE)  # Get range, default to UNIT_ATTACK_RANGE
        return distance <= unit_range

    def get_attack_range(self):
        """
        Get the attack range for this unit.
        """
        return ENEMY_DATA.get(self.type, {}).get("range", ENEMY_ATTACK_RANGE)

    def get_attack_cooldown(self):
        """
        Get the attack cooldown for enemy units
        """
        return ENEMY_DATA.get(self.type, {}).get("attack_cooldown", ENEMY_ATTACK_COOLDOWN)


def draw_debug_info(screen, font, debug_info, x=10, y=40): # Keep this function in utils.py
    for i, line in enumerate(debug_info):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (x, y + i * 20))
