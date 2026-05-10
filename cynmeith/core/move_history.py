from copy import copy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterator

from cynmeith.core.piece import Piece
from cynmeith.utils import Move, MoveHistoryError
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board


Grid = list[list[Piece | None]]


@dataclass(frozen=True)
class MoveDelta:
    """
    Records the cell-level diff produced by a single move.

    `before` maps each touched cell to its piece value (shallow copy)
    immediately before the move applied; `after` maps the same cells to
    their values immediately after. Pieces are shallow-copied so their
    attribute state at that moment is preserved across future mutations.
    """

    before: dict[Coord, Piece | None] = field(default_factory=dict)
    after: dict[Coord, Piece | None] = field(default_factory=dict)


class _LazyStateStack:
    """
    Read-only sequence view over the materialized board states.

    State at index 0 is the seeded baseline; state at index k>0 is the
    baseline with deltas[0..k-1] applied. Materialization is lazy:
    indexing builds one state, iteration walks deltas in a single pass.
    """

    def __init__(self, history: "MoveHistory") -> None:
        self._history = history

    def __len__(self) -> int:
        return 1 + len(self._history._deltas)

    def __getitem__(self, index: int) -> Grid:
        size = len(self)
        if index < 0:
            index += size
        if index < 0 or index >= size:
            raise IndexError(index)
        return self._history._materialize_state(index)

    def __iter__(self) -> Iterator[Grid]:
        return self._history._iter_states()


class MoveHistory:
    """
    Manages move history with delta-based storage.

    Storage model:
    - `_baseline_state`: the seeded grid (shallow piece copies).
    - `_deltas`: per-move before/after cell maps; each delta only
      retains the cells that changed during that move.
    - `state_stack` is a lazy view that materializes states on demand
      so existing consumers (e.g. fingerprinting) keep working without
      paying the steady-state memory cost of full snapshots.

    Recording is driven by `Board._set_at`, which calls
    `record_cell_change` whenever recording is active. Recording is
    activated by `begin_recording()` (called by `MoveManager.apply_move`)
    and finalized by `record_move()`.
    """

    def __init__(self, board: "Board", max_history: int | None = None) -> None:
        self.board = board
        self.move_stack: list[Move] = []
        self.redo_stack: list[Move] = []
        self._baseline_state: Grid = []
        self._deltas: list[MoveDelta] = []
        self._redo_deltas: list[MoveDelta] = []
        self._recording: dict[Coord, Piece | None] | None = None
        self._max_history = max_history

    @property
    def num_moves(self) -> int:
        return len(self._deltas)

    @property
    def state_stack(self) -> _LazyStateStack:
        """
        Lazy sequence of board states (baseline + each move applied).

        Index 0 is the seed state; index k corresponds to the state after
        the k-th recorded move. Materialization cost is O(cells_changed)
        per state, so iterating the full sequence is O(total deltas).
        """
        return _LazyStateStack(self)

    @property
    def max_history(self) -> int | None:
        return self._max_history

    def set_max_history(self, max_history: int | None) -> None:
        """
        Cap how many move deltas are retained.

        When the cap is exceeded, oldest deltas are folded into the
        baseline so undo depth shrinks but state-stack indices past the
        bound shift forward. Use None to disable the cap.
        """
        if max_history is not None and max_history < 0:
            raise ValueError("max_history must be non-negative or None")
        self._max_history = max_history
        self._enforce_max_history()

    def clear(self) -> None:
        self.move_stack.clear()
        self.redo_stack.clear()
        self._baseline_state = []
        self._deltas.clear()
        self._redo_deltas.clear()
        self._recording = None

    def seed_current_state(self) -> None:
        """
        Reset history to use the board's current grid as the new baseline.
        """
        self._baseline_state = self._snapshot_grid(self.board.board)
        self._deltas.clear()
        self._redo_deltas.clear()
        self.move_stack.clear()
        self.redo_stack.clear()
        self._recording = None

    def begin_recording(self) -> None:
        """
        Start capturing cell-level changes for the next recorded move.
        """
        self._recording = {}

    def record_cell_change(
        self, position: Coord, before_piece: Piece | None
    ) -> None:
        """
        Note the pre-mutation value of a cell during an active recording.

        Only the first observation per cell is kept so the captured
        before-state reflects the moment the move started.
        """
        if self._recording is None:
            return
        if position not in self._recording:
            self._recording[position] = copy(before_piece) if before_piece else None

    def record_move(self, move: Move) -> None:
        before = self._recording or {}
        self._recording = None

        after: dict[Coord, Piece | None] = {}
        for position in before:
            current = self.board.board[position.r][position.c]
            after[position] = copy(current) if current else None

        self._deltas.append(MoveDelta(before=before, after=after))
        self.move_stack.append(move)
        self._redo_deltas.clear()
        self.redo_stack.clear()
        self._enforce_max_history()

    def undo_move(self) -> None:
        if not self._deltas or not self.move_stack:
            raise MoveHistoryError("No moves to undo.")
        delta = self._deltas.pop()
        move = self.move_stack.pop()
        for position, piece in delta.before.items():
            self.board.board[position.r][position.c] = (
                copy(piece) if piece else None
            )
        self._redo_deltas.append(delta)
        self.redo_stack.append(move)

    def redo_move(self) -> None:
        if not self._redo_deltas or not self.redo_stack:
            raise MoveHistoryError("No moves to redo.")
        delta = self._redo_deltas.pop()
        move = self.redo_stack.pop()
        for position, piece in delta.after.items():
            self.board.board[position.r][position.c] = (
                copy(piece) if piece else None
            )
        self._deltas.append(delta)
        self.move_stack.append(move)

    def _enforce_max_history(self) -> None:
        if self._max_history is None:
            return
        while len(self._deltas) > self._max_history:
            oldest_delta = self._deltas.pop(0)
            if self.move_stack:
                self.move_stack.pop(0)
            for position, piece in oldest_delta.after.items():
                self._baseline_state[position.r][position.c] = (
                    copy(piece) if piece else None
                )

    def _materialize_state(self, index: int) -> Grid:
        state: Grid = [list(row) for row in self._baseline_state]
        for i in range(index):
            for position, piece in self._deltas[i].after.items():
                state[position.r][position.c] = piece
        return state

    def _iter_states(self) -> Iterator[Grid]:
        state: Grid = [list(row) for row in self._baseline_state]
        yield [list(row) for row in state]
        for delta in self._deltas:
            for position, piece in delta.after.items():
                state[position.r][position.c] = piece
            yield [list(row) for row in state]

    @staticmethod
    def _snapshot_grid(grid: Grid) -> Grid:
        return [[copy(piece) if piece else None for piece in row] for row in grid]
