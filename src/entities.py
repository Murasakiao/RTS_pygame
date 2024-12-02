import math
import pygame
from constants import *
from utils import *

pygame.init()

class GameObject:
    def __init__(self, x, y, image_path, size=(GRID_SIZE, GRID_SIZE)):
        self.x = x
        self.y = y
        try:
            self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        except pygame.error:
            self.image = pygame.Surface(size)
            self.image.fill(BLACK)  # Fallback image
        self.rect = self.image.get_rect(center=(x, y)) # Center the rect
        self.font = pygame.font.Font(None, 15)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        hp_text = self.font.render(f"HP: {self.hp}", True, BLACK)
        screen.blit(hp_text, (self.rect.centerx - hp_text.get_width() // 2, self.rect.top + self.rect.height + 5))

class Building(GameObject):
    def __init__(self, x, y, building_type):
        self.type = building_type
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(x, y, data["image"], size)
        self.hp = data["hp"]

class Unit(GameObject):
    def __init__(self, unit_type, x, y, targets):
        super().__init__(x, y, unit_type["image"])
        self.type = unit_type
        self.speed = unit_type.get("speed", 75)
        self.hp = unit_type.get("hp", 100)
        self.atk = unit_type.get("atk", 10)
        self.target = None
        self.attack_cooldown = 0
        self.destination = None
        self.targets = targets

    def set_destination(self, destination):
        self.destination = destination

    def update(self, dt, game_messages, targets): # targets argument added
        if self.hp <= 0: # Check if unit is dead
            return

        self.find_target(targets) # Pass targets as argument
        self.move(dt)
        self.attack(dt, game_messages)

    def find_target(self, targets):
        if not self.target or self.target.hp <= 0:
            valid_targets = [target for target in targets if target.hp > 0]
            if valid_targets:
                self.target = min(valid_targets, key=lambda target: distance(self, target))

    def move(self, dt):
        if self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            dist = math.hypot(dx, dy)
            if dist > 0:
                travel_distance = self.speed * (dt / 1000)
                if dist <= travel_distance:
                    self.x, self.y = self.destination
                    self.destination = None
                else:
                    self.x += dx / dist * travel_distance
                    self.y += dy / dist * travel_distance
                self.rect.center = (self.x, self.y) # Update rect position

    def attack(self, dt, game_messages):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        if self.target and self.attack_cooldown <= 0 and self.should_attack():
            self.target.hp -= self.atk
            add_game_message(f"{self.type['name']} attacked {self.target.type['name']}", game_messages)
            if self.target.hp <= 0:
                add_game_message(f"{self.type['name']} destroyed {self.target.type['name']}", game_messages)
                self.target = None  # Find a new target next frame
            self.attack_cooldown = self.get_attack_cooldown()

    def should_attack(self):
        raise NotImplementedError

    def get_attack_cooldown(self):
        raise NotImplementedError

class AlliedUnit(Unit):
    def __init__(self, unit_type, x, y, enemies):
        super().__init__(unit_type, x, y, enemies)

    def should_attack(self):
        return self.target and distance(self, self.target) <= UNIT_ATTACK_RANGE

    def get_attack_cooldown(self):
        return UNIT_ATTACK_COOLDOWN

class EnemyUnit(Unit):
    def __init__(self, unit_type, x, y, buildings, units):
        super().__init__(unit_type, x, y, buildings + units)

    def should_attack(self):
        return self.target and self.rect.colliderect(self.target.rect)

    def get_attack_cooldown(self):
        return ENEMY_ATTACK_COOLDOWN

    def update(self, dt, game_messages, buildings, units): # Added buildings and units arguments
        super().update(dt, game_messages, buildings + units) # Pass combined targets

class TerrainGenerator: # Remains unchanged
    # ... (same code as before)

def distance(obj1, obj2): # Helper function to calculate distance
    return math.hypot(obj1.x - obj2.x, obj1.y - obj2.y)

