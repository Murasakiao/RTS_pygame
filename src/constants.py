# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 25
FPS = 30
BUILDING_COOLDOWN_TIME = 1000
MESSAGE_DURATION = 3000
WAVE_INTERVAL = 5000
ENEMY_SPAWN_RATE = 1
UNIT_ATTACK_RANGE = 50
UNIT_ATTACK_COOLDOWN = 2000  
ENEMY_ATTACK_COOLDOWN = 2000

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)



# --- Data ---
# Building data
BUILDING_DATA = {
    "Castle": {"hp": 275, "image": "buildings/castle.png", "cost": 75, "resources": {"gold": 75, "wood": 50, "stone": 100}, "size_multiplier": 2},
    "House": {"hp": 20, "image": "buildings/house.png", "cost": 20, "resources": {"gold": 20, "wood": 15}},
    "Market": {"hp": 230, "image": "buildings/market.png", "cost": 30, "resources": {"gold": 30, "wood": 20, "stone": 25}},
    "Barracks": {"hp": 240, "image": "buildings/barracks.png", "cost": 40, "resources": {"gold": 40, "wood": 20, "stone": 15}, "unit": "Swordsman"},
    "Stable": {"hp": 225, "image": "buildings/stable.png", "cost": 25, "resources": {"gold": 35, "wood": 20, "stone": 15}, "unit": "Archer"},
    "Farm": {"hp": 250, "image": "buildings/farm.png", "cost": 25, "resources": {"gold": 25, "wood": 10}},
    "LumberMill": {"hp": 200, "image": "buildings/lumber.png", "cost": 40, "resources": {"gold": 40, "wood": 30, "stone": 10}},
    "Quarry": {"hp": 250, "image": "buildings/quarry.png", "cost": 50, "resources": {"gold": 20, "wood": 30, "stone": 10}},
}

# Unit data
ALLY_DATA = {
    "Swordsman": {"image": "characters/swordsman.png", "cost": {"gold": 50, "food": 30, "people": 1}, "hp": 10, "atk": 1},
    "Archer": {"image": "characters/bowman.png", "cost": {"gold": 60, "food": 40, "people": 1}, "hp": 8, "atk": 2},
}

# Enemy data
ENEMY_DATA = {
    "Goblin": {"image": "characters/goblin.png", "speed": 20, "hp": 8, "atk": 1, "attack_cooldown": 1500},
    "Orc": {"image": "characters/orc.png", "speed": 10, "hp": 12, "atk": 2, "attack_cooldown": 2500},
}
