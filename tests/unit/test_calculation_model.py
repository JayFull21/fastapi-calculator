"""
Unit tests for Calculation model subclasses.

No database session required — these test the pure Python get_result()
logic on unsaved (transient) instances.
"""

import uuid

import pytest

from app.models.calculation import Addition, Subtraction, Multiplication, Division

FAKE_USER_ID = uuid.uuid4()


def test_addition_result():
    calc = Addition(a=4, b=5, type="Add", user_id=FAKE_USER_ID)
    assert calc.get_result() == 9


def test_subtraction_result():
    calc = Subtraction(a=10, b=4, type="Sub", user_id=FAKE_USER_ID)
    assert calc.get_result() == 6


def test_multiplication_result():
    calc = Multiplication(a=3, b=7, type="Multiply", user_id=FAKE_USER_ID)
    assert calc.get_result() == 21


def test_division_result():
    calc = Division(a=20, b=4, type="Divide", user_id=FAKE_USER_ID)
    assert calc.get_result() == 5


def test_division_by_zero_raises():
    calc = Division(a=10, b=0, type="Divide", user_id=FAKE_USER_ID)
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        calc.get_result()


def test_compute_and_store_sets_result():
    calc = Addition(a=2, b=3, type="Add", user_id=FAKE_USER_ID)
    assert calc.result is None
    calc.compute_and_store()
    assert calc.result == 5


@pytest.mark.parametrize(
    "bad_type",
    ["add", "SUBTRACT", "", "Modulo", None],
)
def test_invalid_type_rejected(bad_type):
    with pytest.raises(ValueError):
        Addition(a=1, b=1, type=bad_type, user_id=FAKE_USER_ID)
