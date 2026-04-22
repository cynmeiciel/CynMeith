# Overview

CynMeith is a Python-first board-game engine focused on modularity,
experimentation, and extension.

Its main purpose is not to be the fastest way to implement standard chess.
Its main purpose is to help you test original board-game ideas without
rewriting board state, turn flow, and move history from scratch.

At runtime, the engine is split into three layers:

- State layer: `Board`, `Piece`, `MoveHistory`
- Rule layer: `MoveManager` and `MoveEffect`
- Orchestration layer: `Game` and `TurnPolicy`

This structure allows you to implement custom rule sets without rewriting board state management.

## Core Workflow

1. Build a `Config` (from YAML or Python mapping).
2. Construct a `Game` with a `MoveManager` and a `TurnPolicy`.
3. Ask `Game.can_move(...)` or call `Game.move(...)`.
4. Let manager resolution/effects handle irregular behavior.
5. Use undo/redo from `Game`.

## Who This Is For

CynMeith works best for users who:

- can write small Python classes and functions
- want to prototype custom board-game rules
- prefer explicit code over opaque editor magic

If that sounds right, CynMeith gives you useful engine structure without
hiding the rules from you.

## What Comes Out of the Box

- Hybrid config input (`Config.from_file`, `Config.from_data`)
- Standard move validation pipeline (`MoveManager`)
- Side-effect pipeline (`MoveEffect` + presets)
- Turn strategies (`FreeTurnPolicy`, `QuotaTurnPolicy`)
- First-class game-level hooks for win conditions, phases, resources, and scoring
- Snapshot-based undo/redo
- Tk sample applications for chess and xiangqi

## Scope

CynMeith provides an engine foundation, not a complete game-content library.

You are expected to define your own piece classes and game-specific move manager for production use.

For project framing and non-goals, read [Project Guide](project.md).
For the minimum Python subset needed to extend the engine, read
[Python Enough for CynMeith](python-enough.md).
