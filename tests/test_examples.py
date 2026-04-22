from cynmeith import Config, Game, GameOutcome, QuotaTurnPolicy
from cynmeith.utils import Coord
from examples.chess.chess_manager import ChessManager
from examples.chess.game import (
    _build_chess_config_data,
    _build_win_conditions as build_chess_win_conditions,
    build_game_spec as build_chess_spec,
)
from examples.xiangqi.game import (
    _build_win_conditions as build_xiangqi_win_conditions,
    _build_xiangqi_config_data,
    build_game_spec as build_xiangqi_spec,
)
from examples.xiangqi.xiangqi_manager import XiangqiManager


def test_chess_example_rejects_moves_that_leave_king_in_check() -> None:
    game = build_chess_spec("data").create_game()
    game.board.clear()

    white_king = game.board.factory.create_piece("K", Coord(0, 4))
    white_rook = game.board.factory.create_piece("R", Coord(1, 4))
    black_king = game.board.factory.create_piece("k", Coord(7, 7))
    black_rook = game.board.factory.create_piece("r", Coord(7, 4))
    game.board.set_at(Coord(0, 4), white_king)
    game.board.set_at(Coord(1, 4), white_rook)
    game.board.set_at(Coord(7, 7), black_king)
    game.board.set_at(Coord(7, 4), black_rook)

    assert not game.can_move(Coord(1, 4), Coord(1, 5))


def test_chess_example_disallows_king_capture() -> None:
    game = build_chess_spec("data").create_game()
    game.board.clear()

    white_king = game.board.factory.create_piece("K", Coord(0, 7))
    white_rook = game.board.factory.create_piece("R", Coord(0, 0))
    black_king = game.board.factory.create_piece("k", Coord(0, 4))
    game.board.set_at(Coord(0, 7), white_king)
    game.board.set_at(Coord(0, 0), white_rook)
    game.board.set_at(Coord(0, 4), black_king)

    assert game.get_scores() == {True: 5, False: 0}
    assert not game.can_move(Coord(0, 0), Coord(0, 4))


def test_chess_example_detects_fools_mate_as_checkmate() -> None:
    game = build_chess_spec("data").create_game()

    game.move(Coord(1, 5), Coord(2, 5))
    game.move(Coord(6, 4), Coord(4, 4))
    game.move(Coord(1, 6), Coord(3, 6))
    game.move(Coord(7, 3), Coord(3, 7))

    assert game.outcome == GameOutcome(False, "win", "Checkmate.")
    assert game.is_over


def test_chess_example_stalemate_is_a_draw() -> None:
    game = Game(
        Config.from_data(_build_chess_config_data()),
        ChessManager,
        turn_policy=QuotaTurnPolicy(moves_per_turn=1, starting_side=False),
        win_conditions=build_chess_win_conditions(),
    )
    game.board.clear()

    white_king = game.board.factory.create_piece("K", Coord(5, 2))
    white_queen = game.board.factory.create_piece("Q", Coord(5, 1))
    black_king = game.board.factory.create_piece("k", Coord(7, 0))
    game.board.set_at(Coord(5, 2), white_king)
    game.board.set_at(Coord(5, 1), white_queen)
    game.board.set_at(Coord(7, 0), black_king)

    assert game.outcome == GameOutcome(None, "draw", "Stalemate.")
    assert game.is_over


def test_xiangqi_example_rejects_moves_that_leave_general_in_check() -> None:
    game = build_xiangqi_spec("data").create_game()
    game.board.clear()

    red_general = game.board.factory.create_piece("G", Coord(0, 4))
    red_chariot = game.board.factory.create_piece("R", Coord(1, 4))
    black_general = game.board.factory.create_piece("g", Coord(9, 4))
    black_chariot = game.board.factory.create_piece("r", Coord(7, 4))
    game.board.set_at(Coord(0, 4), red_general)
    game.board.set_at(Coord(1, 4), red_chariot)
    game.board.set_at(Coord(9, 4), black_general)
    game.board.set_at(Coord(7, 4), black_chariot)

    assert not game.can_move(Coord(1, 4), Coord(1, 5))


def test_xiangqi_example_disallows_general_capture() -> None:
    game = build_xiangqi_spec("data").create_game()
    game.board.clear()

    red_general = game.board.factory.create_piece("G", Coord(0, 4))
    red_chariot = game.board.factory.create_piece("R", Coord(9, 0))
    black_general = game.board.factory.create_piece("g", Coord(9, 4))
    game.board.set_at(Coord(0, 4), red_general)
    game.board.set_at(Coord(9, 0), red_chariot)
    game.board.set_at(Coord(9, 4), black_general)

    assert not game.can_move(Coord(9, 0), Coord(9, 4))


def test_xiangqi_example_stalemate_is_a_loss_for_the_side_to_move() -> None:
    game = Game(
        Config.from_data(_build_xiangqi_config_data()),
        XiangqiManager,
        turn_policy=QuotaTurnPolicy(moves_per_turn=1, starting_side=False),
        win_conditions=build_xiangqi_win_conditions(),
    )
    game.board.clear()

    red_general = game.board.factory.create_piece("G", Coord(0, 4))
    black_general = game.board.factory.create_piece("g", Coord(9, 4))
    left_chariot = game.board.factory.create_piece("R", Coord(8, 3))
    right_chariot = game.board.factory.create_piece("R", Coord(8, 5))
    center_chariot = game.board.factory.create_piece("R", Coord(8, 0))
    blocker = game.board.factory.create_piece("S", Coord(5, 4))
    game.board.set_at(Coord(0, 4), red_general)
    game.board.set_at(Coord(9, 4), black_general)
    game.board.set_at(Coord(8, 3), left_chariot)
    game.board.set_at(Coord(8, 5), right_chariot)
    game.board.set_at(Coord(8, 0), center_chariot)
    game.board.set_at(Coord(5, 4), blocker)

    assert game.outcome == GameOutcome(True, "win", "No legal moves.")
