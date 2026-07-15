"""
Factory for building the correct Calculation subclass from a type string.

This keeps the "which subclass do I instantiate" decision in one place
instead of scattering if/elif chains through routes/services later
(Module 12 BREAD routes will just call CalculationFactory.create(...)).
"""

from typing import Type

from app.models.calculation import (
    Calculation,
    Addition,
    Subtraction,
    Multiplication,
    Division,
)


class CalculationFactory:
    """Maps a type string to the corresponding Calculation subclass."""

    _registry: dict[str, Type[Calculation]] = {
        "Add": Addition,
        "Sub": Subtraction,
        "Multiply": Multiplication,
        "Divide": Division,
    }

    @classmethod
    def create(cls, calculation_type: str, a: float, b: float, user_id: int) -> Calculation:
        """
        Instantiate the correct Calculation subclass for the given type.

        Raises ValueError for an unknown type or an invalid operand
        combination (e.g. divide by zero), so callers can catch one
        exception type at the API layer later.
        """
        calc_cls = cls._registry.get(calculation_type)
        if calc_cls is None:
            raise ValueError(
                f"Unsupported calculation type: {calculation_type}. "
                f"Must be one of {list(cls._registry.keys())}"
            )

        instance = calc_cls(a=a, b=b, type=calculation_type, user_id=user_id)

        # Validate operands up front (e.g. division by zero) so a bad
        # calculation never even makes it to compute_and_store()/commit().
        instance.get_result()

        return instance

    @classmethod
    def register(cls, calculation_type: str, calc_cls: Type[Calculation]) -> None:
        """Allows extending with new operation types without editing this file's core logic."""
        cls._registry[calculation_type] = calc_cls
