# Architecture

CynMeith separates board state, game rules, and turn flow.

## Layer 1: State (`Board`, `Piece`, `MoveHistory`)

`Board` is the source of truth for positions.

Responsibilities:

- Piece placement and retrieval (`at`, `set_at`)
- Geometry helpers (line and directional iterators)
- Primitive movement application (`_apply_move`)
- Access to move history snapshots

`Piece` is a behavior object for movement legality.

- Required: implement `is_valid_move(new_position, board)`
- Optional: override `iter_move_candidates(board)` for performance
- Optional: override `move(new_position)` for piece-local state changes

In 1.0 examples, candidate generation is piece-driven:

- Jump pieces generate bounded offset candidates.
- Sliding pieces iterate rays via `Board.iter_positions_towards(...)` and stop at first blocker.

`MoveHistory` stores snapshots so undo/redo restores exact board state.

## Layer 2: Rules (`MoveManager`, `MoveEffect`)

`MoveManager` is the rule pipeline:

1. `validate_move(move)`
2. `resolve_move(move)`
3. `apply_move(move, piece)`

By default, `resolve_move` is simple validation and `apply_move` performs actor movement.

Irregular behavior is represented by `MoveEffect` objects.

Examples:

- remove captured piece
- relocate another piece (castling rook)
- replace moved piece (promotion)

This keeps custom rules composable and testable.

For chess promotion in current examples, promotion piece selection is explicit input and is consumed by manager logic during apply.

## Layer 3: Orchestration (`Game`, `TurnPolicy`)

`Game` coordinates move lifecycle and turn restrictions:

- checks active policy before move
- delegates resolution/application to board manager
- snapshots turn state for undo/redo symmetry

`TurnPolicy` decides who can move and how turns advance.

Built-ins:

- `FreeTurnPolicy`: unrestricted
- `QuotaTurnPolicy`: fixed moves per side before switching

## Move Lifecycle

1. Caller requests move through `Game.move(...)` or `Board.move(...)`.
2. Piece and side checks run (`Game` only for side policy).
3. `MoveManager.resolve_move(...)` validates and enriches move metadata.
4. `MoveManager.apply_move(...)` performs actor move and applies effects.
5. History and turn snapshots are updated.

## Why This Split Matters

- New game rules do not require rewriting board internals.
- Irregular rules can be modeled as data (`effects`) instead of ad-hoc branching.
- Turn logic can vary independently of piece movement logic.
