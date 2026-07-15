"""
Unit tests confirming the factory chooses the correct subclass and
correctly rejects invalid input.
"""

import uuid

import pytest

from app.factory.calculation_factory import CalculationFactory
from app.models.calculation import Addition, Subtraction, Multiplication, Division

FAKE_USER_ID = uuid.uuid4()


@pytest.mark.parametrize(
    "op_type, expected_cls, a, b, expected_result",
    [
        ("Add", Addition, 2, 3, 5),
        ("Sub", Subtraction, 10, 4, 6),
        ("Multiply", Multiplication, 3, 4, 12),
        ("Divide", Division, 10, 2, 5),
    ],
)
def test_factory_creates_correct_subclass(op_type, expected_cls, a, b, expected_result):
    calc = CalculationFactory.create(op_type, a, b, user_id=FAKE_USER_ID)
    assert isinstance(calc, expected_cls)
    assert calc.get_result() == expected_result


def test_factory_rejects_unknown_type():
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.create("Modulo", 5, 2, user_id=FAKE_USER_ID)


def test_factory_rejects_division_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.create("Divide", 5, 0, user_id=FAKE_USER_ID)
