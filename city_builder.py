import pygame
import sys

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

from pygame.locals import * # Import pygame.locals for key constants

# Building class
class Building:
    def __init__(self, x, y, building_type):
        self.x = x
        self.y = y
        self.type = building_type
        self.size = (GRID_SIZE, GRID_SIZE)
        if building_type == "Castle":
            self.size = (GRID_SIZE * 2, GRID_SIZE * 2)  # Castle occupies 4 grids
        self.image = pygame.transform.scale(pygame.image.load(BUILDING_TYPES[building_type]), self.size)
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])


    def draw(self):
        screen.blit(self.image, (self.x, self.y))


# Function to draw the grid
def draw_grid():
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            rect = pygame.Rect(x, y, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BLACK, rect, 1)

# Resources
gold = 150
gold_increase_rate = 0.25

# Building costs
BUILDING_COSTS = {
    "Castle": 50,
    "House": 20,
    "Market": 30,
    "Barracks": 40,
    "Stable": 25,
}

# List to store buildings
buildings = []
current_building_type = "Castle"  # Start with Castle

font = pygame.font.Font(None, 20) # Font for displaying building info

game_messages = []  # Initialize game messages list
message_start_times = {}  # Keep track of when messages were added


selected_building = None  # Currently selected building

# Building cooldown
building_cooldown = 0
BUILDING_COOLDOWN_TIME = 1000  # 1 second cooldown

message_duration = 5000  # 3 seconds

# Main game loop
running = True
while running:
    dt = clock.tick(30)  # Delta time (time since last frame)
    gold += gold_increase_rate # Increase gold over time

    # Decrement building cooldown
    if building_cooldown > 0:
        building_cooldown -= dt
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:  # added to switch building type with keys 1,2,3,4,5
            if event.key == pygame.K_1:
                current_building_type = "Castle"
            elif event.key == pygame.K_2:
                current_building_type = "House"
            elif event.key == pygame.K_3:
                current_building_type = "Market"
            elif event.key == pygame.K_4:
                current_building_type = "Barracks"
            elif event.key == pygame.K_5:
                current_building_type = "Stable"


        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                grid_x = mouse_x // GRID_SIZE * GRID_SIZE
                grid_y = mouse_y // GRID_SIZE * GRID_SIZE
                new_building = Building(grid_x, grid_y, current_building_type)
                preview_rect = pygame.Rect(grid_x, grid_y, GRID_SIZE, GRID_SIZE)  # Preview rectangle

                # Check for collisions with existing buildings
                collision = False
                for building in buildings:
                    if building.rect.colliderect(new_building.rect):
                        collision = True
                        break

                castle_exists = any(building.type == "Castle" for building in buildings)
                if current_building_type == "Castle":
                    if castle_exists:
                        game_messages.append("Only one castle can be built.")
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                    elif not collision and gold >= BUILDING_COSTS[current_building_type] and building_cooldown <= 0:
                        buildings.append(new_building)
                        gold -= BUILDING_COSTS[current_building_type]
                        building_cooldown = BUILDING_COOLDOWN_TIME  # Reset cooldown
                        game_messages.append(f"Built {current_building_type} for {BUILDING_COSTS[current_building_type]} gold.")
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                    elif collision:
                        game_messages.append("Cannot build here.")  # Collision feedback
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                    elif gold < BUILDING_COSTS[current_building_type]:
                        game_messages.append(f"Not enough gold to build {current_building_type}.")  # Not enough gold feedback
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                else:
                    if not collision and gold >= BUILDING_COSTS[current_building_type] and building_cooldown <= 0:
                        buildings.append(new_building)
                        gold -= BUILDING_COSTS[current_building_type]
                        building_cooldown = BUILDING_COOLDOWN_TIME  # Reset cooldown
                        game_messages.append(f"Built {current_building_type} for {BUILDING_COSTS[current_building_type]} gold.")
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                    elif collision:
                        game_messages.append("Cannot build here.")  # Collision feedback
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time
                    elif gold < BUILDING_COSTS[current_building_type]:
                        game_messages.append(f"Not enough gold to build {current_building_type}.")  # Not enough gold feedback
                        message_start_times[game_messages[-1]] = pygame.time.get_ticks()  # Store message start time

        elif event.type == pygame.MOUSEBUTTONUP: # check for mouse release
            if event.button == 1: # left click
                mouse_pos = pygame.mouse.get_pos()
                selected_building = None # reset selected building
                for building in buildings:
                    if building.rect.collidepoint(mouse_pos):
                        selected_building = building
                        break

    screen.fill(WHITE)

    draw_grid()

    # Display gold
    gold_text = font.render(f"Gold: {int(gold)}", True, BLACK)
    screen.blit(gold_text, (10, 10))
    for building in buildings:
        building.draw()

    # Display game messages
    for i, message in enumerate(game_messages):
        message_text = font.render(message, True, RED)
        screen.blit(message_text, (10, 30 + i * 20))

    # Remove messages after a duration
    game_messages = [message for message in game_messages if pygame.time.get_ticks() - message_start_times[message] < message_duration]

    # Draw preview
    if building_cooldown <=0: # only show preview if not in cooldown
        if not collision and gold >= BUILDING_COSTS[current_building_type]:
            pygame.draw.rect(screen, GREEN, preview_rect, 2)  # Green if valid
        else:
            pygame.draw.rect(screen, RED, preview_rect, 2)  # Red if invalid

    if selected_building:
        info_text = font.render(f"{selected_building.type}", True, BLACK)
        screen.blit(info_text, (selected_building.x, selected_building.y - 20))

    pygame.display.flip()


pygame.quit()
sys.exit()
