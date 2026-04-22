import pytest

from cynmeith import (
    Config,
    FreeTurnPolicy,
    Game,
    GameOutcome,
    PhaseSystem,
    QuotaTurnPolicy,
    ResourceSystem,
    ScoringSystem,
    WinCondition,
)
from cynmeith.core.move_effects import EffectPresets
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.utils import Coord
from cynmeith.utils.aliases import InvalidMoveError, Move
from examples.chess.chess_manager import ChessManager
from examples.xiangqi.game import build_game_spec as build_xiangqi_spec


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
        "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR",
    }


def make_empty_chess_config_data() -> dict:
    data = make_chess_config_data()
    data["fen"] = "!"
    return data


def test_config_can_be_built_from_data() -> None:
    config = Config.from_data(make_chess_config_data())

    assert config.width == 8
    assert config.height == 8
    assert config.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
    assert config.get_piece_symbol("Pawn") == "P"


def test_game_turn_policy_allows_multi_move_turns_and_restores_on_undo_redo() -> None:
    game = Game(
        Config.from_data(make_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=QuotaTurnPolicy(moves_per_turn=2),
    )

    assert game.current_side is True

    game.move(Coord(1, 0), Coord(2, 0))
    assert game.current_side is True

    game.move(Coord(0, 1), Coord(2, 2))
    assert game.current_side is False

    game.undo_move()
    assert game.current_side is True
    assert game.board.at(Coord(0, 1)).get_symbol_with_side() == "N"
    assert game.board.at(Coord(2, 2)) is None

    game.redo_move()
    assert game.current_side is False
    assert game.board.at(Coord(2, 2)).get_symbol_with_side() == "N"


def test_game_supports_en_passant() -> None:
    game = Game(Config.from_data(make_chess_config_data()), move_manager=ChessManager)

    game.move(Coord(1, 4), Coord(3, 4))
    game.move(Coord(3, 4), Coord(4, 4))
    game.move(Coord(6, 5), Coord(4, 5))

    assert game.can_move(Coord(4, 4), Coord(5, 5))
    game.move(Coord(4, 4), Coord(5, 5))

    assert game.board.at(Coord(4, 5)) is None
    assert game.board.at(Coord(5, 5)).get_symbol_with_side() == "P"


def test_game_supports_explicit_promotion_to_queen() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()), move_manager=ChessManager
    )

    pawn = game.board.factory.create_piece("P", Coord(6, 0))
    game.board.set_at(Coord(6, 0), pawn)

    game.move(Coord(6, 0), Coord(7, 0), extra_info={"promotion": "Q"})
    assert game.board.at(Coord(7, 0)).get_symbol_with_side() == "Q"


def test_game_supports_custom_promotion_piece() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()), move_manager=ChessManager
    )

    pawn = game.board.factory.create_piece("p", Coord(1, 0))
    game.board.set_at(Coord(1, 0), pawn)

    game.move(Coord(1, 0), Coord(0, 0), extra_info={"promotion": "N"})
    assert game.board.at(Coord(0, 0)).get_symbol_with_side() == "n"


def test_manual_setup_resets_undo_baseline() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()), move_manager=ChessManager
    )

    pawn = game.board.factory.create_piece("P", Coord(6, 0))
    game.board.set_at(Coord(6, 0), pawn)

    game.move(Coord(6, 0), Coord(7, 0), extra_info={"promotion": "Q"})
    game.undo_move()

    restored = game.board.at(Coord(6, 0))
    assert restored is not None
    assert restored.get_symbol_with_side() == "P"


def test_game_supports_kingside_castling() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()), move_manager=ChessManager
    )

    white_king = game.board.factory.create_piece("K", Coord(0, 4))
    white_rook = game.board.factory.create_piece("R", Coord(0, 7))
    black_king = game.board.factory.create_piece("k", Coord(7, 4))

    game.board.set_at(Coord(0, 4), white_king)
    game.board.set_at(Coord(0, 7), white_rook)
    game.board.set_at(Coord(7, 4), black_king)

    assert game.can_move(Coord(0, 4), Coord(0, 6))
    game.move(Coord(0, 4), Coord(0, 6))

    assert game.board.at(Coord(0, 6)).get_symbol_with_side() == "K"
    assert game.board.at(Coord(0, 5)).get_symbol_with_side() == "R"
    assert game.board.at(Coord(0, 7)) is None


