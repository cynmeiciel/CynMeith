# Overview

CynMeith is a board-game engine focused on modularity and extension.

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

## What Comes Out of the Box

- Hybrid config input (`Config.from_file`, `Config.from_data`)
- Standard move validation pipeline (`MoveManager`)
- Side-effect pipeline (`MoveEffect` + presets)
- Turn strategies (`FreeTurnPolicy`, `QuotaTurnPolicy`)
- Snapshot-based undo/redo
- Tk sample applications for chess and xiangqi

## Scope

CynMeith provides an engine foundation, not a complete game-content library.

You are expected to define your own piece classes and game-specific move manager for production use.
