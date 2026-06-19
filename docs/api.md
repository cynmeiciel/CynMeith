# CynMeith API Reference

This page is a concise reference for the core public surface.

For learning flow and architecture rationale, start from [docs/index.md](index.md).

## Package Exports

`cynmeith` exports the following public surface, grouped by role:

| Category | Names |
| --- | --- |
| Core | `Board`, `BoardSimulation`, `Config`, `ConfigError`, `Game`, `GameOutcome` |
| State | `Piece`, `PieceFactory`, `MoveHistory` |
| Rules | `MoveManager`, `RoyalSafetyMoveManager`, `RoyalRuleset` |
| Effects | `MoveEffect`, `RemovePieceEffect`, `MovePieceEffect`, `PromotePieceEffect`, `PlacePieceEffect`, `EffectPresets` |
| Turn policies | `TurnPolicy`, `FreeTurnPolicy`, `QuotaTurnPolicy` |
| Win conditions | `WinCondition`, `EliminatePieceCondition`, `ReachSquareCondition`, `NoLegalMovesCondition`, `MoveLimitDrawCondition`, `RoyalCheckmateCondition`, `RoyalStalemateCondition` |
| Phase systems | `PhaseSystem`, `StaticPhaseSystem`, `TurnCountPhaseSystem`, `TwoStagePhaseSystem` |
| Resource systems | `ResourceSystem`, `ActionPointSystem` |
| Scoring systems | `ScoringSystem`, `PieceCountScoringSystem`, `MaterialScoreSystem` |

`cynmeith.utils` is also exported as a submodule (`Coord`, `Move`, FEN helpers, type aliases).

## Config

`Config(source)` accepts:

- a file path (`str` or `Path`) pointing to YAML
- a mapping (`Mapping[str, Any]`)
- an existing `Config`

Convenience constructors:

- `Config.from_file(path)`
- `Config.from_data(mapping)`

Invalid config shapes raise `ConfigError`.

Main fields:

- `pieces`
- `width`
- `height`
- `fen`

Piece helpers:

- `get_piece_path(piece_name)`
- `get_piece_symbol(piece_name)`

## PieceFactory

`PieceFactory()` builds `Piece` instances from registered symbols. `Board`
creates and owns one internally, so most users never construct it directly.

Important methods:

- `register_pieces(config)`: load piece classes/symbols from a `Config`.
- `register_piece(...)` / `unregister_piece(symbol)`: manage individual entries.
- `create_piece(symbol, position)`: build a piece by symbol. Side is inferred
  from case (uppercase = first side, lowercase = second side).

You only need it directly when writing tooling that constructs pieces outside a
`Board`.

## Board

`Board(config, move_manager=MoveManager, move_history=MoveHistory)` owns board state and primitive piece operations.

Important methods:

- `move(start, end, move_type="", extra_info=None)`
- `get_valid_moves(piece)`
- `reset()`
- `clear()`
- `at(position)` / `set_at(position, piece)`
- `is_in_bounds(position)`
- `is_empty(position)`
- `is_empty_line(start, end, criteria=Coord.is_omnidirectional)`
- `is_enemy(position, side)` / `is_allied(position, side)`

Iteration helpers:

- `iter_positions()`, `iter_enumerate(...)`
- `iter_positions_line(...)`, `iter_enumerate_line(...)`
- `iter_positions_towards(...)`, `iter_enumerate_towards(...)`

Notes:

- `Board` delegates validation/resolution to `MoveManager`.
- `_apply_move(...)` is the low-level primitive used by managers/effects.

## Game

`Game(config, move_manager=MoveManager, move_history=MoveHistory, turn_policy=None, phase_system=None, resource_system=None, scoring_system=None, win_conditions=None, max_history=None)` orchestrates gameplay with turn control and optional game-level systems.

`config` may be a `Config`, a path (`str`), or a mapping; it is wrapped in a `Config` automatically. `max_history` caps how many moves are retained for undo (`None` means unbounded).

Important methods:

- `can_move(start, end, move_type="", extra_info=None) -> bool`
- `move(start, end, move_type="", extra_info=None)`
- `get_valid_moves(piece)`
- `reset()`
- `undo_move()`
- `redo_move()`
- `get_scores()`

Properties:

- `current_side`
- `current_phase`
- `outcome`
- `is_over`
- `max_history`

Notes:

- `Game` wraps `Board` and snapshots turn state, phase state, resource state, scoring state, and outcome together for undo/redo.
- `can_move(...)` returns `False` for invalid or out-of-bounds coordinates.
- `can_move(...)` also returns `False` once the game is over.

## Turn Policies

Base class: `TurnPolicy`

Required methods for custom policy:

- `can_move(game, piece, move) -> bool`
- `after_move(game, piece, move) -> None`
- `reset() -> None`
- `snapshot() -> Any`
- `restore(snapshot) -> None`
- `current_side` property

Provided implementations:

- `FreeTurnPolicy`: no side restriction.
- `QuotaTurnPolicy(moves_per_turn=1, starting_side=True)`: side switches after fixed quota.

## Game-Level Systems

`GameOutcome(winner, kind, reason)` represents a terminal result.

Base hooks:

- `WinCondition.evaluate(game) -> GameOutcome | None`
- `PhaseSystem.can_move(game, piece, move) -> bool`
- `PhaseSystem.after_move(game, piece, move) -> None`
- `PhaseSystem.current_phase`
- `ResourceSystem.can_move(game, piece, move) -> bool`
- `ResourceSystem.after_move(game, piece, move) -> None`
- `ScoringSystem.get_scores(game) -> Mapping[Side2, int]`

