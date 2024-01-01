from typing import List, Optional

from pydantic import BaseModel

from app.models.representations import (
    User,
    Bank,
    Transaction,
    BankTransaction,
    WalletTransaction,
    DashboardData
)


class Response(BaseModel):

    success: bool

    message: str

    data: Optional[dict | list] = None

    @staticmethod
    def cook(
        success=True,
        message="Request Completed successfully",
        data=None
    ):

        return {
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

    data: Transaction | BankTransaction | WalletTransaction


class TransactionListResponse(Response):

    data: List[Transaction | BankTransaction | WalletTransaction]

