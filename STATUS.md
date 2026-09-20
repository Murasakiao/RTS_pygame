---
name: rts-pygame
description: Real-time-strategy game experiment in pygame
domain: software
status: dormant
stack: pygame · Python (venv)
entry: python -m src.rts
has_repo: true
updated: 2026-09-20
---

# rts-pygame

## State
Dormant Kingdom Conquer RTS prototype. Implements Perlin-noise grass/water terrain, eight building types, passive income, two allied and two enemy unit types, combat, waves, and A* waypoint movement.

Documentation review: 2026-09-15. Existing macOS environment: Python 3.12.13, pygame 2.6.1, noise distribution 1.2.2; pytest 9.1.1 passed a temporary A* smoke test. Source parsing, all 23 PNG loads, dependency checks, and a headless scripted gameplay smoke test passed. This was not a cross-platform installation or full gameplay/performance test; no game code changed.

P0 startup/import work is complete: Pygame initializes inside `main()`, package imports are explicit, and spawning lives in `src/spawning.py`. Remaining gaps include terrain regeneration with the same seed and a stale render reference; navigation permits corner cutting and obstacle-bypassing movement; placement/spawning and building attack range need repair. Runtime and development dependency manifests pin the verified macOS environment, but no committed test source, save/load, or win/lose state exists. Code and art licensing need confirmation.

## Next action
Improvement planning complete; gameplay implementation has not started. Chosen direction: short, single-player base-defense RTS matches. Retain dormant status until development resumes.

If resumed, start P0 in `docs/IMPROVEMENT_PLAN.md`: make imports/startup testable, establish game state and timing, then fix navigation before adding match and army-control features.

## Conventions
- Launch from the unit root with `python -m src.rts` using the project `venv`.
- Relative asset paths require the repository root as the working directory.
- Treat documented suggested changes as proposals, not implemented features.
- Append a specific entry to [docs/LOGS.md](docs/LOGS.md) after each implementation, bug-fix, dependency, or documentation update.

## Pointers
- [README.md](README.md): quick start and controls.
- [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md): beginner-to-intermediate explainer, current behavior, known issues, and validation examples.
- [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md): proposed base-defense release, bug priorities, gameplay contracts, phase gates, and playtesting plan.
- [docs/LOGS.md](docs/LOGS.md): append-only record of concrete updates and verification.
- Entry: `src/rts.py`; assets: `assets/`.
