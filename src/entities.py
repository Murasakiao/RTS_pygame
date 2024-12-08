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
        # Use a default image path if not provided
        default_image = 'default_unit.png'  # Make sure this exists
        try:
            self.image = pygame.transform.scale(
                pygame.image.load(image_path or default_image), 
                size
            )
        except pygame.error:
            # Fallback to a simple surface if image loading fails
            self.image = pygame.Surface(size)
            self.image.fill(BLACK)  # Fallback image
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = pygame.font.Font(None, 12)

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

class Unit(GameObject):
    def __init__(self, unit_type, x, y, targets, font=None):
        # Get unit data based on type
        unit_data = ALLY_DATA.get(unit_type) or ENEMY_DATA.get(unit_type)
        if unit_data is None:
            raise ValueError(f"Invalid unit_type: {unit_type}")
        
        super().__init__(x, y, unit_data["image"])
        
        self.name = unit_data['name']  # Store the name separately
        self.type = unit_type  # Store the unit type as a string
        self.destination = None
        self.speed = unit_data.get("speed")
        self.hp = unit_data.get("hp", 100)
        self.attack = unit_data.get("atk", 10)  # Renamed to 'attack'
        self.path = [] # Initialize path as an empty list

        self.font = font or pygame.font.Font(None, 12)
        
        # Ensure targets is a list
        if targets is None:
            self.targets = []
        elif isinstance(targets, list):
            self.targets = targets
        else:
            # If a single target is passed, convert to a list
            self.targets = [targets]
        
        self.target = None
        self.attack_cooldown = 0

    def update(self, dt, game_messages=None):
        """
        Update method to be implemented by subclasses
        Handles target selection, movement, and attacking
        """
        self.handle_target_selection()
        self.move_towards_target(dt)
        self.handle_attack(dt, game_messages)
        return game_messages

    def handle_target_selection(self):
        """
        Select the nearest target if current target is invalid
        """
        if not self.target or self.target.hp <= 0:
            self.target = self.find_nearest_target()

    def move_towards_target(self, dt):
        """
        Move the unit towards its current target or along a path, or stop if in attack range.
        """

        # if self.target:
        #     dx = self.target.x - self.x
        #     dy = self.target.y - self.y
        #     distance = math.hypot(dx, dy)
        #     unit_range = self.get_attack_range()  # Abstract range calculation

        #     if distance <= unit_range:
        #         self.destination = None  # Stop moving when in range
        #     elif self.destination:
        #         dx = self.destination[0] - self.x
        #         dy = self.destination[1] - self.y
        #         distance = math.hypot(dx, dy)

        #         if distance > 0:
        #             travel_distance = self.speed * (dt / 1000)

        #             if distance <= travel_distance:
        #                 self.x = self.destination[0]
        #                 self.y = self.destination[1]
        #                 self.destination = None
        #             else:
        #                 self.x += (dx / distance) * travel_distance
        #                 self.y += (dy / distance) * travel_distance

        #             self.rect.topleft = (self.x, self.y)
        #     elif distance > unit_range:  # Move towards target if not in range and no destination
        #         travel_distance = self.speed * (dt / 1000)
        #         self.x += (dx / distance) * travel_distance
        #         self.y += (dy / distance) * travel_distance
        #         self.rect.topleft = (self.x, self.y)
        # elif self.destination:  # Move towards destination even if no target
        #     dx = self.destination[0] - self.x
        #     dy = self.destination[1] - self.y
        #     distance = math.hypot(dx, dy)

        #     if distance > 0:
        #         travel_distance = self.speed * (dt / 1000)

        #         if distance <= travel_distance:
        #             self.x = self.destination[0]
        #             self.y = self.destination[1]
        #             self.destination = None
        #         else:
        #             self.x += (dx / distance) * travel_distance
        #             self.y += (dy / distance) * travel_distance

        #         self.rect.topleft = (self.x, self.y)

        if self.path:
            if len(self.path) > 1:
                next_node = self.path[1]
                dx = next_node.x * GRID_SIZE - self.x
                dy = next_node.y * GRID_SIZE - self.y
                distance = math.hypot(dx, dy)

                if distance > 0:
                    travel_distance = self.speed * (dt / 1000)
            elif self.destination and not self.target:
                dx = self.destination[0] - self.x
                dy = self.destination[1] - self.y
                distance = math.hypot(dx, dy)

                if distance > 0:
                    travel_distance = self.speed * (dt / 1000)
                    self.x += (dx / distance) * travel_distance
                    self.y += (dy / distance) * travel_distance
                    self.rect.topleft = (self.x, self.y)


    def handle_attack(self, dt, game_messages):
        """
        Handle attack cooldown and attacking
        """
        if self.target and self.attack_cooldown <= 0:
            if self.should_attack():
                self.attack_target(game_messages)
                self.attack_cooldown = self.get_attack_cooldown()
        
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def attack_target(self, game_messages):
        """
        Attack the current target and generate game messages
        """
        if self.target:
            # Use the unit type name instead of the entire dictionary
            unit_name = self.name  # Use the stored name
            # Use the unit type name instead of the entire dictionary
            unit_name = self.name  # Use the stored name
            if hasattr(self.target, 'name'):
                target_name = self.target.name
            else:
                target_name = self.target.type  # Use type if no name attribute
            self.target.hp -= self.attack
            message = f"{unit_name} attacked {target_name} for {self.attack} damage."

            if self.target and self.target.hp <= 0:  # Check if target still exists
                message = f"{unit_name} destroyed {target_name}"
                # Automatically find a new target after destroying current one
                self.target = None
            
            if game_messages is not None:
                add_game_message(message, game_messages)

    def find_nearest_target(self):
        """
        Find the nearest valid target, prioritizing based on enemy type.
        """
        priority_targets = []
        other_targets = []

        for target in self.targets:
            if (hasattr(target, 'hp') and hasattr(target, 'x') and hasattr(target, 'y') and target.hp > 0):
                if isinstance(self, EnemyUnit) and hasattr(self, 'target_priority'):  # Check if it's an enemy unit
                    if (self.target_priority == "building" and isinstance(target, Building)) or \
                       (self.target_priority == "unit" and isinstance(target, Unit)):
                        priority_targets.append(target)
                    else:
                        other_targets.append(target)
                else:  # If not an enemy unit or no priority, treat all as other targets
                    other_targets.append(target)

        if priority_targets:
            return min(priority_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        elif other_targets:
            return min(other_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        else:
            return None

    def draw(self, screen, units, buildings, enemies, show_debug):  # Add show_debug parameter
        """
        Draw the unit with additional information, including the path.
        """
        super().draw(screen)

        if show_debug:
            # Draw collision information
            collided_with_unit = check_collision_with_unit(self.rect, units, exclude_unit=self)
            collided_with_building = check_collision_with_building(self.rect, buildings)
            collided_with_enemy = check_collision_with_unit(self.rect, enemies, exclude_unit=self)
            if collided_with_unit or collided_with_building or collided_with_enemy:
                collide_text = self.font.render("COLLIDING", True, RED)
                screen.blit(collide_text, (self.rect.centerx - collide_text.get_width() // 2,
                                            self.rect.top + collide_text.get_height() + 5))

            # Draw target information if a target exists
            if self.target and self.target.hp > 0:
                target_text = self.font.render(str(self.target.type), True, RED)
                screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2,
                                        self.rect.top - target_text.get_height() - 5))
            
            # Draw path information
            if self.path:  # Only draw if there's a path
                for node in self.path:
                    grid_x = node.x * GRID_SIZE
                    grid_y = node.y * GRID_SIZE
                    rect = pygame.Rect(grid_x, grid_y, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(screen, BLUE, rect, 2)

class AlliedUnit(Unit):
    def __init__(self, unit_type, x, y, targets, font=None):
        super().__init__(unit_type, x, y, targets, font)

    def should_attack(self):
        """
        Determine if the unit should attack based on attack range
        """
        if not self.target:
            return False
        
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)
        unit_range = ALLY_DATA[self.type].get("range", UNIT_ATTACK_RANGE)  # Get range, default to UNIT_ATTACK_RANGE
        return distance <= unit_range

    def get_attack_range(self):
        """
        Get the attack range for this unit.
        """
        return ALLY_DATA.get(self.type, {}).get("range", UNIT_ATTACK_RANGE)

    def get_attack_cooldown(self):
        """
        Get the attack cooldown for allied units
        """
        return ALLY_DATA.get(self.type, {}).get("attack_cooldown", UNIT_ATTACK_COOLDOWN)

class EnemyUnit(Unit):
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
    
# --- other Funtions --- 
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

# Import add_game_message after Enemy class is defined
from src.utils import add_game_message
