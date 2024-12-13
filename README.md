# Real-Time Strategy Game (RTS) in Pygame

This project implements a real-time strategy (RTS) game using Pygame. The game involves building structures, training units, gathering resources, and battling enemies.

## Features

*   **Building Construction:** Place various buildings like castles, houses, barracks, and resource-generating structures. Each building has specific costs and functionalities. Buildings cannot be placed in water.
*   **Unit Training:** Train units such as swordsmen and archers from respective buildings. Units have different stats and attack ranges.
*   **Resource Management:** Gather gold, wood, stone, food, and people to fund construction and unit training. Resource production is influenced by the number and type of buildings. Resources are now generated over time, with multipliers based on the number of resource buildings.
*   **Enemy Waves:** Face waves of enemies that attack your buildings and units. Enemy types include goblins, orcs, and mini-bosses like dragons, each with unique behaviors and target priorities.
*   **Procedural Terrain:** The game features procedurally generated terrain using Perlin noise, adding visual variety, including rivers and grasslands. The terrain is now generated with a seed, allowing for consistent map generation.
*   **Unit Movement and Combat:** Select and move units across the map. Units automatically engage nearby enemies within their attack range. Unit pathfinding is now more efficient, using A* pathfinding, with fewer recalculations when targets move. Units will now attempt to find a path around obstacles.
*   **Game Messages:** Receive feedback on actions, such as building completion, unit training, and combat results. Messages now display for a set duration.
*   **Key Bindings:** Use number keys to select building types and other commands.
*   **Debug Mode:** Toggle debug mode to view grid, unit paths, and collision information.
*   **Dynamic Grid:** The game grid is dynamically updated to reflect building placements and water tiles, influencing unit pathfinding.
*   **Mini-Bosses:** Every 10th wave, a mini-boss enemy will spawn.

## Installation

1.  **Clone the repository:** `git clone <repository_url>`
2.  **Install Pygame:** `pip install pygame`
3.  **Install noise:** `pip install noise`

## How to Play

1.  **Run the game:** `python src/rts.py`
2.  **Select a building type:** Press number keys 1-8 to choose a building.
3.  **Place buildings:** Left-click on the grid to place a building (cannot be placed in water).
4.  **Train units:** Click on a building that can train units (e.g., Barracks, Stable).
5.  **Select a unit:** Left-click on a friendly unit.
6.  **Move units:** Right-click on the map to move the selected unit.
7.  **Toggle Debug Mode:** Press 'D' to show or hide debug information.
8.  **Regenerate Terrain:** Press 'T' to regenerate the terrain with a new seed.
9.  **Exit to Menu:** Press 'Escape' to deselect a building.

## Code Structure

*   **`src/rts.py`:** Main game file, handles game loop, event handling, updates, and drawing.
*   **`src/entities.py`:** Defines game objects like buildings and units (allied and enemy). Includes logic for unit movement, pathfinding, and combat.
*   **`src/constants.py`:** Stores game constants like screen dimensions, grid size, colors, and building/unit data.
*   **`src/utils.py`:** Contains utility functions for drawing the grid, displaying messages, checking collisions, managing waves, and other helper functions.
*   **`src/procedural.py`:** Handles the procedural terrain generation using Perlin noise.
*   **`src/astar.py`:** Implements the A* pathfinding algorithm.

## Future Improvements

*   **More Unit Types:** Add more variety to the units, each with unique abilities and roles.
*   **Advanced AI:** Improve enemy AI for more challenging gameplay, including more complex target selection and movement patterns.
*   **Resource Gathering:** Implement resource gathering mechanics, such as assigning units to collect resources.
*   **Tech Tree:** Introduce a tech tree for unlocking new buildings and units.
*   **Improved UI:** Enhance the user interface with more information and controls, such as a resource display and unit selection UI.
*   **Sound Effects:** Add sound effects for building, unit training, and combat.
*   **Save/Load Functionality:** Implement the ability to save and load game states.
*   **More Map Variety:** Add more terrain types and features to the procedural generation.
*   **Multiplayer:** Explore the possibility of adding multiplayer functionality.

## Contributing

Contributions are welcome! Feel free to submit pull requests for bug fixes, new features, or improvements to the existing code.

## License

This project is licensed under the MIT License.
