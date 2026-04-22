# Project Guide

CynMeith is a Python-first board-game engine for experimenting with custom rules.

It is aimed at people who want to prototype new turn-based board games without
rewriting the same board-state and move-history plumbing every time.

## Primary Goal

The main goal of CynMeith is to help creative users test original board-game
ideas quickly.

That means:

- custom movement rules
- custom turn structures
- irregular side effects after moves
- unusual board sizes and setups
- fast iteration in code, not engine-level performance work

## Intended Audience

CynMeith is a good fit if you:

- are comfortable reading and editing small Python classes
- want to prototype rule systems, not just replay standard chess
- prefer a programmable framework over a purely visual editor
- want undo/redo and reusable engine primitives while experimenting

It is a weaker fit if you:

- want a no-code game editor
- want a polished end-user app more than a Python package
- want a tournament-grade chess engine or heavily optimized search backend

## What CynMeith Is

At its core, CynMeith is:

- a board-state container
- a move validation and enrichment pipeline
- a side-effect system for irregular moves
- a turn-control layer
- a small set of examples that demonstrate extension patterns

## What CynMeith Is Not

Right now, CynMeith is not:

- a complete board-game authoring application
- a DSL-driven game-definition system
- a built-in AI/search engine
- a rules database for many historical games
- a full multi-side engine yet

## Design Stance

CynMeith deliberately keeps the engine programmable.

The engine should stay good at:

- deterministic board state
- composable rule logic
- debuggable Python extension points

Design-first authoring tools such as a web app, desktop app, or mobile app
should sit on top of this engine rather than distort the engine into a visual
tool before the rules model is ready.

## Current Strengths

- clear separation between state, rules, and turn flow
- practical extension points through `Piece`, `MoveManager`, and `TurnPolicy`
- first-class hooks for win conditions, phases, resources, and scoring
- snapshot-based undo/redo for prototyping
- working chess and xiangqi examples
- small enough codebase to understand without weeks of onboarding

## Current Limits

- game authoring is still mostly code-driven
- core assumptions are still strongest for two-sided games
- win conditions, phases, scoring, and resources are first-class hooks, but built-in presets are still minimal
- snapshot history is convenient but not designed for high-performance play

## Recommended Way To Use CynMeith

1. Start with a tiny ruleset.
2. Create one or two piece classes.
3. Add special rules in `MoveManager`.
4. Use `QuotaTurnPolicy` unless your game truly needs something stranger.
5. Only build UI after the core rules feel stable.

## Documentation Paths

- New to the project: [Overview](overview.md)
- Need only the minimum Python subset: [Python Enough for CynMeith](python-enough.md)
- Want to build a prototype game: [Your First Custom Game](first-game.md)
- Need engine internals: [Architecture](architecture.md)
- Need API details: [API Reference](api.md)
