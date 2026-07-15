import os
import uuid

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models  # noqa: F401  ensures models are registered on Base
from app.models.user import User

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/test_db",
)

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db_session):
    """Creates and commits a User row so calculations have a valid FK target."""
    unique = uuid.uuid4().hex[:8]
    user = User(
        username=f"calc_user_{unique}",
        email=f"calc_user_{unique}@example.com",
        password_hash="not_a_real_hash_just_for_tests",
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user
