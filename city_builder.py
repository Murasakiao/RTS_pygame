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
}

# Building costs
BUILDING_COSTS = {
    "Castle": 50,
    "House": 20,
    "Market": 30,
    "Barracks": 40,
    "Stable": 25,
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

# Initialize game state
gold = 150
gold_increase_rate = 0.25
buildings = []
current_building_type = "Castle"
font = pygame.font.Font(None, 20)
game_messages = []
message_start_times = {}
selected_building = None
building_cooldown = 0
BUILDING_COOLDOWN_TIME = 1000  # 1 second cooldown
message_duration = 5000  # 5 seconds

# Main game loop
running = True
preview_rect = pygame.Rect(0, 0, 0, 0)  # Initialize as an empty Rect
while running:
    dt = clock.tick(30)  # Delta time (time since last frame)
    gold += gold_increase_rate * (dt / 1000)  # Adjust gold increase based on time

    # Decrement building cooldown
    if building_cooldown > 0:
        building_cooldown -= dt

    # Handle events
    mouse_pos = pygame.mouse.get_pos()
    preview_rect = update_preview_rect(mouse_pos, current_building_type)
    
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
        elif event.type == KEYDOWN:
            if event.key in [K_1, K_2, K_3, K_4, K_5]:
                building_map = {
                    K_1: "Castle",
                    K_2: "House",
                    K_3: "Market",
                    K_4: "Barracks",
                    K_5: "Stable"
                }
                current_building_type = building_map.get(event.key, current_building_type)

        elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # Left click
            grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
            grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
            
            new_building = Building(grid_x, grid_y, current_building_type)
            
            # Check for collisions
            collision = any(building.rect.colliderect(new_building.rect) for building in buildings)
            castle_exists = any(building.type == "Castle" for building in buildings)

            # Building placement logic
            if current_building_type == "Castle" and castle_exists:
                game_messages, message_start_times = add_game_message(
                    "Only one castle can be built.", game_messages, message_start_times)
            elif not collision and gold >= BUILDING_COSTS[current_building_type] and building_cooldown <= 0:
                buildings.append(new_building)
                gold -= BUILDING_COSTS[current_building_type]
                building_cooldown = BUILDING_COOLDOWN_TIME
                game_messages, message_start_times = add_game_message(
                    f"Built {current_building_type} for {BUILDING_COSTS[current_building_type]} gold.",
                    game_messages, message_start_times)
            elif collision:
                game_messages, message_start_times = add_game_message(
                    "Cannot build here.", game_messages, message_start_times)
            elif gold < BUILDING_COSTS[current_building_type]:
                game_messages, message_start_times = add_game_message(
                    f"Not enough gold to build {current_building_type}.",
                    game_messages, message_start_times)

        elif event.type == MOUSEBUTTONUP and event.button == 1:
            selected_building = next(
                (building for building in buildings if building.rect.collidepoint(mouse_pos)),
                None
            )

    # Draw game state
    screen.fill(WHITE)
    draw_grid()

    # Draw UI elements
    gold_text = font.render(f"Gold: {int(gold)}", True, BLACK)
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
    if building_cooldown <= 0 and preview_rect:
        color = GREEN if not collision and gold >= BUILDING_COSTS[current_building_type] else RED
        pygame.draw.rect(screen, color, preview_rect, 2)

    # Draw selected building info
    if selected_building:
        info_text = font.render(f"{selected_building.type}", True, BLACK)
        screen.blit(info_text, (selected_building.x, selected_building.y - 20))

    pygame.display.flip()

pygame.quit()
sys.exit()
