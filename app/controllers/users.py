from sqlalchemy.exc import IntegrityError

from app.models.orm import User, Session

from app.utils.security import (
    check_password,
    hash_password,
    jwt_encode
)

from app.utils.exceptions import (
    AuthenticationException,
    EntityExistsException,
    EntityNotFoundException
)


def create_user(user_data: dict):

    try:
        name = f"{user_data.pop('first_name')} {user_data.pop('last_name')}"

        user_data['name'] = name

        password = hash_password(user_data['password'])

        user_data['password'] = password.decode('utf-8')

        with Session() as session:

            user = User(**user_data)

            session.add(user)
            session.commit()

            return user

    except IntegrityError as e:

        raise EntityExistsException(
            "User with E-mail already exists"
        ) from e


def probe_username(username: str):

    """
        Checks the database to see if a username exists
        and returns the ID of the user

    """

    # TODO: cache this on redis

    with Session() as session:

        user = session.query(User).filter_by(username=username).first()

        if user is None:
            return -1, 'Unknown'

        return user.id, user.name


def authenticate_user(email: str, password: str):

    with Session() as session:

        print(email, [user.email for user in session.query(User).all()])
        user = session.query(User).filter_by(email=email).first()

        if user is None:

            raise EntityNotFoundException("User with E-mail does not exist")

        if not check_password(user.password, password):

            raise AuthenticationException("Incorrect Password")

        return jwt_encode({
            'id': user.id,
            'role': 'user'
        })


def update_profile(user_id, updates):

    try:

        if 'password' in updates:

            password = hash_password(updates['password'])
            updates['password'] = password.decode('utf-8')

        with Session() as session:

            update_count = session.query(User).filter_by(
                id=user_id
            ).update(updates)

            session.commit()

            if not update_count:

                raise EntityNotFoundException("User with ID doesn't exist")

            return True

    except IntegrityError:

        raise EntityExistsException("User with username already exists")

