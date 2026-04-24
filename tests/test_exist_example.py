from cynmeith import GameOutcome
from cynmeith.utils import Coord
from examples.exist.game import build_game_spec
from examples.exist.exist_turn_policy import ExistTurnSnapshot


def test_exist_place_consumes_reserve_and_requires_end_turn_after_one_action() -> None:
    game = build_game_spec().create_game()

    assert game.can_move(Coord.null(), Coord(3, 3), "PLACE")
    game.move(Coord.null(), Coord(3, 3), "PLACE")

    placed_piece = game.board.at(Coord(3, 3))
    assert placed_piece is not None
    assert placed_piece.get_symbol_with_side() == "X"
    assert game.reserves.get_count(True) == 7
    assert game.current_side is True

    assert not game.can_move(Coord.null(), Coord(4, 4), "PLACE")
    assert game.can_move(Coord.null(), Coord.null(), "END_TURN")

    game.end_turn()
    assert game.current_side is False


def test_exist_tile_capture_adds_captured_piece_to_attackers_reserve() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(3, 3), game.board.factory.create_piece("X", Coord(3, 3)))
    game.board.set_at(Coord(3, 4), game.board.factory.create_piece("x", Coord(3, 4)))

    assert game.reserves.get_count(True) == 7
    assert game.reserves.get_count(False) == 7

    assert game.can_move(Coord.null(), Coord(4, 4), "PLACE")
    game.move(Coord.null(), Coord(4, 4), "PLACE")

    assert game.board.at(Coord(3, 4)) is None
    assert game.board.at(Coord(4, 4)) is not None
    assert game.reserves.get_count(True) == 7
    assert game.current_side is False


def test_exist_place_may_temporarily_break_line_rule_if_capture_fixes_it() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(3, 3), game.board.factory.create_piece("x", Coord(3, 3)))
    game.board.set_at(Coord(2, 2), game.board.factory.create_piece("X", Coord(2, 2)))
    game.board.set_at(Coord(3, 5), game.board.factory.create_piece("X", Coord(3, 5)))

    assert game.can_move(Coord.null(), Coord(3, 4), "PLACE")
    game.move(Coord.null(), Coord(3, 4), "PLACE")

    assert game.board.at(Coord(3, 3)) is None
    assert game.board.at(Coord(3, 4)) is not None
    assert game.board.at(Coord(3, 5)) is not None


def test_exist_tile_restriction_counts_piece_itself_and_neighbors() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(2, 3), game.board.factory.create_piece("X", Coord(2, 3)))
    game.board.set_at(Coord(4, 4), game.board.factory.create_piece("X", Coord(4, 4)))

    assert game.can_move(Coord.null(), Coord(0, 0), "PLACE")
    assert not game.can_move(Coord.null(), Coord(3, 4), "PLACE")


def test_exist_two_pieces_in_same_tile_are_legal() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(3, 3), game.board.factory.create_piece("X", Coord(3, 3)))

    assert game.can_move(Coord.null(), Coord(4, 4), "PLACE")


def test_exist_move_into_existing_dispute_line_captures_other_piece() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(1, 1), game.board.factory.create_piece("x", Coord(1, 1)))
    game.board.set_at(Coord(1, 3), game.board.factory.create_piece("X", Coord(1, 3)))
    game.board.set_at(Coord(2, 2), game.board.factory.create_piece("X", Coord(2, 2)))

    assert game.can_move(Coord(2, 2), Coord(1, 2), "MOVE")
    game.move(Coord(2, 2), Coord(1, 2), "MOVE")

    assert game.board.at(Coord(1, 2)) is not None
    assert game.board.at(Coord(1, 1)) is None
    assert game.board.at(Coord(1, 3)) is not None


def test_exist_creating_new_dispute_line_does_not_capture() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(1, 1), game.board.factory.create_piece("X", Coord(1, 1)))
    game.board.set_at(Coord(2, 3), game.board.factory.create_piece("x", Coord(2, 3)))

    assert game.can_move(Coord(1, 1), Coord(1, 2), "MOVE")
    game.move(Coord(1, 1), Coord(1, 2), "MOVE")

    assert game.board.at(Coord(1, 2)) is not None
    assert game.board.at(Coord(2, 3)) is not None


def test_exist_moving_along_existing_dispute_line_does_not_capture() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    game.board.set_at(Coord(1, 1), game.board.factory.create_piece("X", Coord(1, 1)))
    game.board.set_at(Coord(1, 3), game.board.factory.create_piece("x", Coord(1, 3)))

    assert game.can_move(Coord(1, 3), Coord(1, 4), "MOVE")
    game.move(Coord(1, 3), Coord(1, 4), "MOVE")

    assert game.board.at(Coord(1, 1)) is not None
    assert game.board.at(Coord(1, 4)) is not None


def test_exist_undo_and_redo_restore_reserves() -> None:
    game = build_game_spec().create_game()

    game.move(Coord.null(), Coord(2, 2), "PLACE")
    game.end_turn()

    assert game.current_side is False
    assert game.reserves.get_count(True) == 7

    game.undo_move()
    assert game.current_side is True
    assert game.reserves.get_count(True) == 7

    game.undo_move()
    assert game.board.at(Coord(2, 2)) is None
    assert game.reserves.get_count(True) == 8

    game.redo_move()
    game.redo_move()
    assert game.board.at(Coord(2, 2)) is not None
    assert game.current_side is False
    assert game.reserves.get_count(True) == 7


def test_exist_draw_only_triggers_at_turn_boundary() -> None:
    game = build_game_spec().create_game()
    game.board.clear()

    placements = [
        Coord(0, 0),
        Coord(0, 1),
        Coord(1, 0),
        Coord(1, 1),
        Coord(2, 0),
        Coord(2, 1),
        Coord(3, 0),
        Coord(3, 1),
        Coord(4, 0),
        Coord(4, 1),
        Coord(5, 0),
        Coord(5, 1),
        Coord(6, 0),
        Coord(6, 1),
        Coord(7, 0),
        Coord(7, 1),
    ]
    for index, position in enumerate(placements):
        symbol = "X" if index % 2 == 0 else "x"
        game.board.set_at(position, game.board.factory.create_piece(symbol, position))

    draw_condition = game.win_conditions[0]
    snapshot = game.turn_policy.snapshot()
    game.turn_policy.restore(
        ExistTurnSnapshot(
            side=snapshot.side,
            turn_index=snapshot.turn_index,
            actions_this_turn=1,
            turn_kind="non_capture",
            last_action_type="PLACE",
        )
    )
    assert draw_condition.evaluate(game) is None

    game.turn_policy.restore(snapshot)
    assert draw_condition.evaluate(game) == GameOutcome(
        None,
        "draw",
        "All 16 pieces are on the board.",
    )
