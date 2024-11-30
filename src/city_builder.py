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
ENEMY_SPAWN_RATE = 1
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
# Building data
BUILDING_DATA = {
    "Castle": {"hp": 2750, "image": "../buildings/castle.png", "cost": 75, "resources": {"gold": 75, "wood": 50, "stone": 100}, "size_multiplier": 2},
    "House": {"hp": 2000, "image": "../buildings/house.png", "cost": 20, "resources": {"gold": 20, "wood": 15}},
    "Market": {"hp": 2300, "image": "../buildings/market.png", "cost": 30, "resources": {"gold": 30, "wood": 20, "stone": 25}},
    "Barracks": {"hp": 2400, "image": "../buildings/barracks.png", "cost": 40, "resources": {"gold": 40, "wood": 20, "stone": 15}, "unit": "Swordsman"},
    "Stable": {"hp": 2250, "image": "../buildings/stable.png", "cost": 25, "resources": {"gold": 35, "wood": 20, "stone": 15}, "unit": "Archer"},
    "Farm": {"hp": 2500, "image": "../buildings/farm.png", "cost": 25, "resources": {"gold": 25, "wood": 10}},
    "LumberMill": {"hp": 2000, "image": "../buildings/lumber.png", "cost": 40, "resources": {"gold": 40, "wood": 30, "stone": 10}},
    "Quarry": {"hp": 2500, "image": "../buildings/quarry.png", "cost": 50, "resources": {"gold": 20, "wood": 30, "stone": 10}},
}

# Unit data
UNIT_DATA = {
    "Swordsman": {"image": "../characters/swordsman.png", "cost": {"gold": 50, "food": 30, "people": 1}, "speed": 40, "hp": 10, "atk": 1},
    "Archer": {"image": "../characters/bowman.png", "cost": {"gold": 60, "food": 40, "people": 1}, "speed": 50, "hp": 8, "atk": 2},
}

# Enemy data
ENEMY_DATA = {
    "Goblin": {"image": "../characters/goblin.png", "speed": 20, "hp": 8, "atk": 1},
    "Orc": {"image": "../characters/orc.png", "speed": 10, "hp": 12, "atk": 2},
}

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

class Building(GameObject):
    def __init__(self, x, y, building_type):
        self.type = building_type
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(x, y, data["image"], size)
        self.hp = data["hp"]

class Unit(GameObject):
    def __init__(self, unit_type, x, y):
        super().__init__(x, y, UNIT_DATA[unit_type]["image"])
        self.type = unit_type
        self.moving = False
        self.destination = None
        self.speed = UNIT_DATA[unit_type]["speed"]
        self.hp = UNIT_DATA[unit_type]["hp"]
        self.atk = UNIT_DATA[unit_type]["atk"]
        self.target = None
        self.attack_cooldown = 0

    def update(self, dt, game_messages):
        enhanced_unit_movement(self, dt, navigation_grid, game_messages)

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
            self.target = self.find_nearest_target(enemies)
        elif self.target.hp <=0: # Find a new target if current target is dead
            self.target = self.find_nearest_target(enemies)

        for unit in units:
            unit.update(dt, game_messages, units, enemies, buildings)

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
            target_text = font.render(self.target.type, True, RED)
            screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, self.rect.top - target_text.get_height() - 5))

