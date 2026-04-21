from cynmeith.utils import Coord


TOP_PALACE_ROWS = range(0, 3)
BOTTOM_PALACE_ROWS = range(7, 10)
PALACE_COLS = range(3, 6)


def in_palace(position: Coord, side: bool) -> bool:
    if side:
        return position.r in TOP_PALACE_ROWS and position.c in PALACE_COLS
    return position.r in BOTTOM_PALACE_ROWS and position.c in PALACE_COLS


def crossed_river(position: Coord, side: bool) -> bool:
    if side:
        return position.r >= 5
    return position.r <= 4


def pieces_between(board, start: Coord, end: Coord) -> int:
    return sum(
        1
        for position in board.iter_positions_line(start, end, Coord.is_orthogonal)
        if position != start and position != end and board.at(position) is not None
    )
