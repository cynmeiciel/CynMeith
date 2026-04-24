from __future__ import annotations

from collections.abc import Mapping


class ReserveManager:
    """
    Tracks off-board pieces for each side in Exist.

    A player starts with 8 pieces in reserve, spends one when placing, and
    gains one for each captured opponent piece.
    """

    def __init__(self) -> None:
        self.reserves = {True: 8, False: 8}

    def has_pieces(self, side: bool) -> bool:
        return self.reserves[side] > 0

    def spend_piece(self, side: bool) -> None:
        if not self.has_pieces(side):
            raise ValueError(f"Side {side} has no pieces left in reserve.")
        self.reserves[side] -= 1

    def gain_pieces(self, side: bool, count: int = 1) -> None:
        if count < 0:
            raise ValueError("count must be non-negative")
        self.reserves[side] += count

    def get_count(self, side: bool) -> int:
        return self.reserves[side]

    def reset(self) -> None:
        self.reserves = {True: 8, False: 8}

    def sync_from_board_counts(
        self,
        occupied_counts: Mapping[bool, int],
        total_owned_per_side: int = 8,
    ) -> None:
        self.reserves = {
            side: max(0, total_owned_per_side - occupied_counts.get(side, 0))
            for side in (True, False)
        }

    def snapshot(self) -> dict[bool, int]:
        return dict(self.reserves)

    def restore(self, snapshot: Mapping[bool, int]) -> None:
        self.reserves = {True: int(snapshot[True]), False: int(snapshot[False])}
