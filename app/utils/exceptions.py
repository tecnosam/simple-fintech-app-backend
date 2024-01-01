

class AppException(Exception):

    def __init__(self, msg, code):

        super().__init__(msg, code)

        self.msg = msg
        self.code = code


class EntityExistsException(AppException):

    def __init__(self, msg):

        super().__init__(msg, 400)


class EntityNotFoundException(AppException):

    def __init__(self, msg):

        super().__init__(msg, 404)


class AuthenticationException(AppException):

    def __init__(self, msg):

        super().__init__(msg, 401)

