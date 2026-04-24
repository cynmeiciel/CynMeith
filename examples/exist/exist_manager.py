from __future__ import annotations

from cynmeith import Board, BoardSimulation, MoveManager
from cynmeith.core.move_effects import EffectPresets
from cynmeith.utils import Coord, Move


class ExistManager(MoveManager):
    """
    Exist move resolver.

    Supported actions:
    - PLACE: spend one reserve piece to place on an empty square
    - MOVE: move an on-board piece one square in any direction
    - END_TURN: finish a one-action non-capture turn

    Current rule interpretation:
    - simulate first, capture second, validate resulting board last
    - line capture is still based on the pre-move board: moving into a square
      that lies on an existing dispute line captures the enemy piece on that
      line
    - tile capture is checked on the same temporary post-action board before
      removals, then the captured enemy pieces are removed, and only then are
      global restrictions re-validated
    """

    def resolve_move(self, move: Move) -> Move | None:
        action_type = self._normalize_action_type(move.move_type)

        if action_type == "END_TURN":
            return self._resolve_end_turn(move)
        if action_type == "PLACE":
            return self._resolve_place(move)
        if action_type == "MOVE":
            return self._resolve_move_existing(move)

        return None

    def _resolve_end_turn(self, move: Move) -> Move | None:
        """Resolve the synthetic action used to manually end a 1-action turn."""
        side = self._extract_side(move)
        if side is None:
            return None

        extra = self._build_extra_info(move)
        extra["move_actor"] = False
        extra["actor_piece"] = self._create_actor_piece(side)
        return Move(move.start, move.end, "END_TURN", extra)

    def _resolve_place(self, move: Move) -> Move | None:
        """
        Resolve a reserve placement.

        Approach:
        1. Simulate the newly placed piece.
        2. Detect captures on the temporary position.
        3. Remove captured enemy pieces.
        4. Re-check full board legality after captures.
        """
        side = self._extract_side(move)
        if side is None:
            return None
        if not self.board.is_in_bounds(move.end) or not self.board.is_empty(move.end):
            return None

        simulation = BoardSimulation(self.board)
        placed_piece = simulation.factory.create_piece(
            "X" if side else "x",
            move.end,
        )
        if placed_piece is None:
            return None
        simulation._set_at(move.end, placed_piece)

        captured_positions = self._find_tile_captures(simulation, side)
        if captured_positions:
            self._remove_positions(simulation, captured_positions)

        # All global restrictions are checked only on the post-capture board.
        if not self._board_obeys_restrictions(simulation):
            return None

        extra = self._build_extra_info(move)
        extra["move_actor"] = False
        extra["actor_piece"] = self._create_actor_piece(side)

        effects = [
            *EffectPresets.drop("X", side=side, position=move.end),
            *EffectPresets.captures(*captured_positions),
        ]
        extra["effects"] = effects
        return Move(move.start, move.end, "PLACE", extra)

    def _resolve_move_existing(self, move: Move) -> Move | None:
        """
        Resolve a normal adjacent move for an on-board Exist piece.

        Approach:
        - simulate the moved piece first
        - derive line captures from the original board
        - derive tile captures from the temporary post-move board
        - all captures are applied together in simulation before the final
          legality check
        """
        if not self.board.is_in_bounds(move.start) or not self.board.is_in_bounds(
            move.end
        ):
            return None

        piece = self.board.at(move.start)
        if piece is None or piece.symbol.upper() != "X":
            return None
        if not self.board.is_empty(move.end):
            return None
        if piece.position.chebyshev_to(move.end) != 1:
            return None
        line_captures = self._find_line_captures(
            self.board,
            move.start,
            move.end,
            piece.side,
        )

        simulation = BoardSimulation(self.board)
        actor = simulation.at(move.start)
        if actor is None:
            return None
        simulation._apply_move(move, actor)

        captured_positions = self._merge_unique_positions(
            line_captures,
            self._find_tile_captures(simulation, piece.side),
        )
        if captured_positions:
            self._remove_positions(simulation, captured_positions)

        if not self._board_obeys_restrictions(simulation):
            return None

        extra = self._build_extra_info(move)
        extra["effects"] = EffectPresets.captures(*captured_positions)
        return Move(move.start, move.end, "MOVE", extra)

    def _find_line_captures(
        self,
        board: Board | BoardSimulation,
        move_start: Coord,
        destination: Coord,
        moving_side: bool,
    ) -> list[Coord]:
        """
        Return enemy positions captured by the line-capture rule.

        This implementation treats a line capture as:
        - the destination square lies on a pre-existing dispute line
        - that line contains exactly two occupied squares
        - the two occupied squares are one piece of each color

        The moving piece's current square must not be one of the two dispute
        line pieces. In other words, line capture is "moving into" an existing
        dispute line, not sliding one of the dispute-line endpoints along that
        same line.
        """
        captured: list[Coord] = []

        for line_start, line_end, criteria in self._iter_lines_through_position(
            board, destination
        ):
            if board.count_pieces_line(line_start, line_end, criteria) != 2:
                continue

            occupied_positions = [
                position
                for position, piece in board.iter_enumerate_line(
                    line_start, line_end, criteria
                )
                if piece is not None
            ]
            if len(occupied_positions) != 2:
                continue
            if move_start in occupied_positions:
                continue

            pieces = [board.at(position) for position in occupied_positions]
            first_piece = pieces[0]
            second_piece = pieces[1]
            assert first_piece is not None
            assert second_piece is not None

            if first_piece.side == second_piece.side:
                continue

            for position, piece in zip(occupied_positions, pieces):
                if piece.side != moving_side:
                    captured.append(position)

        return captured

    def _find_tile_captures(
        self,
        board: BoardSimulation,
        moving_side: bool,
    ) -> list[Coord]:
        """
        Return enemy positions captured by the tile-capture rule.

        This scans the temporary post-action board and marks every enemy piece
        whose "self + adjacent pieces" occupancy exceeds 3.
        """
        captured: list[Coord] = []
        for position, piece in board.iter_enumerate():
            if piece is None or piece.side == moving_side:
                continue
            if self._count_tile_occupancy(board, position) > 3:
                captured.append(position)
        return captured

    def _board_obeys_restrictions(self, board: BoardSimulation) -> bool:
        """Check that both global restrictions hold on the given board state."""
        return self._obeys_line_restrictions(board) and self._obeys_tile_restrictions(
            board
        )

    def _obeys_line_restrictions(self, board: Board | BoardSimulation) -> bool:
        """No row, column, or diagonal may contain more than 2 pieces."""
        for position, piece in board.iter_enumerate():
            if piece is None:
                continue
            if any(count > 2 for count in board.count_pieces_from(position).values()):
                return False

        return True

    def _obeys_tile_restrictions(self, board: BoardSimulation) -> bool:
        """Each occupied square must have tile occupancy <= 3."""
        for position, piece in board.iter_enumerate():
            if piece is None:
                continue
            if self._count_tile_occupancy(board, position) > 3:
                return False
        return True

    @staticmethod
    def _count_tile_occupancy(board: BoardSimulation, position: Coord) -> int:
        """Count the piece itself plus all occupied adjacent squares."""
        count = 1
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                neighbor = position + Coord(dr, dc)
                if board.is_in_bounds(neighbor) and board.at(neighbor) is not None:
                    count += 1
        return count

    @staticmethod
    def _remove_positions(board: BoardSimulation, positions: list[Coord]) -> None:
        """Remove captured pieces from a simulated board state."""
        for position in positions:
            board._set_at(position, None)

    @staticmethod
    def _merge_unique_positions(*groups: list[Coord]) -> list[Coord]:
        """Preserve first-seen order while de-duplicating capture positions."""
        merged: list[Coord] = []
        for group in groups:
            for position in group:
                if position not in merged:
                    merged.append(position)
        return merged

    @staticmethod
    def _iter_lines_through_position(
        board: Board | BoardSimulation,
        position: Coord,
    ) -> list[tuple[Coord, Coord, object]]:
        """
        Build the 4 maximal straight lines that pass through a position:
        row, column, main diagonal, anti-diagonal.
        """
        s = position.r + position.c
        return [
            (
                Coord(position.r, 0),
                Coord(position.r, board.width - 1),
                Coord.is_horizontal,
            ),
            (
                Coord(0, position.c),
                Coord(board.height - 1, position.c),
                Coord.is_vertical,
            ),
            (
                Coord(
                    max(position.r - position.c, 0),
                    max(position.c - position.r, 0),
                ),
                Coord(
                    min(
                        position.r + (board.width - position.c - 1),
                        board.height - 1,
                    ),
                    min(
                        position.c + (board.height - position.r - 1),
                        board.width - 1,
                    ),
                ),
                Coord.is_diagonal,
            ),
            (
                Coord(max(0, s - board.width + 1), min(s, board.width - 1)),
                Coord(min(s, board.height - 1), max(0, s - board.height + 1)),
                Coord.is_diagonal,
            ),
        ]

    def _create_actor_piece(self, side: bool):
        """Create a synthetic actor for non-standard actions like PLACE/END_TURN."""
        return self.board.factory.create_piece("X" if side else "x", Coord.null())

    def _extract_side(self, move: Move) -> bool | None:
        """Read the explicit side used by PLACE/END_TURN synthetic moves."""
        extra = self._build_extra_info(move)
        side = extra.get("side")
        return side if isinstance(side, bool) else None

    @staticmethod
    def _normalize_action_type(move_type: str) -> str:
        normalized = move_type.strip().upper()
        return normalized or "MOVE"
