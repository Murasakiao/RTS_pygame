---
name: rts-pygame
description: Real-time-strategy game experiment in pygame
domain: software
status: dormant
stack: pygame · Python (venv)
entry: python -m src.rts
has_repo: true
updated: 2026-09-21
---

# rts-pygame

## State
Dormant Kingdom Conquer RTS prototype. Implements Perlin-noise grass/water terrain, eight building types, passive income, two allied and two enemy unit types, combat, waves, and A* waypoint movement.

Documentation review: 2026-09-15. Existing macOS environment: Python 3.12.13, pygame 2.6.1, noise distribution 1.2.2; pytest 9.1.1 passed a temporary A* smoke test. Source parsing, all 23 PNG loads, dependency checks, and a headless scripted gameplay smoke test passed. This was not a cross-platform installation or full gameplay/performance test; no game code changed.

P0 startup/import work is complete: Pygame initializes inside `main()`, package imports are explicit, and spawning lives in `src/spawning.py`. The new `src.game.GameState` owns per-match mutable data, `FixedStepRunner` advances simulation at 30 Hz, and `src.assets.AssetLoader` owns shared repository-relative image/font loading with placeholders and diagnostics. P1 world groundwork is now implemented in `src.world`: stable terrain kinds, shared cell geometry helpers, one authoritative world representation, and revisioned navigation data. A* now validates inputs, uses octile costs, rejects corner cutting, skips stale heap entries, and returns explicit results. Unit routes now consume residual waypoint distance, retry failed routes with a delay, and invalidate against the world's navigation revision without direct fallback movement. `UnitOrder` now separates single-unit Move, Attack, and Hold intent from current targets and waypoints. Remaining gaps include full-footprint placement/spawn validation and building attack-position geometry. Runtime and development dependency manifests pin the verified macOS environment; committed P0/P1 tests cover startup, assets, fresh state, fixed timing, world semantics, revisions, and geometry. Code and art licensing still need confirmation.

## Next action
Review the stacked P1 world, A*, route-safety, and order updates after PRs #21–#25, then implement one shared footprint validator plus valid training/enemy spawn-cell selection. Keep the committed headless tests green. Chosen direction remains short, single-player base-defense RTS matches; retain dormant status until development resumes.

## Conventions
- Launch from the unit root with `python -m src.rts` using the project `venv`.
- Launch with `python -m src.rts`; `src.assets.AssetLoader` resolves asset files relative to the repository/module location.
- Treat documented suggested changes as proposals, not implemented features. P0 is implemented; P1 world groundwork is implemented, while movement, placement, combat, and match repairs remain.
- Append a specific entry to [docs/LOGS.md](docs/LOGS.md) after each implementation, bug-fix, dependency, or documentation update.

## Pointers
- [README.md](README.md): quick start and controls.
- [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md): beginner-to-intermediate explainer, current behavior, known issues, and validation examples.
- [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md): proposed base-defense release, bug priorities, gameplay contracts, phase gates, and playtesting plan.
- [docs/LOGS.md](docs/LOGS.md): append-only record of concrete updates and verification.
- Entry: `src/rts.py`; assets: `assets/`.
