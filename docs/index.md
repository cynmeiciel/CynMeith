# CynMeith Documentation

This documentation is organized by learning path.

## Read in This Order

1. [Overview](overview.md)
2. [Quickstart](quickstart.md)
3. [Architecture](architecture.md)
4. [Extending the Engine](extending.md)
5. [Examples Guide](examples.md)
6. [API Reference](api.md)

## 1.0 Focus

This documentation set is synchronized for 1.0.0 with these practical goals:

- Stable engine API for configurable board games.
- Clear extension flow for pieces, managers, effects, and turn policies.
- Working reference examples (chess and xiangqi) with documented behavior.
- Tested baseline (core + game-level integration tests).

## Which Page Should I Start With?

- New to the project: start at [Overview](overview.md).
- Want to run something immediately: go to [Quickstart](quickstart.md).
- Building custom rules and pieces: read [Extending the Engine](extending.md).
- Need specific method/class names: use [API Reference](api.md).

## Design Principles

- Keep `Board` generic and deterministic.
- Put game-specific rules into `MoveManager` subclasses.
- Use `MoveEffect` objects for irregular move side effects.
- Use `Game` + `TurnPolicy` for turn flow, not piece logic.
