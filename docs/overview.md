# Overview

CynMeith is a Python-first board-game engine for experimenting with custom
rules. It helps you test original turn-based board-game ideas without rewriting
board state, turn flow, and move history every time.

Its purpose is not to be the fastest way to implement standard chess. It is to
let you prototype original rule systems on a clean, programmable engine.

## Primary Goal

The main goal is to help creative users test original board-game ideas quickly:

- custom movement rules
- custom turn structures
- irregular side effects after moves
- unusual board sizes and setups
- fast iteration in code, not engine-level performance work

## The Three Layers

At runtime, the engine splits into three layers:

- State layer: `Board`, `Piece`, `MoveHistory`
- Rule layer: `MoveManager` and `MoveEffect`
- Orchestration layer: `Game` and `TurnPolicy`

This lets you implement custom rule sets without rewriting board-state
management.

## Core Workflow

1. Build a `Config` (from YAML or a Python mapping).
2. Construct a `Game` with a `MoveManager` and a `TurnPolicy`.
3. Ask `Game.can_move(...)` or call `Game.move(...)`.
4. Let manager resolution/effects handle irregular behavior.
5. Use undo/redo from `Game`.

## Who This Is For

CynMeith is a good fit if you:

- can write small Python classes and functions
- want to prototype custom board-game rules, not just replay standard chess
- prefer explicit code over a purely visual editor
- want undo/redo and reusable engine primitives while experimenting

It is a weaker fit if you:

- want a no-code game editor
- want a polished end-user app more than a Python package
- want a tournament-grade chess engine or heavily optimized search backend

## What CynMeith Is

At its core, CynMeith gives you:

- a board-state container with hybrid config input (`Config.from_file`, `Config.from_data`)
- a move validation and enrichment pipeline (`MoveManager`)
- a side-effect system for irregular moves (`MoveEffect` + presets)
- a turn-control layer (`FreeTurnPolicy`, `QuotaTurnPolicy`)
- first-class hooks for win conditions, phases, resources, and scoring
- snapshot-based undo/redo
- Tk sample applications for chess and xiangqi that demonstrate extension patterns

## What CynMeith Is Not

Right now, CynMeith is not:

- a complete board-game authoring application
- a DSL-driven game-definition system
- a built-in AI/search engine
- a rules database for many historical games
- a full multi-side engine yet

## Design Stance

CynMeith deliberately keeps the engine programmable. It should stay good at:

- deterministic board state
- composable rule logic
- debuggable Python extension points

Design-first authoring tools such as a web, desktop, or mobile app should sit on
top of this engine rather than distort it into a visual tool before the rules
model is ready.

## Current Limits

- game authoring is still mostly code-driven
- core assumptions are still strongest for two-sided games
- win conditions, phases, scoring, and resources are first-class hooks, but
  built-in presets are still minimal
- snapshot history is convenient but not designed for high-performance play

## Recommended Way To Use CynMeith

1. Start with a tiny ruleset.
2. Create one or two piece classes.
3. Add special rules in `MoveManager`.
4. Use `QuotaTurnPolicy` unless your game truly needs something stranger.
5. Only build UI after the core rules feel stable.

## Next

For the minimum Python subset needed to extend the engine, read
[Python Enough for CynMeith](python-enough.md). To go from a blank slate to a
playable prototype, use [Your First Custom Game](first-game.md).
