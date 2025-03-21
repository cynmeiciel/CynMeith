"""
CynMeith - A flexible and extensible framework for simulating and playing board games.
"""

from cynmeith.core.board import Board
from cynmeith.core.config import Config
from cynmeith.core.piece import Piece
from cynmeith.core.move_history import MoveHistory
from cynmeith.core.move_manager import MoveManager
from cynmeith.core.piece_factory import PieceFactory
from . import utils

__author__ = "Tran Van Duy"
__all__ = ["Board", "Config", "Piece", "MoveHistory", "MoveManager", "PieceFactory"]
__version__ = "0.1.0"