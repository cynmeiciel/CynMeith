from cynmeith import Board
from cynmeith.utils import Coord, InvalidMoveError, PieceError


def test_board_init(board):
    """
    Test the initialization of a board.
    """
    assert board.width == 8
    assert board.height == 8
    assert board.at(Coord(0, 0)).get_symbol_with_side() == "R"
    assert board.at(Coord(0, 1)).get_symbol_with_side() == "N"
    assert board.at(Coord(0, 2)).get_symbol_with_side() == "B"
    assert board.at(Coord(0, 3)).get_symbol_with_side() == "Q"
    assert board.at(Coord(0, 4)).get_symbol_with_side() == "K"
    assert board.at(Coord(0, 5)).get_symbol_with_side() == "B"
    assert board.at(Coord(0, 6)).get_symbol_with_side() == "N"
    assert board.at(Coord(0, 7)).get_symbol_with_side() == "R"
    assert board.at(Coord(1, 0)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 1)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 2)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 3)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 4)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 5)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 6)).get_symbol_with_side() == "P"
    assert board.at(Coord(1, 7)).get_symbol_with_side() == "P"
    assert board.at(Coord(6, 0)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 1)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 2)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 3)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 4)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 5)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 6)).get_symbol_with_side() == "p"
    assert board.at(Coord(6, 7)).get_symbol_with_side() == "p"
    assert board.at(Coord(7, 0)).get_symbol_with_side() == "r"
    assert board.at(Coord(7, 1)).get_symbol_with_side() == "n"
    assert board.at(Coord(7, 2)).get_symbol_with_side() == "b"
    assert board.at(Coord(7, 3)).get_symbol_with_side() == "q"
    assert board.at(Coord(7, 4)).get_symbol_with_side() == "k"
    assert board.at(Coord(7, 5)).get_symbol_with_side() == "b"
    assert board.at(Coord(7, 6)).get_symbol_with_side() == "n"
    assert board.at(Coord(7, 7)).get_symbol_with_side() == "r"


def test_board_getset(board):
    """
    Test getting and setting pieces on the board.
    """
    assert board.at(Coord(0, 0)).get_symbol_with_side() == "R"
    board.set_at(Coord(0, 0), None)
    assert board.at(Coord(0, 0)) is None
    board.set_at(Coord(0, 0), board.at(Coord(0, 1)))
    assert board.at(Coord(0, 0)).get_symbol_with_side() == "N"


def test_board_move(board):
    """
    Test moving pieces on the board.
    """
    start = Coord(1, 0)
    end = Coord(2, 0)
    board.move(start, end)
    assert board.at(start) is None
    assert board.at(end).get_symbol_with_side() == "P"

    start = Coord(6, 0)
    end = Coord(4, 0)
    board.move(start, end)
    assert board.at(start) is None
    assert board.at(end).get_symbol_with_side() == "p"


def test_invalid_move(board):
    """
    Test invalid moves that raise exceptions.
    """
    start = Coord(0, 0)
    end = Coord(4, 0)
    try:
        board.move(start, end)
        assert False, "Expected InvalidMoveError"
    except InvalidMoveError:
        pass


def test_is_empty_line(board):
    """
    Test the is_empty_line method.
    """
    assert not board.is_empty_line(Coord(0, 0), Coord(0, 4), Coord.is_horizontal)
    assert not board.is_empty_line(Coord(0, 0), Coord(4, 0), Coord.is_vertical)

    assert board.is_empty_line(Coord(3, 3), Coord(3, 6), Coord.is_horizontal)
    assert not board.is_empty_line(Coord(3, 3), Coord(3, 7), Coord.is_vertical)


def test_is_enemy_and_is_allied(board):
    """
    Test the is_enemy and is_allied methods.
    """
    assert not board.is_enemy(Coord(1, 0), True)
    assert board.is_enemy(Coord(1, 0), False)
    assert not board.is_allied(Coord(1, 0), False)
    assert board.is_allied(Coord(1, 0), True)
