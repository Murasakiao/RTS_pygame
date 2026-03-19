In this tutorial, i am gonna walk you through on how to make a working real time strategy game in python using a game library called pygame. At the end of this walkthrough you'll have an understanding of how an rts game is made. From setting the world/game environment, game loop, art assets, building units logic, resources logic, enemy and allied units to procedural map generation using a simple noise algorithm and a pathfinding A star (A*) algorthm that units use to navigate the map.

This tutorial is divided into 3 phases, first phase is for the game initialization and building mechanics--this is the core setup for the game. second phase is the Logic for the units, combat and simple AI. Third phase is the procedural generation and A* pathfinding in order to add uniqueness of life to the game.

## Phase 1: The Foundation - Initialization & Building Mechanics

  

In this first stage, the goal is to establish the core engine loop and allow the player to interact with the world by placing structures.

  

### 1.1 Setting Up the Pygame Environment

  

The very first thing i would recommend in any of your python projects is to setup a virtual environment, create a new folder or directory then run this commands:

```

python -m venv venv

source venv/bin/activate

```

  

This would setup an evnironment for libraries you would use specifically for that projects. This would also help not to mix different versions of libraries for your projects. You can now install the libraries we'll gonna use for this tutorial (in this case pygame). Install pygame (assuming you already have pip installed otherwise pip is very easy to install).

```

pip install pygame

```

  

- **Game Window & Constants**: Defining `SCREEN_WIDTH`, `SCREEN_HEIGHT`, and `GRID_SIZE`.

  

Next is to setup the game window and constants. To keep things clean, we'll store our settings in `src/constants.py` and our main logic in `src/rts.py`. This separation makes the project much easier to manage as it grows.

  

```python
# src/constants.py
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
```

  

- **The Main Loop**: Implementing the standard `while game_running` loop with event handling for quitting and frame rate capping (FPS).

  

Now, let us implement the game loop and initialize pygame properly in `src/rts.py`. This loop is the heart of our game, handling events, updates, and drawing. After running this, a window will popup titled "Kingdom Conquer".

  

```python

# src/rts.py
import pygame
import sys
from constants import *

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kingdom Conquer")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)
  

# Game loop
game_running = True
while game_running:
dt = clock.tick(FPS) # Get time delta to ensure smooth logic
for event in pygame.event.get():
if event.type == pygame.QUIT:
game_running = False

# Clear screen with white
screen.fill(WHITE)

# Update the display
pygame.display.flip()

pygame.quit()
sys.exit()
```

  

- **Coordinate Systems**: Understanding the difference between pixel coordinates and the underlying grid logic.

  

In an RTS, we don't just place things anywhere; we want them to snap to a grid. This makes collision detection and pathfinding much easier. We define a `GRID_SIZE` (like 16 pixels) and calculate our grid width and height by dividing the screen dimensions. 

  

```python
# src/constants.py
grid_width = SCREEN_WIDTH // GRID_SIZE
grid_height = SCREEN_HEIGHT // GRID_SIZE

# Initialize a 2D array to represent our map
grid = [[(0, 0) for _ in range(grid_width)] for _ in range(grid_height)]

```

  

### 1.2 Resource Management & Data Structures

Every good RTS needs an economy! We need to track various resources that the player will collect and spend.

- **Global State**: Tracking gold, wood, and stone.

We'll initialize our starting resources and define the base rates at which they increase over time. In our loop, we'll calculate the increase based on `dt` (milliseconds since last frame) to keep growth consistent.

```python
# src/rts.py initialization
gold = 150
resources = {"wood": 200, "stone": 200, "food": 200, "people": 3}
resource_increase_rates = {"gold": 1.5, "wood": 0.5, "stone": 0.5, "food": 0.25, "people": 0.1}

```

  
- **Building Dictionaries**: Using a central dictionary to store HP, image paths, and resource costs for different building types.


Instead of hardcoding every building, we use `BUILDING_DATA` in `src/constants.py`. This acts as a database for our construction logic. Note the `size_multiplier` for larger structures!


```python
# src/constants.py
BUILDING_DATA = {
"Castle": {
"hp": 275,
"image": "assets/buildings/castle.png",
"resources": {"gold": 75, "wood": 50, "stone": 100},
"size_multiplier": 2
},

"House": {
"hp": 20,
"image": "assets/buildings/house.png",
"resources": {"gold": 20, "wood": 15}
},

"Market": {
"hp": 30,
"image": "assets/buildings/market.png",
"resources": {"gold": 30, "wood": 20, "stone": 25}
},
}
```


### 1.3 Placing Buildings

	Now for the exciting part: interaction! We need to allow the player to select a building type and place it on the map. This involves snapping the mouse to our grid and validating the location.

- **Mouse Input**: Converting `pygame.mouse.get_pos()` into grid-aligned coordinates.

		To make the game feel like a classic RTS, buildings should "snap" to the grid. We achieve this by taking the raw pixel position of the mouse and rounding it down to the nearest multiple of `GRID_SIZE`. We've wrapped this logic into a helper in `src/utils.py`.

```python
# src/utils.py
def update_preview_rect(mouse_pos, current_building_type):
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size_multiplier = BUILDING_DATA.get(current_building_type, {}).get("size_multiplier", 1)
    size = GRID_SIZE * size_multiplier
    return pygame.Rect(grid_x, grid_y, size, size)
```

- **Collision Checking**: Ensuring a building cannot be placed on top of an existing one.

		We can't have buildings overlapping. Before placing, we check the `preview_rect` against the rectangles of all existing `buildings` and `units`.

