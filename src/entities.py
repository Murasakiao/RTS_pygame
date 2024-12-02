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
        self.attack_cooldown = 9000
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
        elif self.target.hp <=0: # Find a new target if current target is dead
            self.target = self.find_nearest_target(self.enemies)


        if self.target and not self.moving:
            self.destination = (self.target.x, self.target.y)
            self.moving = True

    def find_nearest_target(self, targets):
        valid_targets = [target for target in targets if target.hp > 0]  # Only target living enemies
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        return None

    def draw(self, screen):
        super().draw(screen)
        # Only draw target indicator if target is alive
        if self.target and self.target.hp > 0:
            target_text = self.font.render(self.target.type, True, RED)
            screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, self.rect.top - target_text.get_height() - 5))
        collided_with_building = check_collision_with_building(self.rect, self.buildings)
        collided_with_unit = check_collision_with_unit(self.rect, self.units, exclude_unit=self)
        collided_with_enemy = check_collision_with_enemy(self.rect, self.enemies)
        collided = collided_with_building or collided_with_unit or collided_with_enemy
        col = self.font.render("COLLIDED" if collided else "not", True, RED)
        screen.blit(col, (self.rect.centerx - col.get_width() // 2, self.rect.top - col.get_height() - 10))

class Enemy(GameObject):
    def __init__(self, unit_type, x, y, initial_target, buildings, units, font):
        super().__init__(x, y, ENEMY_DATA[unit_type]["image"])
        self.type = unit_type
        self.target = initial_target
        self.speed = ENEMY_DATA[unit_type]["speed"]
        self.hp = ENEMY_DATA[unit_type]["hp"]
        self.atk = ENEMY_DATA[unit_type]["atk"]
        self.buildings = buildings
        self.units = units
        self.font = pygame.font.Font(None, 15)
        self.attack_cooldown = 2000  

    def update(self, dt, game_messages=None):
        if self.target and self.target.hp <= 0:
            self.target = self.find_nearest_target(self.buildings + self.units)  # Find new target

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

    def attack_target(self, game_messages=None, dt=0):
        if self.attack_cooldown <= 0:
            if self.target:
                self.target.hp -= self.atk
                message = f"Enemy {self.type} attacked {self.target.type}"
                if self.target.hp <= 0:
                    message = f"Enemy {self.type} destroyed {self.target.type}"
                    self.target = self.find_nearest_target(self.buildings + self.units)
                if game_messages is not None:
                    add_game_message(message, game_messages)
                self.attack_cooldown = 2000  # reset cooldown
        else:
            self.attack_cooldown -= dt  # decrement cooldown

        return game_messages

    def find_nearest_target(self, targets):
        valid_targets = [target for target in targets if target.hp > 0]
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        return None

    def draw(self, screen):
        super().draw(screen)
        if self.target:
            target_text = self.font.render(self.target.type, True, RED)
            screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, self.rect.top - target_text.get_height() - 5))
        # collided_with_building = check_collision_with_building(self.rect, self.buildings)
        # collided_with_unit = check_collision_with_unit(self.rect, self.units, exclude_unit=self)
        # collided = collided_with_building or collided_with_unit
        # col = self.font.render("COLLIDED" if collided else "not", True, RED)
        # screen.blit(col, (self.rect.centerx - col.get_width() // 2, self.rect.top - col.get_height() - 10))

class TerrainGenerator:
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

# Import add_game_message after Enemy class is defined
from src.utils import add_game_message