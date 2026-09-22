SCREEN_WIDTH = 768
SCREEN_HEIGHT = 576
GRID_SIZE = 16
FPS = 30
BUILDING_COOLDOWN_TIME = 1000
MESSAGE_DURATION = 3000
WAVE_INTERVAL = 30000
ENEMY_SPAWN_RATE = 1
UNIT_ATTACK_RANGE = 50
ENEMY_ATTACK_RANGE = 50
UNIT_ATTACK_COOLDOWN = 2000
ENEMY_ATTACK_COOLDOWN = 2000
PATH_RETRY_DELAY = 250

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)


# Static content data. Match state belongs in src.game.GameState.
BUILDING_DATA = {
    "Castle": {
        "hp": 275,
        "asset_key": "building.castle",
        "cost": 75,
        "resources": {"gold": 75, "wood": 50, "stone": 100},
        "size_multiplier": 2,
    },
    "House": {
        "hp": 20,
        "asset_key": "building.house",
        "cost": 20,
        "resources": {"gold": 20, "wood": 15},
    },
    "Market": {
        "hp": 30,
        "asset_key": "building.market",
        "cost": 30,
        "resources": {"gold": 30, "wood": 20, "stone": 25},
    },
    "Barracks": {
        "hp": 40,
        "asset_key": "building.barracks",
        "cost": 40,
        "resources": {"gold": 40, "wood": 20, "stone": 15},
        "unit": "Swordsman",
    },
    "Stable": {
        "hp": 25,
        "asset_key": "building.stable",
        "cost": 25,
        "resources": {"gold": 35, "wood": 20, "stone": 15},
        "unit": "Archer",
    },
    "Farm": {
        "hp": 20,
        "asset_key": "building.farm",
        "cost": 25,
        "resources": {"gold": 25, "wood": 10},
    },
    "LumberMill": {
        "hp": 30,
        "asset_key": "building.lumber_mill",
        "cost": 40,
        "resources": {"gold": 40, "wood": 30, "stone": 10},
    },
    "Quarry": {
        "hp": 50,
        "asset_key": "building.quarry",
        "cost": 50,
        "resources": {"gold": 20, "wood": 30, "stone": 10},
    },
}

ALLY_DATA = {
    "Swordsman": {
        "name": "Swordsman",
        "asset_key": "character.swordsman",
        "cost": {"gold": 90, "food": 30, "people": 1},
        "speed": 20,
        "hp": 10,
        "atk": 1,
        "range": 15,
        "attack_cooldown": 1500,
    },
    "Archer": {
        "name": "Archer",
        "asset_key": "character.bowman",
        "cost": {"gold": 60, "food": 80, "people": 1},
        "speed": 30,
        "hp": 8,
        "atk": 2,
        "range": 70,
        "attack_cooldown": 2000,
    },
}

ENEMY_DATA = {
    "Goblin": {
        "name": "Goblin",
        "asset_key": "character.goblin",
        "speed": 10,
        "hp": 12,
        "atk": 1,
        "range": 15,
        "attack_cooldown": 1500,
        "target_priority": "building",
    },
    "Orc": {
        "name": "Orc",
        "asset_key": "character.orc",
        "speed": 5,
        "hp": 15,
        "atk": 2,
        "range": 5,
        "attack_cooldown": 2000,
        "target_priority": "unit",
    },
}
