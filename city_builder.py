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
    "LumberMill": "buildings/lumber.png",  # Renamed for clarity
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
        "cost": {"gold": 25, "food": 10},
    },
    "Knight": {
        "image": "characters/knight.png",
        "cost": {"gold": 40, "food": 20},
    },
}

# Resource requirements
BUILDING_RESOURCES = {
    "Castle": {"gold": 75, "wood": 50, "stone": 100},
    "House": {"gold": 20, "wood": 15},
    "Market": {"gold": 30, "wood": 20, "stone": 25},
    "Barracks": {"gold": 40, "wood": 30, "stone": 40},
    "Stable": {"gold": 25, "wood": 20, "wood": 10},  # Corrected duplicate key
    "Farm": {"gold": 25, "wood": 10},
    "LumberMill": {"gold": 40, "wood": 20, "stone": 20},
    "Quarry": {"gold": 50, "wood": 25, "stone": 30},
}

class Building:
    def __init__(self, x, y, building_type):
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

def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

def add_game_message(message, messages, start_times):
    messages.append(message)
    start_times[message] = pygame.time.get_ticks()
    return messages, start_times

def update_preview_rect(mouse_pos, current_building_type):
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size = GRID_SIZE * 2 if current_building_type == "Castle" else GRID_SIZE
    return pygame.Rect(grid_x, grid_y, size, size)

def check_collision(preview_rect, buildings):
    for building in buildings:
        if building.rect.colliderect(preview_rect):
            return True
    return False

# Initialize game state
gold = 150
resources = {"wood": 100, "stone": 100, "food": 0}
resource_increase_rates = {
    "gold": 5,
    "wood": 2,
    "stone": 1,
    "food": 3,
}
buildings = []
current_building_type = "Castle"
font = pygame.font.Font(None, 20)
game_messages = []
message_start_times = {}
selected_building = None
building_cooldown = 0
BUILDING_COOLDOWN_TIME = 1000  # 1 second cooldown
message_duration = 5000  # 5 seconds
units = []  # List to store created units

# Define building map outside the loop using pygame key constants
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
    dt = clock.tick(30)  # Delta time (time since last frame)

    # Calculate resource increases based on building counts
    building_counts = {}
    for building in buildings:
        building_counts[building.type] = building_counts.get(building.type, 0) + 1

    resource_multipliers = {
        "gold": 1 + (building_counts.get("Market", 0) * 0.1),  # Each market increases gold rate by 10%
        "wood": 1 + (building_counts.get("LumberMill", 0) * 0.15),  # Each lumber mill increases wood rate by 15%
        "stone": 1 + (building_counts.get("Quarry", 0) * 0.12),  # Each quarry increases stone rate by 12%
        "food": 1 + (building_counts.get("Farm", 0) * 0.2),  # Each farm increases food rate by 20%
    }

    for resource, rate in resource_increase_rates.items():
        multiplier = resource_multipliers.get(resource, 1)
        increase = rate * multiplier * (dt / 1000)  # Correctly apply delta time
        if resource == "gold":
            gold += increase
        else:
            resources[resource] += increase


    # Decrement building cooldown
    if building_cooldown > 0:
        building_cooldown -= dt

    # Handle events
    mouse_pos = pygame.mouse.get_pos()
    preview_rect = update_preview_rect(mouse_pos, current_building_type)
    collision = check_collision(preview_rect, buildings) if preview_rect else False

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key in building_map:
                current_building_type = building_map[event.key]  # Directly access the value

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
            grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
            
            new_building = Building(grid_x, grid_y, current_building_type)
            castle_exists = any(building.type == "Castle" for building in buildings)

            cost = BUILDING_RESOURCES.get(current_building_type) or BUILDING_COSTS.get(current_building_type)
            affordable = all(resources.get(resource, gold) >= cost.get(resource, cost) for resource in cost)

            # Building placement logic
            if current_building_type == "Castle" and castle_exists:
                game_messages, message_start_times = add_game_message(
                    "Only one castle can be built.", game_messages, message_start_times)
            elif not collision and affordable and building_cooldown <= 0:
                buildings.append(new_building)
                for resource, amount in cost.items():
                    if resource == "gold":
                        gold -= amount
                    else:
                        resources[resource] -= amount
                building_cooldown = BUILDING_COOLDOWN_TIME
                game_messages, message_start_times = add_game_message(
                    f"Built {current_building_type} for {cost}.",
                    game_messages, message_start_times)
            elif collision:
                game_messages, message_start_times = add_game_message(
                    "Cannot build here.", game_messages, message_start_times)
            elif not affordable:
                game_messages, message_start_times = add_game_message(
                    f"Not enough resources to build {current_building_type}.",
                    game_messages, message_start_times)

        elif event.type == MOUSEBUTTONUP and event.button == 1:
            if selected_building and selected_building.type in UNIT_TYPES and building_cooldown <=0:
                unit_type = UNIT_TYPES[selected_building.type]
                unit_cost = UNITS[unit_type]["cost"]
                affordable = all(resources.get(resource, gold) >= unit_cost.get(resource, unit_cost) for resource in unit_cost)

                if affordable:
                    units.append({"type": unit_type, "x": selected_building.x, "y": selected_building.y})
                    for resource, amount in unit_cost.items():
                        if resource == "gold":
                            gold -= amount
                        else:
                            resources[resource] -= amount
                    building_cooldown = BUILDING_COOLDOWN_TIME
                    game_messages, message_start_times = add_game_message(
                        f"Trained {unit_type} for {unit_cost}.",
                        game_messages, message_start_times)

                else:
                    game_messages, message_start_times = add_game_message(
                        f"Not enough resources to train {unit_type}.",
                        game_messages, message_start_times)

            selected_building = next(
                (building for building in buildings if building.rect.collidepoint(mouse_pos)),
                None
            )

    # Draw game state
    screen.fill(WHITE)
    draw_grid()

    # Draw UI elements
    resource_text = f"Gold: {int(gold)}"

    for resource, amount in resources.items():
        resource_text += f", {resource.capitalize()}: {int(amount)}"


    gold_text = font.render(resource_text, True, BLACK)
    screen.blit(gold_text, (10, 10))

    # Draw buildings
    for building in buildings:
        building.draw()

    # Draw messages
    current_time = pygame.time.get_ticks()
    game_messages = [msg for msg in game_messages 
                    if current_time - message_start_times[msg] < message_duration]
    
    for i, message in enumerate(game_messages):
        message_text = font.render(message, True, RED)
        screen.blit(message_text, (10, 30 + i * 20))

    # Draw preview
    if building_cooldown <= 0 and preview_rect and gold >= BUILDING_COSTS[current_building_type]:
        color = GREEN if not collision and all(resources.get(resource, gold) >= BUILDING_RESOURCES.get(current_building_type, BUILDING_COSTS.get(current_building_type)).get(resource, gold or 0) for resource in BUILDING_RESOURCES.get(current_building_type, BUILDING_COSTS.get(current_building_type))) else RED
        pygame.draw.rect(screen, color, preview_rect, 2)

    # Draw selected building info
    if selected_building:
        info_text = font.render(f"{selected_building.type}", True, BLACK)
        screen.blit(info_text, (selected_building.x, selected_building.y - 20))


    for unit in units:
        unit_type = unit["type"]
        try:
            image = pygame.transform.scale(pygame.image.load(UNITS[unit_type]["image"]), (GRID_SIZE, GRID_SIZE))
            screen.blit(image, (unit["x"], unit["y"]))
        except pygame.error as e:
            print(f"Error loading image for {unit_type}: {e}")


    pygame.display.flip()

pygame.quit()
sys.exit()
