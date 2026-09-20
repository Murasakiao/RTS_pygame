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