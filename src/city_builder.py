import pygame
import sys
from pygame.locals import *

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25  # Smaller grid size

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("City Builder")

# Clock to control the frame rate
clock = pygame.time.Clock()

# Building types
BUILDING_TYPES = {
    "Castle": "buildings/castle.png",
    "House": "buildings/house.png",
    "Market": "buildings/market.png",
    "Barracks": "buildings/barracks.png",
    "Stable": "buildings/stable.png",
    "Farm": "buildings/farm.png",
    "LumberMill": "buildings/lumber.png",
    "Quarry": "buildings/quarry.png",
}

# Building costs
BUILDING_COSTS = {
    "Farm": 25,
    "LumberMill": 40,
    "Quarry": 50,
    "Castle": 75,
    "House": 20,
    "Market": 30,
    "Barracks": 40,
    "Stable": 25,
}

# Unit types that can be trained in certain buildings
UNIT_TYPES = {
    "Barracks": "Swordsman",
    "Stable": "Knight",
}

# Unit data (images, costs, etc.)
UNITS = {
    "Swordsman": {
        "image": "characters/swordsman.png",
        "cost": {"gold": 25, "food": 10, "people": 1},
    },
    "Knight": {
        "image": "characters/bowman.png",
        "cost": {"gold": 40, "food": 20, "people": 1},
    },
}

# Resource requirements
BUILDING_RESOURCES = {
    "Castle": {"gold": 75, "wood": 50, "stone": 100},
    "House": {"gold": 20, "wood": 15},
    "Market": {"gold": 30, "wood": 20, "stone": 25},
    "Barracks": {"gold": 40, "wood": 20, "stone": 15},
    "Stable": {"gold": 35, "wood": 20, "stone": 15},
    "Farm": {"gold": 25, "wood": 10},
    "LumberMill": {"gold": 40, "wood": 20, "stone": 20},
    "Quarry": {"gold": 20, "wood": 15, "stone": 10},
}

class Building:
    def __init__(self, x, y, building_type):
        if building_type is None:
            raise ValueError("Building type cannot be None")
        self.x = x
        self.y = y
        self.type = building_type
        self.size = (GRID_SIZE, GRID_SIZE)
        if building_type == "Castle":
            self.size = (GRID_SIZE * 2, GRID_SIZE * 2)  # Castle occupies 4 grids
        try:
            self.image = pygame.transform.scale(pygame.image.load(BUILDING_TYPES[building_type]), self.size)
        except pygame.error:
            # Fallback if image loading fails
            self.image = pygame.Surface(self.size)
            self.image.fill(BLACK)
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])

    def draw(self):
        if self.image and self.rect:
            screen.blit(self.image, (self.x, self.y))

class Unit:
    def __init__(self, unit_type, x, y):
        self.type = unit_type
        self.x = x
        self.y = y
        try:
            self.image = pygame.transform.scale(pygame.image.load(UNITS[unit_type]["image"]), (GRID_SIZE, GRID_SIZE))
        except pygame.error as e:
            print(f"Error loading image for {unit_type}: {e}")
            self.image = pygame.Surface((GRID_SIZE, GRID_SIZE))
            self.image.fill(RED)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.moving = False
        self.destination = None
        self.speed = 100  # pixels per second

    def update(self, dt):
        if self.moving and self.destination:
            dx = self.destination[0] - self.x
            dy = self.destination[1] - self.y
            
            # Prioritize horizontal movement
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.x += self.speed * (dt / 1000)
                else:
                    self.x -= self.speed * (dt / 1000)
            # Prioritize vertical movement
            elif abs(dy) > abs(dx):
                if dy > 0:
                    self.y += self.speed * (dt / 1000)
                else:
                    self.y -= self.speed * (dt / 1000)
            
            # Check if we've reached the destination
            if abs(dx) < self.speed * (dt / 1000) and abs(dy) < self.speed * (dt / 1000):
                self.x = self.destination[0]
                self.y = self.destination[1]
                self.moving = False
                self.destination = None
            
            self.rect.topleft = (self.x, self.y)

    def draw(self):
        screen.blit(self.image, self.rect)

