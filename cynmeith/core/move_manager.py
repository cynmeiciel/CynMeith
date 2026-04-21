from typing import TYPE_CHECKING

from cynmeith.core.move_effects import MoveEffect
from cynmeith.core.piece import Piece
from cynmeith.utils.aliases import Move, MoveExtraInfo
from cynmeith.utils.coord import Coord

if TYPE_CHECKING:
    from cynmeith.core.board import Board


class MoveManager:
    """
    This class is responsible for determining whether an move is legal based on general game rules that apply to all pieces.

    This class is intended to be subclassed if users wish to implement custom rules.
    """

    def __init__(self, board: "Board"):
        self.board = board

    def validate_move(self, move: Move) -> bool:
        """
        Validate a move for a given piece.
        """
        piece = self.board.at(move.start)
        if piece is None:
            return False
        new_position = move.end
        return piece.is_valid_move(new_position, self.board)

    def resolve_move(self, move: Move) -> Move | None:
        """
        Validate and enrich a move.

        Subclasses can override to support irregular moves (en passant,
        promotion, drops, etc.) by returning an enriched Move with metadata.
        """
        if not self.validate_move(move):
            return None
        return move

    def apply_move(self, move: Move, piece: Piece) -> None:
        """
        Apply a move that has already been resolved.

        Subclasses can override this to apply special side effects.
        """
        extra = self._build_extra_info(move)

        move_actor = bool(extra.get("move_actor", True))
        if move_actor:
            self.board._apply_move(move, piece)
        else:
            self.board.history.record_move(move)

        effects = self._build_effects(move)
        for effect in effects:
            effect.apply(self.board, move, piece)

    @staticmethod
    def _build_extra_info(move: Move) -> MoveExtraInfo:
        if isinstance(move.extra_info, dict):
            return dict(move.extra_info)
        return {}

    def _build_effects(self, move: Move) -> list[MoveEffect]:
        extra = self._build_extra_info(move)
        effects = extra.get("effects")
        if isinstance(effects, list):
            return [effect for effect in effects if isinstance(effect, MoveEffect)]

        # Backward compatibility for older custom managers.
        legacy: list[MoveEffect] = []
        capture = extra.get("capture")
        if isinstance(capture, Coord):
            from cynmeith.core.move_effects import RemovePieceEffect

            legacy.append(RemovePieceEffect(capture))
        elif isinstance(capture, list):
            from cynmeith.core.move_effects import RemovePieceEffect

            for position in capture:
                if isinstance(position, Coord):
                    legacy.append(RemovePieceEffect(position))
        return legacy

    def get_validated_moves(self, piece: Piece) -> list[Coord]:
        """
        Get the valid moves for a piece.
        """
        return [
            coord
            for coord in piece.iter_move_candidates(self.board)
            if self.resolve_move(Move(piece.position, coord)) is not None
        ]
