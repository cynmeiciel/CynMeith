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

The Tk UI now also reflects game-level systems when present:

- current turn
- current phase
- score summaries
- terminal outcome/winner messages

## Chess Example

The chess stack uses:

- `QuotaTurnPolicy(moves_per_turn=1)` for standard one-move turns
- `ChessManager` for irregular moves
- `RoyalSafetyMoveManager` + `ChessRoyalRules` to reject self-check and king capture
- built-in `RoyalCheckmateCondition` for checkmate
- built-in `RoyalStalemateCondition` for stalemate draws
- built-in `MaterialScoreSystem` for material totals
- piece classes in `examples/chess`

Special rules currently implemented:

- en passant
- promotion via explicit user input (`extra_info["promotion"]`)
- castling (including attacked-square checks)
- king safety on all legal moves
- real checkmate/stalemate end conditions

Promotion flow in chess example:

- Tk UI prompts player for promotion piece (`Q`, `R`, `B`, `N`).
- Move is submitted with explicit promotion metadata.
- Manager validates and applies promotion effect.

## Xiangqi Example

The xiangqi stack uses:

- `QuotaTurnPolicy(moves_per_turn=1)` for standard one-move turns
- `XiangqiManager` for general-facing rule
- `RoyalSafetyMoveManager` + `XiangqiRoyalRules` to reject exposed generals and general capture
- built-in `RoyalCheckmateCondition` for checkmate
- built-in `RoyalStalemateCondition(kind="win")` for stalemate loss
- built-in `MaterialScoreSystem` for material totals
- piece classes in `examples/xiangqi`

The xiangqi UI spec also enables river rendering.

## Creating a New Example Package

1. Create a package under `examples/<your_game>`.
2. Add piece classes and a manager class.
3. Add a config file (`yaml`) for board setup.
4. Implement `build_game_spec()` returning a `GameSpec`.
5. Register it in the launcher (or create a dedicated launcher).
