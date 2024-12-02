# entities.py

import math
import pygame
from constants import *
from utils import *

pygame.init()

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
        self.font = pygame.font.Font(None, 15)

class Unit(GameObject):
    def __init__(self, unit_type, x, y, enemies, font, buildings, units):
        super().__init__(x, y, UNIT_DATA[unit_type]["image"])
        self.type = unit_type
        self.moving = False
        self.destination = None
        self.speed = 75
        self.hp = UNIT_DATA[unit_type]["hp"]
        self.atk = UNIT_DATA[unit_type]["atk"]
        self.target = None
        self.attack_cooldown = 0
        self.enemies = enemies
        self.font = pygame.font.Font(None, 15)
        self.buildings = buildings
        self.units = units

    def update(self, dt, game_messages):
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

        if self.target:
            if self.attack_cooldown <= 0:
                if math.hypot(self.target.x - self.x, self.target.y - self.y) <= UNIT_ATTACK_RANGE:
                    self.target.hp -= self.atk
                    add_game_message(f"{self.type} attacked {self.target.type}", game_messages)
                    if self.target.hp <= 0:
                        add_game_message(f"{self.type} killed {self.target.type}", game_messages)
                        self.target = None  # Reset target if killed
                    self.attack_cooldown = UNIT_ATTACK_COOLDOWN
            else:
                self.attack_cooldown -= dt

        if not self.target:
            self.target = self.find_nearest_target(self.enemies)
        elif self.target.hp <= 0: # Find a new target if current target is dead
            self.target = self.find_nearest_target(self.enemies)

        if self.target and not self.moving:
            self.destination = (self.target.x, self.target.y)

    def find_nearest_target(self, enemies):
        # Find the nearest enemy
        nearest_enemy = None
        min_distance = float('inf')

        for enemy in enemies:
            distance = math.hypot(enemy.x - self.x, enemy.y - self.y)
            if distance < min_distance:
                min_distance = distance
                nearest_enemy = enemy
        return nearest_enemy

class Enemy(GameObject):
    def __init__(self, enemy_type, x, y, buildings, units, font):
        super().__init__(x, y, ENEMY_DATA[enemy_type]["image"])
        self.type = enemy_type
        self.speed = ENEMY_DATA[enemy_type]["speed"]
        self.hp = ENEMY_DATA[enemy_type]["hp"]
        self.atk = ENEMY_DATA[enemy_type]["atk"]
        self.attack_cooldown = 0
        self.target = self.find_nearest_target(buildings)  # Initially target buildings
        if not self.target:
            self.target = self.find_nearest_target(units)
        self.font = font

    def update(self, dt, game_messages):
        if self.target:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.hypot(dx, dy)

            if distance > 0:
                travel_distance = self.speed * (dt / 1000)
                self.x += (dx / distance) * travel_distance
                self.y += (dy / distance) * travel_distance
                self.rect.topleft = (self.x, self.y)

            if self.attack_cooldown <= 0:
                if distance <= GRID_SIZE:  # Attack if close enough
                    self.target.hp -= self.atk
                    add_game_message(f"{self.type} attacked {self.target.type}", game_messages)
                    if self.target.hp <= 0:
                        add_game_message(f"{self.type} destroyed {self.target.type}", game_messages)
                        if isinstance(self.target, Building):
                            self.target = self.find_nearest_target(buildings)
                            if not self.target:
                                self.target = self.find_nearest_target(units)
                        else:
                            self.target = self.find_nearest_target(units)
                            if not self.target:
                                self.target = self.find_nearest_target(buildings)
                    self.attack_cooldown = ENEMY_DATA[self.type]["attack_cooldown"]
            else:
                self.attack_cooldown -= dt
        return game_messages

    def find_nearest_target(self, targets):
        nearest_target = None
        min_distance = float('inf')

        for target in targets:
            distance = math.hypot(target.x - self.x, target.y - self.y)
            if distance < min_distance:
                min_distance = distance
                nearest_target = target

        return nearest_target
