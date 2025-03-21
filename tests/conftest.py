import pytest

from cynmeith import Board, Config


@pytest.fixture
def board():
    config = Config("examples/chess/testchess.yaml")
    board = Board(config)
    return board
