# Tutorial: Developing "Kingdom Conquer" - An RTS in Pygame

## Phase 1: The Foundation - Initialization & Building Mechanics
In this first stage, the goal is to establish the core engine loop and allow the player to interact with the world by placing structures.

### 1.1 Setting Up the Pygame Environment
- **Game Window & Constants**: Defining `SCREEN_WIDTH`, `SCREEN_HEIGHT`, and `GRID_SIZE`.
- **The Main Loop**: Implementing the standard `while running` loop with event handling for quitting and frame rate capping (FPS).
- **Coordinate Systems**: Understanding the difference between pixel coordinates and the underlying grid logic.

### 1.2 Resource Management & Data Structures
- **Global State**: Tracking gold, wood, and stone.
- **Building Dictionaries**: Using a central dictionary to store HP, image paths, and resource costs for different building types.

### 1.3 Placing Buildings
- **Mouse Input**: Converting `pygame.mouse.get_pos()` into grid-aligned coordinates.
- **Collision Checking**: Ensuring a building cannot be placed on top of an existing one.
- **Rendering**: Drawing surfaces/images onto the screen based on the building list.

#### Phase 1: Constants (Basic Setup)
```python
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
GRID_SIZE = 40
FPS = 60
WHITE, BLACK, GREEN = (255, 255, 255), (0, 0, 0), (0, 255, 0)

BUILDING_DATA = {
    "Castle": {"hp": 500, "color": GREEN, "cost": 100},
    "House": {"hp": 100, "color": (150, 75, 0), "cost": 20}
}
```

#### Phase 1: Utils (Placement Logic)
```python
def check_collision(rect, buildings):
    return any(rect.colliderect(b.rect) for b in buildings)

def get_grid_pos(mouse_pos):
    x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    return x, y
```

#### Phase 1: RTS (Main Loop)
```python
import pygame
# ... imports ...
while running:
    screen.fill(WHITE)
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            gx, gy = get_grid_pos(mouse_pos)
            new_rect = pygame.Rect(gx, gy, GRID_SIZE, GRID_SIZE)
            if not check_collision(new_rect, buildings):
                buildings.append(Building(gx, gy, "Castle"))
    
    for b in buildings: b.draw(screen)
    pygame.display.flip()
```

---

## Phase 2: Biological Warfare - Units, Combat, & Simple AI
Once we have a static world, we introduce mobile entities that can interact with each other.

### 2.1 The Unit Class
- **Inheritance**: Creating a base `GameObject` class that both Buildings and Units share.
- **Unit Properties**: Adding speed, attack damage, and health points.

### 2.2 Movement and Spawning
- **Unit Production**: Linking building types (like Barracks) to unit creation logic.
- **Linear Interpolation (Lerp)**: Moving units in a straight line toward a target by calculating the vector between start and end.
- **Enemy Waves**: Implementing a timer-based system that spawns enemies at the screen boundaries.

### 2.3 Combat Logic
- **Target Selection**: Units scanning for the nearest enemy or building.
- **Attack Cooldowns**: Using delta time (`dt`) to prevent units from attacking every single frame.
- **State Management**: Removing objects from the game lists when their HP hits zero.

#### Phase 2: Constants (Combat & Units)
```python
ALLY_DATA = {"Swordsman": {"speed": 50, "hp": 50, "atk": 5, "range": 20}}
ENEMY_DATA = {"Orc": {"speed": 30, "hp": 40, "atk": 3, "range": 15}}
```

#### Phase 2: Utils (Enemy Spawning)
```python
def spawn_enemy(side):
    if side == "left": return 0, random.randint(0, SCREEN_HEIGHT)
    # ... logic for other sides ...
```

#### Phase 2: RTS (Simple AI Movement)
```python
# Inside Unit.update()
def move_simple(self, target, dt):
    dx = target.x - self.x
    dy = target.y - self.y
    distance = math.hypot(dx, dy)
    
    if distance > self.range:
        self.x += (dx / distance) * self.speed * (dt / 1000)
        self.y += (dy / distance) * self.speed * (dt / 1000)
        self.rect.topleft = (self.x, self.y)
    else:
        self.attack(target)
```

---

## Phase 3: Advanced Systems - Procedural Generation & A* Pathfinding
The final stage transforms the game from a flat plane into a complex, navigable environment.

### 3.1 Procedural Terrain Generation
- **Perlin Noise**: Using the `noise` library to generate smooth, natural-looking heightmaps.
- **Tile Mapping**: Assigning noise value thresholds to specific tile types (e.g., values < -0.1 are water).
- **Impassable Terrain**: Integrating the terrain map into the game's collision logic so units cannot walk on water.

### 3.2 A* Pathfinding Algorithm
- **Grid Representation**: Creating a graph of "Nodes" where each node is either passable or a wall.
- **The Heuristic**: Using Manhattan or Euclidean distance to guide the search toward the goal efficiently.
- **Path Integration**: Replacing Phase 2's simple linear movement with a "path-following" behavior where units move node-by-node.

### 3.3 Optimization & Debugging
- **Debug Overlays**: Drawing the calculated paths and grid lines to visualize AI decision-making.
- **Performance**: Managing the A* calls so they don't lag the game loop when many units are moving simultaneously.

#### Phase 3: Constants (Final)
```python
# Full resource rates and thresholds
WAVE_INTERVAL = 30000 # 30 seconds
WATER_THRESHOLD = -0.1
```

#### Phase 3: Utils (Grid Updating)
```python
def update_grid(terrain, buildings):
    grid = []
    for y, row in enumerate(terrain):
        grid_row = []
        for x, tile in enumerate(row):
            is_obstacle = 1 if tile == "water" else 0
            # Overwrite with buildings
            for b in buildings:
                if b.rect.collidepoint(x * GRID_SIZE, y * GRID_SIZE):
                    is_obstacle = 1
            grid_row.append(is_obstacle)
        grid.append(grid_row)
    return grid
```

#### Phase 3: RTS (A* Integration)
```python
# Triggering pathfinding on Right Click
if event.button == 3 and selected_unit:
    start = (selected_unit.x // GRID_SIZE, selected_unit.y // GRID_SIZE)
    end = (mouse_pos[0] // GRID_SIZE, mouse_pos[1] // GRID_SIZE)
    selected_unit.path = a_star(current_grid, start, end)
```

---

## Suggested Enhancements for Readers
- **Fog of War**: Hiding enemies until allied units are within a certain radius.
- **Unit Formations**: Grouping units together so they move as a squad rather than overlapping.
- **Sound Effects**: Adding feedback for building placement and sword swings.
