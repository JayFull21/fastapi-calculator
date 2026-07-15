"""
Integration tests for the Calculation model against a real Postgres
database (matches the postgres service container in the GitHub Actions
workflow).

Uses the db_session and test_user fixtures from tests/conftest.py.
"""

import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from app.factory.calculation_factory import CalculationFactory
from app.models.calculation import Calculation


def test_insert_calculation_stores_correct_data(db_session, test_user):
    calc = CalculationFactory.create("Add", a=7, b=3, user_id=test_user.id)
    calc.compute_and_store()

    db_session.add(calc)
    db_session.commit()
    db_session.refresh(calc)

    fetched = db_session.query(Calculation).filter_by(id=calc.id).one()
    assert fetched.a == 7
    assert fetched.b == 3
    assert fetched.type == "Add"
    assert fetched.result == 10
    assert fetched.user_id == test_user.id


def test_insert_all_operation_types(db_session, test_user):
    cases = [
        ("Add", 2, 3, 5),
        ("Sub", 10, 4, 6),
        ("Multiply", 3, 4, 12),
        ("Divide", 10, 2, 5),
    ]
    for op_type, a, b, expected in cases:
        calc = CalculationFactory.create(op_type, a=a, b=b, user_id=test_user.id)
        calc.compute_and_store()
        db_session.add(calc)
    db_session.commit()

    rows = db_session.query(Calculation).filter_by(user_id=test_user.id).all()
    results = {row.type: row.result for row in rows}
    for op_type, _, _, expected in cases:
        assert results[op_type] == expected


def test_invalid_type_never_reaches_database(db_session, test_user):
    with pytest.raises(ValueError, match="Unsupported calculation type"):
        CalculationFactory.create("Modulo", a=1, b=1, user_id=test_user.id)

    count = db_session.query(Calculation).filter_by(user_id=test_user.id).count()
    assert count == 0


def test_division_by_zero_never_reaches_database(db_session, test_user):
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        CalculationFactory.create("Divide", a=5, b=0, user_id=test_user.id)

    count = (
        db_session.query(Calculation)
        .filter_by(user_id=test_user.id, type="Divide")
        .count()
    )
    assert count == 0


def test_calculation_requires_valid_user_foreign_key(db_session):
    """A user_id that doesn't exist should be rejected by the FK constraint."""
    nonexistent_user_id = uuid.uuid4()
    calc = CalculationFactory.create("Add", a=1, b=1, user_id=nonexistent_user_id)
    calc.compute_and_store()
    db_session.add(calc)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
