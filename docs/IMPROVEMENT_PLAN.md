# Kingdom Conquer: improvement plan

**Date:** 2026-09-15<br>
**Status:** P0 implementation in progress<br>
**Chosen direction:** short, single-player base-defense RTS matches<br>
**First release target:** `v0.1`, a complete, replayable small game

The goal is a game where you can trust your orders, understand the next threat, and finish a match wanting another attempt. Keep Python, Pygame, tile-based terrain, and A*. Improve the existing prototype in small steps rather than replace it with another engine.

The user chose the base-defense direction. The detailed rules and numbers below are recommended starting points, not implemented behavior or proven balance. The [developer guide](DEVELOPER_GUIDE.md) describes the current code; this document describes the intended changes.

## Contents

1. [The first playable target](#1-the-first-playable-target)
2. [Current problems and their priorities](#2-current-problems-and-their-priorities)
3. [Rules to settle before adding features](#3-rules-to-settle-before-adding-features)
4. [Implementation phases](#4-implementation-phases)
5. [A small technical structure](#5-a-small-technical-structure)
6. [Testing and playtesting](#6-testing-and-playtesting)
7. [Later features and scope limits](#7-later-features-and-scope-limits)
8. [The first implementation session](#8-the-first-implementation-session)

## 1. The first playable target

### A match in plain language

You start with a Castle on safe ground and enough resources to train a small defense. During preparation, you place buildings and choose where your soldiers should stand. A warning shows where the next wave will enter.

During the fight, you reposition Swordsmen, protect Archers, and stop enemies reaching the Castle. Between waves, you replace losses, improve income, and decide whether to spend on a Castle repair. Clear the final wave to win. Lose the Castle and the match ends.

A short match gives us a useful test: can a new player build, command, fight, and understand the result without needing the developer beside them?

### Release scope

| Keep and improve | Add for `v0.1` | Leave for later |
|---|---|---|
| Perlin grass/water maps | Valid starting areas and announced spawn lanes | Large scrolling worlds, biomes, map editor |
| A* and waypoint movement | Reliable orders, group selection, distinct group destinations | Perfect formations, advanced crowd simulation |
| Existing building roles | Training queues, rally points, population capacity | Workers, resource deposits, technology tree |
| Swordsmen, Archers, Goblins, Orcs | Clear roles, local targeting, readable attacks | More factions, cavalry, bosses |
| Passive income | Useful production buildings and recovery choices | Trading, upkeep, complex supply systems |
| Menu and debug tools | Pause, finite waves, victory/defeat, retry, readable HUD | Save campaigns, multiplayer, full replays |

Keep construction instant for this release. A builder system would add travel, construction progress, and cancellation rules before it improves the core fight.

### Provisional playtest settings

These are knobs to test, not promises about the final game:

| Setting | Starting proposal | Reason |
|---|---|---|
| Match length | Aim for 8–12 minutes | Enough time for growth and several fights, short enough to retry |
| Waves | 8 finite waves | Give the player a visible finish line |
| Preparation | 60 simulation seconds | Time to learn the build/train controls |
| Intermission | 25 simulation seconds after a cleared wave; optional Start Early button | Allow recovery without forcing experienced players to wait |
| Starting base | One free, preplaced Castle; no replacement Castle | Establish the objective and avoid a lost first minute placing it |
| Starting resources | Gold 250, wood 150, stone 100, food 150 | At current prices, Barracks + two Swordsmen cost 220 gold, 20 wood, 15 stone, and 60 food |
| Population | Castle provides 4 slots; each House adds 4; hard cap 24 | Houses have a clear purpose and army size stays manageable |
| Training | Swordsman 8 seconds; Archer 10 seconds; queue length 5 per trainer | Give production a visible pace |
| Live enemies | Cap at 24; keep excess wave entries pending | Avoid sudden unbounded armies |
| First arena | Trial a 32 × 20 cell map with 16-pixel source tiles | Fit a readable battlefield and HUD on one screen |

The existing map is 48 × 36 cells and has different starting balances. Retain that configuration as a regression fixture when introducing the compact arena. If the trial arena feels cramped, adjust it with the display layout before adding a camera.

Do not change all combat stats at once. Fix movement and damage rules first, then tune the opening economy and enemy strength against these playtime targets.

## 2. Current problems and their priorities

These findings come from the current source and the earlier review. Each needs a regression case, not only a code edit. “Blocker” means it prevents trustworthy play or testing; “high” means it causes frequent confusion or invalid game state.

| ID | Priority | Current problem and player effect | Source | Main phase |
|---|---|---|---|---|
| B01 | Resolved in P0 | Mixed imports loaded two entity class identities; circular imports hid dependencies | `entities.py`, `utils.py`, `rts.py` imports | P0 |
| B02 | Resolved in P0 | Startup ran on import; menu buttons could be read before creation; menu time entered the first game tick | `rts.py` initialization/menu; import-time `pygame.init()` in helpers | P0 |
| B03 | Partly resolved in P1 | `World` now owns stable terrain/navigation semantics and live `T` regeneration is disabled; seeded-map connectivity and reserved starts remain | `TerrainGenerator`, `World`, match controls | P1, P2 |
| B04 | Resolved in P1 | A* now uses matching octile costs, blocks corner cutting, skips stale entries, validates inputs, and returns explicit statuses | `astar.py` | P1 |
| B05 | Partly resolved in P1 | Failed routes stop without direct fallback, consume residual waypoint travel, normalize fractional positions before A*, retry with a delay, and invalidate on navigation revisions; order/target intent is still coupled | `Unit.move_towards_target()`, right-click handler | P1 |
| B06 | Partly resolved in P1 | Rectangle-gap range, cell-based line of sight, and reachable candidate attack cells now support building approaches; full combat geometry remains | Unit movement/attack methods; main cleanup | P1 |
| B07 | Partly resolved in P1 | Shared `World.validate_footprint()` and `validate_connectivity()` now cover full bounds, terrain, actor occupancy, and living routes to Castle approach cells; shared atomic affordability/deduction covers costs; future spawn lanes, trainer connectivity, and transaction unification remain | `world.py`, `game.py`, placement handler and preview helpers | P1, P3 |
| B08 | Partly resolved in P1 | Training uses adjacent free exits and enemy waves use free walkable edge cells with a reachable attack-position check; protected lanes and pending blocked spawns remain | Training handler, `world.py`, `spawning.py` | P1, P2 |
| B09 | Partly resolved in P1 | Enemy priorities now load from data, Move/Attack/Hold intent is explicit, and unreachable attack routes retry with a delay; chase limits and full AI policy remain | `EnemyUnit`, target selection, order handling | P1, P4 |
| B10 | Partly resolved in P1 | Dead actors are skipped during updates, removed after the update phase, and stale target/selection references are cleared; reservation/accounting cleanup remains | `rts.py` update/cleanup blocks | P1 |
| B11 | High | Text overlaps or clips; HUD clicks reach the map; build mode can linger; input uses current mouse position instead of each click's position | `rts.py` events, UI helpers | P3 |
| B12 | Partly resolved in P0 | Shared image/font loading now has repository-relative lookup, diagnostics, and placeholders; movement diagnostics and final presentation cleanup remain | `assets.py`, object construction, movement prints | P0, P5 |

Current source: [`rts.py`](../src/rts.py), [`entities.py`](../src/entities.py), [`astar.py`](../src/astar.py), [`procedural.py`](../src/procedural.py), [`utils.py`](../src/utils.py), [`constants.py`](../src/constants.py).

**Design gaps, not necessarily code bugs:** no ending or restart, one-unit selection, instant training, people as a replenishing currency, and wave waits that increase from 30 to 60 to 90 seconds. The next sections deliberately replace those rules. Missing dependency metadata, tests, and code/art license records also need project work.

## 3. Rules to settle before adding features

These contracts prevent one fix from creating a different problem. A green placement outline, for example, should use the same rules as the final click.

### 3.1 One world and one game clock

- `World` owns terrain kinds, visual variants, dimensions, and derived walkability. Drawing and navigation read that same world.
- Use stable terrain kinds such as `GRASS` and `WATER`. Missing grass PNGs must not change which cells count as water.
- Separate map dimensions from the window. UI panels, resizing, and scaling must not change the world's cell count.
- Use a fixed simulation step of `1/30` second. Keep seconds inside simulation code; convert millisecond configuration values at a clear boundary during migration.
- Render with a frame cap. Bound catch-up work after a stall; after pause or a menu transition, reset the accumulator instead of simulating the time spent away.
- Auto-pause on focus loss and require a deliberate resume. Pause freezes income, orders, movement, combat, queues, waves, and gameplay-message lifetimes. Menus remain responsive. Reject new gameplay commands while paused.

A fixed tick makes “one second of attacks” testable without depending on how often the display redraws. It does not create network determinism or a replay system by itself.

Recommended tick order:

```text
Apply valid player commands and update affected walkability
    -> income and production progress
    -> choose targets and request routes
    -> move living actors
    -> resolve attacks in a stable order, skipping actors already dead
    -> remove dead objects and release their reservations
    -> check defeat, then advance wave/victory state
    -> render without changing gameplay state
```

Use stable entity IDs to break same-tick ties rather than giving all allies a separate first turn. This is a simple sequential combat rule, not simultaneous damage. Newly created actors should enter the next actor-update pass, not join an iteration already in progress.

### 3.2 Movement must obey the map

- Keep eight-direction movement. Choose one diagonal cost, preferably `sqrt(2)`, and use it in both step costs and the octile heuristic.
- A diagonal step requires both side cells to be walkable. Match that rule in connectivity tests.
- Return a path result with an explicit status: `FOUND`, `ALREADY_THERE`, `UNREACHABLE`, or `INVALID_INPUT`. A path contains cell coordinates, not rendering objects.
- Ordinary move orders do not silently turn a blocked goal into a different goal. Report blocked ground; stop affected units and clear the failed order's route/destination.
- Remove the direct-movement fallback. No route means no movement through terrain.
- Track a navigation revision. Placement, destruction, or a new map updates walkability immediately; units check the next segment and replan when needed.
- Spend the remaining travel distance across waypoints, skipping a starting waypoint already reached. Check the full movement segment so a large step cannot pass through a wall.
- Limit route requests per tick and throttle failed retries. Coalesce requests per unit so a new order replaces an older pending request. A waiting unit can stop; it must not continue along an invalid path.

For position conventions, keep building placement anchored to cells. Use floating-point unit centers and derive their rectangles from those centers. Convert cell goals to cell centers. Add geometry helpers before changing callers so half-tile offsets do not spread through the code.

Moving units should not become permanent A* walls. For the first release, use distinct group destinations and modest local avoidance. Temporary unit overlap in a narrow passage is acceptable; crossing terrain/buildings or settling an entire squad on one point is not. Full collision-free formations are outside this release.

### 3.3 Orders, targeting, and damage are separate jobs

Keep the player's order and final goal separate from the current path and next waypoint.

| Order | Intended behavior |
|---|---|
| Move | Go to the ground destination without breaking off to chase enemies; return to idle on arrival |
| Attack target | Pursue that living target while reachable; return to idle when it dies or the order fails |
| Attack-move | Travel toward a ground goal, engage nearby threats, then resume that goal |
| Stop / hold | Clear the route and stay in place; attack enemies already in range without chasing |
| Idle | Acquire enemies within a local detection radius; use a bounded chase distance and return if drawn too far away |

Local detection and chase limits govern automatic engagements. An explicit Attack Target order may pursue farther because the player asked for it. For Attack-move, return to the original ground goal after a target dies or exceeds the chase limit.

Enemies need a strategic order as well: advance toward the Castle from their spawn, even when it is outside detection range. Their type determines which nearby threats interrupt that advance; after the diversion, resume the Castle route. Otherwise a local-only AI could wait at the border forever.

Remember failed target searches briefly; retry when the target changes cells, navigation changes, or the retry timer expires. Otherwise select a reachable alternative rather than reacquiring the same unreachable target each frame.

Combat rules:

- Friendly fire is off. Validate that an attack target is a living opponent; a repair command is a separate action.
- Measure attack range as the shortest gap between combat rectangles, in world pixels. Touching rectangles have gap zero. Share the same range helper with attack-position selection.
- Generate walkable attack cells around the target's footprint, then find a reachable one. Do not choose a single “nearest empty cell” from inside a blocked building and assume the attacker can reach it.
- Use a simple grid line-of-sight check: buildings block attacks; water blocks walking but not sight. Exclude the attacker and intended target from their own obstruction checks. Test corner cases so melee cannot strike through a wall corner.
- Apply damage once per valid cooldown event. Start an attack cue from that event; do not let an animation or decorative arrow apply damage a second time.
- For `v0.1`, damage is immediate at the valid attack event. Arrows are visual feedback, not physical projectiles. Impact-time damage can be a later feature.
- Goblins prefer reachable buildings. Orcs prefer reachable allied units, falling back to buildings. Both eventually threaten the Castle if defenders are absent.

Changing from top-left distance to rectangle-gap distance changes balance. Retest ranges and unit matchups before deciding that an enemy needs more damage.

### 3.4 Placement and spawning cannot trap the match

Create one placement validator that returns success or a useful reason: outside map, water, occupied, insufficient resources, cooldown, reserved area, or blocked route. Recheck on commit using current state, even if the preview looked valid a frame earlier.

Validate the full footprint against terrain, buildings, and living actors. Trainers must retain an exit connected to the main playable land area, not merely an isolated empty neighbor. Pay once after validation; a failed command spends nothing.

For the first release, reject construction that cuts a reserved spawn lane or any living actor off from the Castle's melee approach area. Include future-wave lanes and use each team's movement permissions. Checking only the lanes could still trap an enemy already inside a side passage.

For this connectivity check, use terrain and building footprints, not temporary unit occupancy. Test routes to legal approach cells, not the Castle's blocked center. Destructible walls and siege behavior can replace the no-sealing rule later.

Mark protected entry strips on the map and exclude allied construction and movement from them. Otherwise, parking allies on all spawn cells could block a wave forever. Derive team-specific movement permissions from the same world; enemy entry cells are not ordinary allied move destinations.

Spawn only on valid, free land within the world. An occupied spawn cell delays creation or uses another validated cell in the same lane. Enemies must be able to leave the entry strip and attack a defender blocking its exit. Do not teleport an enemy through the defense, drop a wave entry, or mark it defeated because its spawn failed.

Training exits use a small ring outside the trainer footprint. If no cell is free, the finished unit waits in its queue with “Exit blocked” feedback. Never spawn it in water or search arbitrarily far away for a convenient empty cell.

### 3.5 A generated map must support the game

Use this pipeline:

```text
Seed + generator settings
    -> Perlin terrain kinds and grass variants
    -> clear a safe Castle/building area
    -> reserve at least two spawn lanes away from the Castle
    -> validate routes, exits, and space for initial construction
    -> accept map, retry within a limit, or use a known-good fallback
```

Start with these checks:

- Castle footprint on land, with room for two trainers and early economy buildings.
- At least two reserved entry lanes with reachable melee approach cells at the Castle.
- Main approaches at least two cells wide where practical, so small groups can pass.
- A useful connected land area; a pretty island that cannot support the opening build is a rejected map.
- A bounded generation attempt count, initially 32, followed by a deterministic, known-good fallback arena. No endless reroll loop.

Keep master seed, generator version, and settings in the match report. Use separate seeded random streams for terrain, wave composition, and cosmetic variation; adding a particle effect must not change the next wave. Derive seeds with a stable method, not Python's process-dependent string hash.

Same seed and rules should reproduce the map and wave schedule in the supported environment. This does not promise an identical battle without identical player inputs.

Offer seed entry, Copy Seed, Retry Same Map, and New Map through menus. Disable live terrain regeneration in a normal match. A new map starts a fresh match rather than leaving old units or paths on new terrain.

### 3.6 Finite waves and a clear ending

Use an explicit match flow:

```text
MENU -> PREPARATION -> WAVE -> INTERMISSION -> WAVE ... -> VICTORY
                         \                         \
                          +------ Castle lost ------> DEFEAT

PAUSED temporarily suspends any live-match state.
VICTORY / DEFEAT -> Retry Same Map, New Map, or Menu.
```

- A wave has a spawn queue and a count of living spawned enemies. It is clear only when **both are empty**.
- The enemy cap delays pending spawns; it never consumes them. Stage spawning with a configurable cadence rather than creating the whole wave on one frame.
- Show current wave, enemies remaining including pending entries, next-wave direction/type preview, and preparation/intermission countdown.
- Start the next wave after its intermission or a deliberate Start Early click. Do not reuse `interval * current_wave` or start another wave while enemies from this one remain.
- Pay a clear reward once per wave, using a wave ID to prevent duplicate rewards.
- After the final wave clears, win only if the Castle remains alive. Castle loss takes precedence if both conditions occur on the same tick.
- Victory and defeat freeze simulation and cancel pending gameplay input. Retry resets entities, IDs, queues, reservations, timers, selection, RNG streams, map state, and messages.

A lane with no progress for several seconds should create a diagnostic and trigger limited replanning. A persistent unreachable wave is a failed test. Do not hide it by granting victory or making enemies phase through buildings.

### 3.7 Economy, population, and production

Keep passive gold, wood, stone, and food for the first release. Put balances, costs, and building production data in one place. Use a `cost` resource dictionary for both units and buildings; migrate the current building `resources` field and discard its unused scalar `cost`. Reject unknown resource keys and negative costs instead of falling back to gold.

Replace spendable `people` with population:

```text
population_used     = population of living allied units
population_reserved = population committed to unspawned queue entries
population_cap      = min(24, Castle capacity + capacity from living Houses)

A new queue entry is allowed only if:
used + reserved + new_unit_population <= cap
```

Queue policy:

1. Check resources, capacity, queue length, and trainer type when enqueueing. Deduct costs and reserve population once.
2. Train one entry at a time per building, oldest first. Show progress and remaining entries; a finished entry waiting for an exit holds up that queue.
3. On spawn, transfer reserved population to used population. Check that the unit still fits the current capacity and that an exit is free.
4. If a House is destroyed, keep existing units alive. Finished entries wait if they no longer fit; reject additional orders that exceed the new cap.
5. Let the player cancel any unspawned entry for a full resource refund and reservation release. On trainer destruction, apply that same policy to its remaining entries, exactly once.
6. A dead unit releases used population without refunding its purchase price.

Display live, queued, and maximum population so “population full” is explainable. Queue cancellation and continued baseline income give the player a recovery path after losing a House or blocking an exit.

Building roles remain small and readable:

- **Castle:** objective and baseline income/capacity.
- **House:** population capacity, replacing its tiny current people-income bonus.
- **Market / Farm / LumberMill / Quarry:** produce their named resources. Store production in data and show the actual gain per second.
- **Barracks:** Swordsmen.
- **Archery Range:** rename the player-facing Stable role to match the Archers it trains; a data ID and art change should be deliberate, not silently inferred from a filename.

During balance work, add one Castle repair purchase per intermission: initially 30 gold + 10 stone for 20% of maximum HP, clamped at full health. Disable it while a wave is active or the Castle is undamaged. The numbers are provisional; the point is a visible recovery choice that competes with buying defenders.

### 3.8 Controls and readable feedback

Keep the whole first arena visible. A reference layout is a 640 × 360 logical canvas: 512 × 320 battlefield, 40-pixel top strip, and 128-pixel sidebar. At 2× scale this becomes a 1280 × 720 window with 32-pixel displayed tiles. Confirm fit on the test machine before locking the layout.

Use one screen-to-world conversion, including scaling and letterboxing. HUD and letterbox clicks must never place buildings or order units.

| Input | Proposed behavior |
|---|---|
| Left-click ally | Select it |
| Left-click empty ground | Clear selection when no cursor mode is active |
| Drag on the battlefield | Select allied units in the box |
| Shift-click ally | Toggle that ally's selection |
| Shift-drag | Add boxed allies without clearing the current selection; no queued movement orders yet |
| Left-click building | Select it and show actions; do not train from the selection click |
| Train button | Add one queue entry if allowed |
| Right-click ground with units selected | Move the group to separate reachable cells around the clicked point |
| Right-click enemy with units selected | Attack that target |
| Right-click ground with a trainer selected | Set a valid rally point |
| `A`, then left-click ground | Attack-move with selected units |
| `S` | Stop selected units and hold position |
| `1` | Select the existing Castle |
| `2`–`8` | Choose the current House-to-Quarry building types, preserving their order |
| Right-click / `Esc` in a placement or attack-move cursor mode | Cancel that mode without issuing another order |
| `Esc` otherwise | Toggle pause |
| `D` | Toggle debug overlay; no unconditional console dump |

Start a new match with the Castle selected and no placement cursor. Order dispatch must consume each input once: modal UI first, then active cursor mode, then selection or world commands. Use `event.pos` for clicks and a drag threshold to distinguish a click from a selection box.

Give invalid actions a short reason. Use selection outlines, destination markers, health bars, queue progress, and visible spawn warnings. Do not require color or sound alone to communicate a threat. Remove constant HP text and combat-message spam from ordinary play; keep detailed diagnostics behind debug mode.

## 4. Implementation phases

Work on one phase at a time. Each phase should leave a runnable game and a short demo. A checked box means its acceptance tests pass, not merely that code exists.

No calendar estimates yet: the import and navigation fixes will show how much refactoring the prototype needs. Split a task that crosses several systems into small changes with passing tests rather than scheduling a large rewrite.

### P0. Make the game safe to change

**Player/developer benefit:** the game starts reliably, and tests can inspect rules without opening a menu.

**Depends on:** none. Fixes B01, B02, and the startup portion of B12.

- [x] Add runtime dependency pins based on the verified environment and a separate development dependency file with a tested pytest version. `requirements.txt` and `requirements-dev.txt` are verified on macOS 26.6.2 arm64 with Python 3.12.13; `pytest==9.1.1` passed a temporary A* smoke test. Other platforms remain unverified.
- [x] Put startup behind `main()`; initialize Pygame, display, fonts, menu rectangles, and the clock at runtime.
- [x] Keep `src/` as the package for now. Use explicit package-relative imports and remove wildcard imports and `sys.path` edits. Move spawning into `src/spawning.py` so entities no longer depend on a helper that imports entities back.
- [x] Introduce `src.game.GameState` and `FixedStepRunner`. `create_match()` builds fresh lists, timers, resources, terrain, and navigation state; runtime flags no longer live in `constants.py`.
- [x] Resolve asset paths from the repository/module location with `src.assets.AssetLoader`. Shared images/fonts are cached before they are passed into rule objects; entities retain asset keys. Missing files produce logger diagnostics and visible development placeholders.
- [x] Add committed import, startup, asset, and timing smoke tests in `tests/test_p0_runtime.py`. Diagnostics use an injectable logger and remain quiet when all assets exist.

**Exit checks:** import the model/path modules without creating a window or entering a loop; assert one `Building`/`Unit` class identity; wait in the menu for 60 seconds without gaining resources; close from the first menu frame without an exception; exercise missing assets without an unexplained traceback.

**Launch migration:** complete. Use `python -m src.rts` from the repository root. The direct script command `python src/rts.py` is no longer supported because the source now uses package-relative imports.

### P1. Make movement, placement, and damage trustworthy

**Player benefit:** soldiers obey the map, clicks do what they show, and melee can hit a building it has reached.

**Depends on:** P0. Use small hand-authored fixtures before random maps. Fixes B03–B10 at the rule level.

- [x] Introduce `src.world.World`, stable `TerrainKind`/`TerrainTile` values, shared geometry helpers, and a navigation revision that changes only when walkability changes.
- [x] Correct A*: use octile costs/heuristic, reject diagonal corner cutting, skip stale heap entries, validate inputs, and return explicit `PathResult` statuses. Attack-position candidate search remains part of the later combat step.
- [x] Remove obstacle-bypassing motion, reuse routes, consume residual waypoint travel, normalize float pixel positions to integer cells, and limit failed-route retries. Store the world navigation revision with each route and invalidate it after walkability changes.
- [x] Separate `UnitOrder` intent from current targets and waypoints. Implement single-unit Move, Attack, and Hold/Stop behavior before group controls.
- [x] Add `World.validate_footprint()` plus valid trainer exits and target-reachable free edge spawn-cell selection. Shared `can_afford()`/`deduct_cost()` helpers now validate and apply costs atomically. Proposed construction now rejects buildings that disconnect living actors from Castle approach cells, surround trainers, or reduce reachable future entry edges below two; successful construction updates costs and navigation together. Protected entry strips, transaction unification, and pending spawn accounting remain.
- [x] Share rectangle-gap attack range and cell-based line of sight between targeting and damage, search reachable attack-position candidates, load enemy priorities from data, and bound unreachable-target retries. Projectile/cover geometry remains a later refinement.
- [x] Move cleanup out of drawing. Dead actors are skipped during updates, removed after the update phase, and dead target/order/selection references are cleared. Population and reservation accounting remain later match-state work.

**Exit checks:** no movement through water, buildings, or blocked diagonal corners; no movement on a failed route; the start-equals-goal case succeeds without an error message; a building placed across a route forces a safe replan; Goblin and Orc can damage both a 1 × 1 building and the 2 × 2 Castle from legal cells; killing a selected unit leaves no ghost selection.

**Demo:** one Swordsman routes around a pond, changes route after construction, and fights an enemy beside a Castle. Debug shows one reason for each repath, not duplicate requests.

### P2. Complete one match from start to finish

**Player benefit:** there is a fair starting position, a goal, an ending, and a fast retry.

**Depends on:** P1. Completes the map/spawn portions of B03/B08 and introduces the match loop. Use the existing single-unit controls and temporary training flow here; P3 replaces them before full-match balancing.

- [ ] Validate seeded maps and add reserved Castle/building space, spawn lanes, bounded retries, and a fallback arena.
- [ ] Reject construction that seals lanes, isolates living actors, or encloses trainers using current world rules. Living-actor routes, trainer exits, and a two-edge future-lane minimum are implemented; protected strips and full generated-map rules remain.
- [ ] Preplace the Castle, apply opening resources, and add preparation, wave, intermission, victory, defeat, and pause states.
- [ ] Track pending spawns separately from living enemies. Add finite wave definitions, protected entry strips, cap-aware staged spawning, countdowns, and lane warnings. Give spawned enemies their default Castle-advance order.
- [ ] Add wave-clear rewards with exactly-once accounting. Start with simple scripted wave compositions; sophisticated selection is unnecessary here.
- [ ] Implement Retry Same Map, New Map, and Return to Menu. Disable live `T` regeneration.

**Exit checks:** a harmless fixture can win after its final enemy; losing the Castle ends a match; pending spawns prevent premature victory; a blocked spawn retains its queue entry; pause freezes all gameplay timers; five retries leave no old units, money, timers, selections, or messages.

**Demo:** a complete short fixture match with two waves. The full eight-wave configuration can exist, but do not spend hours balancing it yet.

### P3. Make a small army comfortable to control

**Player benefit:** build and train without accidental actions, see why an action failed, and command several soldiers at once.

**Depends on:** P2 and P1 order/geometry contracts. Fixes B11 and replaces instant training/people currency.

- [ ] Separate the battlefield, top HUD, and action panel; implement scaling and one coordinate conversion path.
- [ ] Add box selection, Shift selection, group Move/Attack, Attack-move, Stop/Hold, and distinct destination cells.
- [ ] Assign nearby reachable destinations per unit. A failed member stops and contributes to one group feedback message; do not hide partial success.
- [ ] Separate building selection from training. Add queue buttons, progress, cancellation, and rally markers.
- [ ] Replace people currency with used/reserved/capacity accounting and apply the queue policies above.
- [ ] Show costs, income rates, population, Castle HP, wave status, and contextual failure reasons. Keep pause/help accessible.
- [ ] Add destination/attack markers and compact health bars; separate normal feedback from debug output.

**Exit checks:** HUD clicks never affect the world; the same cell is selected at supported scales; a group spreads around its goal; move orders do not become unintended chases; queued units never spend twice or spawn off-map; house/trainer destruction and queue cancellation keep resources and population consistent.

**Demo:** build a trainer, queue three soldiers, set a rally point, select the group, attack-move to a lane, and stop them there using only the visible controls.

### P4. Tune the fights and the choices

**Player benefit:** the first waves teach, later waves challenge, and buildings and units have reasons to exist.

**Depends on:** P3. Revisit B09 after controls and pathfinding are stable.

- [ ] Tune Swordsmen as front-line defenders and Archers as fragile ranged support. Verify that a mixed army is useful and that free kiting is not the only winning tactic.
- [ ] Tune Goblins as lighter building threats and Orcs as tougher unit threats. Introduce the second enemy type after the opening waves; show the change in the wave preview.
- [ ] Define wave strength with a budget instead of multiplying raw count. Trial budgets `[2, 3, 5, 7, 10, 13, 16, 20]`, with Goblin weight 1 and Orc weight 3. These are starting values, not measured difficulty.
- [ ] Constrain wave composition and lanes by stage. Early waves should not surprise a beginner from every side. Keep enemy HP/damage readable rather than multiplying all stats each wave.
- [ ] Tune starting stocks, building production, unit costs, clear rewards, and training times together. Do not fix a pathing failure by making enemies weaker.
- [ ] Add the intermission Castle repair purchase and expose its cost/healing before confirmation.
- [ ] Add a brief first-match objective prompt and context hints. End with a summary: outcome, wave reached, time, seed, Castle HP, units trained/lost, and enemies defeated.

**Exit checks:** a new player can produce a first defender within 15 seconds and a small defense before wave one; an income building has a useful payoff within the match; players can explain their defeat; both an army-first and an economy-first opening can win with competent play on the fixed test seeds.

Start with Normal difficulty. An Easy preset is useful if newcomer tests demand it, but do not build a large difficulty system before tuning one mode.

### P5. Make the result readable and shareable

**Player benefit:** actions feel responsive, sound and visuals agree with the rules, and another person can launch the game.

**Depends on:** P4. Completes B12 and release hygiene.

- [ ] Add attack flashes, hit/death cues, and decorative arrows driven by combat events. Keep effects short; avoid hiding units under particles.
- [ ] Add brief build/train/wave/hit sounds with volume controls and mute. Audio-device failure must not prevent play. Use only verified or self-made assets.
- [ ] Improve selection contrast, hover/tooltips, text layout, and warning icons. Ensure critical information remains available without sound or color alone.
- [ ] Profile the capped-army scenario. Cache terrain/overlays by revision and images/fonts by asset key. Add spatial lookup only if measurements justify it.
- [ ] Record code ownership/license intent and art/audio provenance. Replace assets whose redistribution rights cannot be established; development placeholders are acceptable until then.
- [ ] Test a fresh environment on the primary development platform. Add Windows/Linux smoke coverage where available and label untested platforms honestly.
- [ ] Update setup instructions, controls, screenshots, known issues, and dependency metadata to match the implemented release. Remove tracked caches/scratch artifacts in a separate reviewed cleanup.

**Exit checks:** finish the release checklist below. A source release with a reliable setup is enough; a standalone executable is a later packaging task unless installation testing shows it is necessary.

## 5. A small technical structure

The present project has about 1,700 lines of Python. It does not need an entity-component framework, plugin architecture, or generic event bus to reach `v0.1`.

Grow these boundaries only as the phases need them:

| Area | Responsibility | Starting point |
|---|---|---|
| `rts.py` | Entry point, Pygame lifetime, commands, and rendering | Existing initialization and menu bootstrap |
| `game.py` | Match state and fixed simulation tick | `GameState` and `FixedStepRunner` introduced in P0 |
| `world.py` | Terrain, bounds, occupancy, revision, placement and spawn validation | Stable terrain kinds, geometry helpers, and navigation revision introduced in P1 |
| `entities.py` | Buildings/units and their runtime state/behavior | Existing classes, without import-time initialization |
| `spawning.py` | Enemy spawn-point selection and enemy construction | Moved out of `utils.py` during P0 |
| `astar.py` | Pure route search and explicit path results | Octile A*, validated inputs, stale-entry handling, and no-corner-cutting search implemented in P1 |
| `procedural.py` | Seeded terrain generation, independent of image loading | Existing noise sampling |
| `economy.py` | Balances, production, population, queue transactions | Resource and training blocks |
| `waves.py` | Wave definitions, pending spawn schedule, lane selection | Timer and spawn helpers |
| `ui.py` / `assets.py` | Input routing, rendering, asset paths/cache, normal/debug feedback | Drawing helpers and the shared `AssetLoader` introduced in P0 |
| `constants.py` | Validated configuration and content data, no mutable match state | Existing tables |
| `tests/` | Small pure-rule fixtures plus headless integration checks | P0 runtime smoke tests committed; broader rule fixtures remain |

These paths are proposed destinations, not files to create empty at the start. Keep related functions together until moving them removes a real dependency.

Dependency rule: the entry/controller can call the world, entities, UI, and assets. Terrain generation and A* must not import UI or start Pygame. UI can submit commands, but it must not subtract resources or delete entities while drawing. Avoid the current `entities -> utils -> entities` cycle.

A command can begin as a small function call or record: `Build`, `Train`, `CancelTraining`, `Move`, or `Attack`. A shared validator and one mutation point are enough; do not build a generic command framework before it is needed.

For combat presentation, pass simple events such as `AttackLanded` or `UnitDied` to the renderer/audio layer. The simulation owns HP. Turning sound off or skipping an animation must not change the battle.

## 6. Testing and playtesting

### Automated checks to add

Use pytest for rules and SDL dummy video/audio for headless integration. Add tests with the fixes, not after the full feature pass. Regression tests should describe intended behavior; a current bug must not become the expected result forever.

| Area | Required cases |
|---|---|
| Startup/imports | No window or loop on import; one entity class identity; close on first menu frame; missing assets; installed versions |
| Time | Menu wait, pause/resume, focus loss, long frame, equivalent elapsed simulation time under different rendering rates |
| A* | Open/blocked grids, start equals goal, invalid/negative coordinates, blocked start/goal, unreachable goal, no diagonal corner cutting, repeated requests |
| Route quality | Compare route cost with Dijkstra using identical steps/obstacles; check returned segments and goal-set behavior |
| Movement | Failed order stays stopped; route blocked mid-travel; waypoint residual distance; no wall crossing at large steps; newest pending order wins; bounded replans; allied entry-strip exclusion |
| Placement | All footprint cells, edges, units/enemies, cooldown/cost changes, same-tick multiple commands, current/future lane sealing, actor isolation, connected trainer exits |
| Terrain | Stable kinds independent of assets; seed/version repeatability; display and walkability agree; bounded retries/fallback |
| Combat | Melee against both building sizes, range boundaries, sight across water/behind buildings, cooldown, friendly-fire rejection, priorities, bounded diversions, Castle advance without visible defenders, unreachable targets, no dead actor attacks |
| Economy/queues | Invalid costs, insufficient funds, exactly-once charge/refund, capacity loss, cancellation, trainer death, blocked exit, population release on death, repair limits/price/HP clamp |
| Match | Pending spawns prevent clear/victory; cap/backpressure; reward once; Castle/final-enemy death tie; pause; complete restart |
| Controls/UI | Click versus drag; Shift rules; modal/cancel precedence; group partial failure; screen/world conversion; HUD never issues world commands |

**Map batch:** validate seeds `0..99` with fixed settings, plus a few hand-authored failure maps. Record fallback frequency as well as success. A generator that passes only by returning the fallback most of the time still needs improvement.

**Performance fixture:** target sustained 30 FPS with up to 24 allies, 24 live enemies, roughly 20 buildings, active path requests, and debug off. Measure update/draw work separately from frame-cap sleep; a starting budget is p95 work below 25 ms on the recorded test machine. These are targets, not existing benchmark results.

Capture frame time, path requests per second, route failures/retries, blocked spawn duration, and live/pending counts. Prefer counters and a toggleable overlay over prints from every soldier.

### Human playtest loop

After each phase, replay the same short scenario. After P4, test full matches on at least three fixed seeds, then unfamiliar seeds. Ask a few people who did not write the code to try the opening without coaching.

Record:

```text
Build/version and seed:
Tester familiarity:
Time to first trained unit:
Wave reached / win or loss / match duration:
Command that behaved unexpectedly:
Action whose cost or result was unclear:
Longest period with nothing useful to do:
What caused the loss, in the player's words:
Would they try another match, and why?
```

Change one category at a time: command reliability, pacing, economy, or enemy strength. A loss caused by an ignored order is a bug report, not evidence that the difficulty is good.

### Release checklist

- [ ] All in-scope blocker/high-priority defects above are resolved with passing regression tests; no obstacle-bypassing movement remains.
- [ ] A new player can build, train, select, move, stop, and identify the Castle objective through the UI.
- [ ] Eight waves can complete without unreachable enemies, lost pending spawns, or a timer deadlock.
- [ ] Both victory and defeat lead to working same-map retry and new-map flows.
- [ ] Pause never advances gameplay, and five consecutive retries retain no prior-match state.
- [ ] Group movement, queue cancellation, population loss, and trainer destruction have regression coverage.
- [ ] Seed-batch validation and the capped-army performance fixture pass on a recorded environment.
- [ ] Text fits; input maps correctly at supported scales; critical warnings work with sound muted.
- [ ] Installation instructions work in a fresh environment on each platform claimed as supported.
- [ ] Code license and shipped art/audio permissions are documented; unclear assets are replaced before redistribution.
- [ ] The developer guide and status describe implemented behavior, not this plan's uncompleted promises.

## 7. Later features and scope limits

Choose one next feature after `v0.1` playtests, based on a reported need.

| Candidate | Player benefit | Prerequisites / reason to wait |
|---|---|---|
| Control groups and queued orders | Faster army control | Stable multi-selection; resolve conflicts with `1`–`8` building keys first |
| Walls, gates, and one defensive tower | More base-layout decisions | Siege/obstruction targeting and tests that replace the no-sealing rule |
| A branching unit/building upgrade | A meaningful mid-match choice | Stable economy and proof the current choices are too shallow |
| Workers and deposits | More economic planning | A separate design pass for gathering orders, carrying, delivery, depletion, and terrain placement |
| Larger maps, camera, minimap | More positioning and exploration | Reliable screen/world conversion, map validation, and profiling |
| New biome or terrain cost | More map variety | Clear visual distinction and a heuristic valid for the new traversal costs |
| Cavalry, a new enemy, or a boss | More tactical variety | Existing roles and wave budgets must already be understandable and balanced |
| Save/load | Resume longer games | A versioned state format covering IDs, RNG state, queues, orders, waves, and time; short matches reduce the need |
| Physical projectiles | Dodging and impact timing | A deliberate damage-model change, with target-death and collision tests |
| Standalone builds | Easier installation | Verified source setup, native dependency packaging, asset paths, and redistribution rights |

**Outside the near-term plan:** multiplayer, campaigns, several factions, procedural quest systems, mod support, and an engine rewrite. Each could consume more effort than finishing the current game loop.

Scope rule: a new unit should answer a tactical need that the existing four types cannot cover. An unused knight PNG alone is not a reason to add cavalry.

## 8. The first implementation session

The first P0 checklist item is complete. The manifests pin `pygame==2.6.1`, `noise==1.2.2`, and the tested development runner `pytest==9.1.1`; no compatibility claim extends beyond the verified macOS arm64/Python 3.12.13 environment.

Start the remaining P0 work with a narrow patch rather than touching combat balance and imports together.

1. Record the current working launch, dependency versions, and a headless startup check. Keep unrelated local edits out of the implementation change. The dependency versions are now recorded in the two requirements files.
2. Reproduce the duplicate `entities` / `src.entities` identity and import-time startup in small checks. **Done:** the current package import test now exposes one `src.entities` identity and importing `src.rts` does not initialize Pygame.
3. Break the entity/utility cycle, adopt one import style, and put startup behind `main()`. **Done:** spawning moved to `src/spawning.py`, startup is guarded, and the module launch works.
4. Confirm module imports do not start the game, then verify menu start/exit with the new launch command. **Done:** headless start/quit smoke test passed.
5. Update launch documentation and add the regression tests. **Partly done:** launch documentation is updated; committed regression tests remain part of the next P0 task.

The next patches should handle the fixed simulation clock/state owner, asset loader, and committed smoke tests before P1. Mark progress and attach test evidence to this document as work happens. Retain the workspace's dormant status until gameplay development is actually resumed; planning alone does not start a new active project.
