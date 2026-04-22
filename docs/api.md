# CynMeith API Reference

This page is a concise reference for the core public surface.

For learning flow and architecture rationale, start from [docs/index.md](index.md).

## Package Exports

`cynmeith` exports:

- `Board`
- `Config`
- `Game`
- `MoveManager`
- `MoveHistory`
- `Piece`
- `PieceFactory`
- `TurnPolicy`
- `FreeTurnPolicy`
- `QuotaTurnPolicy`
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

`Game(config, move_manager=MoveManager, move_history=MoveHistory, turn_policy=None)` orchestrates gameplay with turn control.

Important methods:

- `can_move(start, end, move_type="", extra_info=None) -> bool`
- `move(start, end, move_type="", extra_info=None)`
- `get_valid_moves(piece)`
- `reset()`
- `undo_move()`
- `redo_move()`

Properties:

- `current_side`

Notes:

- `Game` wraps `Board` and turn policy snapshots so undo/redo restores both board and turn state.

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
