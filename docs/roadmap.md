# Roadmap

This page describes the direction of the project rather than the current API.

## Current Position

CynMeith is already a usable prototyping engine for custom two-sided board
games written in Python.

The current strengths are:

- custom piece logic
- custom move resolution
- irregular side effects
- configurable turn flow
- snapshot undo/redo

## Near-Term Priorities

The next major engine goals are to make whole-game structure more first-class.

### 1. Win Conditions

Examples:

- eliminate a key piece
- no legal moves
- reach a target square
- survive a fixed number of turns

This should become a dedicated engine concept instead of ad-hoc manager logic.

### 2. Phase Systems

Examples:

- placement phase, then movement phase
- draft phase, then battle phase
- turn-count-driven rule changes

These rules do not belong naturally in a piece class, and they deserve their
own structure.

### 3. Scoring Systems

Examples:

- material score
- territory score
- checkpoint score
- round-end points

Scoring matters for prototype games that are not pure elimination games.

### 4. Resource Systems

Examples:

- action points
- mana or energy
- summon charges
- per-turn skill budgets

These systems open up a much wider class of prototype games.

## Later Priorities

### Multiple Sides

The engine is currently strongest around two-sided play.

Broader side support is planned later, but it is not the immediate priority
because win conditions, phases, scoring, and resources will unlock more useful
design space first.

### Higher-Level Rule Composition

Longer term, CynMeith should reduce the amount of custom Python users need to
write for common rules.

That could mean:

- reusable rule objects
- declarative move constraints
- serializable win and phase definitions

The likely end state is not "no Python". The likely end state is "Python when
needed, built-in composition when possible."

### Design-Centric Applications

A web app, desktop app, or mobile app may eventually sit on top of CynMeith.

That should be treated as a separate product layer built on the engine, not as
an excuse to weaken the engine's internal design.

## What Will Probably Stay True

- the engine should remain small enough to read
- core rules should stay explicit and debuggable
- engine abstractions should serve prototyping first
- performance work should follow clarity, not replace it

