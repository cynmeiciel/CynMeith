from cynmeith import MoveManager
from cynmeith.core.move_effects import EffectPresets
from cynmeith.utils import Coord, Move

from .king import King
from .pawn import Pawn
from .rook import Rook


class ChessManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None:
            return None
        new_position = move.end

        if isinstance(piece, King):
            castling_move = self._resolve_castling(piece, move)
            if castling_move is not None:
                return castling_move

        if self.board.is_allied(move.end, piece.side):
            return None

        extra = self._build_extra_info(move)

        if isinstance(piece, Pawn) and self._is_valid_en_passant(piece, move):
            capture_position = Coord(move.start.r, move.end.c)
            return self._with_effects(
                move,
                EffectPresets.capture(capture_position),
                extra,
            )

        if not piece.is_valid_move(new_position, self.board):
            return None

        if isinstance(piece, Pawn) and self._is_promotion_rank(piece, move.end):
            promotion_symbol = str(extra.get("promotion", "Q"))
            return self._with_effects(
                move,
                EffectPresets.promote(promotion_symbol),
                extra,
            )

        return move

    def _is_valid_en_passant(self, piece: Pawn, move: Move) -> bool:
        dr = move.end.r - move.start.r
        dc = move.end.c - move.start.c
        if abs(dc) != 1:
            return False

        expected_dr = 1 if piece.side else -1
        if dr != expected_dr:
            return False
        if not self.board.is_empty(move.end):
            return False

        capture_position = Coord(move.start.r, move.end.c)
        captured_piece = self.board.at(capture_position)
        if not isinstance(captured_piece, Pawn) or captured_piece.side == piece.side:
            return False

        if not self.board.history.move_stack:
            return False

        last_move = self.board.history.move_stack[-1]
        if last_move.end != capture_position:
            return False

        return abs(last_move.start.r - last_move.end.r) == 2

    def _is_promotion_rank(self, piece: Pawn, position: Coord) -> bool:
        if piece.side:
            return position.r == self.board.height - 1
        return position.r == 0

    def _resolve_castling(self, king: King, move: Move) -> Move | None:
        if king.has_moved:
            return None

        if move.start.r != move.end.r:
            return None
        if abs(move.end.c - move.start.c) != 2:
            return None

        direction = 1 if move.end.c > move.start.c else -1
        rook_col = self.board.width - 1 if direction == 1 else 0
        rook_position = Coord(move.start.r, rook_col)
        rook = self.board.at(rook_position)
        if not isinstance(rook, Rook) or rook.side != king.side or rook.has_moved:
            return None

        if not self.board.is_empty_line(move.start, rook_position, Coord.is_horizontal):
            return None

        enemy_side = not king.side
        if self._is_square_attacked(move.start, enemy_side):
            return None

        mid_square = Coord(move.start.r, move.start.c + direction)
        if self._is_square_attacked(mid_square, enemy_side):
            return None

        if self._is_square_attacked(move.end, enemy_side):
            return None

        extra = self._build_extra_info(move)
        rook_to = Coord(move.start.r, move.start.c + direction)
        return self._with_effects(
            move,
            EffectPresets.relocate(rook_position, rook_to),
            extra,
        )

    def _is_square_attacked(self, target: Coord, by_side: bool) -> bool:
        for position, piece in self.board.iter_enumerate():
            if piece is None or piece.side != by_side:
                continue

            if isinstance(piece, Pawn):
                dr = target.r - position.r
                dc = target.c - position.c
                expected = 1 if piece.side else -1
                if dr == expected and abs(dc) == 1:
                    return True
                continue

            if isinstance(piece, King):
                if piece.position.is_adjacent(target):
                    return True
                continue

            if piece.is_valid_move(target, self.board):
                return True

        return False

    def _with_effects(self, move: Move, effects: list, extra: dict) -> Move:
        merged = dict(extra)
        existing = merged.get("effects")
        if isinstance(existing, list):
            merged["effects"] = [*existing, *effects]
        else:
            merged["effects"] = list(effects)
        return Move(move.start, move.end, move.move_type, merged)
