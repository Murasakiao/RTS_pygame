# entities.py

import math

import pygame

from .astar import a_star
from .world import cell_to_pixel, pixel_to_cell
from .constants import (
    ALLY_DATA,
    BLACK,
    BLUE,
    BUILDING_DATA,
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_ATTACK_RANGE,
    ENEMY_DATA,
    GRID_SIZE,
    RED,
    UNIT_ATTACK_COOLDOWN,
    UNIT_ATTACK_RANGE,
)
from .utils import (
    add_game_message,
    check_collision_with_building,
    check_collision_with_enemy,
    check_collision_with_unit,
)

# --- Classes ---
class GameObject:
    def __init__(self, x, y, asset_key, image, font, size=(GRID_SIZE, GRID_SIZE)):
        self.x = x
        self.y = y
        self.asset_key = asset_key
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.font = font

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        hp = self.font.render(f"HP: {self.hp}", True, BLACK)
        screen.blit(hp, (self.rect.centerx - hp.get_width() // 2, self.rect.top + self.rect.height + 5))

class Building(GameObject):
    def __init__(self, x, y, building_type, image, font):
        self.type = building_type
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(
            x,
            y,
            data["asset_key"],
            image,
            font,
            size,
        )
        self.hp = data["hp"]

class Unit(GameObject):
    def __init__(self, unit_type, x, y, targets, image, font):
        # Get unit data based on type
        unit_data = ALLY_DATA.get(unit_type) or ENEMY_DATA.get(unit_type)
        if unit_data is None:
            raise ValueError(f"Invalid unit_type: {unit_type}")
        
        super().__init__(
            x,
            y,
            unit_data["asset_key"],
            image,
            font,
        )
        
        self.name = unit_data['name']  # Store the name separately
        self.type = unit_type  # Store the unit type as a string
        self.destination = None
        self.speed = unit_data.get("speed")
        self.hp = unit_data.get("hp", 100)
        self.attack = unit_data.get("atk", 10)  # Renamed to 'attack'
        self.path = [] # Initialize path as an empty list

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
        self.previous_target_position = None # Store previous target position

    def update(self, dt, grid, game_messages=None):
        """
        Update method to be implemented by subclasses
        Handles target selection, movement, and attacking
        """
        if game_messages is None:
            game_messages = []  # Create an empty list if None

        self.handle_target_selection()
        self.move_towards_target(dt, grid)
        self.handle_attack(dt, game_messages)
        return game_messages

    def handle_target_selection(self):
        """
        Select the nearest target if current target is invalid
        """
        if not self.target or self.target.hp <= 0:
            self.target = self.find_nearest_target()

    def move_towards_target(self, dt, grid):
        """Follow a valid route toward a target without a direct fallback."""
        path_needs_update = False
        movement_threshold = 2 * GRID_SIZE

        if self.target and self.target.hp > 0:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance_to_target = math.hypot(dx, dy)
            unit_range = self.get_attack_range()

            if distance_to_target <= unit_range:
                self.path = []
                self.destination = None
            elif not self.path or self.destination is None:
                path_needs_update = True
            elif self.previous_target_position:
                target_movement = math.hypot(
                    self.target.x - self.previous_target_position[0],
                    self.target.y - self.previous_target_position[1],
                )
                if target_movement > movement_threshold:
                    path_needs_update = True

            if path_needs_update:
                start_cell = pixel_to_cell((self.x, self.y), GRID_SIZE)
                target_cell = pixel_to_cell(
                    (self.target.x, self.target.y),
                    GRID_SIZE,
                )
                self.previous_target_position = (self.target.x, self.target.y)
                result = a_star(grid, start_cell, target_cell)
                self.path = list(result.path) if result.succeeded else []
                self.destination = (
                    cell_to_pixel(self.path[0], GRID_SIZE)
                    if self.path
                    else None
                )

        if not self.path:
            return

        next_cell = self.path[0]
        target_x, target_y = cell_to_pixel(next_cell, GRID_SIZE)
        dx = target_x - self.x
        dy = target_y - self.y
        distance_to_next_node = math.hypot(dx, dy)
        travel_distance = self.speed * (dt / 1000)

        if distance_to_next_node == 0:
            self.path.pop(0)
            self.destination = (
                cell_to_pixel(self.path[0], GRID_SIZE)
                if self.path
                else None
            )
        elif distance_to_next_node <= travel_distance:
            self.x = target_x
            self.y = target_y
            self.rect.topleft = (self.x, self.y)
            self.path.pop(0)
            self.destination = (
                cell_to_pixel(self.path[0], GRID_SIZE)
                if self.path
                else None
            )
        else:
            self.x += (dx / distance_to_next_node) * travel_distance
            self.y += (dy / distance_to_next_node) * travel_distance
            self.rect.topleft = (self.x, self.y)

    def handle_attack(self, dt, game_messages=None):
        """
        Handle attack cooldown and attacking
        """
        if game_messages is None:
            game_messages = []

        if self.target and self.attack_cooldown <= 0:
            if self.should_attack():
                self.attack_target(game_messages if game_messages is not None else [])
                self.attack_cooldown = self.get_attack_cooldown()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

    def attack_target(self, game_messages=None):
        """
        Attack the current target and generate game messages
        """
        if self.target:
            unit_name = self.name  # Use the stored name
            if hasattr(self.target, 'name'):
                target_name = self.target.name
            else:
                target_name = self.target.type  # Use type if no name attribute
            self.target.hp -= self.attack
            message = f"{unit_name} attacked {target_name} for {self.attack} damage."

            if self.target and self.target.hp <= 0:  # Check if target still exists
                message = f"{unit_name} destroyed {target_name}"
                self.target = None  # Clear target after destroying it
            
            if game_messages is not None:
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
                for cell in self.path:
                    grid_x, grid_y = cell_to_pixel(cell, GRID_SIZE)
                    rect = pygame.Rect(grid_x, grid_y, GRID_SIZE, GRID_SIZE)
                    pygame.draw.rect(screen, BLUE, rect, 2)

class AlliedUnit(Unit):
    def __init__(self, unit_type, x, y, targets, image, font):
        super().__init__(unit_type, x, y, targets, image, font)

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
    def __init__(self, unit_type, x, y, buildings, units, image, font):
        targets = buildings + units
        super().__init__(unit_type, x, y, targets, image, font)
        self.target_priority = "building"

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
