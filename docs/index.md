# CynMeith Documentation

This documentation is organized around how people actually approach the project:

- "What is this project and can I run it?"
- "Do I know enough Python to extend it?"
- "How do I build my own game?"
- "What exactly does the API expose?"

## Read in This Order

**Start here**

1. [Overview](overview.md) — what this is, who it is for, and its scope
2. [Quickstart](quickstart.md) — install and run an example

**Learn to build**

3. [Python Enough for CynMeith](python-enough.md) — the small Python subset you need
4. [Your First Custom Game](first-game.md) — blank slate to playable prototype
5. [Extending the Engine](extending.md) — every extension point in one place

**Reference**

6. [Architecture](architecture.md) — how the layers fit together
7. [Examples Guide](examples.md) — the chess and xiangqi stacks
8. [API Reference](api.md) — exact classes, methods, and signatures
9. [Roadmap](roadmap.md) — where the project is going

## 1.0 Focus

This documentation set is synchronized for 1.0.0 with these practical goals:

- Stable engine API for configurable board games.
- Clear extension flow for pieces, managers, effects, and turn policies.
- Working reference examples (chess and xiangqi) with documented behavior.
- Tested baseline (core + game-level integration tests).
- Better onboarding for creative users who are comfortable with small amounts of Python.

## Which Page Should I Start With?

- New to the project, or want its intent and limits: start at [Overview](overview.md).
- Want to run something immediately: go to [Quickstart](quickstart.md).
- Unsure whether you know enough Python: read [Python Enough for CynMeith](python-enough.md).
- Want to build something original quickly: use [Your First Custom Game](first-game.md).
- Building custom rules and pieces: read [Extending the Engine](extending.md).
- Curious about upcoming work: read [Roadmap](roadmap.md).
- Need specific method/class names: use [API Reference](api.md).

## Design Principles

- Keep `Board` generic and deterministic.
- Put game-specific rules into `MoveManager` subclasses.
- Use `MoveEffect` objects for irregular move side effects.
- Use `Game` + `TurnPolicy` for turn flow, not piece logic.
- Prefer a clean programmable engine first; build design-centric tools on top later.
