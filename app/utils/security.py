from bcrypt import hashpw, checkpw, gensalt

import jwt


from app.utils.settings import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM
)


def hash_password(string: str) -> bytes:

    salt = gensalt()

    return hashpw(string.encode('utf-8'), salt)


def check_password(hashed_password: str | bytes, string: str) -> bool:

    if isinstance(hashed_password, str):

        hashed_password = hashed_password.encode('utf-8')

    string = string.encode('utf-8')

    return checkpw(string, hashed_password)


def jwt_encode(data: dict | list) -> str:

    return jwt.encode(data, JWT_SECRET_KEY, JWT_ALGORITHM)


def jwt_decode(token: str | bytes) -> dict | list:

    return jwt.decode(token, JWT_SECRET_KEY, [JWT_ALGORITHM])

