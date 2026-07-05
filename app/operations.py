"""
operations.py

Core arithmetic operations used by the FastAPI calculator application.
"""


def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b (a - b)."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    return a * b


def divide(a: float, b: float) -> float:
    """
    Return the quotient of a and b (a / b).

    Raises:
        ValueError: if b is zero, since division by zero is undefined.
    """
    if b == 0:
        raise ValueError("Division by zero is not allowed.")
    return a / b