`PhaseSystem`, `ResourceSystem`, and `ScoringSystem` also support:

- `reset()`
- `snapshot()`
- `restore(snapshot)`

Built-in win conditions:

- `EliminatePieceCondition(piece_symbol, side=None, winner=None, kind="win", reason=None)`
- `ReachSquareCondition(side, target, piece_symbol=None, winner=None, kind="win", reason=None)`
- `NoLegalMovesCondition(side=None, winner=None, kind="win", reason=None)`
- `MoveLimitDrawCondition(move_limit, kind="draw", winner=None, reason=None)`
- `RoyalCheckmateCondition(royal_rules, kind="win", reason=None)`
- `RoyalStalemateCondition(royal_rules, kind="draw", winner=None, reason=None)`

Royal-safety helpers:

- `RoyalRuleset(royal_symbol)`
- `RoyalSafetyMoveManager`
- `BoardSimulation`

Typical use:

- make a `RoyalRuleset` subclass that knows how to detect attacks
- make your manager inherit `RoyalSafetyMoveManager`
- use `RoyalCheckmateCondition` / `RoyalStalemateCondition` as win conditions

Built-in phase systems:

- `StaticPhaseSystem(phase="main")`
- `TurnCountPhaseSystem(schedule, initial_phase="opening")`
- `TwoStagePhaseSystem(switch_after_moves, opening_phase="opening", later_phase="battle")`

Built-in resource systems:

- `ActionPointSystem(points_per_turn=1, starting_side=True)`

Built-in scoring systems:

- `PieceCountScoringSystem()`
- `MaterialScoreSystem(piece_values, default_value=0)`

## MoveManager

`MoveManager(board)` is the extension point for game-specific rules.

Core pipeline:

- `validate_move(move) -> bool`
- `resolve_move(move) -> Move | None`
- `apply_move(move, piece) -> None`

Default behavior:

- `resolve_move` validates and returns the same move.
- `apply_move` applies actor move, executes effects, then records history snapshot.

## Move Effects

Base class: `MoveEffect`

Built-ins:

- `RemovePieceEffect(position)`
- `MovePieceEffect(start, end)`
- `PromotePieceEffect(symbol, position=None)`
- `PlacePieceEffect(symbol, side=None, position=None)`

Builders:

- `EffectPresets.capture(position)`
- `EffectPresets.captures(*positions)`
- `EffectPresets.relocate(start, end)`
- `EffectPresets.promote(symbol, position=None)`
- `EffectPresets.drop(symbol, side=None, position=None)`

Effects are normally attached via `Move.extra_info[MoveKeys.EFFECTS]` in `resolve_move`.

For input-driven effects (such as chess promotion choice), required metadata should be included in `Move.extra_info` by the caller or UI flow.

## Piece

Base class: `Piece(side, position)`

Contract:

- implement `is_valid_move(new_position, board)`
- optional optimization: override `iter_move_candidates(board)`
- update internal state (if needed): override `move(new_position)`

Recommended pattern for sliding pieces:

- iterate with `Board.iter_positions_towards(start, direction)`
- stop when first blocker is reached

`get_valid_moves(board)` filters candidates through `is_valid_move`.

## Move History

`MoveHistory(board, max_history=None)` records moves for undo/redo. State is
stored as per-move deltas against a baseline grid rather than full snapshots, so
full board states are materialized lazily only when requested.

Important methods:

- `seed_current_state()`
- `record_move(move)`
- `undo_move()`
- `redo_move()`
- `clear()`
- `set_max_history(max_history)`

Counters/stacks:

- `num_moves`
- `move_stack`, `redo_stack` (the `Move` objects)
- `state_stack` (a lazy view that materializes board states on access)
- `max_history` (cap on retained moves; `None` means unbounded)

Note: `Game` sets `max_history` on its `MoveHistory` from the `Game(max_history=...)`
argument.

## Common Data Types

- `Coord(row, col)`: a board position (row first, then column). Construct moves
  by passing two `Coord`s as `start` and `end`.
- `Move(start, end, move_type="", extra_info=None)`
- `MoveType`: move category string.
- `MoveExtraInfo`: metadata dictionary (`dict[str, object]`). Stays open so games
  can attach their own keys.
- `MoveKeys`: named constants for the `extra_info` keys the engine itself reads
  (`MoveKeys.EFFECTS`, `MoveKeys.MOVE_ACTOR`, `MoveKeys.ACTOR_PIECE`). Prefer these
  over raw strings. Both are in `cynmeith.utils`.

### Sides

A side is just a boolean (`Side2`): `True` is the first side, `False` is the
second. This shows up throughout the API:

- `Piece.side` is `True` or `False`.
- `board.is_enemy(position, side)` / `board.is_allied(position, side)` take a side.
- `QuotaTurnPolicy(starting_side=True)` and `game.current_side` use the same convention.
- In FEN, uppercase symbols are the first side (`True`), lowercase the second (`False`).

## Quick Example

```python
from pathlib import Path

from cynmeith import Config, Game, QuotaTurnPolicy
from cynmeith.utils import Coord
from examples.chess.chess_manager import ChessManager

game = Game(
    Config.from_file(Path("examples/chess/chess.yaml")),
    move_manager=ChessManager,
    turn_policy=QuotaTurnPolicy(moves_per_turn=1),
)

# Coord is (row, column). This moves the piece on row 6 to row 4 in column 4.
start, end = Coord(6, 4), Coord(4, 4)
if game.can_move(start, end):
    game.move(start, end)
```