def draw_grid(color=BLACK, line_width=1):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, color, rect, line_width)

def add_game_message(message, messages, start_times):
    messages.append(message)
    start_times[message] = pygame.time.get_ticks()
    return messages, start_times

def update_preview_rect(mouse_pos, current_building_type):
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size = GRID_SIZE * 2 if current_building_type == "Castle" else GRID_SIZE
    return pygame.Rect(grid_x, grid_y, size, size)

def draw_grass_tile(screen):
    # Load the grass tile image
    grass_tile = pygame.image.load('buildings/tile_1.png')

    # Scale the grass tile to the size of the GRID_SIZE
    scaled_grass_tile = pygame.transform.scale(grass_tile, (GRID_SIZE, GRID_SIZE))

    # Draw the grass tile onto the screen
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            screen.blit(scaled_grass_tile, (x, y))

def draw_resources(screen, font, resources, gold):
    resource_text = f"Gold: {int(gold)}"
    for resource, amount in resources.items():
        resource_text += f", {resource.capitalize()}: {int(amount)}"
    gold_text = font.render(resource_text, True, BLACK)
    screen.blit(gold_text, (10, 10))

def draw_buildings(screen, buildings):
    for building in buildings:
        building.draw()

def draw_units(screen, units, selected_unit):
    for unit in units:
        unit.draw()
        if unit == selected_unit:
            pygame.draw.rect(screen, GREEN, unit.rect, 2)

def draw_building_preview(screen, preview_rect, collision, resources, current_building_type):
    color = GREEN if not collision and all(resources.get(resource, gold) >= BUILDING_RESOURCES.get(current_building_type, {}).get(resource, 0) for resource in BUILDING_RESOURCES.get(current_building_type, {})) else RED
    pygame.draw.rect(screen, color, preview_rect, 2)

def draw_messages(screen, font, game_messages, message_start_times, message_duration):
    current_time = pygame.time.get_ticks()
    game_messages = [msg for msg in game_messages 
                    if current_time - message_start_times[msg] < message_duration]
    
    for i, message in enumerate(game_messages):
        message_text = font.render(message, True, RED)
        screen.blit(message_text, (10, 30 + i * 20))

def draw_key_bindings(screen, font, building_map, screen_width, screen_height, GRID_SIZE, BUILDING_RESOURCES):
    text_lines = []
    x = screen_width - 10
    y = 10

    for key, building_type in building_map.items():
        text_line = f"{pygame.key.name(key)}: {building_type}"
        requirements = BUILDING_RESOURCES.get(building_type, {})
        if requirements:
            text_line += f" ({', '.join(f'{resource}: {amount}' for resource, amount in requirements.items())})"
        text_lines.append(text_line)

    text_surfaces = [font.render(line, True, RED) for line in text_lines]

    for i, surface in enumerate(text_surfaces):
        screen.blit(surface, (x - 10 * GRID_SIZE, y + i * 20))

def check_collision(preview_rect, buildings):
    for building in buildings:
        if building.rect.colliderect(preview_rect):
            return True
    return False

# Initialize game state
gold = 150
resources = {"wood": 100, "stone": 100, "food": 100, "people": 3}
resource_increase_rates = {
    "gold": 5,
    "wood": 2,
    "stone": 1,
    "food": 3,
    "people": 0.05,
}
buildings = []
units = []
current_building_type = "Castle"
font = pygame.font.Font(None, 20)
game_messages = []
message_start_times = {}
selected_building = None
selected_unit = None  # Track selected unit
building_cooldown = 0
BUILDING_COOLDOWN_TIME = 1000  # 1 second cooldown
message_duration = 5000  # 5 seconds

# Building hotkeys
building_map = {
    K_1: "Castle",
    K_2: "House",
    K_3: "Market",
    K_4: "Barracks",
    K_5: "Stable",
    K_6: "Farm",
    K_7: "LumberMill",
    K_8: "Quarry",
}

