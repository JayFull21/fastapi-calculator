"""
Pydantic schemas for the Calculation model.

CalculationCreate validates incoming data (type enum + divide-by-zero
rejection at the schema level). CalculationRead defines the serialized
output shape.
"""

import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, model_validator, ConfigDict


class CalculationType(str, Enum):
    ADD = "Add"
    SUB = "Sub"
    MULTIPLY = "Multiply"
    DIVIDE = "Divide"


class CalculationBase(BaseModel):
    a: float = Field(..., description="First operand")
    b: float = Field(..., description="Second operand")
    type: CalculationType = Field(..., description="Operation type")


class CalculationCreate(CalculationBase):
    """Schema for incoming calculation requests."""

    user_id: uuid.UUID = Field(..., description="ID of the user this calculation belongs to")

    @model_validator(mode="after")
    def validate_operands(self) -> "CalculationCreate":
        if self.type == CalculationType.DIVIDE and self.b == 0:
            raise ValueError("Division by zero is not allowed")
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "a": 10,
                "b": 2,
                "type": "Divide",
                "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            }
        }
    )


class CalculationRead(CalculationBase):
    """Schema for calculation responses."""

    id: int
    result: float | None = None
    user_id: uuid.UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
