"""
Calculation model.

Single-table inheritance: Addition/Subtraction/Multiplication/Division are
subclasses discriminated by the `type` column, all stored in one
`calculations` table. Each subclass implements its own get_result().

user_id is a UUID foreign key to users.id (matches the User model).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, validates

from app.database import Base


class Calculation(Base):
    """Base calculation row. Polymorphic on `type`."""

    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    a = Column(Float, nullable=False)
    b = Column(Float, nullable=False)
    type = Column(String(20), nullable=False)  # discriminator + operation name
    result = Column(Float, nullable=True)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="calculations")

    __mapper_args__ = {
        "polymorphic_identity": "Calculation",
        "polymorphic_on": type,
    }

    @validates("type")
    def validate_type(self, key, value):
        allowed = {"Add", "Sub", "Multiply", "Divide"}
        if value not in allowed:
            raise ValueError(f"Invalid calculation type: {value}. Must be one of {allowed}")
        return value

    def get_result(self) -> float:
        """Subclasses override this. Base class has no operation."""
        raise NotImplementedError("Subclasses must implement get_result()")

    def compute_and_store(self) -> float:
        """Compute the result and persist it on the instance (call before commit)."""
        self.result = self.get_result()
        return self.result

    def __repr__(self):
        return f"<Calculation(id={self.id}, type={self.type}, a={self.a}, b={self.b}, result={self.result})>"


class Addition(Calculation):
    __mapper_args__ = {"polymorphic_identity": "Add"}

    def get_result(self) -> float:
        return self.a + self.b


class Subtraction(Calculation):
    __mapper_args__ = {"polymorphic_identity": "Sub"}

    def get_result(self) -> float:
        return self.a - self.b


class Multiplication(Calculation):
    __mapper_args__ = {"polymorphic_identity": "Multiply"}

    def get_result(self) -> float:
        return self.a * self.b


class Division(Calculation):
    __mapper_args__ = {"polymorphic_identity": "Divide"}

    def get_result(self) -> float:
        if self.b == 0:
            raise ValueError("Cannot divide by zero")
        return self.a / self.b