# Main game loop
running = True
preview_rect = None

while running:
    dt = clock.tick(30)
    mouse_pos = pygame.mouse.get_pos()

    # Calculate resource increases based on building counts
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

    if building_cooldown > 0:
        building_cooldown -= dt

    # Update preview rect if no unit is selected
    if not selected_unit:
        preview_rect = update_preview_rect(mouse_pos, current_building_type)
        collision = check_collision(preview_rect, buildings) if preview_rect else False

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key in building_map:
                current_building_type = building_map[event.key]
                selected_unit = None  # Deselect unit when switching to building mode
            if event.key == pygame.K_ESCAPE:
                current_building_type = None

        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                # First, check if we're clicking on a unit
                clicked_unit = None
                for unit in units:
                    if unit.rect.collidepoint(mouse_pos):
                        clicked_unit = unit
                        break

                if clicked_unit:
                    selected_unit = clicked_unit
                    game_messages, message_start_times = add_game_message(
                        f"Selected {clicked_unit.type}",
                        game_messages,
                        message_start_times
                    )
                    continue  # Skip building placement if we clicked a unit

                # If no unit was clicked, handle building placement
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                
                # Check if we clicked on a building that can train units
                clicked_building = None
                for building in buildings:
                    if building.rect.collidepoint(mouse_pos):
                        clicked_building = building
                        break

                if clicked_building and clicked_building.type in UNIT_TYPES:
                    unit_type = UNIT_TYPES[clicked_building.type]
                    unit_cost = UNITS[unit_type]["cost"]
                    
                    if all(resources.get(resource, gold) >= amount for resource, amount in unit_cost.items()):
                        # Create new unit
                        new_unit = Unit(unit_type, clicked_building.x, clicked_building.y + GRID_SIZE)
                        units.append(new_unit)
                        
                        # Deduct resources
                        for resource, amount in unit_cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                                
                        game_messages, message_start_times = add_game_message(
                            f"Trained {unit_type}",
                            game_messages,
                            message_start_times
                        )
                    else:
                        game_messages, message_start_times = add_game_message(
                            f"Not enough resources to train {unit_type}",
                            game_messages,
                            message_start_times
                        )
                else:
                    # Handle building placement
                    castle_exists = any(building.type == "Castle" for building in buildings)
                    cost = BUILDING_RESOURCES.get(current_building_type, {})
                    affordable = all(resources.get(resource, gold) >= amount for resource, amount in cost.items())

                    if current_building_type == "Castle" and castle_exists:
                        game_messages, message_start_times = add_game_message(
                            "Only one castle can be built.",
                            game_messages,
                            message_start_times
                        )
                    elif not collision and affordable and building_cooldown <= 0:
                        if current_building_type is not None:
                            new_building = Building(grid_x, grid_y, current_building_type)
                        buildings.append(new_building)
                        for resource, amount in cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                        building_cooldown = BUILDING_COOLDOWN_TIME
                        game_messages, message_start_times = add_game_message(
                            f"Built {current_building_type}",
                            game_messages,
                            message_start_times
                        )

            elif event.button == 3 and selected_unit:  # Right click to move selected unit
                grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
                grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
                selected_unit.destination = (grid_x, grid_y)
                selected_unit.moving = True
                game_messages, message_start_times = add_game_message(
                    f"Moving {selected_unit.type} to new position",
                    game_messages,
                    message_start_times
                )

    # Update all units
    for unit in units:
        unit.update(dt)

    # Draw game state
    screen.fill(WHITE)
    # Draw the grass tile
    draw_grass_tile(screen)
    draw_grid()

    draw_resources(screen, font, resources, gold)
    draw_buildings(screen, buildings)
    draw_units(screen, units, selected_unit)
    draw_building_preview(screen, preview_rect, collision, resources, current_building_type)
    draw_messages(screen, font, game_messages, message_start_times, message_duration)
    draw_key_bindings(screen, font, building_map, SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, BUILDING_RESOURCES)

    pygame.display.flip()

pygame.quit()
sys.exit()