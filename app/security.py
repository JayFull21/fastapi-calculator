"""Password hashing """

import bcrypt

_MAX_BCRYPT_BYTES = 72


def hash_password(password: str) -> str:
    """Hash a plain-text password for storage."""
    password_bytes = password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    password_bytes = plain_password.encode("utf-8")[:_MAX_BCRYPT_BYTES]
    hash_bytes = password_hash.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hash_bytes)