import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_user_create_valid():
    user = UserCreate(username="jayfull", email="jay@example.com", password="password123")
    assert user.username == "jayfull"
    assert user.email == "jay@example.com"


def test_user_create_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(username="jayfull", email="not-an-email", password="password123")


def test_user_create_password_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="jayfull", email="jay@example.com", password="short")


def test_user_create_username_too_short():
    with pytest.raises(ValidationError):
        UserCreate(username="jj", email="jay@example.com", password="password123")


def test_user_create_missing_field_raises():
    with pytest.raises(ValidationError):
        UserCreate(username="jayfull", password="password123")