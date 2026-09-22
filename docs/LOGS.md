# Kingdom Conquer development log

This file records concrete project changes. Add a new dated entry after each implementation, bug-fix, dependency, or documentation update. Keep entries specific enough that another developer can tell what changed, why it changed, and how it was checked.

Use this format:

```text
## YYYY-MM-DD · Short title

### Changed
- File or feature: exact change.

### Why
- Player or developer problem addressed.

### Verification
- Commands, tests, or manual checks performed.

### Scope
- What was not changed, plus the next relevant step.
```

## 2026-09-20 · Add pinned dependency manifests

### Changed
- Added `requirements.txt` with the verified runtime pins `pygame==2.6.1` and `noise==1.2.2`.
- Added `requirements-dev.txt`, which includes the runtime file and pins `pytest==9.1.1`.
- Updated `README.md` and `docs/DEVELOPER_GUIDE.md` to install dependencies from the requirement files instead of individual package commands.
- Updated `STATUS.md` and `docs/IMPROVEMENT_PLAN.md` to record the completed P0 dependency task and the verified platform boundary.

### Why
- New developers need one repeatable install command for runtime packages and a separate command for development tools.
- The project must not imply support for platforms or Python versions that have not been tested.

### Verification
- Installed the development requirements in the project virtual environment.
- Ran `python -m pip check`: no broken requirements.
- Ran `python -m pytest --version`: `pytest 9.1.1`.
- Ran a temporary A* smoke test with pytest: `1 passed in 0.01s`.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- No gameplay or `src/` code changed.
- No committed test source was added; the temporary smoke test only verified the selected pytest installation.
- Next P0 task: make imports and startup testable by removing the circular import arrangement and moving runtime startup behind `main()`.

## 2026-09-20 · Add the development log

### Changed
- Added this append-only `docs/LOGS.md` file.
- Added links to the log from `README.md` and `STATUS.md`.

### Why
- Each future update needs a clear record of files changed, purpose, verification, and remaining scope.

### Verification
- Checked the Markdown links and confirmed the new log path resolves.

### Scope
- This change adds project documentation only. It does not alter gameplay or dependencies.

## 2026-09-20 · Make startup import-safe and normalize package imports

### Changed
- Reworked `src/rts.py` so `pygame.init()`, the display, fonts, menu rectangles, and the clock are created inside `main()`.
- Added the `if __name__ == "__main__":` guard and made `python -m src.rts` the supported launch command.
- Replaced wildcard and top-level source imports with explicit package-relative imports.
- Removed import-time Pygame initialization from `src/entities.py` and `src/utils.py`.
- Added `src/spawning.py` and moved enemy spawn-point selection and enemy construction out of `src/utils.py`.
- Removed the `sys.path` edit and the entity/helper circular import arrangement.
- Updated the README, developer guide, status, and improvement plan to describe the new startup and import behavior.

### Why
- Importing a game module should not open a window, create runtime UI objects, or enter the game loop. Tests and other tools need to import rules without starting a match.
- Loading entities under both `entities` and `src.entities` created distinct Python class identities. The package-only imports give the game one `Building` and `Unit` class identity.
- Spawning is game orchestration work. Keeping it in a helper that entities import created a cycle and made dependencies difficult to follow.

### Verification
- Imported `src.rts` in a fresh process and confirmed Pygame remained uninitialized.
- Confirmed `src.entities.Building` has one package identity and `src.spawning.spawn_enemies` imports from the dedicated module.
- Ran `python -m compileall -q src`.
- Ran a headless `main()` start/quit smoke test: menu start, gameplay entry, and Pygame shutdown passed.
- Ran a scripted headless gameplay smoke test: menu start, Barracks placement, Swordsman training, unit selection, right-click movement, and shutdown passed.
- Ran `git diff --check` successfully.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- This update does not implement the fixed simulation clock, game-state owner, asset loader, pathfinding repairs, or new gameplay features.
- Existing movement, placement, combat, terrain, and wave limitations remain documented in the developer guide and improvement plan.
- The next P0 task is to introduce the small game-state owner and fixed-step runner, then add committed import/startup regression tests.

