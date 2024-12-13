# entities.py

import math
import pygame
from constants import *
from utils import *
from astar import a_star, Node

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
        unit_data = (ALLY_DATA.get(unit_type) or ENEMY_DATA.get(unit_type)) 
        if unit_data is None:
            raise ValueError(f"Invalid unit_type: {unit_type}")
        
        size_multiplier = unit_data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        
        super().__init__(x, y, unit_data["image"], size)
        
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
        self.previous_target_position = None # Store previous target position

    def update(self, dt, grid, game_messages=None): # Add grid parameter
        """
        Update method to be implemented by subclasses
        Handles target selection, movement, and attacking
        """
        if game_messages is None:
            game_messages = []  # Create an empty list if None

        self.handle_target_selection(grid) # Pass grid to handle_target_selection
        self.move_towards_target(dt, grid)
        self.handle_attack(dt, game_messages)
        return game_messages

    def handle_target_selection(self, grid): # Add grid parameter
        """
        Select the nearest target if current target is invalid
        """
        if not self.target or self.target.hp <= 0:
            self.target = self.find_nearest_target(grid) # Pass grid to find_nearest_target

    def move_towards_target(self, dt, grid):
        """Moves the unit towards its target or destination, using A* pathfinding."""
        path_needs_update = False  # Flag to track path updates
        movement_threshold = 3 * GRID_SIZE # Adjust this threshold as needed

        if self.target and self.target.hp > 0 and self.destination is None:
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance_to_target = math.hypot(dx, dy)
            unit_range = self.get_attack_range()

            target_grid_x = int(self.target.x // GRID_SIZE)
            target_grid_y = int(self.target.y // GRID_SIZE)

            # Check if target is in water/obstacle
            grid_width = len(grid[0])
            grid_height = len(grid)
            if 0 <= target_grid_x < grid_width and 0 <= target_grid_y < grid_height and grid[target_grid_y][target_grid_x][1] == 1:
                self.path = []  # Clear path
                self.destination = None
                return  # Skip pathfinding

            if distance_to_target <= unit_range:
                self.destination = None  # Stop if in attack range
                self.path = []  # Clear path if in range
            elif not self.path:  # Recalculate path if no path exists
                path_needs_update = True
            elif self.previous_target_position: # Check if previous position is available
                target_movement = math.hypot(self.target.x - self.previous_target_position[0], self.target.y - self.previous_target_position[1])
                if target_movement > movement_threshold:
                    path_needs_update = True
            else:
                 path_needs_update = True # First time, recalculate

            if path_needs_update:
                start_grid_x = int(self.x // GRID_SIZE)
                start_grid_y = int(self.y // GRID_SIZE)
                end_grid_x = int(self.target.x // GRID_SIZE)
                end_grid_y = int(self.target.y // GRID_SIZE)
                self.previous_target_position = (self.target.x, self.target.y) # Update previous position

                # Add boundary checks here
                grid_width = len(grid[0])
                grid_height = len(grid)
                if 0 <= start_grid_x < grid_width and 0 <= start_grid_y < grid_height and 0 <= end_grid_x < grid_width and 0 <= end_grid_y < grid_height:
                    self.path = a_star(grid, (start_grid_x, start_grid_y), (end_grid_x, end_grid_y)) or [] # Find path to target
                else:
                    self.path = []  # Clear path if out of bounds

        # Destination handling (for both mouse clicks and path following)
        if self.path:  # Prioritize following the path
             next_node = self.path[0]  # Get the next node from the path
             dx = next_node.x * GRID_SIZE - self.x
             dy = next_node.y * GRID_SIZE - self.y
             distance_to_next_node = math.hypot(dx, dy)

             # Check if target is within attack range
             if self.target:
                 dx_target = self.target.x - self.x
                 dy_target = self.target.y - self.y
                 distance_to_target = math.hypot(dx_target, dy_target)
                 if distance_to_target <= self.get_attack_range():
                     self.path = []  # Clear path if target is within range
                     return  # Stop moving

             travel_distance = self.speed * (dt / 1000)

             if distance_to_next_node <= travel_distance:  # Reached the next node
                 self.x = next_node.x * GRID_SIZE
                 self.y = next_node.y * GRID_SIZE
                 self.rect.topleft = (self.x, self.y)
                 self.path.pop(0)  # Remove the current node from the path

                 if not self.path:  # If path is empty, clear destination
                     self.destination = None
             else:  # Move towards the next node
                 self.x += (dx / distance_to_next_node) * travel_distance
                 self.y += (dy / distance_to_next_node) * travel_distance
                 self.rect.topleft = (self.x, self.y)

        elif self.destination:  # Move towards clicked destination if no path
             dx = self.destination[0] - self.x
             dy = self.destination[1] - self.y
             distance_to_destination = math.hypot(dx, dy)

             # Check if target is within attack range
             if self.target:
                 dx_target = self.target.x - self.x
                 dy_target = self.target.y - self.y
                 distance_to_target = math.hypot(dx_target, dy_target)
                 if distance_to_target <= self.get_attack_range():
                     self.destination = None  # Clear destination if target is within range
                     return  # Stop moving

             travel_distance = self.speed * (dt / 1000)

             if distance_to_destination <= travel_distance:
                 self.x = self.destination[0]
                 self.y = self.destination[1]
                 self.rect.topleft = (self.x, self.y)
                 self.destination = None  # Clear destination once reached
             else:
                 self.x += (dx / distance_to_destination) * travel_distance
                 self.y += (dy / distance_to_destination) * travel_distance
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

    def find_nearest_target(self, grid):
        """
        Find the nearest valid target, prioritizing based on enemy type.
        """
        reachable_targets = []
        unreachable_targets = []

        for target in self.targets:
            if target.hp > 0: # Check if target is alive
                target_grid_x = int(target.x // GRID_SIZE)
                target_grid_y = int(target.y // GRID_SIZE)
                grid_width = len(grid[0]) # Access grid dimensions
                grid_height = len(grid)


                is_reachable = True
                if 0 <= target_grid_x < grid_width and 0 <= target_grid_y < grid_height and grid[target_grid_y][target_grid_x][1] == 1:
                    is_reachable = False

                if is_reachable:
                    reachable_targets.append(target)
                else:
                    unreachable_targets.append(target)

        if reachable_targets:
            return min(reachable_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        elif unreachable_targets:
            return min(unreachable_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
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
    def __init__(self, unit_type, x, y, buildings, units, font=None, enhanced_data=None):
        targets = buildings + units
        super().__init__(unit_type, x, y, targets, font)
        self.enhanced_data = enhanced_data # Store enhanced data

        if enhanced_data and "size_multiplier" in enhanced_data:
            self.image = pygame.transform.scale(self.image, (int(self.rect.width * enhanced_data["size_multiplier"]), int(self.rect.height * enhanced_data["size_multiplier"])))
            self.rect = self.image.get_rect(topleft=(x, y)) # Update rect after scaling

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
