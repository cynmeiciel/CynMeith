# CynMeith API Reference

This page is a concise reference for the core public surface.

For learning flow and architecture rationale, start from [docs/index.md](index.md).

## Package Exports

`cynmeith` exports:

- `Board`
- `Config`
- `Game`
- `GameOutcome`
- `BoardSimulation`
- `EliminatePieceCondition`
- `ReachSquareCondition`
- `NoLegalMovesCondition`
- `MoveLimitDrawCondition`
- `RoyalCheckmateCondition`
- `RoyalStalemateCondition`
- `MoveManager`
- `RoyalRuleset`
- `RoyalSafetyMoveManager`
- `MoveHistory`
- `PhaseSystem`
- `StaticPhaseSystem`
- `TurnCountPhaseSystem`
- `TwoStagePhaseSystem`
- `Piece`
- `PieceFactory`
- `ResourceSystem`
- `ActionPointSystem`
- `ScoringSystem`
- `PieceCountScoringSystem`
- `MaterialScoreSystem`
- `TurnPolicy`
- `FreeTurnPolicy`
- `QuotaTurnPolicy`
- `WinCondition`
- `MoveEffect`
- `RemovePieceEffect`
- `MovePieceEffect`
- `PromotePieceEffect`
- `EffectPresets`

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

`Game(config, move_manager=MoveManager, move_history=MoveHistory, turn_policy=None, phase_system=None, resource_system=None, scoring_system=None, win_conditions=None)` orchestrates gameplay with turn control and optional game-level systems.

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

Builders:

- `EffectPresets.capture(position)`
- `EffectPresets.captures(*positions)`
- `EffectPresets.relocate(start, end)`
- `EffectPresets.promote(symbol, position=None)`

Effects are normally attached via `Move.extra_info["effects"]` in `resolve_move`.

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

`MoveHistory(board)` stores snapshots for undo/redo.

Important methods:

- `seed_current_state()`
- `record_move(move)`
- `undo_move()`
- `redo_move()`
- `clear()`

Counters/stacks:

- `num_moves`
- `move_stack`, `state_stack`
- `redo_stack`, `redo_state_stack`

## Common Data Types

- `Move(start, end, move_type="", extra_info=None)`
- `MoveType`: move category string.
- `MoveExtraInfo`: metadata dictionary (`dict[str, object]`).

## Quick Example

```python
from pathlib import Path

from cynmeith import Config, Game, QuotaTurnPolicy
from examples.chess.chess_manager import ChessManager

game = Game(
    Config.from_file(Path("examples/chess/chess.yaml")),
    move_manager=ChessManager,
    turn_policy=QuotaTurnPolicy(moves_per_turn=1),
)

if game.can_move(start, end):
    game.move(start, end)
```
