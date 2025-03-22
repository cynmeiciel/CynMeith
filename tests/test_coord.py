import pytest

from cynmeith.utils.coord import Coord


def test_coord_addition():
    """Test vector addition with Coord."""
    assert Coord(1, 1) + Coord(2, 3) == Coord(3, 4)
    assert Coord(5, 5) + 2 == Coord(7, 7)


def test_coord_subtraction():
    """Test vector subtraction with Coord."""
    assert Coord(4, 4) - Coord(1, 1) == Coord(3, 3)
    assert Coord(5, 5) - 2 == Coord(3, 3)


def test_coord_multiplication():
    """Test element-wise multiplication."""
    assert Coord(2, 3) * 2 == Coord(4, 6)
    assert Coord(2, 3) * Coord(3, 2) == Coord(6, 6)


def test_coord_floordiv():
    """Test integer division of coordinates."""
    assert Coord(6, 9) // 3 == Coord(2, 3)
    assert Coord(8, 6) // Coord(2, 3) == Coord(4, 2)


def test_creation_methods():
    """Test directional vector methods."""
    assert Coord.up() == Coord(-1, 0)
    assert Coord.down() == Coord(1, 0)
    assert Coord.left() == Coord(0, -1)
    assert Coord.right() == Coord(0, 1)
    assert Coord.from_str("3:4") == Coord(3, 4)
    assert Coord.batch((1, 2), (3, 4)) == [Coord(1, 2), Coord(3, 4)]
    assert Coord.null() == Coord(-1, -1)


def test_is_lshape():
    """Test if two coordinates are L-shaped."""
    assert Coord(1, 1).is_lshape(Coord(2, 3))
    assert not Coord(3, 3).is_lshape(Coord(3, 5))
    assert Coord(1, 3).is_lshape(Coord(2, 1))
    assert not Coord(3, 3).is_lshape(Coord(4, 6))


def test_is_diagonal():
    """Test if two coordinates are diagonally aligned."""
    assert Coord(2, 2).is_diagonal(Coord(4, 4))
    assert not Coord(3, 3).is_diagonal(Coord(3, 5))
    assert Coord(1, 3).is_diagonal(Coord(4, 0))
    assert not Coord(3, 3).is_diagonal(Coord(4, 5))


def test_is_orthogonal():
    """Test if two coordinates are orthogonally aligned."""
    assert Coord(2, 3).is_orthogonal(Coord(2, 8)) is True
    assert Coord(3, 3).is_orthogonal(Coord(4, 5)) is False


def test_is_omnidirectional():
    """Test if two coordinates are either diagonal or orthogonal."""
    assert Coord(1, 1).is_omnidirectional(Coord(4, 4)) is True
    assert Coord(5, 5).is_omnidirectional(Coord(5, 2)) is True
    assert Coord(3, 3).is_omnidirectional(Coord(4, 5)) is False


def test_manhattan_distance():
    """Test Manhattan distance calculation."""
    assert Coord(1, 1).manhattan_to(Coord(4, 5)) == 7
    assert Coord(3, 3).manhattan_to(Coord(3, 3)) == 0
    assert Coord(3, 3).manhattan_to(Coord(4, 4)) == 2


def test_chebyshev_distance():
    """Test Chebyshev distance calculation."""
    assert Coord(1, 1).chebyshev_to(Coord(4, 5)) == 4
    assert Coord(3, 3).chebyshev_to(Coord(3, 3)) == 0


def test_mirror():
    """Test mirroring coordinates on a board."""
    assert Coord(2, 3).mirror(8, 8, "h") == Coord(2, 4)
    assert Coord(2, 3).mirror(8, 8, "v") == Coord(5, 3)
    assert Coord(2, 3).mirror(8, 8, "hv") == Coord(5, 4)
    try:
        Coord(2, 3).mirror(8, 8, "d")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_direction_unit():
    """Test direction unit vector calculation."""
    assert Coord(2, 2).direction_unit(Coord(5, 5)) == Coord(1, 1)
    assert Coord(4, 4).direction_unit(Coord(4, 1)) == Coord(0, -1)
    assert Coord(3, 3).direction_unit(Coord(3, 3)) == Coord(0, 0)