def test_game_rejects_castling_through_check() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()), move_manager=ChessManager
    )

    white_king = game.board.factory.create_piece("K", Coord(0, 4))
    white_rook = game.board.factory.create_piece("R", Coord(0, 7))
    black_king = game.board.factory.create_piece("k", Coord(7, 7))
    black_rook = game.board.factory.create_piece("r", Coord(3, 5))

    game.board.set_at(Coord(0, 4), white_king)
    game.board.set_at(Coord(0, 7), white_rook)
    game.board.set_at(Coord(7, 7), black_king)
    game.board.set_at(Coord(3, 5), black_rook)

    assert not game.can_move(Coord(0, 4), Coord(0, 6))


def test_game_can_move_returns_false_for_out_of_bounds_positions() -> None:
    game = Game(Config.from_data(make_chess_config_data()), move_manager=ChessManager)

    assert not game.can_move(Coord(1, 0), Coord(-1, 0))
    assert not game.can_move(Coord(99, 0), Coord(0, 0))


class StrikePiece(Piece):
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


class ReachRowWinCondition(WinCondition):
    def __init__(self, side: bool, row: int) -> None:
        self.side = side
        self.row = row

    def evaluate(self, game: Game) -> GameOutcome | None:
        for piece in game.board.iter_pieces():
            if piece is None:
                continue
            if piece.side == self.side and piece.position.r == self.row:
                return GameOutcome(
                    self.side, "win", f"Side {self.side} reached row {self.row}"
                )
        return None


class OpeningOnlyFirstRankPhaseSystem(PhaseSystem):
    def __init__(self) -> None:
        self.phase = "opening"

    def can_move(self, game: Game, piece: Piece, move: Move) -> bool:
        if self.phase == "opening":
            return move.start.r == 0
        return True

    def after_move(self, game: Game, piece: Piece, move: Move) -> None:
        self.phase = "battle"

    def reset(self) -> None:
        self.phase = "opening"

    def snapshot(self) -> str:
        return self.phase

    def restore(self, snapshot: str) -> None:
        self.phase = snapshot

    @property
    def current_phase(self) -> str:
        return self.phase


class SingleChargeResourceSystem(ResourceSystem):
    def __init__(self, starting_charges: int = 1) -> None:
        self.starting_charges = starting_charges
        self.charges = {True: starting_charges, False: starting_charges}

    def can_move(self, game: Game, piece: Piece, move: Move) -> bool:
        return self.charges[piece.side] > 0

    def after_move(self, game: Game, piece: Piece, move: Move) -> None:
        self.charges[piece.side] -= 1

    def reset(self) -> None:
        self.charges = {True: self.starting_charges, False: self.starting_charges}

    def snapshot(self) -> dict[bool, int]:
        return dict(self.charges)

    def restore(self, snapshot: dict[bool, int]) -> None:
        self.charges = dict(snapshot)


class PieceCountScoringSystem(ScoringSystem):
    def reset(self) -> None:
        return None

    def snapshot(self) -> None:
        return None

    def restore(self, snapshot: None) -> None:
        return None

    def get_scores(self, game: Game) -> dict[bool, int]:
        return {
            True: sum(
                1
                for piece in game.board.iter_pieces()
                if piece is not None and piece.side
            ),
            False: sum(
                1
                for piece in game.board.iter_pieces()
                if piece is not None and not piece.side
            ),
        }


def test_game_supports_stationary_skill_move_with_side_effect() -> None:
    config = Config.from_data(
        {
            "pieces": {
                "StrikePiece": {
                    "symbol": "S",
                    "class_path": "tests.test_game",
                }
            },
            "width": 3,
            "height": 3,
            "fen": "!",
        }
    )
    game = Game(config, move_manager=StrikeManager)

    actor = game.board.factory.create_piece("S", Coord(1, 1))
    target = game.board.factory.create_piece("s", Coord(1, 2))
    game.board.set_at(Coord(1, 1), actor)
    game.board.set_at(Coord(1, 2), target)

    assert game.can_move(Coord(1, 1), Coord(1, 1), extra_info={"target": Coord(1, 2)})
    game.move(Coord(1, 1), Coord(1, 1), extra_info={"target": Coord(1, 2)})

    assert game.board.at(Coord(1, 1)).get_symbol_with_side() == "S"
    assert game.board.at(Coord(1, 2)) is None
    assert game.board.history.num_moves == 1
    assert len(game.board.history.move_stack) == 1
    assert len(game.board.history.state_stack) == 2


