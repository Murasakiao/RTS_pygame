# Kingdom Conquer · RTS in Pygame

A small real-time strategy prototype: place buildings, train soldiers, earn resources, and fight enemy waves on a Perlin-noise tile map.

**Status:** dormant prototype. The core loop runs in the reviewed environment, but navigation, placement, targeting, and terrain regeneration need fixes. See [STATUS.md](STATUS.md) for the project summary.

## Developer documentation

Read **[the developer guide](docs/DEVELOPER_GUIDE.md)** for a beginner-to-intermediate explanation of the current code:

- Python virtual environments, dependency installation, and troubleshooting.
- Pygame windows, surfaces, input, coordinates, and the game loop.
- Loading PNG art, cropping sprite sheets, and handling asset licenses.
- Perlin-noise parameters and converting noise into grass and water.
- Buildings, resource income, unit training, combat, and enemy waves.
- A* search, heuristics, blocked goals, and smooth waypoint movement.
- Known bugs, validation examples, and a suggested repair order.

The guide distinguishes implemented behavior from proposed improvements. It includes source links, stat tables, and learning examples.

For the next version, see **[the improvement plan](docs/IMPROVEMENT_PLAN.md)**: a proposed short base-defense RTS, with prioritized bug fixes, gameplay rules, phased implementation, and acceptance tests. Implementation has not started.

See **[the development log](docs/LOGS.md)** for specific changes, verification results, and the next implementation step.

## Quick start

The pinned dependencies were verified with **Python 3.12.13 on macOS 26.6.2 arm64**. Other operating systems and Python versions are not verified by this project. Run from the repository root:

```sh
# macOS / Linux
python3.12 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
python -m src.rts
```

For development tools, including the tested `pytest==9.1.1` version:

```sh
python -m pip install -r requirements-dev.txt
```

For Windows, compiler requirements, the development install, and environment troubleshooting, use the [setup instructions](docs/DEVELOPER_GUIDE.md#2-set-up-python-and-run-the-game).

Launch with `python -m src.rts` from the repository root. Asset paths still require the root working directory.

## Controls

| Input | Action |
|---|---|
| `1`–`8` | Choose Castle, House, Market, Barracks, Stable, Farm, LumberMill, or Quarry |
| Left-click land | Attempt building placement |
| Left-click Barracks / Stable | Train Swordsman / Archer if affordable |
| Left-click allied unit | Select one unit |
| Right-click | Request movement for the selected unit |
| `Esc` | Clear the building choice |
| `D` | Toggle on-screen debug information; also print the grid |
| `T` | Request terrain regeneration; currently returns the same map |
| Close window | Quit |

For a first session, build a Barracks, click it to train a Swordsman, then select the soldier and right-click nearby grass.

## Current scope

The prototype includes eight building types, two allied unit types, two enemy types, passive resource income, HP/cooldown combat, and eight-direction A* routing.

It has no worker gathering, animation, sound, save/load, multiplayer, or victory/defeat system. Building footprints and spawns lack complete validation. Failed movement can bypass obstacles, and melee units can get stuck outside building attack range. The guide documents these issues rather than presenting the prototype as a finished game.

## Licensing

An earlier README claimed MIT licensing, but this checkout contains no `LICENSE` file or art-credit record. Confirm the code and asset licenses before redistribution.
