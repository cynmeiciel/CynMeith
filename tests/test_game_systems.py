from cynmeith import (
    ActionPointSystem,
    Config,
    EliminatePieceCondition,
    FreeTurnPolicy,
    Game,
    GameOutcome,
    MaterialScoreSystem,
    MoveLimitDrawCondition,
    NoLegalMovesCondition,
    Piece,
    PieceCountScoringSystem,
    QuotaTurnPolicy,
    ReachSquareCondition,
    StaticPhaseSystem,
    TurnCountPhaseSystem,
    TwoStagePhaseSystem,
)
from cynmeith.core.move_effects import EffectPresets
from cynmeith.core.move_manager import MoveManager
from cynmeith.utils import Coord
from cynmeith.utils.aliases import InvalidMoveError, Move
from examples.chess.chess_manager import ChessManager


def make_chess_config_data() -> dict:
    return {
        "pieces": {
            "Pawn": {"symbol": "P", "class_path": "examples.chess.pawn"},
            "Rook": {"symbol": "R", "class_path": "examples.chess.rook"},
            "Knight": {"symbol": "N", "class_path": "examples.chess.knight"},
            "Bishop": {"symbol": "B", "class_path": "examples.chess.bishop"},
            "Queen": {"symbol": "Q", "class_path": "examples.chess.queen"},
            "King": {"symbol": "K", "class_path": "examples.chess.king"},
        },
        "width": 8,
        "height": 8,
        "fen": "!",
    }


class ImmobilePiece(Piece):
    symbol = "I"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        return False


class StrikePiece(Piece):
    symbol = "S"

    def is_valid_move(self, new_position: Coord, board) -> bool:
        return new_position == self.position


class StrikeManager(MoveManager):
    def resolve_move(self, move: Move) -> Move | None:
        piece = self.board.at(move.start)
        if piece is None or piece.symbol.upper() != "S":
            return None
        if move.start != move.end:
            return None

        extra = self._build_extra_info(move)
        target = extra.get("target")
        if not isinstance(target, Coord):
            return None
        if not move.start.is_adjacent(target):
            return None

        target_piece = self.board.at(target)
        if target_piece is None or target_piece.side == piece.side:
            return None

        extra["effects"] = EffectPresets.capture(target)
        return Move(move.start, move.end, move.move_type, extra)


def test_eliminate_piece_condition_declares_winner() -> None:
    config = Config.from_data(
        {
            "pieces": {
                "StrikePiece": {
                    "symbol": "S",
                    "class_path": "tests.test_game_systems",
                }
            },
            "width": 3,
            "height": 3,
            "fen": "!",
        }
    )
    game = Game(
        config,
        move_manager=StrikeManager,
        turn_policy=FreeTurnPolicy(),
        win_conditions=[EliminatePieceCondition("S", side=False)],
    )

    actor = game.board.factory.create_piece("S", Coord(1, 1))
    target = game.board.factory.create_piece("s", Coord(1, 2))
    game.board.set_at(Coord(1, 1), actor)
    game.board.set_at(Coord(1, 2), target)

    game.move(Coord(1, 1), Coord(1, 1), extra_info={"target": Coord(1, 2)})

    assert game.outcome == GameOutcome(
        True, "win", "Side False has no `S` pieces remaining."
    )
    assert game.is_over


def test_reach_square_condition_uses_built_in_target_check() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        win_conditions=[ReachSquareCondition(True, Coord(7, 0), piece_symbol="R")],
    )

    rook = game.board.factory.create_piece("R", Coord(6, 0))
    game.board.set_at(Coord(6, 0), rook)

    game.move(Coord(6, 0), Coord(7, 0))

    assert game.outcome == GameOutcome(True, "win", "Side True reached (7, 0).")


def test_no_legal_moves_condition_can_trigger_on_initial_state() -> None:
    config = Config.from_data(
        {
            "pieces": {
                "ImmobilePiece": {
                    "symbol": "I",
                    "class_path": "tests.test_game_systems",
                }
            },
            "width": 3,
            "height": 3,
            "fen": "!",
        }
    )
    game = Game(
        config,
        turn_policy=QuotaTurnPolicy(moves_per_turn=1, starting_side=True),
        win_conditions=[NoLegalMovesCondition()],
    )

    piece = game.board.factory.create_piece("I", Coord(1, 1))
    game.board.set_at(Coord(1, 1), piece)

    assert game.outcome == GameOutcome(False, "win", "Side True has no legal moves.")
    assert game.is_over


def test_move_limit_draw_condition_triggers_after_threshold() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        win_conditions=[MoveLimitDrawCondition(2)],
    )

    white_rook = game.board.factory.create_piece("R", Coord(0, 0))
    black_rook = game.board.factory.create_piece("r", Coord(7, 7))
    game.board.set_at(Coord(0, 0), white_rook)
    game.board.set_at(Coord(7, 7), black_rook)

    game.move(Coord(0, 0), Coord(0, 1))
    assert game.outcome is None

    game.move(Coord(7, 7), Coord(7, 6))
    assert game.outcome == GameOutcome(None, "draw", "Move limit 2 reached.")


