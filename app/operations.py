

import logging

logger = logging.getLogger("calculator.operations")


def add(a: float, b: float) -> float:
    """Return the sum of a and b."""
    result = a + b
    logger.info(f"ADD: {a} + {b} = {result}")
    return result


def subtract(a: float, b: float) -> float:
    """Return the difference of a and b (a - b)."""
    result = a - b
    logger.info(f"SUBTRACT: {a} - {b} = {result}")
    return result


def multiply(a: float, b: float) -> float:
    """Return the product of a and b."""
    result = a * b
    logger.info(f"MULTIPLY: {a} * {b} = {result}")
    return result


def divide(a: float, b: float) -> float:
    """
    Return the quotient of a and b (a / b).

    Raises:
        ValueError: if b is zero, since division by zero is undefined.
    """
    if b == 0:
        logger.error(f"DIVIDE: Attempted division by zero ({a} / {b})")
        raise ValueError("Division by zero is not allowed.")
    result = a / b
    logger.info(f"DIVIDE: {a} / {b} = {result}")
    return result
