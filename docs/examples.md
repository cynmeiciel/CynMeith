# Examples Guide

CynMeith includes chess and xiangqi examples with a shared Tk UI shell.

## Entry Point

Use the launcher:

```bash
poetry run python examples/tk_demo.py chess
poetry run python examples/tk_demo.py xiangqi
```

The launcher picks a `GameSpec` and starts `TkGameApp`.

## Shared UI Architecture

The UI modules in `examples/ui` are intentionally generic:

- `spec.py`: immutable game descriptors (`GameSpec`, `BoardTheme`)
- `app.py`: event flow, selection, status, and command shortcuts
- `canvas.py`: board/piece drawing and click-to-position mapping
- `widgets.py`: control/status widgets

This split lets each game provide only configuration and rule objects.

## Chess Example

The chess stack uses:

- `QuotaTurnPolicy(moves_per_turn=1)` for standard one-move turns
- `ChessManager` for irregular moves
- piece classes in `examples/chess`

Special rules currently implemented:

- en passant
- promotion via explicit user input (`extra_info["promotion"]`)
- castling (including attacked-square checks)

Promotion flow in chess example:

- Tk UI prompts player for promotion piece (`Q`, `R`, `B`, `N`).
- Move is submitted with explicit promotion metadata.
- Manager validates and applies promotion effect.

## Xiangqi Example

The xiangqi stack uses:

- `FreeTurnPolicy` in example setup
- `XiangqiManager` for general-facing rule
- piece classes in `examples/xiangqi`

Note: `FreeTurnPolicy` is used in the sample to emphasize engine flexibility. If you want strict side alternation, use `QuotaTurnPolicy(moves_per_turn=1)`.

The xiangqi UI spec also enables river rendering.

## Creating a New Example Package

1. Create a package under `examples/<your_game>`.
2. Add piece classes and a manager class.
3. Add a config file (`yaml`) for board setup.
4. Implement `build_game_spec()` returning a `GameSpec`.
5. Register it in the launcher (or create a dedicated launcher).
