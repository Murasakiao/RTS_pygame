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

		Next is to setup the game window and constants. Be sure to store it in a python script file (ending with a .py) you can name it however you want. I'll gonna name it rts.py. 
		
```
import pygame

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30

# Initialize Pygame

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	
```

- **The Main Loop**: Implementing the standard `while running` loop with event handling for quitting and frame rate capping (FPS).

		Now, let us implement the game loop and initialize pygame properly. Try to read it line by line to help you understand the code. This is very easy to understand. After that, you can now run the entire code to show the actual game window. A pygame window will popup titled "RTS Game Tutorial" at the top of the window with a green screen. If you get the same, congrats! you have properly setup a basic pygame window. This would be the foundation of our next steps. 

```
import pygame

SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RTS Game Tutorial")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 20)  

# Game loop
running = True
while running:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False  
	
	# Fill with green screen
	screen.fill((0, 255, 0)) # This is color value for (Red, Green, Blue)
  

	# Update the display
	pygame.display.flip()
	clock.tick(FPS)

# Quit Pygame
pygame.quit()
	
```

- **Coordinate Systems**: Understanding the difference between pixel coordinates and the underlying grid logic.

  
### 1.2 Resource Management & Data Structures

- **Global State**: Tracking gold, wood, and stone.

- **Building Dictionaries**: Using a central dictionary to store HP, image paths, and resource costs for different building types.


### 1.3 Placing Buildings

- **Mouse Input**: Converting `pygame.mouse.get_pos()` into grid-aligned coordinates.

- **Collision Checking**: Ensuring a building cannot be placed on top of an existing one.

- **Rendering**: Drawing surfaces/images onto the screen based on the building list.
