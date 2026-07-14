import pytest
from sqlalchemy.exc import IntegrityError

from app.models.user import User
from app.security import hash_password, verify_password


def test_create_user(db_session):
    user = User(
        username="jayfull",
        email="jay@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    assert user.id is not None
    assert user.created_at is not None
    assert verify_password("password123", user.password_hash) is True


def test_duplicate_username_raises_integrity_error(db_session):
    user1 = User(
        username="jayfull",
        email="jay1@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        username="jayfull",
        email="jay2@example.com",
        password_hash=hash_password("password456"),
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_duplicate_email_raises_integrity_error(db_session):
    user1 = User(
        username="jayfull1",
        email="jay@example.com",
        password_hash=hash_password("password123"),
    )
    db_session.add(user1)
    db_session.commit()

    user2 = User(
        username="jayfull2",
        email="jay@example.com",
        password_hash=hash_password("password456"),
    )
    db_session.add(user2)
    with pytest.raises(IntegrityError):
        db_session.commit()