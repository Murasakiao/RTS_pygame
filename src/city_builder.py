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
ENEMY_SPAWN_RATE = 2

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
    "Swordsman": {"image": "../characters/swordsman.png", "cost": {"gold": 50, "food": 30, "people": 1}, "hp": 10, "atk": 1},
    "Archer": {"image": "../characters/bowman.png", "cost": {"gold": 60, "food": 40, "people": 1}, "hp": 8, "atk": 2},
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
        self.speed = 75
        self.hp = UNIT_DATA[unit_type]["hp"]
        self.atk = UNIT_DATA[unit_type]["atk"]
        self.target = None

    def update(self, dt):
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

                if clicked_building and "unit" in BUILDING_DATA[clicked_building.type]:
                    unit_type = BUILDING_DATA[clicked_building.type]["unit"]
                    unit_cost = UNIT_DATA[unit_type]["cost"]
                    if all(resources.get(resource, gold) >= amount for resource, amount in unit_cost.items()):
                        new_unit = Unit(unit_type, clicked_building.x, clicked_building.y + GRID_SIZE)
                        units.append(new_unit)
                        for resource, amount in unit_cost.items():
                            if resource == "gold":
                                gold -= amount
                            else:
                                resources[resource] -= amount
                        add_game_message(f"Trained {unit_type}", game_messages)
                    else:
                        add_game_message(f"Not enough resources to train {unit_type}", game_messages)

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
        unit.update(dt)

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
    draw_grid(screen)

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

    pygame.display.flip()

pygame.quit()
sys.exit()
