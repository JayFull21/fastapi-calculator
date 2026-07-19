from app.database import SessionLocal
from app.models import User


def test_register_user_success(client):
    resp = client.post(
        "/users/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "Password123",
        },
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_persists_user_with_hashed_password(client):
    client.post(
        "/users/register",
        json={
            "username": "dbcheck",
            "email": "dbcheck@example.com",
            "password": "Password123",
        },
    )
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == "dbcheck").first()
        assert user is not None
        assert user.email == "dbcheck@example.com"
        # Password must be stored hashed, never in plaintext
        assert user.password_hash != "Password123"
        assert user.password_hash.startswith("$2")  # bcrypt prefix
    finally:
        db.close()


def test_register_duplicate_username_fails(client, registered_user):
    resp = client.post(
        "/users/register",
        json={
            "username": registered_user["username"],
            "email": "different@example.com",
            "password": "Password123",
        },
    )
    assert resp.status_code == 400
    assert "already registered" in resp.json()["detail"]


def test_register_duplicate_email_fails(client, registered_user):
    resp = client.post(
        "/users/register",
        json={
            "username": "differentname",
            "email": registered_user["email"],
            "password": "Password123",
        },
    )
    assert resp.status_code == 400


def test_register_invalid_email_fails(client):
    resp = client.post(
        "/users/register",
        json={
            "username": "bademail",
            "email": "not-an-email",
            "password": "Password123",
        },
    )
    assert resp.status_code == 422


def test_register_short_password_fails(client):
    resp = client.post(
        "/users/register",
        json={
            "username": "shortpw",
            "email": "shortpw@example.com",
            "password": "abc",
        },
    )
    assert resp.status_code == 422


def test_login_success_returns_token(client, registered_user):
    resp = client.post(
        "/users/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20
    assert data["user"]["username"] == registered_user["username"]


def test_login_with_email_works(client, registered_user):
    resp = client.post(
        "/users/login",
        json={
            "username": registered_user["email"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200


def test_login_wrong_password_fails(client, registered_user):
    resp = client.post(
        "/users/login",
        json={
            "username": registered_user["username"],
            "password": "WrongPassword999",
        },
    )
    assert resp.status_code == 401


def test_login_unknown_user_fails(client):
    resp = client.post(
        "/users/login",
        json={"username": "ghost", "password": "Password123"},
    )
    assert resp.status_code == 401