def test_game_tracks_outcome_and_restores_it_on_undo_redo() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        win_conditions=[ReachRowWinCondition(True, 7)],
    )

    rook = game.board.factory.create_piece("R", Coord(6, 0))
    game.board.set_at(Coord(6, 0), rook)

    assert game.outcome is None
    assert not game.is_over

    game.move(Coord(6, 0), Coord(7, 0))

    assert game.outcome == GameOutcome(True, "win", "Side True reached row 7")
    assert game.is_over
    assert not game.can_move(Coord(7, 0), Coord(7, 1))

    with pytest.raises(InvalidMoveError, match="already over"):
        game.move(Coord(7, 0), Coord(7, 1))

    game.undo_move()
    assert game.outcome is None
    assert not game.is_over

    game.redo_move()
    assert game.outcome == GameOutcome(True, "win", "Side True reached row 7")
    assert game.is_over


def test_game_phase_system_restricts_moves_and_restores_on_undo_redo() -> None:
    game = Game(
        Config.from_data(make_empty_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        phase_system=OpeningOnlyFirstRankPhaseSystem(),
    )

    rook = game.board.factory.create_piece("R", Coord(0, 0))
    pawn = game.board.factory.create_piece("P", Coord(1, 1))
    game.board.set_at(Coord(0, 0), rook)
    game.board.set_at(Coord(1, 1), pawn)

    assert game.current_phase == "opening"
    assert game.can_move(Coord(0, 0), Coord(0, 2))
    assert not game.can_move(Coord(1, 1), Coord(2, 1))

    game.move(Coord(0, 0), Coord(0, 2))
    assert game.current_phase == "battle"
    assert game.can_move(Coord(1, 1), Coord(2, 1))

    game.undo_move()
    assert game.current_phase == "opening"
    assert not game.can_move(Coord(1, 1), Coord(2, 1))

    game.redo_move()
    assert game.current_phase == "battle"


def test_game_resource_system_blocks_spent_side_and_restores_on_undo() -> None:
    resource_system = SingleChargeResourceSystem(starting_charges=1)
    game = Game(
        Config.from_data(make_empty_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=FreeTurnPolicy(),
        resource_system=resource_system,
    )

    rook = game.board.factory.create_piece("R", Coord(0, 0))
    game.board.set_at(Coord(0, 0), rook)

    assert game.can_move(Coord(0, 0), Coord(0, 2))
    game.move(Coord(0, 0), Coord(0, 2))

    assert resource_system.charges[True] == 0
    assert not game.can_move(Coord(0, 2), Coord(0, 3))

    game.undo_move()
    assert resource_system.charges[True] == 1
    assert game.can_move(Coord(0, 0), Coord(0, 2))


def test_game_scoring_system_reports_scores_from_current_state() -> None:
    game = Game(
        Config.from_data(
            {
                "pieces": {
                    "StrikePiece": {
                        "symbol": "S",
                        "class_path": "tests.test_game",
                    }
                },
                "width": 3,
                "height": 3,
                "fen": "!",
            }
        ),
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

    game.undo_move()
    assert game.get_scores() == {True: 1, False: 1}


def test_manual_board_setup_reseeds_game_level_state() -> None:
    phase_system = OpeningOnlyFirstRankPhaseSystem()
    resource_system = SingleChargeResourceSystem(starting_charges=1)
    game = Game(
        Config.from_data(make_empty_chess_config_data()),
        move_manager=ChessManager,
        turn_policy=QuotaTurnPolicy(moves_per_turn=1, starting_side=False),
        phase_system=phase_system,
        resource_system=resource_system,
        win_conditions=[ReachRowWinCondition(True, 7)],
    )

    rook = game.board.factory.create_piece("R", Coord(0, 0))
    game.board.set_at(Coord(0, 0), rook)

    assert game.current_side is False
    assert game.current_phase == "opening"
    assert resource_system.charges == {True: 1, False: 1}
    assert game.outcome is None

    winning_rook = game.board.factory.create_piece("R", Coord(7, 0))
    game.board.set_at(Coord(7, 0), winning_rook)

    assert game.current_side is False
    assert game.current_phase == "opening"
    assert resource_system.charges == {True: 1, False: 1}
    assert game.outcome == GameOutcome(True, "win", "Side True reached row 7")


def test_xiangqi_example_uses_standard_turn_order() -> None:
    game = build_xiangqi_spec().create_game()

    assert game.current_side is True
