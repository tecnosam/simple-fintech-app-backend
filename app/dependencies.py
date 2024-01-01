from fastapi import (
    Depends,
    Header
)

from app.utils.security import jwt_decode
from app.utils.exceptions import AuthenticationException


def raise_authorization_exception():
    raise AuthenticationException(
        msg="Invalid Token!"
    )


def get_user_data(token: str = Header()) -> dict:

    try:
        return jwt_decode(token)
    except:
        print("Yooooooo")
        raise_authorization_exception()


def get_user_id(user_data: dict = Depends(get_user_data)):

    if 'id' not in user_data:

        raise_authorization_exception()

    return user_data.get('id')