## 2026-09-21 · Add match state, fixed timing, and shared asset loading

### Changed
- Added `src/game.py` with `GameState.new_match()` and an accumulator-based `FixedStepRunner`.
- Moved mutable match values such as resources, entity lists, wave timers, selection, and debug visibility into `GameState`; `constants.py` now contains configuration/content data rather than runtime loop flags.
- Added `src/assets.py` with repository-relative keyed image/font caching, injectable logging, diagnostics, and visible placeholders for missing files.
- Changed entity construction to receive preloaded image surfaces and shared fonts while retaining each asset key in model state.
- Changed terrain setup to receive preloaded tile surfaces and kept regenerated terrain references aligned between the generator and `GameState`.
- Updated `src/rts.py` to create a fresh match state, run simulation updates at a fixed 30 Hz, and use local menu/game flow flags.
- Added five committed P0 tests covering import safety, asset fallback/path resolution, fresh state isolation, fixed-step catch-up, and headless start/quit shutdown.
- Updated the README, status, improvement plan, and developer guide for the new runtime structure.

### Why
- A match should be restartable without leaking entities, balances, timers, or selection from a previous match.
- Simulation rules should not change speed when rendering stalls or the display rate varies.
- Asset loading should not depend on the current working directory or repeat filesystem/font work for every entity.
- Missing development art should be diagnosable without crashing startup.

### Verification
- `venv/bin/python -m pytest -q`: `5 passed`.
- `venv/bin/python -m compileall -q src tests`.
- `venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`.
- Headless manual smoke: menu start, gameplay entry, and window quit passed.
- Scripted headless gameplay smoke: Barracks placement and Swordsman training passed with the keyed asset loader.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- Navigation correctness, placement/spawn validation, combat range, finite match endings, pause, and terrain map validation remain P1/P2 work.
- PR #21 remains open; merge the startup/import branch before beginning the next gameplay phase.

## 2026-09-21 · Correct P0 developer-guide details

### Changed
- Updated the developer guide's asset-key instructions and terrain-regeneration section to match `AssetLoader`, `GameState`, and the fixed-step loop.
- Corrected the asset checklist numbering and removed stale claims that the working directory controls asset lookup or that terrain regeneration leaves the renderer reference stale.

### Why
- Developer documentation should describe the implemented P0 boundaries rather than the pre-refactor prototype.

### Verification
- Re-read the affected guide sections and ran `git diff --check`.

### Scope
- No source or gameplay rules changed. P1 navigation and placement repairs remain out of scope.

## 2026-09-21 · Refresh validation examples

### Changed
- Updated the developer guide's repair-order and headless terrain examples for the new `AssetLoader`/`GameState` boundaries.
- Marked the implemented P0 timing and runtime-test work without changing the remaining P1/P2 repair list.

### Why
- The validation instructions should be runnable against the current constructor signatures and should distinguish completed P0 work from future gameplay repairs.

### Verification
- Ran `venv/bin/python -m pytest -q`: `5 passed`.
- Re-read the updated example and ran `git diff --check`.

### Scope
- Documentation only; no source or gameplay rules changed.

## 2026-09-21 · Document committed test coverage

### Changed
- Updated the developer guide and improvement-plan structure table to list the committed P0 tests and the new `assets.py`/`game.py` boundaries.
- Removed stale statements that the repository had no committed test source.

### Why
- Setup and architecture documentation should point new contributors to the tests that now protect import safety, assets, state isolation, fixed timing, and shutdown.

### Verification
- Ran `venv/bin/python -m pytest -q`: `5 passed`.
- Ran `git diff --check`.

### Scope
- Documentation only; broader A*, movement, placement, combat, and match tests remain future work.

## 2026-09-21 · Add the P1 authoritative world model

### Changed
- Added `src/world.py` with stable `TerrainKind`/`TerrainTile` values, shared pixel/cell geometry helpers, occupancy-derived navigation, and `navigation_revision` tracking.
- Changed `TerrainGenerator` to produce stable terrain tiles and create a `World`; visual grass variants no longer define the water identity.
- Changed `GameState` and the controller to use one `World` for terrain rendering, placement checks, and navigation input.
- Reused the geometry helpers in placement previews and movement/building click conversion.
- Added `tests/test_p1_world.py` for terrain semantics, revision behavior, and coordinate conversion.
- Updated the developer guide, improvement plan, and status to mark the first P1 step complete.

