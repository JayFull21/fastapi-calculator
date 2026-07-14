from app.security import hash_password, verify_password


def test_hash_password_returns_different_string():
    raw = "SuperSecret123!"
    hashed = hash_password(raw)
    assert hashed != raw
    assert hashed.startswith("$2b$")


def test_verify_password_success():
    raw = "SuperSecret123!"
    hashed = hash_password(raw)
    assert verify_password(raw, hashed) is True


def test_verify_password_failure():
    hashed = hash_password("SuperSecret123!")
    assert verify_password("WrongPassword", hashed) is False


def test_hash_password_is_salted():
    raw = "SuperSecret123!"
    hash_one = hash_password(raw)
    hash_two = hash_password(raw)
    assert hash_one != hash_two