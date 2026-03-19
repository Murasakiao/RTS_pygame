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

  

- **Mouse Input**: Converting `pygame.mouse.get_pos()` into grid-aligned coordinates.

  

- **Collision Checking**: Ensuring a building cannot be placed on top of an existing one.

  

- **Rendering**: Drawing surfaces/images onto the screen based on the building list.