```python
# src/utils.py
def check_collision(preview_rect, buildings, units):
    for building in buildings:
        if preview_rect.colliderect(building.rect):
            return True
    for unit in units:
        if preview_rect.colliderect(unit.rect):
            return True
    return False
```

- **Rendering**: Drawing surfaces/images onto the screen based on the building list.

		In our main loop in `src/rts.py`, we iterate through the `buildings` list and call their `draw` method. We also draw a "ghost" preview of the building following the mouse cursor to show where it *would* be placed.

```python
# src/rts.py (Inside the drawing section)
for building in buildings:
    building.draw(screen)

# Draw the preview (Green if valid, Red if blocked)
if preview_rect:
    color = GREEN if not collision and affordable else RED
    pygame.draw.rect(screen, color, preview_rect, 2)
```

### Complete Code for Phase 1

To wrap up Phase 1, here are the complete files you need to run the game and start placing buildings. Make sure these are in a folder named `src/`.

**src/constants.py**
```python
# src/constants.py
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30
BUILDING_COOLDOWN_TIME = 1000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

BUILDING_DATA = {
    "Castle": {
        "hp": 275, 
        "image": "assets/buildings/castle.png", 
        "resources": {"gold": 75, "wood": 50, "stone": 100}, 
        "size_multiplier": 2
    },
    "House": {
        "hp": 20, 
        "image": "assets/buildings/house.png", 
        "resources": {"gold": 20, "wood": 15}
    },
    "Market": {
        "hp": 30, 
        "image": "assets/buildings/market.png", 
        "resources": {"gold": 30, "wood": 20, "stone": 25}
    }
}
```

**src/entities.py**

		This script manages the "living" objects in our game. We use a base `GameObject` class to handle basic image loading and drawing, and a `Building` class that inherits from it to store specific structure data like HP. We also define `Unit`, `AlliedUnit`, and `EnemyUnit` to handle AI and combat.

```python
# src/entities.py
import math
import pygame
from constants import *
from utils import *
from astar import a_star, Node

class GameObject:
    def __init__(self, x, y, image_path, size=(GRID_SIZE, GRID_SIZE)):
        self.x = x
        self.y = y
        try:
            self.image = pygame.transform.scale(pygame.image.load(image_path), size)
        except:
            self.image = pygame.Surface(size)
            self.image.fill(BLACK)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hp = 0

    def draw(self, screen):
        screen.blit(self.image, self.rect)

class Building(GameObject):
    def __init__(self, x, y, building_type):
        data = BUILDING_DATA[building_type]
        size_multiplier = data.get("size_multiplier", 1)
        size = (GRID_SIZE * size_multiplier, GRID_SIZE * size_multiplier)
        super().__init__(x, y, data["image"], size)
        self.type = building_type
        self.hp = data["hp"]
```

**src/utils.py**
```python
# src/utils.py
import pygame
from constants import *

def update_preview_rect(mouse_pos, current_building_type):
    if not current_building_type: return None
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    size_multiplier = BUILDING_DATA.get(current_building_type, {}).get("size_multiplier", 1)
    size = GRID_SIZE * size_multiplier
    return pygame.Rect(grid_x, grid_y, size, size)

def check_collision(preview_rect, buildings, units):
    for building in buildings:
        if preview_rect.colliderect(building.rect):
            return True
    for unit in units:
        if preview_rect.colliderect(unit.rect):
            return True
    return False

def draw_resources(screen, font, resources, gold):
    resource_text = f"Gold: {int(gold)}"
    for resource, amount in resources.items():
        resource_text += f", {resource.capitalize()}: {int(amount)}"
    text_surface = font.render(resource_text, True, BLACK)
    screen.blit(text_surface, (10, 10))

def add_game_message(message, game_messages):
    game_messages.append({"text": message, "start_time": pygame.time.get_ticks(), "duration": 3000})
```

**src/rts.py**
```python
# src/rts.py
import pygame
import sys
from constants import *
from entities import *
from utils import update_preview_rect, check_collision, draw_resources

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Kingdom Conquer")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)

# State
gold = 150
resources = {"wood": 200, "stone": 200, "food": 200, "people": 3}
resource_increase_rates = {"gold": 1.5, "wood": 0.5, "stone": 0.5, "food": 0.25, "people": 0.1}
buildings = []
units = []
current_building_type = "House"
building_cooldown = 0

game_running = True
while game_running:
    dt = clock.tick(FPS)
    mouse_pos = pygame.mouse.get_pos()
    
    # Update Resources
    gold += resource_increase_rates["gold"] * (dt / 1000)
    for res, rate in resource_increase_rates.items():
        if res != "gold": resources[res] += rate * (dt / 1000)

    # Building Logic
    preview_rect = update_preview_rect(mouse_pos, current_building_type)
    collision = check_collision(preview_rect, buildings, units) if preview_rect else False
    
    cost = BUILDING_DATA[current_building_type]["resources"] if current_building_type else {}
    affordable = all(resources.get(r, gold if r == "gold" else 0) >= a for r, a in cost.items())

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if current_building_type and not collision and affordable:
                new_b = Building(preview_rect.x, preview_rect.y, current_building_type)
                buildings.append(new_b)
                for r, a in cost.items():
                    if r == "gold": gold -= a
                    else: resources[r] -= a

    # Draw
    screen.fill(WHITE)
    for b in buildings: b.draw(screen)
    if preview_rect:
        color = GREEN if not collision and affordable else RED
        pygame.draw.rect(screen, color, preview_rect, 2)
    
    draw_resources(screen, font, resources, gold)
    pygame.display.flip()

pygame.quit()
sys.exit()
```
