# CynMeith Documentation

This documentation is organized around how people actually approach the project:

- "What is this project?"
- "Can I run it?"
- "Do I know enough Python to extend it?"
- "How do I build my own game?"
- "What exactly does the API expose?"

## Read in This Order

1. [Project Guide](project.md)
2. [Overview](overview.md)
3. [Quickstart](quickstart.md)
4. [Python Enough for CynMeith](python-enough.md)
5. [Your First Custom Game](first-game.md)
6. [Architecture](architecture.md)
7. [Extending the Engine](extending.md)
8. [Examples Guide](examples.md)
9. [Roadmap](roadmap.md)
10. [API Reference](api.md)

## 1.0 Focus

This documentation set is synchronized for 1.0.0 with these practical goals:

- Stable engine API for configurable board games.
- Clear extension flow for pieces, managers, effects, and turn policies.
- Working reference examples (chess and xiangqi) with documented behavior.
- Tested baseline (core + game-level integration tests).
- Better onboarding for creative users who are comfortable with small amounts of Python.

## Which Page Should I Start With?

- Want the project's intent and limits first: start at [Project Guide](project.md).
- New to the project: start at [Overview](overview.md).
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
