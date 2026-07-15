"""
Unit tests for CalculationCreate / CalculationRead validation.
"""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.calculation import CalculationCreate, CalculationRead, CalculationType

FAKE_USER_ID = uuid.uuid4()


def test_calculation_create_valid():
    calc = CalculationCreate(a=4, b=2, type="Add", user_id=FAKE_USER_ID)
    assert calc.a == 4
    assert calc.type == CalculationType.ADD


def test_calculation_create_rejects_bad_type():
    with pytest.raises(ValidationError):
        CalculationCreate(a=4, b=2, type="Modulo", user_id=FAKE_USER_ID)


def test_calculation_create_rejects_divide_by_zero():
    with pytest.raises(ValidationError, match="Division by zero"):
        CalculationCreate(a=4, b=0, type="Divide", user_id=FAKE_USER_ID)


def test_calculation_create_allows_zero_for_non_divide():
    calc = CalculationCreate(a=4, b=0, type="Add", user_id=FAKE_USER_ID)
    assert calc.b == 0


def test_calculation_create_requires_user_id():
    with pytest.raises(ValidationError):
        CalculationCreate(a=4, b=2, type="Add")


def test_calculation_create_rejects_missing_operand():
    with pytest.raises(ValidationError):
        CalculationCreate(a=4, type="Add", user_id=FAKE_USER_ID)


def test_calculation_create_rejects_invalid_uuid():
    with pytest.raises(ValidationError):
        CalculationCreate(a=4, b=2, type="Add", user_id="not-a-uuid")


def test_calculation_read_serializes_expected_fields():
    calc = CalculationRead(
        id=1,
        a=4,
        b=2,
        type="Add",
        result=6,
        user_id=FAKE_USER_ID,
        created_at=datetime.now(timezone.utc),
    )
    dumped = calc.model_dump()
    assert set(dumped.keys()) == {"a", "b", "type", "id", "result", "user_id", "created_at"}
    assert dumped["result"] == 6
