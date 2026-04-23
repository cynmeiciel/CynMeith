"""
CynMeith - A flexible and extensible framework for simulating
and playing board games.
"""

from cynmeith import utils
from cynmeith.core.board import Board, BoardSimulation
from cynmeith.core.config import Config
from cynmeith.core.game import FreeTurnPolicy, Game, QuotaTurnPolicy, TurnPolicy
from cynmeith.core.game_systems import (
    ActionPointSystem,
    EliminatePieceCondition,
    GameOutcome,
    MaterialScoreSystem,
    MoveLimitDrawCondition,
    NoLegalMovesCondition,
    PhaseSystem,
    PieceCountScoringSystem,
    ReachSquareCondition,
    ResourceSystem,
    ScoringSystem,
    StaticPhaseSystem,
    TurnCountPhaseSystem,
    TwoStagePhaseSystem,
    WinCondition,
)
from cynmeith.core.move_effects import (
    EffectPresets,
    MoveEffect,
    MovePieceEffect,
    PromotePieceEffect,
    RemovePieceEffect,
)
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.core.piece_factory import PieceFactory
from cynmeith.core.royal_rules import (
    RoyalCheckmateCondition,
    RoyalRuleset,
    RoyalSafetyMoveManager,
    RoyalStalemateCondition,
)
from cynmeith.utils.aliases import ConfigError

__author__ = "Tran Van Duy"
__all__ = [
    "Board",
    "Config",
    "ConfigError",
    "EffectPresets",
    "ActionPointSystem",
    "BoardSimulation",
    "EliminatePieceCondition",
    "FreeTurnPolicy",
    "Game",
    "GameOutcome",
    "MaterialScoreSystem",
    "MoveEffect",
    "MovePieceEffect",
    "MoveLimitDrawCondition",
    "NoLegalMovesCondition",
    "PhaseSystem",
    "Piece",
    "PieceCountScoringSystem",
    "PromotePieceEffect",
    "ReachSquareCondition",
    "RemovePieceEffect",
    "ResourceSystem",
    "MoveHistory",
    "MoveManager",
    "QuotaTurnPolicy",
    "ScoringSystem",
    "PieceFactory",
    "RoyalCheckmateCondition",
    "RoyalRuleset",
    "RoyalSafetyMoveManager",
    "RoyalStalemateCondition",
    "StaticPhaseSystem",
    "TurnCountPhaseSystem",
    "TurnPolicy",
    "TwoStagePhaseSystem",
    "WinCondition",
    "utils",
]
__version__ = "1.0.0"
