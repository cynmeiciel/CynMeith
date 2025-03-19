"""
CynMeith - A flexible and extensible framework for simulating and playing board games.
"""

from .core.board import Board
from .core.config import Config
from .core.piece import Piece
from .core.move_history import MoveHistory
from .core.move_manager import MoveManager
from .core.piece_factory import PieceFactory
from . import utils

__author__ = "Tran Van Duy"
__all__ = ["Board", "Config", "Piece", "MoveHistory", "MoveManager", "PieceFactory"]
__version__ = "0.1.0"