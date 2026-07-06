

from sqlalchemy import Column, Integer, String, Float, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    calculations = relationship(
        "Calculation", back_populates="user", cascade="all, delete-orphan"
    )


class Calculation(Base):
    __tablename__ = "calculations"

    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String(20), nullable=False)
    operand_a = Column(Float, nullable=False)
    operand_b = Column(Float, nullable=False)
    result = Column(Float, nullable=False)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="calculations")
