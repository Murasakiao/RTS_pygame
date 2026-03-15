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

#### Phase 1 Code Snippet
```python
# Simple grid-based building placement
if event.type == MOUSEBUTTONDOWN and event.button == 1:
    grid_x = (mouse_pos[0] // GRID_SIZE) * GRID_SIZE
    grid_y = (mouse_pos[1] // GRID_SIZE) * GRID_SIZE
    if not any(b.rect.collidepoint(mouse_pos) for b in buildings):
        new_building = Building(grid_x, grid_y, current_building_type)
        buildings.append(new_building)
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

#### Phase 2 Code Snippet
```python
# Linear movement toward a target
def move_simple(self, dt):
    if self.target:
        dx, dy = self.target.x - self.x, self.target.y - self.y
        dist = math.hypot(dx, dy)
        if dist > self.range:
            self.x += (dx / dist) * self.speed * (dt / 1000)
            self.y += (dy / dist) * self.speed * (dt / 1000)
            self.rect.topleft = (self.x, self.y)
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

#### Phase 3 Code Snippet
```python
# A* Pathfinding Integration
def update_path(self, grid, end_pos):
    start = (int(self.x // GRID_SIZE), int(self.y // GRID_SIZE))
    end = (int(end_pos[0] // GRID_SIZE), int(end_pos[1] // GRID_SIZE))
    self.path = a_star(grid, start, end)

# Procedural Noise
noise_val = noise.pnoise2(x / scale, y / scale, octaves=4)
terrain_type = "water" if noise_val < -0.1 else "grass"
```

---

## Suggested Enhancements for Readers
- **Fog of War**: Hiding enemies until allied units are within a certain radius.
- **Unit Formations**: Grouping units together so they move as a squad rather than overlapping.
- **Sound Effects**: Adding feedback for building placement and sword swings.
