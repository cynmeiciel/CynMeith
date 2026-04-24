from typing import TYPE_CHECKING, cast

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

        Subclasses can override this to implement custom validation logic.
        By default, this checks if the piece at the move's starting coordinate considers the move valid.
        """
        piece = self.board.at(move.start)
        if piece is None:
            return False
        return piece.is_valid_move(move.end, self.board)

    def resolve_move(self, move: Move) -> Move | None:
        """
        Validate and enrich a move.

        This is the primary entry point for move validation.

        Default behavior:
        1. Basic physical validation via validate_move().
        2. Prevention of capturing allied pieces (common for most games).

        Returns None if the move is illegal under any game rule.
        """
        if not self.validate_move(move):
            return None

        if self.board.is_allied(move.end, self.board.side_at(move.start)):  # type: ignore
            return None

        return move

    def apply_move(self, move: Move, piece: Piece) -> None:
        """
        Apply a move that has already been resolved.

        Subclasses can override this to apply special side effects.
        """
        extra = self._build_extra_info(move)

        # Optimization: use get with default to avoid extra dict lookups
        move_actor = cast(bool, extra.get("move_actor", True))
        if move_actor:
            self.board._apply_move(move, piece)

        effects = self._build_effects(move)
        for effect in effects:
            effect.apply(self.board, move, piece)

        self.board.history.record_move(move)

    def get_actor_piece(self, move: Move) -> Piece | None:
        """
        Resolve the piece used by turn/resource/phase systems for this move.

        For irregular moves (e.g. drops), subclasses can inject an actor piece
        into `extra_info["actor_piece"]` during resolve_move.
        """
        extra = self._build_extra_info(move)
        actor_piece = extra.get("actor_piece")
        if isinstance(actor_piece, Piece):
            return actor_piece
        return self.board.at(move.start)

    @staticmethod
    def _build_extra_info(move: Move) -> MoveExtraInfo:
        if isinstance(move.extra_info, dict):
            # Return the original if it's already a dict to avoid unnecessary copying
            # unless mutation is expected. Move is frozen, so extra_info should be treated as read-only here.
            return move.extra_info
        return {}

    def _build_effects(self, move: Move) -> list[MoveEffect]:
        if move.extra_info:
            effects = move.extra_info.get("effects")
            if isinstance(effects, list):
                return [effect for effect in effects if isinstance(effect, MoveEffect)]
        return []

    def get_validated_moves(self, piece: Piece) -> list[Coord]:
        """
        Get the valid moves for a piece.

        Note: This relies on resolve_move to filter out moves that might be
        physically possible but contextually illegal (e.g. moving into check).
        """
        # Cache position to avoid repeated property access in loop
        start_pos = piece.position
        # Pre-creating a Move template can be slightly faster if resolve_move is called frequently
        return [
            coord
            for coord in piece.iter_move_candidates(self.board)
            if self.resolve_move(Move(start_pos, coord)) is not None
        ]
