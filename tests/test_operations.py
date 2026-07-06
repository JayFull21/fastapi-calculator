

import pytest

from app import operations


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (-1, 1, 0),
    (-5, -5, -10),
    (0, 0, 0),
    (2.5, 2.5, 5.0),
])
def test_add(a, b, expected):
    assert operations.add(a, b) == expected


# ---------------------------------------------------------------------------
# subtract
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (5, 3, 2),
    (3, 5, -2),
    (0, 0, 0),
    (-5, -5, 0),
    (2.5, 0.5, 2.0),
])
def test_subtract(a, b, expected):
    assert operations.subtract(a, b) == expected


# ---------------------------------------------------------------------------
# multiply
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (3, 4, 12),
    (-3, 4, -12),
    (0, 100, 0),
    (-2, -2, 4),
    (2.5, 2, 5.0),
])
def test_multiply(a, b, expected):
    assert operations.multiply(a, b) == expected


# ---------------------------------------------------------------------------
# divide
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("a, b, expected", [
    (10, 2, 5),
    (9, 3, 3),
    (-10, 2, -5),
    (5, 2, 2.5),
])
def test_divide(a, b, expected):
    assert operations.divide(a, b) == expected


def test_divide_by_zero_raises_value_error():
    with pytest.raises(ValueError, match="Division by zero is not allowed."):
        operations.divide(10, 0)
