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
- first-class hooks for win conditions, phases, resources, and scoring
- snapshot undo/redo

## Near-Term Priorities

The next major engine goals are to make those new hooks genuinely convenient.

### 1. More Built-In Win Conditions

Examples:

- eliminate a key piece
- no legal moves
- reach a target square
- survive a fixed number of turns

The first built-ins now exist. The next step is broadening that library.

### 2. More Built-In Phase Systems

Examples:

- placement phase, then movement phase
- draft phase, then battle phase
- turn-count-driven rule changes

The first built-ins now exist. The next step is adding more reusable phase
systems for setup/battle, draft/battle, and other prototype patterns.

### 3. More Built-In Scoring Systems

Examples:

- material score
- territory score
- checkpoint score
- round-end points

Scoring hooks and a first built-in set now exist. The next step is territory,
checkpoint, and round-based scoring helpers.

### 4. More Built-In Resource Systems

Examples:

- action points
- mana or energy
- summon charges
- per-turn skill budgets

Resource hooks and a first built-in set now exist. The next step is richer
systems such as mana pools, charge systems, and custom refresh policies.

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