### Why
- Rendering and pathfinding need one authoritative map. Missing or changed art must not alter which cells are water.
- Repeated pixel/cell arithmetic made boundary behavior easy to diverge between placement and movement.
- Units need a navigation revision before later P1 work can invalidate stale routes safely.

### Verification
- `venv/bin/python -m pytest -q`: `7 passed`.
- `venv/bin/python -m compileall -q src tests`.
- `venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`.
- Headless menu start/quit and scripted Barracks/Swordsman smoke checks passed after the world migration.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- A* correctness, obstacle-bypassing movement, order/target separation, placement/spawn validation, combat geometry, and dead-actor cleanup remain later P1 steps.
- This branch is stacked on the P0 state/assets update; review it after PRs #21 and #22.

## 2026-09-21 · Correct P1 A* routing

### Changed
- Replaced node-object A* results with coordinate-based `PathResult`/`PathStatus` values in `src/astar.py`.
- Added rectangular-grid and coordinate validation, explicit blocked-start/blocked-goal outcomes, octile movement costs and heuristic, stale heap-entry skipping, and diagonal corner-cutting prevention.
- Updated entity movement and right-click commands to consume coordinate paths, clear failed destinations, and remove the old direct movement fallback.
- Added `tests/test_p1_astar.py` for diagonal routes, already-there results, invalid/blocked inputs, corner cutting, and blocked-goal behavior.
- Updated the A* and movement sections of the developer guide and marked the P1 A* step complete in the plan/status files.

### Why
- The old search mixed an inadmissible Manhattan heuristic with diagonal movement, allowed units through blocked corners, and returned the same empty list for success and failure.
- Direct fallback movement could carry a unit through an obstacle after a failed route.
- Coordinate paths keep the pathfinder independent of rendering objects and make result handling testable.

### Verification
- `venv/bin/python -m pytest -q`: `12 passed`.
- `venv/bin/python -m compileall -q src tests`.
- `venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`.
- Headless scripted movement after Barracks/Swordsman training produced a coordinate path and advanced the unit without runtime errors.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- Navigation-revision route invalidation, residual waypoint movement, bounded retries, order/target separation, attack-position search, placement/spawn validation, and combat geometry remain later P1 steps.
- This branch is stacked on the P1 world-model update; review it after PR #23.

## 2026-09-21 · Make P1 route following safe

### Changed
- Added route revision tracking, bounded retry timing, and route storage helpers to `Unit`.
- Passed `World.navigation_revision` into allied/enemy updates so construction or destruction invalidates stored routes before movement.
- Removed the failed-route direct-movement fallback and consumed residual travel distance across multiple waypoints in one fixed update.
- Updated player move commands to store coordinate routes with their navigation revision.
- Added `tests/test_p1_movement.py` for residual waypoint travel, revision invalidation, and bounded failed-route retries.
- Updated the developer guide, improvement plan, and status to mark the route-safety P1 step complete.

### Why
- A unit must not cross an obstacle after its path fails or becomes stale.
- Consuming only one waypoint per update made movement speed depend on waypoint spacing and discarded available travel distance.
- Replanning every failed frame wastes CPU and makes unreachable targets noisy; a short retry delay gives the world time to change.

### Verification
- `venv/bin/python -m pytest -q`: `15 passed`.
- `venv/bin/python -m compileall -q src tests`.
- `venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`.
- Headless scripted movement after Barracks/Swordsman training passed with a coordinate path, route revision, and position advance.
- Verification environment: macOS 26.6.2 arm64, Python 3.12.13. Other platforms remain unverified.

### Scope
- Explicit Move/Chase/Attack intent, Stop/Hold behavior, attack-position search, placement/spawn validation, and combat geometry remain later P1 steps.
- This branch is stacked on the A* correctness update; review it after PR #24.