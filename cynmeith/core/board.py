from typing import Callable, Iterable

from cynmeith.core.config import Config
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.core.piece_factory import PieceFactory
from cynmeith.utils.aliases import (
    InvalidMoveError,
    Move,
    MoveExtraInfo,
    MoveType,
    PieceClass,
    PieceError,
    PieceSymbol,
    PositionError,
    Side2,
)
from cynmeith.utils.coord import Coord
from cynmeith.utils.fen import fen_parser


class Board:
    """
    The Board class represents the game board and acts as the central
    interface for managing game state.

    It provides methods for placing, removing, and moving pieces.
    """

    def __init__(
        self,
        config: Config,
        move_manager: type[MoveManager] = MoveManager,
        move_history: type[MoveHistory] = MoveHistory,
    ) -> None:
        self.config = config
        self.width = config.width
        self.height = config.height
        self.board: list[list[Piece | None]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

        self.factory = PieceFactory()
        self.factory.register_pieces(config)

        self.manager = move_manager(self)
        self.history = move_history(self)
        self._state_listener: Callable[[], None] | None = None

        self._init_pieces()
        self.history.seed_current_state()

    def _init_pieces(self) -> None:
        grid = fen_parser(self.config.fen, self.config.width, self.config.height)
        for r, row in enumerate(grid):
            for c, piece in enumerate(row):
                if piece != " ":
                    position = Coord(r, c)
                    self._set_at(position, self.factory.create_piece(piece, position))

    def __str__(self) -> str:
        return "\n".join(
            " ".join(piece.symbol if piece else "□" for piece in row)
            for row in self.board
        )

    def __repr__(self) -> str:
        return "\n".join(
            " ".join(repr(piece) if piece else "□" for piece in row)
            for row in self.board
        )

    def print_highlighted(self, highlights: list[Coord] = []) -> None:
        """
        Print the board with highlighted positions.
        """
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece is None:
                    symbol = "□"
                else:
                    symbol = piece.symbol if piece.side else piece.symbol.lower()
                position = Coord(r, c)
                if position in highlights:
                    print(f"\033[93m{symbol}\033[0m", end=" ")
                else:
                    print(symbol, end=" ")
            print()

    def iter_pieces(self, none_piece: bool = False) -> Iterable[Piece | None]:
        """
        Iterate over all pieces on the board.

        If none_piece is True, the iteration will also include empty positions.
        """
        for row in self.board:
            for piece in row:
                if piece is not None or none_piece:
                    yield piece

    def iter_pieces_by_side(self, side: Side2) -> Iterable[Piece | None]:
        """
        Iterate over all pieces by side.
        """
        for piece in self.iter_pieces():
            assert piece is not None
            if piece.side == side:
                yield piece

    def iter_pieces_by_type(self, piece_symbol: PieceSymbol) -> Iterable[Piece | None]:
        """
        Iterate over all pieces by type.
        """
        for piece in self.iter_pieces():
            assert piece is not None
            if piece.symbol == piece_symbol:
                yield piece

    def iter_positions(self) -> Iterable[Coord]:
        """
        Iterate over all coordinates on the board.
        """
        for r in range(self.height):
            for c in range(self.width):
                yield Coord(r, c)

    def iter_enumerate(
        self, none_piece: bool = False
    ) -> Iterable[tuple[Coord, Piece | None]]:
        """
        Iterate over all pieces on the board with their positions.
        """
        for r, row in enumerate(self.board):
            for c, piece in enumerate(row):
                if piece is not None or none_piece:
                    yield Coord(r, c), piece

    def iter_positions_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
    ) -> Iterable[Coord]:
        """
        Iterate over all positions in a line between two positions.
        """
        if not criteria(start, end):
            raise StopIteration
        direction = start.direction_unit(end)
        while start != end + direction:
            yield start
            start += direction

    def iter_pieces_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
        none_piece: bool = False,
    ) -> Iterable[Piece | None]:
        """
        Iterate over all pieces in a line between two positions.

        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_line(start, end, criteria):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield piece

    def iter_enumerate_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
        none_piece: bool = False,
    ) -> Iterable[tuple[Coord, Piece | None]]:
        """
        Iterate over all pieces with their positions in a line between two positions.

        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_line(start, end, criteria):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield position, piece

    def iter_positions_towards(self, start: Coord, direction: Coord) -> Iterable[Coord]:
        """
        Iterate over all positions in a direction from a starting position.
        """
        while self.is_in_bounds(start):
            yield start
            start += direction

    def iter_pieces_towards(
        self, start: Coord, direction: Coord
    ) -> Iterable[Piece | None]:
        """
        Iterate over all pieces in a direction from a starting position.
        """
        for position in self.iter_positions_towards(start, direction):
            piece = self.at(position)
            if piece is not None:
                yield piece

    def iter_enumerate_towards(
        self, start: Coord, direction: Coord, none_piece: bool = False
    ) -> Iterable[tuple[Coord, Piece | None]]:
        """
        Iterate over all pieces with their positions in a direction from a starting position.

        If none_piece is True, the iteration will also include empty positions.
        """
        for position in self.iter_positions_towards(start, direction):
            piece = self.at(position)
            if piece is not None or none_piece:
                yield position, piece

    def count_pieces_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
    ) -> int:
        """
        Count the number of pieces along a line or diagonal between two positions.

        Args:
            start (Coord): The starting position.
            end (Coord): The ending position.
            criteria (Callable[[Coord, Coord], bool]): A function to determine the movement rule (e.g., is_diagonal, is_orthogonal).

        Returns:
            int: The number of pieces along the line or diagonal.
        """
        if not criteria(start, end):
            raise ValueError(f"Invalid line criteria between {start} and {end}")

        return len(list(self.iter_pieces_line(start, end, criteria)))

    def count_pieces_from(self, position: Coord) -> dict[str, int]:
        """
        Count the number of pieces from a given position along the row, column, and diagonals.

        Args:
            position (Coord): The starting position.

        Returns:
            dict[str, int]: A dictionary with counts for "row", "column", "diagonal1", and "diagonal2".
        """
        if not self.is_in_bounds(position):
            raise PositionError(f"Position out of bounds {position}")

        counts = {"row": 0, "column": 0, "diagonal1": 0, "diagonal2": 0}

        # Count pieces in the row
        counts["row"] = self.count_pieces_line(
            Coord(position.r, 0), Coord(position.r, self.width - 1), Coord.is_orthogonal
        )

        # Count pieces in the column
        counts["column"] = self.count_pieces_line(
            Coord(0, position.c),
            Coord(self.height - 1, position.c),
            Coord.is_orthogonal,
        )

        # Count pieces in the first diagonal (top-left to bottom-right)
        start_diag1 = Coord(
            max(position.r - position.c, 0), max(position.c - position.r, 0)
        )
        end_diag1 = Coord(
            min(position.r + (self.width - position.c - 1), self.height - 1),
            min(position.c + (self.height - position.r - 1), self.width - 1),
        )
        counts["diagonal1"] = self.count_pieces_line(
            start_diag1, end_diag1, Coord.is_diagonal
        )

        # Count pieces in the second diagonal (top-right to bottom-left)
        s = position.r + position.c
        start_diag2 = Coord(max(0, s - self.width + 1), min(s, self.width - 1))
        end_diag2 = Coord(min(s, self.height - 1), max(0, s - self.height + 1))
        counts["diagonal2"] = self.count_pieces_line(
            start_diag2, end_diag2, Coord.is_diagonal
        )

        return counts

    def reset(self) -> None:
        """
        Reset the board to its initial state.
        """
        self.clear()
        self._init_pieces()
        self.history.seed_current_state()
        self._notify_state_listener()

    def clear(self) -> None:
        """
        Clear the board.
        """
        self.board = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.history.clear()
        self._notify_state_listener()

    def set_state_listener(self, listener: Callable[[], None] | None) -> None:
        """
        Register a callback invoked when public board reseeding operations occur.
        """
        self._state_listener = listener

    def _notify_state_listener(self) -> None:
        if self._state_listener is not None:
            self._state_listener()

    def at(self, position: Coord) -> Piece | None:
        """
        Get the piece at a given position.
        """
        if not self.is_in_bounds(position):
            raise PositionError(f"Position out of bounds {position}")
        return self.board[position.r][position.c]

    def set_at(self, position: Coord, piece: Piece | None) -> None:
        """
        Set a piece at a given position and reseed history from the new board state.

        This method is intended for setup-time board editing. Direct mutations
        invalidate existing undo/redo history, so the current position becomes
        the new baseline state.
        """
        self._set_at(position, piece)
        self.history.seed_current_state()
        self._notify_state_listener()

    def _set_at(self, position: Coord, piece: Piece | None) -> None:
        """
        Low-level placement primitive used by move application and effects.
        """
        if not self.is_in_bounds(position):
            raise PositionError(f"Position out of bounds {position}")
        self.board[position.r][position.c] = piece

    def type_at(self, position: Coord) -> PieceClass | None:
        """
        Get the type of piece at a given position.
        """
        piece = self.at(position)
        return type(piece) if piece is not None else None

    def side_at(self, position: Coord) -> Side2 | None:
        """
        Get the side of the piece at a given position, returns None if the position is empty.
        """
        piece = self.at(position)
        return piece.side if piece is not None else None

    def move(
        self,
        start: Coord,
        end: Coord,
        move_type: MoveType = "",
        extra_info: MoveExtraInfo | None = None,
    ) -> None:
        """
        Perform a move by a player, not a piece.
        """
        piece = self.at(start)
        if piece is None:
            raise PieceError("No piece at starting position")
        move = Move(start, end, move_type, extra_info)
        resolved_move = self.manager.resolve_move(move)
        if resolved_move is None:
            raise InvalidMoveError("Invalid move!")
        self.manager.apply_move(resolved_move, piece)

    def _apply_move(self, move: Move, piece: Piece) -> None:
        """
        Apply a move that has already been validated.
        """
        self._set_at(move.start, None)
        self._set_at(move.end, piece)
        piece.move(move.end)

    def get_valid_moves(self, piece: Piece | None) -> list[Coord] | None:
        """
        Get the valid moves for a piece at a given position.
        """
        if piece is None:
            return None
        return self.manager.get_validated_moves(piece)

    def is_in_bounds(self, position: Coord) -> bool:
        """
        Check if a position is in bounds.
        """
        return (
            position.r >= 0
            and position.r < self.height
            and position.c >= 0
            and position.c < self.width
        )

    def is_empty(self, position: Coord) -> bool:
        """
        Check if a position is empty.
        """
        return self.at(position) is None

    def is_empty_line(
        self,
        start: Coord,
        end: Coord,
        criteria: Callable[[Coord, Coord], bool] = Coord.is_omnidirectional,
    ) -> bool:
        """
        Checks if the line between two coordinates is empty, following a specific movement rule.

        This method verifies whether all squares along the path from `start` to `end`
        are unoccupied, based on a criteria that must be a `Coord`'s method.

        Args:
            start: The starting coordinate.
            end: The target coordinate.
            criteria: A Coord method that determines the movement rule to follow, must be is_orthogonal, is_diagonal or is_omnidirectional.

        Returns:
            bool: True if the path between `start` and `end` is completely empty; False otherwise.

        Example:
            >>> board.is_empty_line(Coord(0, 0), Coord(0, 7))  # Check if the column is empty
            True

            >>> board.is_empty_line(Coord(2, 2), Coord(5, 5), Coord.is_diagonal)  # Check diagonal path
            False

        Notes:
            - The empty line check is exclusive, meaning that the start and end positions are not included in the check.
        """
        if not (criteria(start, end)):
            return False
        for position in self.iter_positions_line(start, end, criteria):
            if position == start or position == end:
                continue
            if self.at(position) is not None:
                return False
        return True

    def is_enemy(self, position: Coord, side: Side2) -> bool:
        """
        Check if a position contains an enemy piece.
        """
        enemy_side = self.side_at(position)
        if enemy_side is None:
            return False
        return enemy_side != side

    def is_allied(self, position: Coord, side: Side2) -> bool:
        """
        Check if a position contains an allied piece.
        """
        return self.side_at(position) == side
