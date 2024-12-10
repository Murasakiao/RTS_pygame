# Real-Time Strategy Game (RTS) in Pygame

This project implements a simple real-time strategy (RTS) game using Pygame.  The game involves building structures, training units, gathering resources, and battling enemies.

## Features

* **Building Construction:** Place various buildings like castles, houses, barracks, and resource-generating structures. Each building has specific costs and functionalities.  Buildings cannot be placed in water.
* **Unit Training:** Train units such as swordsmen and archers from respective buildings. Units have different stats and attack ranges.
* **Resource Management:** Gather gold, wood, stone, food, and people to fund construction and unit training. Resource production is influenced by the number and type of buildings.
* **Enemy Waves:** Face waves of enemies that attack your buildings and units.  Enemy types include goblins and orcs, each with unique behaviors.
* **Procedural Terrain:** The game features procedurally generated terrain using Perlin noise, adding visual variety, including rivers and grasslands.
* **Unit Movement and Combat:** Select and move units across the map. Units automatically engage nearby enemies within their attack range.  Unit pathfinding is now more efficient, with fewer recalculations when targets move.
* **Game Messages:** Receive feedback on actions, such as building completion, unit training, and combat results.
* **Key Bindings:** Use number keys to select building types and other commands.

## Installation

1. **Clone the repository:** `git clone <repository_url>`
2. **Install Pygame:** `pip install pygame`
3. **Install noise:** `pip install noise`

## How to Play

1. **Run the game:** `python src/rts.py`
2. **Select a building type:** Press number keys 1-8 to choose a building.
3. **Place buildings:** Left-click on the grid to place a building (cannot be placed in water).
4. **Train units:** Click on a building that can train units (e.g., Barracks, Stable).
5. **Select a unit:** Left-click on a friendly unit.
6. **Move units:** Right-click on the map to move the selected unit.
7. **Toggle Debug Mode:** Press 'D' to show or hide debug information.
8. **Regenerate Terrain:** Press 'T' to regenerate the terrain.

## Code Structure

* **`src/rts.py`:** Main game file, handles game loop, event handling, updates, and drawing.
* **`src/entities.py`:** Defines game objects like buildings and units (allied and enemy).
* **`src/constants.py`:** Stores game constants like screen dimensions, grid size, colors, and building/unit data.
* **`src/utils.py`:** Contains utility functions for drawing the grid, displaying messages, checking collisions, and other helper functions.
* **`src/procedural.py`:** Handles the procedural terrain generation.
* **`src/astar.py`:** Implements the A* pathfinding algorithm.

## Future Improvements

* **More Unit Types:** Add more variety to the units, each with unique abilities and roles.
* **Advanced AI:** Improve enemy AI for more challenging gameplay.
* **Resource Gathering:** Implement resource gathering mechanics, such as assigning units to collect resources.
* **Tech Tree:** Introduce a tech tree for unlocking new buildings and units.
* **Improved UI:** Enhance the user interface with more information and controls.
* **Sound Effects:** Add sound effects for building, unit training, and combat.

## Contributing

Contributions are welcome!  Feel free to submit pull requests for bug fixes, new features, or improvements to the existing code.

## License

This project is licensed under the MIT License.

