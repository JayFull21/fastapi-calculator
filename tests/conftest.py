import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import User
from app.security import hash_password


@pytest.fixture(autouse=True)
def fresh_database():
    """Drop and recreate all tables before every test for isolation."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ---- Module 11 fixtures (restored) ----
@pytest.fixture
def db_session():
    """Raw SQLAlchemy session for direct DB-level integration tests."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture
def test_user(db_session):
    """A persisted user for calculation FK tests."""
    user = User(
        username="fixtureuser",
        email="fixtureuser@example.com",
        password_hash=hash_password("Password123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ---- Module 12 fixtures ----
@pytest.fixture
def registered_user(client):
    payload = {
        "username": "jaytest",
        "email": "jaytest@example.com",
        "password": "SuperSecret123",
    }
    resp = client.post("/users/register", json=payload)
    assert resp.status_code == 201
    return payload


@pytest.fixture
def auth_headers(client, registered_user):
    resp = client.post(
        "/users/login",
        json={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}