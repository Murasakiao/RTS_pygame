from pathlib import Path
import logging

import pygame


ASSET_PATHS = {
    "building.castle": "buildings/castle.png",
    "building.house": "buildings/house.png",
    "building.market": "buildings/market.png",
    "building.barracks": "buildings/barracks.png",
    "building.stable": "buildings/stable.png",
    "building.farm": "buildings/farm.png",
    "building.lumber_mill": "buildings/lumber.png",
    "building.quarry": "buildings/quarry.png",
    "character.swordsman": "characters/swordsman.png",
    "character.bowman": "characters/bowman.png",
    "character.goblin": "characters/goblin.png",
    "character.orc": "characters/orc.png",
    "tile.grass_1": "tiles/plains/grass_1.png",
    "tile.grass_2": "tiles/plains/grass_2.png",
    "tile.grass_3": "tiles/plains/grass_3.png",
    "tile.grass_4": "tiles/plains/grass_4.png",
    "tile.grass_5": "tiles/plains/grass_5.png",
    "tile.grass_6": "tiles/plains/grass_6.png",
    "tile.water_1": "tiles/plains/water_1.png",
}

PLACEHOLDER_COLOR = (255, 0, 255, 255)
PLACEHOLDER_BORDER = (0, 0, 0, 255)


class AssetLoader:
    """Resolve, cache, and diagnose shared Pygame assets."""

    def __init__(self, project_root=None, logger=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).resolve().parents[1]
        self.asset_root = self.project_root / "assets"
        self.logger = logger or logging.getLogger(__name__)
        self.diagnostics = []
        self._reported = set()
        self._images = {}
        self._scaled_images = {}
        self._fonts = {}

    def path_for(self, asset_key):
        relative_path = ASSET_PATHS.get(asset_key)
        if relative_path is None:
            return None
        return self.asset_root / relative_path

    def image(self, asset_key, size=None):
        """Return a cached image or a visible placeholder when it cannot load."""
        normalized_size = tuple(size) if size is not None else None
        cache_key = (asset_key, normalized_size)
        if normalized_size is not None and cache_key in self._scaled_images:
            return self._scaled_images[cache_key]

        if asset_key not in self._images:
            path = self.path_for(asset_key)
            if path is None:
                self._report(
                    f"Unknown asset key '{asset_key}'; using a development placeholder."
                )
                image = self._placeholder(normalized_size or (16, 16))
            else:
                try:
                    image = pygame.image.load(str(path))
                except (OSError, pygame.error) as error:
                    self._report(
                        f"Could not load asset '{asset_key}' from '{path}': {error}; "
                        "using a development placeholder."
                    )
                    image = self._placeholder(normalized_size or (16, 16))
            self._images[asset_key] = image

        image = self._images[asset_key]
        if normalized_size is None:
            return image

        if image.get_size() == normalized_size:
            scaled_image = image
        else:
            scaled_image = pygame.transform.scale(image, normalized_size)
        self._scaled_images[cache_key] = scaled_image
        return scaled_image

    def font(self, size, name=None):
        """Return a cached font, with a default-font fallback and diagnostic."""
        cache_key = (name, size)
        if cache_key in self._fonts:
            return self._fonts[cache_key]

        try:
            font = pygame.font.Font(name, size)
        except pygame.error as error:
            self._report(
                f"Could not load font '{name}' at size {size}: {error}; "
                "using the default Pygame font."
            )
            font = pygame.font.Font(None, size)
        self._fonts[cache_key] = font
        return font

    def _placeholder(self, size):
        width, height = size
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(PLACEHOLDER_COLOR)
        pygame.draw.rect(surface, PLACEHOLDER_BORDER, surface.get_rect(), 1)
        return surface

    def _report(self, message):
        if message in self._reported:
            return
        self._reported.add(message)
        self.diagnostics.append(message)
        self.logger.warning(message)
