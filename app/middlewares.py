from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


from app.utils.exceptions import AppException


class AppExceptionHandler(BaseHTTPMiddleware):

    """
        This middleware catches all exceptions and returns a generic response
    """

    def __init__(
        self,
        app: ASGIApp,
    ) -> None:
        super().__init__(app)

    async def dispatch(self, request, call_next):
        try:

            response = await call_next(request)
            return response

        except AppException as exc:

            return JSONResponse(content={
                'success': False,
                'status': exc.code,
                'message': exc.msg,
                'data': None
            })

