from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.representations import (
    User,
    Bank,
    Transaction,
    DashboardData
)


class Response(BaseModel):

    success: bool = Field(default=True)

    status: bool | str | int

    message: str

    data: Optional[dict | list] = None

    @staticmethod
    def cook(
        success=True,
        message="Request Completed successfully",
        data=None,
        status=200
    ):

        return {
            "status": status,
            "success": success,
            "message": message,
            "data": data
        }


class AuthResponse(Response):

    class Token(BaseModel):

        token: str

    data: Token


class BalanceResponse(Response):

    class Balance(BaseModel):

        balance: float

    data: Balance


class DashboardResponse(Response):

    data: DashboardData


class TransactionResponse(Response):

    data: Transaction


class TransactionListResponse(Response):

    data: List[Transaction]
