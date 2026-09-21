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

P0 startup/import work is complete: Pygame initializes inside `main()`, package imports are explicit, and spawning lives in `src/spawning.py`. The new `src.game.GameState` owns per-match mutable data, `FixedStepRunner` advances simulation at 30 Hz, and `src.assets.AssetLoader` owns shared repository-relative image/font loading with placeholders and diagnostics. Remaining gaps include terrain regeneration rules, navigation corner cutting and obstacle-bypassing movement, placement/spawning validation, and building attack range. Runtime and development dependency manifests pin the verified macOS environment; five committed P0 regression tests now cover import safety, assets, fresh state, fixed timing, and start/quit shutdown. Code and art licensing still need confirmation.

## Next action
P0 state/timing/asset work is implemented on the active refactor branch. Keep the five committed startup, asset, and fixed-step regression tests green, then review/merge PR #21 before beginning P1 navigation and movement repairs. Chosen direction remains short, single-player base-defense RTS matches; retain dormant status until development resumes.

## Conventions
- Launch from the unit root with `python -m src.rts` using the project `venv`.
- Launch with `python -m src.rts`; `src.assets.AssetLoader` resolves asset files relative to the repository/module location.
- Treat documented suggested changes as proposals, not implemented features. The P0 state owner, fixed-step runner, and asset loader are implemented; P1 gameplay repairs are not.
- Append a specific entry to [docs/LOGS.md](docs/LOGS.md) after each implementation, bug-fix, dependency, or documentation update.

## Pointers
- [README.md](README.md): quick start and controls.
- [docs/DEVELOPER_GUIDE.md](docs/DEVELOPER_GUIDE.md): beginner-to-intermediate explainer, current behavior, known issues, and validation examples.
- [docs/IMPROVEMENT_PLAN.md](docs/IMPROVEMENT_PLAN.md): proposed base-defense release, bug priorities, gameplay contracts, phase gates, and playtesting plan.
- [docs/LOGS.md](docs/LOGS.md): append-only record of concrete updates and verification.
- Entry: `src/rts.py`; assets: `assets/`.
