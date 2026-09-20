# Kingdom Conquer: a developer's guide to the current prototype

**Project:** `rts-pygame`<br>
**Review date:** 2026-09-15<br>
**Lifecycle:** dormant, with a working prototype and unresolved gameplay bugs<br>
**Audience:** Python beginners through developers learning game architecture and algorithms

You can place buildings, spend resources, train soldiers, and send them across a tile map while enemies arrive in waves.

To understand the code, follow one soldier: a click requests a destination, A* looks for a route, movement updates the position, and Pygame draws the next frame. Each system handles one part of that action.

This guide describes the code in this checkout. Sections marked **Suggested change** or **Learning example** describe work you could do next; they do not describe implemented features. This documentation review did not change the game code.

## Contents

1. [Current status](#1-current-status)
2. [Set up Python and run the game](#2-set-up-python-and-run-the-game)
3. [Learn the Pygame building blocks](#3-learn-the-pygame-building-blocks)
4. [Find your way around the source](#4-find-your-way-around-the-source)
5. [Define the game environment](#5-define-the-game-environment)
6. [Load and use art assets](#6-load-and-use-art-assets)
7. [Generate terrain with Perlin noise](#7-generate-terrain-with-perlin-noise)
8. [Understand the game loop and controls](#8-understand-the-game-loop-and-controls)
9. [Build the economy and construction rules](#9-build-the-economy-and-construction-rules)
10. [Define units, combat, and enemy waves](#10-define-units-combat-and-enemy-waves)
11. [Find routes with A*](#11-find-routes-with-a)
12. [Turn paths into movement](#12-turn-paths-into-movement)
13. [Draw the interface and debug the simulation](#13-draw-the-interface-and-debug-the-simulation)
14. [Known issues and a repair order](#14-known-issues-and-a-repair-order)
15. [Validate changes](#15-validate-changes)
16. [Extend the prototype in small steps](#16-extend-the-prototype-in-small-steps)
17. [Glossary and further reading](#17-glossary-and-further-reading)

## 1. Current status

The window title is **Kingdom Conquer**. The project contains about 1,200 lines of Python across eight source files, plus 23 PNG assets. It has pinned runtime and development dependency manifests, but no committed automated test source, save system, or packaging configuration.

| System | Current implementation | Limits you should know |
|---|---|---|
| Startup | Title screen, Start New Game, Exit | No restart flow; imports depend on the script launch method |
| World | One 768 × 576 pixel map, 16-pixel tiles | No camera, scrolling, zoom, or larger off-screen world |
| Terrain | Perlin-noise grass and water | No separate river algorithm; `T` does not produce a new visible map |
| Construction | Eight building types, resource costs, placement preview | Incomplete footprint, water, and boundary validation |
| Economy | Passive income with building multipliers | No workers, resource deposits, storage limits, or population cap |
| Units | Swordsman and Archer, single-unit selection and movement | No group selection, formations, or training queue |
| Enemies | Goblin and Orc, border spawns, increasing waves | Spawns can land in water; target-priority bugs |
| Combat | Range checks, HP reduction, attack cooldowns | No projectiles, line of sight, armor, or reliable building assaults |
| Navigation | Eight-direction A* and waypoint following | Corner cutting, imperfect route quality, obstacle-bypassing fallback |
| Interface | Resource text, messages, HP labels, debug paths/grid | Overlapping text and clipped building-cost labels |
| Game outcome | Play until you close the window | No victory, defeat, pause, sound, multiplayer, or persistence |

### Review evidence

The existing local environment ran **Python 3.12.13, Pygame 2.6.1, and the `noise` distribution 1.2.2** on macOS. Its dependency check passed. All seven Python files parsed, and Pygame loaded all 23 PNG files.

A headless smoke test exercised the menu, building a Barracks, training and selecting a Swordsman, right-click movement, enemy-wave spawning, the `T` and `D` keys, and closing the game. The test used synthetic mouse/keyboard events and 1-second simulation ticks. A later P0 smoke test confirmed that importing `src.rts` does not initialize Pygame and that the module entry point can start and close a match. The terrain and pathfinding issues described below remain.

These checks confirm those code paths in this environment. They do not establish Windows/Linux installation compatibility, normal-frame-rate gameplay quality, or performance with a large army. No test suite was added to the repository during this review.

## 2. Set up Python and run the game

### 2.1 Install the tools

You need:

- **Python 3.12:** the interpreter that runs the `.py` files. This is the reviewed version family; the project does not declare a supported-version range.
- **Git:** to clone the repository, unless you download and extract a ZIP.
- **A text editor:** VS Code, PyCharm, or another editor with Python support.
- **A desktop session:** for the game window. A server without a display needs the headless testing setup in [Section 15](#15-validate-changes).

Install Python from [python.org](https://www.python.org/downloads/) or your operating system's package manager. On Windows, enable the installer option to add Python to your path. On macOS with Homebrew, `brew install python@3.12` is another option.

### 2.2 Get the project

```sh
git clone https://github.com/Murasakiao/RTS_pygame.git rts-pygame
cd rts-pygame
```

If you already have this checkout, open a terminal in its root directory instead. You should see `src/`, `assets/`, `README.md`, and `STATUS.md`.

### 2.3 Create a virtual environment

Treat a virtual environment as this project's toolbox. It holds the packages this game uses, while another project can keep different versions. You can then upgrade a package for another app without changing this game's environment.

**macOS / Linux:**

```sh
python3.12 --version
python3.12 -m venv venv
source venv/bin/activate
```

**Windows PowerShell:**

```powershell
py -3.12 --version
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

Use your Python 3.12 executable if it has a different name. The directory name `venv` matches this project's `.gitignore`.

Activation tells your terminal to use the environment's Python; it does not install packages or move your source files. `python -m pip` runs pip through that interpreter, helping you avoid installing into the wrong Python. Confirm the interpreter:

```sh
python -c "import sys; print(sys.executable)"
```

Expect a path inside this project's `venv` directory. Select that interpreter in your editor as well.

PowerShell may block activation scripts. You can use the environment without changing execution policy:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe src/rts.py
```

A virtual environment contains machine-specific paths. Do not copy one from another computer. If an old environment no longer runs after a move or Python upgrade, create a fresh environment rather than editing its internal paths.

### 2.4 Install runtime or development dependencies

With the environment active, install the runtime dependencies:

```sh
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip check
```

- **Pygame** supplies the window, image loading, drawing, input, fonts, and clock.
- **`noise`** supplies `pnoise2()`, the Perlin-noise function for terrain.
- `math`, `random`, `heapq`, `sys`, and `os` belong to Python's standard library. Do not install separate packages for them.

Install the development file when you need the test runner:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest --version
```

`requirements-dev.txt` includes `requirements.txt`, so this command also installs the runtime packages. The repository does not yet contain committed test source; `pytest==9.1.1` ran a temporary A* smoke test in the reviewed environment.

The manifests pin the direct package versions verified on **macOS 26.6.2 arm64 with Python 3.12.13**. Other operating systems and Python versions are not verified by this project. The files do not claim cross-platform compatibility.

Check the installed distribution versions:

```sh
python -c "from importlib.metadata import version; print('pygame', version('pygame')); print('noise', version('noise'))"
```

Use package metadata for the `noise` version. In the reviewed environment, `noise.__version__` reported `1.2.1` even though the installed distribution was `1.2.2`.

### 2.5 Launch from the repository root

```sh
python -m src.rts
```

Expect the **KINGDOM CONQUER** menu with a castle image and Start New Game / Exit buttons.

Keep the working directory at the repository root. The code loads images using paths such as `assets/buildings/castle.png`; those paths depend on your working directory.

The source uses package-relative imports, so `python src/rts.py` is not supported. [Section 4](#4-find-your-way-around-the-source) explains the package arrangement.

Close the window to stop playing. Run `deactivate` in the terminal when you finish using the environment.

### 2.6 Common setup problems

| Symptom | Check or action |
|---|---|
| `No module named 'pygame'` or `'noise'` | Check `sys.executable`; install with that interpreter's `-m pip` |
| `No module named 'src'` | Run `python -m src.rts` from the repository root, not from inside `src/` |
| Missing `assets/...` file | Launch from the root and confirm that the asset files exist |
| `noise` fails to build | It includes native code. If pip cannot find a compatible wheel, install a C/C++ toolchain and Python development headers for your interpreter |
| Compiler missing on macOS | Install Xcode Command Line Tools with `xcode-select --install` |
| Compiler missing on Windows | Install Visual Studio Build Tools with the C++ workload |
| Compiler/header missing on Linux | Use your distribution's compiler and matching Python development packages; a missing `venv` module may also need a distro package |
| No display device on a remote machine | Use a desktop session for play or SDL's dummy drivers for tests |
| Lots of terminal output | Movement diagnostics remain enabled even with the on-screen debug overlay off |

## 3. Learn the Pygame building blocks

Pygame handles window, drawing, and input work so you can spend your time on game rules. It does not know what a Barracks or an enemy is. You define those objects and decide what they can do.

| Concept | Meaning in this project |
|---|---|
| `pygame.init()` | Initialize available Pygame modules |
| `Surface` | An image or drawing area, including the display surface |
| `Rect` | A rectangle used for position, size, mouse hits, and overlap tests |
| `pygame.image.load()` | Read a PNG into a surface |
| `screen.blit(image, position)` | Copy an image onto the screen surface |
| `pygame.event.get()` | Read queued events, such as clicks and window-close requests |
| `Clock.tick(FPS)` | Limit the game-loop rate and return elapsed milliseconds |
| `Font.render()` | Create a surface containing text |
| `pygame.display.flip()` | Present the completed frame |
| `pygame.quit()` | Shut down Pygame modules |

### Learning example: a moving square

Think of the game as a flipbook: each frame shows the world a moment later. The loop reads input, updates positions, and draws the next page. `screen.fill()` covers the old image so the square does not leave a trail; `pygame.display.flip()` presents the finished frame.

Save this as a separate practice script outside the project source:

```python
import pygame

pygame.init()
screen = pygame.display.set_mode((768, 576))
clock = pygame.time.Clock()
x = 40.0
running = True

while running:
    dt_ms = clock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    direction = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
    x += direction * 100 * (dt_ms / 1000)
    x = max(0, min(x, 768 - 16))

    screen.fill((210, 230, 180))
    pygame.draw.rect(screen, (30, 70, 150), (int(x), 100, 16, 16))
    pygame.display.flip()

pygame.quit()
```

Hold the left or right arrow. The square moves at 100 pixels per second because you multiply speed by elapsed seconds.

Without elapsed time, adding 3 pixels per frame would move 90 pixels per second at 30 FPS and 180 at 60 FPS. The RTS uses elapsed time for movement, income, and cooldowns. Its path-following details introduce some remaining timing issues, covered in [Section 12](#12-turn-paths-into-movement).

## 4. Find your way around the source

```text
rts-pygame/
├── README.md                 Short introduction and launch instructions
├── STATUS.md                 Workspace lifecycle and current-state summary
├── requirements.txt          Pinned runtime dependencies
├── requirements-dev.txt      Runtime dependencies plus pytest
├── docs/
│   └── DEVELOPER_GUIDE.md     This guide
├── src/
│   ├── __init__.py            Empty package marker
│   ├── constants.py           Settings, building data, unit data
│   ├── rts.py                 Startup, menu, global state, main loop
│   ├── entities.py            Game objects, targeting, movement, combat
│   ├── utils.py               UI helpers and placement checks
│   ├── spawning.py            Enemy spawn-point selection and construction
│   ├── procedural.py          Tile loading and Perlin terrain
│   └── astar.py               Grid nodes and route search
└── assets/
    ├── buildings/            Building PNGs and unused sheets
    ├── characters/           Unit PNGs and an unused knight image
    └── tiles/plains/         Six grass tiles and one water tile
```

The file split lets you change an Archer's stats without rewriting movement, or test A* without opening a window. Read `constants.py`, then the main loop in `rts.py`. Follow units into `entities.py`; study terrain and pathfinding in their own files.

`sys.exit()` and `temp` are root-level scratch files, not game modules. The program's `sys.exit()` call uses Python's `sys` module. Treat `__pycache__` as generated bytecode, not editable source.

### Shared game state

Game state is what the game remembers between frames. Drawing "Gold: 150" does not store a balance; purchases need a number they can check and subtract from. In `rts.py`, the main state consists of:

- `buildings`, `units`, and `enemies`: lists of object instances.
- `gold` and `resources`: current balances.
- `terrain`: tile appearance IDs.
- `grid`: tile IDs plus pathfinding obstacle flags.
- `selected_unit`, `current_building_type`, and `building_cooldown`: player interaction state.
- `game_messages`: text and expiration timestamps.
- `wave_timer` and `current_wave`: enemy-spawn progress.

An **instance** is one object made from a class. Two Swordsmen share the same class and starting data, but each has its own position, HP, path, and target.

The game uses ordinary Python lists and objects. It does not use Pygame sprite groups or a separate engine framework.

### Package imports and startup

`src` is the package boundary. Modules now import one another explicitly:

```text
src.rts       -> src.entities, src.procedural, src.spawning, src.utils
src.entities  -> src.astar, src.constants, src.utils
src.spawning  -> src.constants, src.entities
src.utils     -> src.constants
```

`utils.py` no longer edits `sys.path` or imports entity classes. Enemy creation lives in `src/spawning.py`, which the controller imports separately. That removes the old `entities -> utils -> src.entities` cycle and ensures Python loads one `src.entities` module.

`rts.py` defines `main()` and starts it only under:

```python
if __name__ == "__main__":
    raise SystemExit(main())
```

Importing `src.rts` for a test therefore does not open a window, create fonts, enter the menu, or initialize Pygame. `main()` initializes Pygame, the display, fonts, menu rectangles, and clock at runtime, then resets the clock before gameplay so menu time does not become the first game `dt`.

Run the module from the repository root:

```sh
python -m src.rts
```

This arrangement favors predictable imports and testable startup. It also means `python src/rts.py` no longer works; direct script execution has no package context for the leading-dot imports.

## 5. Define the game environment

**Source:** [`src/constants.py`](../src/constants.py), `update_grid()` in [`src/rts.py`](../src/rts.py).

### Screen coordinates and grid coordinates

The current settings are:

```python
SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30
```

The world fills the window. Its grid has:

```text
columns = 768 / 16 = 48
rows    = 576 / 16 = 36
cells   = 48 × 36 = 1,728
```

The origin `(0, 0)` sits at the upper-left corner. X increases to the right; Y increases downward.

Use the grid like a board with numbered squares. A pathfinder can ask whether **cell** `(3, 2)` is blocked without interpreting the artwork. Keep finer **pixel** positions for drawing and smooth travel between squares:

```text
cell_x = pixel_x // 16
cell_y = pixel_y // 16

pixel_x = cell_x * 16
pixel_y = cell_y * 16
```

The `//` operator performs floor division. A click at pixel `(53, 38)` selects cell `(3, 2)` and snaps placement to pixel `(48, 32)`.

Store and access cells as `grid[y][x]`: row first, column second. Mixing that order is a common source of map bugs.

### Two map representations

Placing a Barracks leaves the ground's tile ID unchanged but makes the cell blocked. Keeping appearance and walkability separate lets you change an image without rewriting movement rules.

With all grass tiles loaded:

```text
terrain[y][x] = 0 through 5   # grass appearance
terrain[y][x] = 6            # water appearance

grid[y][x] = (tile_index, obstacle_flag)
obstacle_flag = 0            # walkable
obstacle_flag = 1            # blocked
```

Water uses `len(terrain_generator.grass_tiles)` as its ID, rather than a fixed constant. Six loaded grass images give water ID 6. Missing grass files can change that ID.

`update_grid(buildings)` rebuilds the navigation map at the start of each gameplay frame:

1. Copy each terrain ID and mark water as blocked.
2. Mark the cells beneath building rectangles as blocked.

Most buildings occupy one 16 × 16 cell. The Castle uses a size multiplier of 2, so its 32 × 32 rectangle occupies four cells.

Units and enemies do **not** block this map. They can overlap because the movement code also lacks physical collision resolution. A red `COLLIDING` debug label reports overlap; it does not stop movement.

For a future larger world, keep world size separate from display size and introduce a camera offset. The current project has neither distinction.

## 6. Load and use art assets

**Source:** `GameObject.__init__()` in [`src/entities.py`](../src/entities.py), `TerrainGenerator.load_plains_tiles()` in [`src/procedural.py`](../src/procedural.py).

### Current asset inventory

| Files | Source dimensions | Current use |
|---|---|---|
| `buildings/castle.png` | 32 × 32 | Castle; also scaled to 150 × 150 for the menu logo |
| `house.png`, `market.png`, `barracks.png`, `stable.png`, `farm.png`, `lumber.png`, `quarry.png` under `buildings/` | 16 × 16 | Other buildings |
| `characters/swordsman.png`, `bowman.png`, `goblin.png`, `orc.png` | 16 × 16 | Allied and enemy units |
| `tiles/plains/grass_1.png` through `grass_6.png` | 16 × 16 | Grass variants |
| `tiles/plains/water_1.png` | 16 × 16 | Water |
| `buildings/Houses.png`, `Keep.png`, `stables.png` | 48 × 64; 96 × 64; 80 × 16 | Unused sprite sheets |
| `characters/knight.png` | 32 × 32 | Unused image |

The asset filenames and game names need not match. The Archer uses `bowman.png`; the Stable uses `stable.png`, not `stables.png`.

### The load, size, position, draw sequence

The existing object constructor follows this pattern:

```python
self.image = pygame.transform.scale(
    pygame.image.load(image_path),
    size,
)
self.rect = self.image.get_rect(topleft=(x, y))
```

During drawing:

```python
screen.blit(self.image, self.rect)
```

`scale()` resizes the image without the smoothing used by `smoothscale()`. Integer scale factors tend to preserve the appearance of pixel art. The menu enlarges a 32-pixel castle to 150 pixels, which is not an integer multiple.

Use the image for how a unit looks and its `Rect` for the area you can click or collide with. Rectangle checks stay simple even if you replace the artwork. They also count transparent pixels inside that rectangle; this game does not test collisions pixel by pixel.

### Learning example: transparency and sprite sheets

After initializing Pygame and creating a display, you can prepare a PNG with per-pixel transparency:

```python
image = pygame.image.load("assets/buildings/castle.png").convert_alpha()
```

`convert_alpha()` prepares an alpha-capable surface for the display format. It does not remove a solid background already painted into an image. The current asset loaders do not call it.

A sprite sheet stores several frames or objects in one image. Loading `stables.png` as a whole and shrinking it to 16 × 16 would squash all five tiles together. Crop a frame first:

```python
sheet = pygame.image.load("assets/buildings/stables.png").convert_alpha()
frame = sheet.subsurface(pygame.Rect(0, 0, 16, 16)).copy()
```

The crop uses `(left, top, width, height)` in source-image pixels. For animation, you would store several frames and advance a frame index with elapsed time. No animation system exists in the current game.

### Replace or add artwork

1. Put the image in the matching `assets/` folder.
2. Set its path in `BUILDING_DATA`, `ALLY_DATA`, or `ENEMY_DATA`.
3. Check its proportions at the runtime size. Units use 16 × 16; buildings use their size multiplier.
4. Test mouse selection and building overlap. Changing visible artwork does not create a new collision shape.
5. Record the source, artist, license, and required attribution before distribution.

**Current limits:** each new entity loads and scales its own image and creates a font. There is no shared asset cache. `GameObject` catches `pygame.error`, but a missing image raised `FileNotFoundError` in the reviewed environment and bypassed that fallback. The menu logo has no fallback. Terrain loading catches failures and supplies colored tiles if it cannot load any grass or water images.

The earlier README claimed MIT licensing, but this checkout has no `LICENSE` file or asset-credit record. Do not assume an intended code license also covers the artwork. Confirm both before redistributing the project or its assets.

## 7. Generate terrain with Perlin noise

**Source:** [`src/procedural.py`](../src/procedural.py).

### 7.1 Choose a continuous field instead of independent random tiles

Imagine rolling ground with water filling the low spots. Nearby points tend to have similar heights, so land and water form patches. Perlin noise gives you that smooth variation; a separate random choice per tile would scatter both across the map.

You can treat the result as a rough height field:

```text
lower value -> water
higher value -> one of the grass appearances
```

The map remains two-dimensional. A tile's noise value does not create physical elevation or change movement cost.

Inside each noise layer, the library assigns repeatable, pseudorandom direction vectors to grid points. A dot product compares a corner's direction with the vector from that corner to the sample. The library then blends the four corner contributions with a smooth curve.

That blending lets small changes in position give small changes in value. This mathematical grid is separate from the game's 16-pixel tile grid. `pnoise2()` handles the calculations; you control where to sample, how to combine layers, and which values become grass or water.

### 7.2 Sample the field

`TerrainGenerator` loads the tile images and calls `generate_terrain()` in its constructor. The generator visits screen positions in 16-pixel steps and samples:

```python
noise_value = noise.pnoise2(
    (x + self.noise_seed) / scale,
    (y + self.noise_seed) / scale,
    octaves=octaves,
    persistence=persistence,
    lacunarity=lacunarity,
    repeatx=self.screen_width,
    repeaty=self.screen_height,
    base=0,
)
```

Current parameters:

| Parameter | Value | Meaning |
|---|---|---|
| `scale` | `150.0` | Divide sample positions by this. A larger divisor stretches features across more pixels |
| `octaves` | `4` | Combine four noise layers at different frequencies |
| `persistence` | `0.5` | Multiply each successive layer's amplitude by 0.5 |
| `lacunarity` | `1.5` | Multiply each successive layer's frequency by 1.5 |
| `noise_seed` | Random integer from 0 to 1000 | Offset both input coordinates before division |
| `base` | `0` | Keep the library's base setting fixed |
| `repeatx`, `repeaty` | `768`, `576` | Repeat periods in noise-coordinate space |

At scale 150, moving one tile changes a sample coordinate by `16 / 150`, about `0.107`. Neighboring cells therefore sample nearby positions.

Use the first layer for broad shapes and the later, weaker layers for smaller details. Here their relative amplitudes are `1, 0.5, 0.25, 0.125` and frequencies are `1, 1.5, 2.25, 3.375`. `pnoise2()` combines them for you.

A fixed seed helps you return to a troublesome map while debugging. Here `noise_seed` offsets coordinates; it does not call `random.seed()` or set `base`. Reproducing terrain also requires the same other inputs and environment. It does not fix the enemy-spawn random sequence.

The repeat periods do not make opposite screen edges match: the code samples divided pixel coordinates rather than traversing a full 768 × 576 noise-coordinate period. There is no wrapping-world mechanic.

### 7.3 Convert values to tile IDs

Perlin values vary around zero. The code uses this threshold and mapping:

```python
water_threshold = -0.1

if noise_value < water_threshold:
    tile_index = len(self.grass_tiles)
else:
    tile_index = int(
        (noise_value - water_threshold)
        / (1 - water_threshold)
        * len(self.grass_tiles)
    )
    tile_index = max(0, min(tile_index, len(self.grass_tiles) - 1))
```

For six grass images:

| Example noise value | Result |
|---|---|
| `-0.2` | Water, ID 6 |
| `-0.1` | Grass, ID 0 |
| `0.3` | Grass, ID 2 |
| `1.0` | Grass, ID 5 after clamping |

Clamping keeps the grass index inside `0..5`. You should not expect equal use of the six grass variants; noise values do not have a uniform distribution.

Treat the threshold as the waterline on that imaginary ground. Raising it floods more samples; lowering it exposes more grass. Scale changes the size of the landforms, while the threshold decides which parts count as water.

### 7.4 Render the tile grid

`draw_terrain(screen)` visits `self.terrain` and draws each tile at:

```text
screen position = (column * grid_size, row * grid_size)
```

The grass IDs select images from `grass_tiles`. The water ID selects `water_tiles[0]`.

The terrain contains grass patches and water shapes. It has no dedicated river carving, erosion, coastline autotiling, biome system, or connectivity guarantee. A water shape might resemble a river, but the code does not enforce a source, mouth, or continuous river path.

### 7.5 The regeneration bug

There are two terrain references:

- `terrain_generator.terrain`, which `draw_terrain()` reads.
- The global `terrain` in `rts.py`, which placement and `update_grid()` read.

The constructor sets the first. Startup calls `generate_terrain()` again to set the second. Both contain equal values because they use the same parameters.

Pressing `T` assigns another result to the global `terrain`, but:

1. The code keeps the same `noise_seed`, so it returns the same map values.
2. `generate_terrain()` returns a list without replacing `self.terrain`, so the renderer keeps its original map reference.

Changing the seed alone would leave visible terrain and collision terrain out of sync.

**Suggested change, partial example:** keep the two references aligned while testing regeneration:

```python
terrain_generator.noise_seed += 1
terrain = terrain_generator.generate_terrain()
terrain_generator.terrain = terrain
```

A complete regeneration feature must also rebuild the navigation grid, clear obsolete paths, and decide what to do with buildings and units now standing in water. This example does not implement those policies.

For a playable procedural map, add validation after generation: reserve starting land, check connected walkable regions, and choose spawn points with routes into the play area.

## 8. Understand the game loop and controls

**Source:** [`src/rts.py`](../src/rts.py).

In an RTS, income and enemies keep advancing while you decide what to build. The loop keeps the world running even when there is no new input.

### Startup and menu

At module scope, the script initializes Pygame, the display, a clock, fonts, resource balances, entity lists, and terrain. It draws the menu terrain onto a background surface and loads the castle logo.

The menu loop reads events and draws its buttons. Start New Game leaves the menu loop and enters the game loop. Exit or closing the menu leaves the program.

Two timing details need repair:

- The menu has no `clock.tick()` call, so it has no frame-rate cap.
- The game creates the clock before entering the menu. Its first gameplay `dt` includes time spent in the menu, which can cause an income jump and advance the wave timer.

The menu also creates `start_button` and `exit_button` after processing events. A mouse event in its first iteration can reference a button before assignment.

### One gameplay frame, in source order

```text
Rebuild navigation grid from water and buildings
    ↓
Read dt and mouse; assemble debug text
    ↓
Add resource income; reduce placement cooldown
    ↓
Compute building preview and overlap flag
    ↓
Process keyboard and mouse events
    ↓
Update allies, then enemies: target → move → attack
    ↓
Check wave timer; spawn enemies if due
    ↓
Remove dead allies and enemies
    ↓
Draw terrain, HUD, objects, preview, messages, debug
    ↓
Present the frame
```

The order has gameplay effects. A building placed during event handling does not enter the navigation grid until the next frame. A building removed during drawing still blocked the grid earlier that frame. Preview collision data comes from before the event loop, so changing building type and clicking within one frame can use an outdated footprint.

### Controls

| Input | Current behavior |
|---|---|
| `1` | Choose Castle |
| `2` | Choose House |
| `3` | Choose Market |
| `4` | Choose Barracks |
| `5` | Choose Stable |
| `6` | Choose Farm |
| `7` | Choose LumberMill |
| `8` | Choose Quarry |
| Left-click friendly unit | Select it and clear the building choice |
| Left-click Barracks / Stable | Train its assigned unit if affordable |
| Left-click other land | Attempt to place the chosen building |
| Right-click with a unit selected | Request a route to the clicked cell |
| `Esc` | Clear the building choice; it does not pause, quit, or clear unit selection |
| `D` | Toggle on-screen debug information and print the navigation grid |
| `T` | Call terrain generation, with the regeneration limits above |
| Close window | Quit |

Number keys also clear unit selection. There is no box selection, shift selection, attack-move command, or explicit hold-position mode.

### A short first play session

1. Click Start New Game.
2. Press `4` and place a Barracks on grass, away from water and the bottom edge.
3. Click the Barracks to train a Swordsman.
4. Click the Swordsman, then right-click nearby grass.
5. Watch the blue path outline with debug on. Press `D` to hide the overlay.
6. Keep playing to see enemy waves and automatic targeting.

You start with enough resources for a Barracks and a Swordsman. A Castle is optional; there is no rule requiring it before other buildings.

## 9. Build the economy and construction rules

**Source:** building tables in [`src/constants.py`](../src/constants.py); resource and click-handling blocks in [`src/rts.py`](../src/rts.py).

### Starting resources and passive income

Gold spent on a Market cannot buy a soldier at the same time. Costs create that choice; income lets you recover after spending. Enemy waves give you a reason to weigh future growth against defense now.

Gold lives in its own variable. The other four resources live in a dictionary.

| Resource | Starting amount | Base gain per second | Multiplier |
|---|---:|---:|---|
| Gold | 150 | 1.5 | `1 + 0.1 × Markets + 0.2 × Castles` |
| Wood | 200 | 0.5 | `1 + 0.15 × LumberMills + 0.1 × Castles` |
| Stone | 200 | 0.5 | `1 + 0.12 × Quarries + 0.15 × Castles` |
| Food | 200 | 0.25 | `1 + 0.2 × Farms + 0.1 × Castles` |
| People | 3 | 0.1 | `1 + 0.0005 × Houses + 0.001 × Castles` |

Each frame adds:

```text
increase = base_rate × multiplier × (dt_ms / 1000)
```

One Market and one Castle give a gold multiplier of `1.3`. Gold income becomes `1.5 × 1.3 = 1.95` per second, or about `0.06435` during a 33-millisecond frame.

The multipliers add bonuses. Two Markets give `1 + 0.2`, not `1.1 × 1.1`. Houses have a small current bonus: one raises people income from `0.1` to `0.10005` per second.

Balances can contain fractions. The HUD displays `int(amount)`, hiding the fractional part. People act as a regenerating, spendable resource; they are not a population cap. Dead soldiers do not refund people.

Buildings increase abstract income. You do not assign workers or place a LumberMill next to a forest. Grass variants have no economic effect.

### Building definitions

A data table lets the same purchase code handle all eight buildings. You can change a price without adding a new construction rule. The charges below come from each entry's **`resources` dictionary**.

| Key | Building | HP | Footprint | Gold | Wood | Stone | Effect |
|---|---|---:|---|---:|---:|---:|---|
| `1` | Castle | 275 | 2 × 2 | 75 | 50 | 100 | Income bonuses; at most one living Castle |
| `2` | House | 20 | 1 × 1 | 20 | 15 | 0 | People income bonus |
| `3` | Market | 30 | 1 × 1 | 30 | 20 | 25 | Gold income bonus |
| `4` | Barracks | 40 | 1 × 1 | 40 | 20 | 15 | Train Swordsman |
| `5` | Stable | 25 | 1 × 1 | 35 | 20 | 15 | Train Archer |
| `6` | Farm | 20 | 1 × 1 | 25 | 10 | 0 | Food income bonus |
| `7` | LumberMill | 30 | 1 × 1 | 40 | 30 | 10 | Wood income bonus |
| `8` | Quarry | 50 | 1 × 1 | 20 | 30 | 10 | Stone income bonus |

`BUILDING_DATA` also has a scalar `cost` field. Construction does not use it. For example, the Stable's scalar cost is 25, but its actual gold charge is 35. Treat the resource dictionary as the current purchase rule.

A building's `unit` field connects it to a unit type. `size_multiplier` changes its image and rectangle size. Omit that field and it defaults to 1.

### Placement and payment

The left-click handler checks for a friendly unit first. Otherwise, it snaps the click to a grid cell and checks that cell for water. A clicked training building gets the training action. Other clicks can attempt construction.

Construction checks the selected type, cached overlap flag, placement cooldown, Castle limit, and available resources. On success, it creates a `Building`, subtracts its resource costs, and starts a 1,000-millisecond shared placement cooldown.

Construction is instant. The cooldown limits successive placement; it is not construction progress. There is no builder unit, build animation, repair, demolition command, or refund.

The affordability code uses `resources.get(resource, gold)` to handle the separate gold variable. This works for the existing keys, but a misspelled resource key would also fall back to the gold balance. A unified resource dictionary would make validation clearer.

### Incomplete placement validation

- Water rejection checks the clicked top-left cell, not all four Castle cells.
- The overlap preview checks buildings and allied units, but not enemies.
- The preview color checks overlap and affordability, not water, bounds, Castle count, or cooldown.
- Large buildings can extend past the right or bottom screen edge.
- The code computes preview and collision state before processing input events.

**Suggested change:** implement one `can_place_building(type, cell)` function. Check the full footprint against bounds, terrain, occupancy, costs, cooldown, and unique-building rules. Use it for both preview and final placement so the green outline and the click follow the same rules.

## 10. Define units, combat, and enemy waves

**Source:** [`src/entities.py`](../src/entities.py), [`src/constants.py`](../src/constants.py), and [`src/spawning.py`](../src/spawning.py).

### Class structure

```text
GameObject
├── Building
└── Unit
    ├── AlliedUnit
    └── EnemyUnit
```

- `GameObject` loads an image, stores position and a rectangle, and draws the image plus HP text. Subclasses provide HP.
- `Building` reads its dimensions and HP from `BUILDING_DATA`.
- `Unit` stores speed, HP, damage, targets, route, waypoint/destination state, and cooldown. It implements shared targeting, movement, and attack behavior.
- `AlliedUnit` reads attack settings from `ALLY_DATA`.
- `EnemyUnit` reads attack settings from `ENEMY_DATA` and sets a targeting priority.

Allies and enemies both follow paths and attack on a timer. **Inheritance** keeps that shared behavior in `Unit`, so a movement fix can apply to both. Subclasses supply range and cooldown settings; instantiate `AlliedUnit` or `EnemyUnit`, since the base class depends on those methods.

### Allied unit stats

Speeds and ranges use pixels; cooldowns use milliseconds.

| Unit | Trainer | Gold | Food | People | HP | Speed px/s | Damage | Range px | Cooldown ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Swordsman | Barracks | 90 | 30 | 1 | 10 | 20 | 1 | 15 | 1500 |
| Archer | Stable | 60 | 80 | 1 | 8 | 30 | 2 | 70 | 2000 |

Training creates a unit at `(building.x, building.y + GRID_SIZE)`, one tile below the building, and deducts its costs. There is no queue or training timer. Repeated affordable clicks can produce overlapping units.

The code does not validate that spawn cell. It can contain water, another object, or lie below the screen for a building on the bottom row. The local `speed = 50` assignment in the click handler has no effect; the unit reads speed from its data table.

### Target selection

`Unit.update()` calls these methods in order:

```text
handle_target_selection()
move_towards_target(dt, grid)
handle_attack(dt, game_messages)
```

Allies receive the `enemies` list as candidate targets. Enemies receive `units + buildings`.

`find_nearest_target()` filters out dead or invalid targets, groups candidates by priority where applicable, and selects the shortest straight-line distance in the chosen group:

```text
distance = sqrt((target.x - unit.x)² + (target.y - unit.y)²)
```

`math.hypot(dx, dy)` computes that distance. This is distance between **top-left positions**, not sprite centers or nearest rectangle edges.

Units keep a living target until it dies; they do not switch to a closer target each frame. There is no detection radius, line-of-sight requirement, or route-reachability test in target selection. An allied soldier can start chasing a distant enemy without a player order.

### Enemy stats and priority bugs

| Enemy | HP | Speed px/s | Damage | Range px | Cooldown ms | Priority declared in data |
|---|---:|---:|---:|---:|---:|---|
| Goblin | 12 | 10 | 1 | 15 | 1500 | Building |
| Orc | 15 | 5 | 2 | 5 | 2000 | Unit |

`EnemyUnit.__init__()` sets `self.target_priority = "building"` for both types. It does not read the declared Orc priority.

The duplicate-module class problem is resolved by the package imports. The Orc priority bug remains: `EnemyUnit.__init__()` still sets `self.target_priority = "building"` for both types instead of reading `ENEMY_DATA`. Fix that behavior separately from the import cleanup.

### Attack cycle

Without a cooldown, an in-range unit could attack once per frame, making damage depend on frame rate. The cooldown gives each weapon a time-based pace.

A unit with a target and an expired cooldown checks its range. If the target is within range, it subtracts damage from target HP, adds a message, and resets its cooldown. The method then subtracts this frame's `dt` from a positive cooldown, including one it just reset.

An Archer damages a target through this same direct HP subtraction. There is no flying arrow or delayed impact. Terrain does not block attacks, so an Archer can shoot across water within range.

A long frame permits at most one attack per update; the code does not replay missed attacks. Cooldowns can become negative before the next check.

### Building-attack mismatch

Pathfinding redirects a blocked building goal to a walkable cell near it. But a neighboring cell is at least 16 pixels from the building's top-left position, while Goblin and Orc ranges are 15 and 5.

An enemy can therefore reach its redirected destination and remain out of attack range. Larger buildings add further error because the code measures distance to their top-left corner rather than their nearest edge.

**Suggested change:** choose a reachable attack position around the target footprint and measure range using a consistent geometric rule, such as distance from a unit center to the target rectangle. Keep that rule shared between navigation and combat.

### Waves

`current_wave` starts at 1; `wave_timer` starts at 0. The trigger is:

```python
wave_timer >= WAVE_INTERVAL * current_wave
```

`WAVE_INTERVAL` is 30,000 milliseconds. After a spawn, the code resets the timer to zero and increments `current_wave`.

| Wave being spawned | Approximate wait since previous wave/start | Enemy count |
|---|---:|---:|
| 1 | 30 seconds | 1 |
| 2 | 60 more seconds | 2 |
| 3 | 90 more seconds | 3 |

Ignoring frame-level delays and the menu-time issue, those waves occur near cumulative times 30, 90, and 180 seconds. The wait increases; this is not a fixed 30-second wave schedule. The debug counter shows the next wave number after a spawn.

`spawn_enemies()` creates `current_wave * ENEMY_SPAWN_RATE` enemies. `ENEMY_SPAWN_RATE` is 1. Each enemy gets a random type and a random grid-aligned position on one of the four map edges. Coordinates stay within the grid, but the code does not check water, occupancy, or reachable land.

### Death and cleanup

The main loop removes dead allies and enemies after both update loops, using slice assignment:

```python
enemies[:] = [enemy for enemy in enemies if enemy.hp > 0]
```

Some units hold a reference to this same list. `[:]` changes its contents without replacing the list, so those units see the removals too.

However, a unit killed earlier in the frame can still take its turn before cleanup because updates do not begin with an HP guard. Buildings are removed during drawing with `buildings.remove(building)` inside iteration, which can skip the next building. A selected unit can also remain selected after its removal.

Separate update, death cleanup, and drawing to make these rules consistent. Destroying a Castle currently does not cause defeat.

## 11. Find routes with A*

**Source:** [`src/astar.py`](../src/astar.py).

### 11.1 Treat the grid as a graph

Walking straight toward a goal can lead a soldier into a lake. A* looks for a route through neighboring cells instead. We describe these possible steps as a **graph**: cells are nodes, and allowed steps connect them.

You give `a_star()`:

```text
navigation grid + start cell + goal cell
```

It returns a list of `Node` objects. Drawing and smooth movement happen elsewhere; A* searches cell coordinates.

A* combines two costs:

```text
g(n) = known cost from the start to cell n
h(n) = estimated remaining cost from n to the goal
f(n) = g(n) + h(n)
```

The soldier has not moved yet. The search compares possible routes: `g` counts a route's known cost, and `h` estimates the unfinished part. A* examines the lowest `f` next, considering both progress toward the goal and the cost of getting there.

### 11.2 Nodes and neighbors in this implementation

`create_nodes_from_grid()` creates a fresh `Node` for each cell. Each stores:

- `x`, `y`: cell coordinates.
- `type`: `'wall'` if the obstacle flag is set, otherwise `'road'`.
- `g_score` and `f_score`: infinity until the search finds a route to the node.

A node's equality and hash depend on coordinates. This lets the search store nodes in a set.

`get_neighbors()` permits eight directions:

```text
NW   N   NE
 W   n    E
SW   S   SE
```

It checks map bounds. The main search then rejects wall neighbors and already-closed neighbors.

For adjacent cells, `distance()` charges:

```text
horizontal or vertical step = 1
diagonal step               = 1.414
```

The diagonal cost approximates `sqrt(2)`, the distance across a unit square. These costs measure cell travel, not pixels or milliseconds; all grass variants cost the same.

### 11.3 The search, step by step

The current implementation follows this outline:

1. Build the node grid and obtain the start node.
2. If the requested goal is a wall, choose a replacement with `find_nearest_walkable()`.
3. Return `[]` if there is no walkable replacement or if start equals the resolved goal.
4. Set the start's `g` score to 0 and push it into the open heap.
5. Pop the candidate with the smallest queued `f` score.
6. If it is the goal, reconstruct the path.
7. Close that node and inspect its neighbors.
8. Compute `tentative_g = current.g_score + step_cost`.
9. If that improves a neighbor's cost, update its scores and predecessor, then push a heap entry.
10. Continue until the goal is found or the heap is empty.

Important structures:

| Name | Purpose |
|---|---|
| `open_set` | A `heapq` priority queue of candidates to explore |
| `in_open_set` | Coordinate membership tracking; it does not choose priority |
| `closed_set` | Nodes the search has expanded |
| `came_from` | A coordinate-to-predecessor map for rebuilding the route |
| `counter` | A growing number in heap entries to break equal-priority ties |

The heap keeps the lowest-score entry ready to take next, without sorting all candidates after each addition. Entries are `(f_score, counter, node)`; `heapq.heappop()` removes the smallest queued tuple.

If a better route reaches a node already in the heap, the code pushes another entry with the new score. Older entries remain. The current loop does not discard stale entries or skip an already-closed node when popping it, so it can repeat work.

### 11.4 A small route

On an open 3 × 3 grid:

```text
S . .
. . .
. . G
```

A diagonal path is:

```text
(0, 0) -> (1, 1) -> (2, 2)
```

Its movement cost is `1.414 + 1.414 = 2.828`. The returned list includes the starting node, so three nodes represent two movement steps.

To trace the first decision, expand `(0, 0)` and score its three available neighbors. With the current Manhattan heuristic and goal `(2, 2)`:

| Candidate | `g`: cost from start | `h`: estimated cost to goal | `f = g + h` |
|---|---:|---:|---:|
| `(1, 0)` | 1 | 3 | 4 |
| `(0, 1)` | 1 | 3 | 4 |
| `(1, 1)` | 1.414 | 2 | 3.414 |

The heap selects `(1, 1)` next because it has the lowest `f`. From there, the goal is one diagonal step away. This example produces the shortest route, but the heuristic mismatch discussed below prevents that guarantee on other maps.

**Runnable learning example:** save as a temporary script in the repository root and run it with the environment's Python. `src.astar` has no Pygame dependency.

```python
from src.astar import a_star

# Each cell contains (terrain_id, obstacle_flag).
grid = [[(0, 0) for _ in range(3)] for _ in range(3)]
path = a_star(grid, (0, 0), (2, 2))
print([(node.x, node.y) for node in path])
# [(0, 0), (1, 1), (2, 2)]
```

`came_from` remembers which cell led to each improved route. This avoids copying a whole path into every candidate. Once the goal is found, `reconstruct_path()` follows those links back to the start and inserts each predecessor at the front of the result.

### 11.5 The heuristic does not match diagonal movement

The current `h_score()` uses **Manhattan distance**:

```text
h = abs(goal.x - node.x) + abs(goal.y - node.y)
```

Manhattan distance fits four-direction movement with cost 1 per step. With diagonals, it can overestimate: from `(0, 0)` to `(1, 1)`, it estimates 2 even though a legal diagonal costs 1.414.

An **admissible heuristic** never overestimates the true remaining cost. The current mismatch means you cannot assume that this A* returns the shortest route. A comparison during review found a route costing 11.070 where a Dijkstra search using the same movement rules found 10.484.

**Suggested change:** use octile distance, matching this file's movement costs:

```text
dx = abs(goal.x - node.x)
dy = abs(goal.y - node.y)
h  = 1.414 * min(dx, dy) + abs(dx - dy)
```

The existing `distance()` already computes this formula. An initial correction would be:

```python
def h_score(start, end):
    return distance(start, end)
```

This is a proposed replacement, not the current function. Pair it with heap/closed-set tests. If you change the diagonal cost to `sqrt(2)`, use that same value in the heuristic.

Setting `h` to zero gives Dijkstra-style search, which is useful as a small-map reference for checking route costs.

### 11.6 Corner cutting

The current neighbor logic allows this diagonal:

```text
S #
# G
```

`#` means blocked. The code returns `S -> G` because it checks the destination cell without checking the two side cells. A 16 × 16 soldier cannot fit through that shared corner without touching obstacles.

**Suggested change:** for a diagonal step from `(x, y)` to `(x + dx, y + dy)`, require both `(x + dx, y)` and `(x, y + dy)` to be walkable if your design forbids corner cutting.

### 11.7 Blocked goals and the BFS helper

A building blocks its own cell, so the pathfinder cannot end there. `find_nearest_walkable()` searches outward from a blocked goal using **breadth-first search**, or BFS.

BFS visits nearby cells in layers with a first-in, first-out queue. This helper returns the first walkable cell it encounters. It may search beyond immediate neighbors and across blocked cells while looking for that candidate.

Its limits:

- It measures proximity outward from the goal, not reachability from the start.
- It treats diagonal and straight search steps as equal for this outward search.
- It does not consider the unit's attack range or the target's full footprint.
- It can choose an unreachable replacement even if another nearby cell has a route.
- It uses `list.pop(0)`, which shifts remaining entries; `collections.deque.popleft()` would avoid that overhead.

For combat, generate candidate attack cells around the target, then choose one the unit can reach. A single nearby empty cell is not enough to guarantee an attack.

### 11.8 Return values and input assumptions

`a_star()` returns `[]` for several different outcomes: no route, no walkable goal, or already standing at the resolved goal. The caller cannot distinguish success-with-no-movement from failure through that value alone.

The function assumes a nonempty rectangular grid and valid coordinates. It does not reject a blocked start; a search can leave one. Out-of-range positive coordinates can raise an index error; negative coordinates can invoke Python's negative indexing.

**Suggested change:** validate inputs and return explicit status, such as `FOUND`, `ALREADY_THERE`, or `UNREACHABLE`, along with the path and resolved goal.

## 12. Turn paths into movement

**Source:** right-click handling in [`src/rts.py`](../src/rts.py), `Unit.move_towards_target()` in [`src/entities.py`](../src/entities.py).

### Player order to waypoint list

A* plans a route; movement follows it. Keeping those jobs separate lets a unit reuse a route across many frames while `dt` controls how far it walks in each one.

A right-click on a selected unit:

1. Snaps the click to a pixel-aligned cell position.
2. Stores that position in `destination` and sets `moving = True`.
3. Converts start and goal positions into cell coordinates.
4. Calls `a_star()` and assigns its result to `path`.
5. Adds a movement or no-path message.
6. Finds a nearest enemy target as well.

The `moving` attribute does not control later movement; no code reads it. The unit uses `path`, `destination`, and `target` instead.

### Smooth movement between cells

For the next path node:

```text
target_x = node.x * 16
target_y = node.y * 16
dx = target_x - unit.x
dy = target_y - unit.y
distance = hypot(dx, dy)
travel = speed * (dt_ms / 1000)
```

If the waypoint is within `travel`, the unit snaps to it and removes it from the path. Otherwise:

```text
unit.x += (dx / distance) * travel
unit.y += (dy / distance) * travel
```

Dividing by distance gives a direction vector of length 1. This keeps diagonal travel speed equal to straight-line travel speed. At 20 pixels per second with a 33-millisecond frame, a Swordsman travels about 0.66 pixels.

Floating-point `x` and `y` let small steps add up. Rounding each 0.66-pixel step down to zero would leave a soldier stuck. The unit copies its accumulated position to an integer-based `Rect` for drawing and collision checks.

### Chasing and repathing

For a living target, movement stops within attack range. Outside range, the unit requests a route if it has no path, no destination, or the target has moved **more than 32 pixels** from its last recorded position. This threshold limits searches for small target movements while following a route.

The method clamps chase start and goal cells to the grid. It currently contains two calls to `a_star()` in the same repath branch, so a valid repath performs the same search twice. It also retries unreachable targets on later frames rather than applying a retry delay.

The code tracks target movement, but it does not invalidate routes when someone places a building across them.

### Movement bugs you can observe

**Failed path still permits movement.** A right-click stores `destination` before searching. If A* returns no route, the empty-path fallback moves in a straight line toward that destination without checking obstacles. A review test placed a wall between a soldier and its destination; the soldier entered the wall cell.

**Player order and combat intent overlap.** The code finds enemy targets even after movement orders. The next update can chase a target, stop within its range, or replace the player's route. There is no defined priority between move orders and automatic combat.

**Waypoint timing loses travel distance.** The method consumes at most one path node per frame and discards unused travel distance after reaching it. Because paths include the start, the first node can also consume a frame without movement. Low frame rates and large `dt` values can reduce effective movement speed.

**Routes can become stale.** A unit follows stored waypoints without checking whether the next step remains walkable. New construction can block a route the unit already has.

**Suggested change:** give each unit an explicit intent such as `IDLE`, `MOVE`, `CHASE`, or `ATTACK`. That lets you define whether a new enemy should interrupt a move order. Keep the final player goal separate from the next waypoint. On route failure, stop and report failure rather than bypassing the obstacle rules. Revalidate or replan after navigation-map changes.

## 13. Draw the interface and debug the simulation

**Source:** drawing block in [`src/rts.py`](../src/rts.py), UI helpers in [`src/utils.py`](../src/utils.py), entity `draw()` methods.

The game draws in this order:

```text
background terrain
resource text
buildings and HP labels
allied units and selection outline
enemies
building preview
messages
building-key hints
debug text and grid, if enabled
```

Later drawing can cover earlier drawing. Buildings can cover resource text because the HUD starts before the objects. The full window remains playable map space; there is no dedicated UI panel that consumes clicks.

### Helper functions

| Helper | Responsibility |
|---|---|
| `draw_resources()` | Display integer resource balances at the upper left |
| `update_preview_rect()` | Snap a candidate building rectangle to the grid |
| `draw_building_preview()` | Draw green for affordable/non-overlapping, otherwise red |
| `check_collision()` | Check a placement rectangle against buildings and allies |
| `add_game_message()` | Remove expired entries, suppress active duplicate text, append a timed message |
| `draw_messages()` | Draw unexpired messages |
| `draw_key_bindings()` | Draw building keys and resource requirements |
| `draw_debug_info()` | Draw counts, FPS, mouse position, selection, and wave data |
| `draw_grid()` | Draw the grid on a transparent overlay |
| `generate_spawn_point()` / `spawn_enemies()` | Choose border positions and instantiate enemies |

Messages last 3,000 milliseconds by default. `draw_messages()` hides expired entries, but only `add_game_message()` removes them from the stored list. Duplicate text does not refresh the existing message's expiration.

Debug mode starts enabled. Units draw targets, path rectangles, and overlap labels. A blue route helps you distinguish a soldier with no path from one that has a path but is not moving, narrowing where to inspect. Turning the overlay off does not stop movement `print()` calls, so the terminal stays noisy after pressing `D`.

Current UI issues include overlapping messages/debug text, building-cost text clipped past the right edge, and a preview rectangle that can remain after `Esc` because the preview helper still returns a default-sized rectangle for `None`.

`draw_grid()` nests row and column loops while drawing full-length lines, causing repeated copies of the same lines. Draw each vertical and horizontal line once, or cache the overlay.

## 14. Known issues and a repair order

Keep fixes smaller than feature additions. The table groups the current findings by a practical repair order, not by a claim that the prototype is production-ready.

| Order | Area | Repair target |
|---:|---|---|
| 1 | Imports and startup | Complete in P0: one module identity, no circular import, guarded `main()`, runtime menu/display setup |
| 2 | Timing | Cap the menu; reset the clock before gameplay; define long-frame behavior |
| 3 | Navigation correctness | Match heuristic and movement costs; prevent corner cutting; handle stale heap entries and explicit outcomes |
| 4 | Movement safety | Remove straight-line failure fallback; separate move/chase intent; invalidate stale paths; avoid duplicate searches |
| 5 | Placement and spawning | Validate entire footprints, bounds, occupancy, and terrain; choose valid unit/enemy spawns |
| 6 | Combat | Honor configured priorities; choose reachable attack positions; use consistent distance geometry |
| 7 | Terrain ownership | Keep one authoritative map, change the seed for regeneration, and handle affected objects/routes |
| 8 | Entity lifecycle | Skip dead actors, clean lists outside drawing, clear dead selections |
| 9 | UI and diagnostics | Fix clipping/overlap, align preview with placement rules, gate prints, cache debug grid |
| 10 | Project hygiene | Add dependency metadata and tests; resolve code/art licensing; remove tracked caches and irrelevant scratch artifacts in a separate cleanup |

The separate [improvement plan](IMPROVEMENT_PLAN.md) puts these repairs into a proposed short base-defense release, with gameplay rules and phase-by-phase acceptance tests. Implementation has not started; `STATUS.md` retains the dormant lifecycle.

## 15. Validate changes

A tiny test map makes a route bug easier to repeat than a whole battle. Use code checks for exact rules and manual play for controls and visual feedback.

### Quick local checks

With the environment active, from the root:

```sh
python -m pip check
python -m compileall -q src
python -m src.rts
```

`compileall` checks Python syntax and creates bytecode caches. It does not validate imports, assets, menu behavior, or gameplay. The repository already tracks some old caches; review your diff before committing generated files.

### Headless terrain check

Save this as a temporary root-level script. It uses an SDL dummy display, so it will not open a visible window. Run it from the repository root so the `src` package is importable.

```python
import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from src.procedural import TerrainGenerator

pygame.init()
pygame.display.set_mode((768, 576))

generator = TerrainGenerator(768, 576, 16, noise_seed=123)
terrain = generator.terrain
assert len(terrain) == 36
assert all(len(row) == 48 for row in terrain)
assert all(0 <= tile <= len(generator.grass_tiles)
           for row in terrain for tile in row)
assert terrain == generator.generate_terrain()
generator.draw_terrain(pygame.display.get_surface())

pygame.quit()
print("Terrain dimensions, tile IDs, repeatability, and drawing passed.")
```

A dummy display cannot establish that the real window, input devices, or visual layout feel correct. Importing `rts.py` for a unit test also starts its top-level menu/game code; avoid that until startup has a main guard.

### Regression tests to add

For **A***, test an open diagonal route, an unreachable goal, a blocked goal, an already-reached goal, invalid coordinates, and the corner-cutting map. Compare path cost against Dijkstra on small generated grids. First record current behavior, then update expectations with each intended fix.

For **movement**, test that a failed route leaves the soldier in place, a new building invalidates its route, equivalent elapsed time gives comparable travel at different frame rates, and a move order follows your chosen policy around enemies.

For **terrain**, check fixed-seed repeatability, tile ID bounds, rendered/navigation map agreement, connected starting areas, and valid spawn positions.

For **economy and combat**, test exact deductions, insufficient funds, one-Castle enforcement, full-footprint water rejection, training at the bottom edge, target priorities, building attack range, and dead-unit cleanup.

### Manual playtest checklist

- Start and exit from the menu; leave the menu open before starting to expose the first-frame timing issue.
- Try each building, including a Castle beside water and at map edges.
- Spend resources until a purchase fails; compare the preview and result.
- Train both unit types, including repeated clicks and blocked spawn areas.
- Move a unit across land, toward water, and toward unreachable land.
- Place a building across an existing path.
- Watch a ranged fight and an enemy approaching a building.
- Kill a selected unit and check selection cleanup.
- Observe multiple waves and compare waits with the implemented schedule.
- Toggle `D`, press `T`, and close the window.

Some checks expose known failures today. Use them as regression cases during repairs rather than treating the list as a promise of passing behavior.

## 16. Extend the prototype in small steps

### Beginner: change data, then observe

Start with `constants.py`. Change one unit's speed or HP, run a short fight, and compare the outcome. Change one building bonus in `rts.py` and measure income over a fixed time.

To introduce a new allied type, add its data and image, then assign its name to a building's `unit` field. The current UI supports one trainable type per building. Supporting several requires a selection interface and a new training command.

Adding a building also requires a key mapping and, if it produces income, a multiplier entry in `rts.py`. A new table entry alone does not create a new economic rule.

### Intermediate: separate input, rules, and rendering

A useful proposed structure is:

```text
Game state
├── World: terrain, walkability, map revision
├── Economy: balances, prices, production
├── Entities: buildings, allies, enemies
├── Commands: build, train, move
└── UI state: selection, preview, messages

Frame:
read input -> create commands -> validate/apply commands
           -> simulate -> remove dead entities -> render
```

This structure is a proposal; no `World`, command system, or central `Game` class exists now. Introduce one boundary at a time. A shared placement validator is a smaller first change than rewriting the entire main loop.

Keep drawing free of gameplay mutations. Then you can test income, combat, and route rules without opening a window.

### Intermediate: improve performance after correctness

At current settings, one route request allocates 1,728 nodes. Multiple chasing units, duplicate searches, and unreachable goals can multiply that work. Target selection scans candidates; debug collision checks compare many pairs.

A cache keeps a prepared result for reuse: 20 Swordsmen could share one loaded image. It saves repeated work, but you must refresh cached data when its inputs change. Measure frame time before optimizing. Candidate improvements include:

- Cache terrain and grid-overlay surfaces until their inputs change.
- Cache images and fonts instead of loading them per entity.
- Rebuild walkability after map changes rather than each frame.
- Remove duplicate path searches and add a retry interval for unreachable targets.
- Track a map revision so units know when their routes need checking.
- Use a spatial grid for nearby-target/collision queries once entity counts justify it.

A conventional heap-based A* search on a bounded-degree grid has an approximate `O(V log V)` worst-case time bound under standard implementation assumptions, with `V` cells, and uses graph-sized bookkeeping. The current duplicate heap entries and repeated searches add overhead; that bound is not a measured performance result for this game.

### Add game features after the repair pass

Worker gathering needs resource nodes, worker orders, travel, harvesting time, carrying capacity, and delivery rules. A training queue needs queued orders, payment timing, a progress timer, and valid spawn selection.

Animation needs cropped frames, animation state, and elapsed-time frame selection. Sound needs licensed files and event-triggered playback. Victory/defeat needs a defined objective and a state transition that stops or replaces active play.

Larger maps need camera/world coordinate separation. Multiplayer needs an authority model and synchronized commands or state; the current global, random, variable-time simulation is not a multiplayer foundation without further design work.

## 17. Glossary and further reading

| Term | Short definition |
|---|---|
| RTS | Real-time strategy: players issue orders while the simulation continues |
| Frame | One pass of updates and drawing |
| FPS | Frames per second |
| Delta time / `dt` | Time elapsed since a previous clock tick |
| Tile | A small image used for one map cell |
| Sprite | A drawable game image; this project does not require `pygame.sprite.Sprite` |
| Sprite sheet | Several images or animation frames packed into one image |
| Blit | Copy pixels from one surface to another |
| Hitbox / footprint | The area used for collision, selection, or occupancy |
| Procedural generation | Creating content from rules and inputs instead of hand-authoring each cell |
| Seed | An input used to reproduce generated results; this project's terrain seed is an offset |
| Octave | One noise layer in a multi-layer field |
| Graph | Nodes connected by possible steps or relationships |
| Heuristic | An estimate that guides a search |
| Priority queue | A collection that lets you remove the lowest-priority-value item first |
| Waypoint | An intermediate position along a route |
| State machine | Explicit states and rules for transitions between behaviors |

Further reading:

- [Python virtual environments](https://docs.python.org/3/library/venv.html)
- [Pygame documentation and tutorials](https://www.pygame.org/docs/)
- [Python `heapq`](https://docs.python.org/3/library/heapq.html)
- [`noise` package](https://pypi.org/project/noise/)
- [Red Blob Games: introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html)

For this project's actual behavior, use the linked source files and the review notes above. General tutorials may assume different movement costs, collision rules, or game-loop structure.
