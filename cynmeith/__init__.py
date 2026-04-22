"""
CynMeith - A flexible and extensible framework for simulating
and playing board games.
"""

from cynmeith import utils
from cynmeith.core.board import Board
from cynmeith.core.config import Config
from cynmeith.core.game import FreeTurnPolicy, Game, QuotaTurnPolicy, TurnPolicy
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

__author__ = "Tran Van Duy"
__all__ = [
    "Board",
    "Config",
    "EffectPresets",
    "FreeTurnPolicy",
    "Game",
    "MoveEffect",
    "MovePieceEffect",
    "Piece",
    "PromotePieceEffect",
    "RemovePieceEffect",
    "MoveHistory",
    "MoveManager",
    "QuotaTurnPolicy",
    "PieceFactory",
    "TurnPolicy",
    "utils",
]
__version__ = "1.0.0"
