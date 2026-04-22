"""
The core module contains the core classes and functions
of the CynMeith package.
"""

from cynmeith.core.board import Board
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
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece import Piece
from cynmeith.core.piece_factory import PieceFactory
from cynmeith.core.royal_rules import (
    BoardSimulation,
    RoyalCheckmateCondition,
    RoyalRuleset,
    RoyalSafetyMoveManager,
    RoyalStalemateCondition,
)

__all__ = [
    "Board",
    "BoardSimulation",
    "Config",
    "ActionPointSystem",
    "EliminatePieceCondition",
    "FreeTurnPolicy",
    "Game",
    "GameOutcome",
    "MaterialScoreSystem",
    "MoveHistory",
    "MoveLimitDrawCondition",
    "MoveManager",
    "NoLegalMovesCondition",
    "PhaseSystem",
    "Piece",
    "PieceFactory",
    "PieceCountScoringSystem",
    "QuotaTurnPolicy",
    "ReachSquareCondition",
    "ResourceSystem",
    "RoyalCheckmateCondition",
    "RoyalRuleset",
    "RoyalSafetyMoveManager",
    "RoyalStalemateCondition",
    "ScoringSystem",
    "StaticPhaseSystem",
    "TurnCountPhaseSystem",
    "TurnPolicy",
    "TwoStagePhaseSystem",
    "WinCondition",
]