def test_static_phase_system_reports_constant_phase() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        phase_system=StaticPhaseSystem("setup"),
    )

    assert game.current_phase == "setup"


def test_turn_count_phase_system_advances_and_restores_on_undo() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        phase_system=TurnCountPhaseSystem({2: "midgame", 4: "endgame"}),
    )

    white_rook = game.board.factory.create_piece("R", Coord(0, 0))
    black_rook = game.board.factory.create_piece("r", Coord(7, 7))
    game.board.set_at(Coord(0, 0), white_rook)
    game.board.set_at(Coord(7, 7), black_rook)

    assert game.current_phase == "opening"

    game.move(Coord(0, 0), Coord(0, 1))
    assert game.current_phase == "opening"

    game.move(Coord(7, 7), Coord(7, 6))
    assert game.current_phase == "midgame"

    game.undo_move()
    assert game.current_phase == "opening"


def test_two_stage_phase_system_switches_after_threshold() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        phase_system=TwoStagePhaseSystem(
            1, opening_phase="deploy", later_phase="battle"
        ),
    )

    rook = game.board.factory.create_piece("R", Coord(0, 0))
    game.board.set_at(Coord(0, 0), rook)

    assert game.current_phase == "deploy"
    game.move(Coord(0, 0), Coord(0, 1))
    assert game.current_phase == "battle"


def test_action_point_system_refreshes_when_turn_changes() -> None:
    action_points = ActionPointSystem(points_per_turn=2, starting_side=True)
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=QuotaTurnPolicy(moves_per_turn=2, starting_side=True),
        resource_system=action_points,
    )

    white_rook = game.board.factory.create_piece("R", Coord(0, 0))
    black_rook = game.board.factory.create_piece("r", Coord(7, 7))
    game.board.set_at(Coord(0, 0), white_rook)
    game.board.set_at(Coord(7, 7), black_rook)

    assert action_points.points_left == {True: 2, False: 2}

    game.move(Coord(0, 0), Coord(0, 1))
    assert action_points.points_left[True] == 1
    game.move(Coord(0, 1), Coord(0, 2))
    assert game.current_side is False
    assert action_points.points_left == {True: 0, False: 2}

    game.move(Coord(7, 7), Coord(7, 6))
    game.move(Coord(7, 6), Coord(7, 5))
    assert game.current_side is True
    assert action_points.points_left == {True: 2, False: 0}

    game.undo_move()
    assert game.current_side is False
    assert action_points.points_left == {True: 0, False: 1}


def test_action_point_system_can_block_moves_under_free_turn_policy() -> None:
    action_points = ActionPointSystem(points_per_turn=1, starting_side=True)
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        resource_system=action_points,
    )

    rook = game.board.factory.create_piece("R", Coord(0, 0))
    game.board.set_at(Coord(0, 0), rook)

    game.move(Coord(0, 0), Coord(0, 1))
    assert not game.can_move(Coord(0, 1), Coord(0, 2))

    try:
        game.move(Coord(0, 1), Coord(0, 2))
        assert False, "Expected InvalidMoveError"
    except InvalidMoveError:
        pass


def test_piece_count_scoring_system_counts_remaining_pieces() -> None:
    config = Config.from_data(
        {
            "pieces": {
                "StrikePiece": {
                    "symbol": "S",
                    "class_path": "tests.test_game_systems",
                }
            },
            "width": 3,
            "height": 3,
            "fen": "!",
        }
    )
    game = Game(
        config,
        move_manager=StrikeManager,
        scoring_system=PieceCountScoringSystem(),
    )

    actor = game.board.factory.create_piece("S", Coord(1, 1))
    target = game.board.factory.create_piece("s", Coord(1, 2))
    game.board.set_at(Coord(1, 1), actor)
    game.board.set_at(Coord(1, 2), target)

    assert game.get_scores() == {True: 1, False: 1}

    game.move(Coord(1, 1), Coord(1, 1), extra_info={"target": Coord(1, 2)})
    assert game.get_scores() == {True: 1, False: 0}


def test_material_score_system_sums_configured_values() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        scoring_system=MaterialScoreSystem({"R": 5, "P": 1}),
    )

    white_rook = game.board.factory.create_piece("R", Coord(0, 0))
    white_pawn = game.board.factory.create_piece("P", Coord(1, 0))
    black_rook = game.board.factory.create_piece("r", Coord(7, 7))
    black_pawn = game.board.factory.create_piece("p", Coord(6, 7))
    game.board.set_at(Coord(0, 0), white_rook)
    game.board.set_at(Coord(1, 0), white_pawn)
    game.board.set_at(Coord(7, 7), black_rook)
    game.board.set_at(Coord(6, 7), black_pawn)

    assert game.get_scores() == {True: 6, False: 6}

    game.board.set_at(Coord(6, 7), None)
    assert game.get_scores() == {True: 6, False: 5}