class Enemy(GameObject):
    def __init__(self, unit_type, x, y, initial_target):
        super().__init__(x, y, ENEMY_DATA[unit_type]["image"])
        self.type = unit_type
        self.target = initial_target
        self.speed = ENEMY_DATA[unit_type]["speed"]
        self.hp = ENEMY_DATA[unit_type]["hp"]
        self.atk = ENEMY_DATA[unit_type]["atk"]

    def update(self, dt, game_messages=None):
        if self.target and self.target.hp <= 0:
            self.target = self.find_nearest_target(buildings + units)  # Find new target

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

    def attack_target(self, game_messages=None):
        if self.target:
            self.target.hp -= self.atk
            message = f"Enemy {self.type} attacked {self.target.type}"

            if self.target.hp <= 0:
                message = f"Enemy {self.type} destroyed {self.target.type}"
                self.target = self.find_nearest_target(buildings + units)

            if game_messages is not None:  # Only add message if list is provided
                add_game_message(message, game_messages)

        return game_messages

    def find_nearest_target(self, targets):
        valid_targets = [target for target in targets if target.hp > 0]
        if valid_targets:
            return min(valid_targets, key=lambda target: math.hypot(target.x - self.x, target.y - self.y))
        return None

    def draw(self, screen):
        super().draw(screen)
        if self.target:
            target_text = font.render(self.target.type, True, RED)
            screen.blit(target_text, (self.rect.centerx - target_text.get_width() // 2, self.rect.top - target_text.get_height() - 5))

class TerrainGenerator:
    def __init__(self, screen_width, screen_height, grid_size):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_size = grid_size
        self.grass_tiles = self.load_grass_tiles()
        self.scale = 100.0
        self.octaves = 12
        self.persistence = 0.01
        self.lacunarity = 2.0

    def load_grass_tiles(self):
        grass_tiles = []
        for i in range(1, 7):
            try:
                tile = pygame.image.load(f'../buildings/tile_{i}.png')
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
                noise_value = noise.pnoise2(x / self.scale, y / self.scale,
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

class NavigationGrid:
    def __init__(self, screen_width, screen_height, grid_size):
        self.width = screen_width
        self.height = screen_height
        self.grid_size = grid_size
        self.grid = self.create_navigation_grid()

    def create_navigation_grid(self):
        """
        Create a grid representing navigable areas.
        0 = impassable, 1 = passable
        """
        grid = [[1 for _ in range(self.width // self.grid_size)] 
                for _ in range(self.height // self.grid_size)]
        return grid

    def update_grid_from_buildings(self, buildings):
        """
        Mark areas occupied by buildings as impassable
        """
        for building in buildings:
            grid_x = int(building.x // self.grid_size)
            grid_y = int(building.y // self.grid_size)
            size_multiplier = max(1, int(building.rect.width / self.grid_size))
            
            for dx in range(size_multiplier):
                for dy in range(size_multiplier):
                    try:
                        self.grid[grid_y + dy][grid_x + dx] = 0
                    except IndexError:
                        pass

    def is_passable(self, x, y):
        """
        Check if a specific grid cell is passable
        """
        grid_x = int(x // self.grid_size)
        grid_y = int(y // self.grid_size)
        
        # Boundary check
        if (grid_x < 0 or grid_x >= len(self.grid[0]) or 
            grid_y < 0 or grid_y >= len(self.grid)):
            return False
        
        return self.grid[grid_y][grid_x] == 1

    def find_path(self, start, end, max_iterations=100, avoid_objects=None):
        """
        Enhanced pathfinding with object avoidance
        """
        def heuristic(a, b):
            return math.hypot(b[0] - a[0], b[1] - a[1])

        def get_neighbors(node):
            neighbors = [
                (node[0]+self.grid_size, node[1]),
                (node[0]-self.grid_size, node[1]),
                (node[0], node[1]+self.grid_size),
                (node[0], node[1]-self.grid_size),
                # Optional: Add diagonal movement
                (node[0]+self.grid_size, node[1]+self.grid_size),
                (node[0]-self.grid_size, node[1]-self.grid_size),
                (node[0]+self.grid_size, node[1]-self.grid_size),
                (node[0]-self.grid_size, node[1]+self.grid_size)
            ]
            
            # Filter neighbors based on passability and object avoidance
            valid_neighbors = []
            for n in neighbors:
                is_passable = self.is_passable(n[0], n[1])
                
                # Additional check for object avoidance
                if avoid_objects:
                    temp_obj = type('TempObject', (), {
                        'x': n[0], 
                        'y': n[1], 
                        'rect': pygame.Rect(n[0], n[1], self.grid_size, self.grid_size)
                    })
                    
                    object_collision = any(
                        check_object_collision(temp_obj, obj) 
                        for obj in avoid_objects
                    )
                    
                    is_passable = is_passable and not object_collision
                
                if is_passable:
                    valid_neighbors.append(n)
            
            return valid_neighbors

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

def draw_building_preview(screen, preview_rect, collision, resources, current_building_type):
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

def check_collision(preview_rect, buildings):
    return any(building.rect.colliderect(preview_rect) for building in buildings)

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
    castle = next((building for building in buildings if building.type == "Castle"), None)
    initial_target = castle or (buildings[0] if buildings else (units[0] if units else None))

    if not initial_target:
        return []

    spawned_enemies = []
    for _ in range(current_wave * enemy_spawn_rate):
        spawn_x, spawn_y = generate_spawn_point()
        enemy_type = random.choice(list(ENEMY_DATA.keys()))
        enemy = Enemy(enemy_type, spawn_x, spawn_y, initial_target)
        spawned_enemies.append(enemy)
    print(spawned_enemies)
    return spawned_enemies

def draw_debug_info(screen, font, debug_info, x=10, y=40):
    for i, line in enumerate(debug_info):
        text_surface = font.render(line, True, BLACK)
        screen.blit(text_surface, (x, y + i * 20))

def enhanced_unit_movement(self, dt, navigation_grid, game_messages, units, enemies, buildings):
    """
    Enhanced movement method for Unit class with advanced collision avoidance
    """
    if self.moving and self.destination:
        # Calculate next position
        dx = self.destination[0] - self.x
        dy = self.destination[1] - self.y
        distance = math.hypot(dx, dy)

        if distance > 0:
            travel_distance = self.speed * (dt / 1000)
            next_x = self.x + (dx / distance) * travel_distance
            next_y = self.y + (dy / distance) * travel_distance

            # Check for collisions with other units, enemies, and buildings
            all_objects = units + enemies + buildings
            collision_detected = any(
                check_object_collision(self, other) 
                for other in all_objects 
                if other != self
            )

            # Check if next position is passable and no collision
            if navigation_grid.is_passable(next_x, next_y) and not collision_detected:
                self.x = next_x
                self.y = next_y
                self.rect.topleft = (self.x, self.y)

                # Check if close enough to destination
                if math.hypot(dx, dy) <= travel_distance:
                    self.moving = False
                    self.destination = None
            else:
                # Find an alternative path with collision avoidance
                path = navigation_grid.find_path(
                    (self.x, self.y), 
                    self.destination,
                    max_iterations=200,
                    avoid_objects=all_objects
                )
                
                if path and len(path) > 1:
                    # Set next waypoint as destination
                    self.destination = path[1]
                else:
                    # Cannot find path, stop moving
                    self.moving = False
                    add_game_message("Cannot find safe path", game_messages)

def check_object_collision(obj1, obj2, buffer=GRID_SIZE/2):
    """
    Advanced collision detection with configurable buffer
    Checks if two objects are too close to each other
    """
    # If obj2 is a list, check collision with each item in the list
    if isinstance(obj2, list):
        return any(check_object_collision(obj1, item, buffer) for item in obj2)
    
    # Existing collision check logic
    obj1_rect = pygame.Rect(
        obj1.x - buffer, 
        obj1.y - buffer, 
        obj1.rect.width + 2*buffer, 
        obj1.rect.height + 2*buffer
    )
    
    obj2_rect = pygame.Rect(
        obj2.x - buffer, 
        obj2.y - buffer, 
        obj2.rect.width + 2*buffer, 
        obj2.rect.height + 2*buffer
    )
    
    return obj1_rect.colliderect(obj2_rect)

def find_valid_placement(buildings, units, x, y, building_type=None, unit_type=None, max_search_radius=GRID_SIZE*3):
    """
    Find a valid placement location near the original coordinates with extended search
    
    Args:
    - buildings: List of existing buildings
    - units: List of existing units
    - x, y: Original placement coordinates
    - building_type: Type of building being placed (optional)
    - unit_type: Type of unit being spawned (optional)
    - max_search_radius: Maximum distance to search for a valid placement
    
    Returns:
    - Tuple of (x, y) coordinates for valid placement, or None if no valid location
    """
    all_objects = buildings + units
    
    # Generate a spiral search pattern
    def spiral_search():
        for radius in range(0, max_search_radius // GRID_SIZE + 1):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    # Skip center point if radius is 0
                    if radius == 0 and dx == 0 and dy == 0:
                        continue
                    
                    # Only continue if we're on the "edge" of the current radius
                    if abs(dx) == radius or abs(dy) == radius:
                        new_x = x + dx * GRID_SIZE
                        new_y = y + dy * GRID_SIZE
                        
                        # Ensure placement is within screen bounds
                        if (new_x < 0 or new_x >= SCREEN_WIDTH or 
                            new_y < 0 or new_y >= SCREEN_HEIGHT):
                            continue
                        
                        # Create a temporary object to check collision
                        size = (GRID_SIZE, GRID_SIZE)
                        temp_object = type('TempObject', (), {
                            'x': new_x, 
                            'y': new_y, 
                            'rect': pygame.Rect(new_x, new_y, size[0], size[1])
                        })
                        
                        # If no collision, yield this location
                        if not check_object_collision(temp_object, all_objects):
                            yield (new_x, new_y)
    
    # Convert generator to list and return first valid placement
    valid_placements = list(spiral_search())
    
    # Print debug information if no placements found
    if not valid_placements:
        print(f"DEBUG: No valid placement found near ({x}, {y})")
        print(f"Existing objects: {len(buildings)} buildings, {len(units)} units")
        
        # Additional debug: print locations of existing objects
        for obj in all_objects:
            print(f"Existing object at ({obj.x}, {obj.y})")
    
    # Return first valid placement or None
    return valid_placements[0] if valid_placements else None

def modify_unit_spawning(buildings, units, clicked_building):
    """
    Modify unit spawning to prevent collisions
    
    Returns:
    - Tuple (new_unit, message)
    """
    unit_type = BUILDING_DATA[clicked_building.type]["unit"]
    unit_cost = UNIT_DATA[unit_type]["cost"]
    
    # Check resource affordability
    if not all(resources.get(resource, gold) >= amount for resource, amount in unit_cost.items()):
        return None, f"Not enough resources to train {unit_type}"
    
    # Try multiple placement locations around the building
    placement_attempts = [
        (clicked_building.x, clicked_building.y + GRID_SIZE),  # Default placement
        (clicked_building.x + GRID_SIZE, clicked_building.y),
        (clicked_building.x - GRID_SIZE, clicked_building.y),
        (clicked_building.x, clicked_building.y - GRID_SIZE)
    ]
    
    for x, y in placement_attempts:
        placement = find_valid_placement(
            buildings, 
            units, 
            x, 
            y, 
            unit_type=unit_type
        )
        
        if placement:
            new_unit = Unit(unit_type, placement[0], placement[1])
            return new_unit, None
    
    # If all placement attempts fail
    return None, f"Cannot spawn {unit_type}. Area is too crowded."

def modify_building_placement(buildings, units, current_building_type, grid_x, grid_y):
    """
    Modify building placement to prevent collisions
    
    Returns:
    - Tuple (valid_placement, message)
    """
    # Check for castle uniqueness
    if current_building_type == "Castle" and any(building.type == "Castle" for building in buildings):
        return None, "Only one castle can be built."
    
    cost = BUILDING_DATA[current_building_type].get("resources", {})
    affordable = all(resources.get(resource, gold) >= amount for resource, amount in cost.items())
    
    if not affordable:
        return None, f"Not enough resources to build {current_building_type}"
    
    # Find valid placement
    placement = find_valid_placement(buildings, units, grid_x, grid_y, building_type=current_building_type)
    
    if placement is None:
        return None, "No valid placement found. Area is too crowded."
    
    return placement, None

def modify_unit_spawning(buildings, units, clicked_building):
    """
    Modify unit spawning to prevent collisions
    
    Returns:
    - Tuple (new_unit, message)
    """
    unit_type = BUILDING_DATA[clicked_building.type]["unit"]
    unit_cost = UNIT_DATA[unit_type]["cost"]
    
    # Check resource affordability
    if not all(resources.get(resource, gold) >= amount for resource, amount in unit_cost.items()):
        return None, f"Not enough resources to train {unit_type}"
    
    # Find valid placement near the building
    placement = find_valid_placement(
        buildings, 
        units, 
        clicked_building.x, 
        clicked_building.y + GRID_SIZE, 
        unit_type=unit_type
    )
    
    if placement is None:
        return None, "Cannot spawn unit. Area is too crowded."
    
    new_unit = Unit(unit_type, placement[0], placement[1])
    
    return new_unit, None

# --- Game Initialization ---
gold = 150
resources = {"wood": 100, "stone": 100, "food": 100, "people": 3}
resource_increase_rates = {
    "gold": 3, "wood": 2, "stone": 1, "food": 1, "people": 0.05
}

buildings = []
units = []
enemies = []
game_messages = [] # Initialize game_messages list

current_building_type = "Castle"
building_cooldown = 0
selected_unit = None

terrain_generator = TerrainGenerator(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)
terrain = terrain_generator.generate_terrain()

navigation_grid = NavigationGrid(SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE)
navigation_grid.update_grid_from_buildings(buildings)

wave_timer = 0
current_wave = 1

building_map = {
    K_1: "Castle", K_2: "House", K_3: "Market", K_4: "Barracks",
    K_5: "Stable", K_6: "Farm", K_7: "LumberMill", K_8: "Quarry",
}

# --- Game Loop ---
game_messages = []
running = True
show_debug = True
while running:
    dt = clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    debug_info = [
        f"FPS: {int(clock.get_fps())}",
        f"Buildings: {len(buildings)}",
        f"Units: {len(units)}",
        f"Enemies: {len(enemies)}",
        f"Mouse Position: {mouse_pos}",
        f"Selected Unit: {selected_unit.type if selected_unit else 'None'}",
        f"Current Wave: {current_wave}",
        # f"Gold: {int(gold)}",
        # f"Resources: {int(resources['gold'])}, {int(resources['wood'])}, {int(resources['stone'])}, {int(resources['food'])}, {int(resources['people'])}",
        # Add more debug variables as needed
    ]

    # --- Resource Management ---
    building_counts = {}
    for building in buildings:
        building_counts[building.type] = building_counts.get(building.type, 0) + 1

    resource_multipliers = {
        "gold": 1 + (building_counts.get("Market", 0) * 0.1) + (building_counts.get("Castle", 0) * 0.2),
        "wood": 1 + (building_counts.get("LumberMill", 0) * 0.15) + (building_counts.get("Castle", 0) * 0.1),
        "stone": 1 + (building_counts.get("Quarry", 0) * 0.12) + (building_counts.get("Castle", 0) * 0.15),
        "food": 1 + (building_counts.get("Farm", 0) * 0.2) + (building_counts.get("Castle", 0) * 0.1),
        "people": 1 + (building_counts.get("House", 0) * 0.0005) + (building_counts.get("Castle", 0) * 0.001),
    }

    for resource, rate in resource_increase_rates.items():
        multiplier = resource_multipliers.get(resource, 1)
        increase = rate * multiplier * (dt / 1000)
        if resource == "gold":
            gold += increase
        else:
            resources[resource] += increase

    # --- Building Cooldown ---
    building_cooldown = max(0, building_cooldown - dt)

    # --- Preview Rect ---
    if not selected_unit:
        preview_rect = update_preview_rect(mouse_pos, current_building_type)
        collision = check_collision(preview_rect, buildings) if preview_rect else False
    else:
        preview_rect = None  # No preview while unit is selected
        collision = False

    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key in building_map:
                current_building_type = building_map[event.key]
                selected_unit = None  # Deselect unit when switching building
            elif event.key == pygame.K_ESCAPE:
                current_building_type = None
            elif event.key == K_t:
                terrain = terrain_generator.generate_terrain()
            elif event.key == K_d:  # 'D' key to toggle debug info display
                show_debug = not show_debug
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                # Unit Selection
                clicked_unit = None
                for unit in units:
                    if unit.rect.collidepoint(mouse_pos):
                        clicked_unit = unit
                        break

                if clicked_unit:
                    selected_unit = clicked_unit
                    add_game_message(f"Selected {clicked_unit.type}", game_messages)
                    continue  # Skip building placement

                # Building Placement / Unit Training
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE

                clicked_building = next((building for building in buildings if building.rect.collidepoint(mouse_pos)), None)

                # Building Placement
                if current_building_type and not collision and building_cooldown <= 0:
                    placement, message = modify_building_placement(
                        buildings, units, current_building_type, grid_x, grid_y
                    )
                    
                    if placement:
                        new_building = Building(placement[0], placement[1], current_building_type)
                        buildings.append(new_building)
                        
                        # Deduct resources
                        cost = BUILDING_DATA[current_building_type].get("resources", {})
                        for resource, amount in cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                        
                        building_cooldown = BUILDING_COOLDOWN_TIME
                        add_game_message(f"Built {current_building_type}", game_messages)
                    elif message:
                        add_game_message(message, game_messages)

                if clicked_building and "unit" in BUILDING_DATA[clicked_building.type]:
                    new_unit, message = modify_unit_spawning(buildings, units, clicked_building)
                    
                    if new_unit:
                        units.append(new_unit)
                        
                        # Deduct resources
                        unit_cost = UNIT_DATA[new_unit.type]["cost"]
                        for resource, amount in unit_cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                        
                        add_game_message(f"Trained {new_unit.type}", game_messages)
                    elif message:
                        add_game_message(message, game_messages)

                elif current_building_type and not collision and building_cooldown <= 0:
                    castle_exists = any(building.type == "Castle" for building in buildings)
                    if current_building_type == "Castle" and castle_exists:
                        add_game_message("Only one castle can be built.", game_messages)
                    else:
                        cost = BUILDING_DATA[current_building_type].get("resources", {})
                        affordable = all(resources.get(resource, gold) >= amount for resource, amount in cost.items())
                        if affordable:
                            new_building = Building(grid_x, grid_y, current_building_type)
                            buildings.append(new_building)
                            for resource, amount in cost.items():
                                if resource == "gold":
                                    gold -= amount
                                else:
                                    resources[resource] -= amount
                            building_cooldown = BUILDING_COOLDOWN_TIME
                            add_game_message(f"Built {current_building_type}", game_messages)
                        else:
                            add_game_message(f"Not enough resources to build {current_building_type}", game_messages)

            elif event.button == 3 and selected_unit:  # Move selected unit
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                selected_unit.destination = (grid_x, grid_y)
                selected_unit.moving = True

                # Find nearest target for the selected unit
                selected_unit.target = selected_unit.find_nearest_target(enemies)

                add_game_message(f"Moving {selected_unit.type}", game_messages)

    # --- Game Updates ---
    for unit in units:
        unit.update(dt, game_messages)

    for enemy in enemies:
        game_messages = enemy.update(dt, game_messages)  # Pass game_messages to enemy update

    if wave_timer >= WAVE_INTERVAL:
        new_enemies = spawn_enemies(buildings, units, current_wave, ENEMY_SPAWN_RATE)
        enemies.extend(new_enemies)
        wave_timer = 0
        current_wave += 1
    else:
        wave_timer += dt

    enemies[:] = [enemy for enemy in enemies if enemy.hp > 0]  # Remove dead enemies
    units[:] = [unit for unit in units if unit.hp > 0] # Remove dead units

    # --- Drawing ---
    screen.fill(WHITE)
    terrain_generator.draw_terrain(screen, terrain)

    draw_resources(screen, font, resources, gold)

    for building in buildings:
        building.draw(screen)

    for unit in units:
        unit.draw(screen)
        if unit == selected_unit:
            pygame.draw.rect(screen, GREEN, unit.rect, 2)

    for enemy in enemies:
        enemy.draw(screen)

    draw_building_preview(screen, preview_rect, collision, resources, current_building_type)
    draw_messages(screen, font, game_messages)
    draw_key_bindings(screen, font, building_map, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BUILDING_DATA)

    print(wave_timer, current_wave)
    # Draw debug information if enabled
    if show_debug:
        draw_debug_info(screen, font, debug_info)
        draw_grid(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()
