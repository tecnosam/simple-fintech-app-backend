from typing import List, Optional

from datetime import datetime
from pydantic import BaseModel


class OurBase(BaseModel):

    id: int

    created_at: datetime


class Transaction(OurBase):

    user_id: int

    transaction_type: str
    amount: float

    transaction_status: str


class User(OurBase):

    name: str
    email: str
    username: str | None
    phone_no: str


class Bank(OurBase):

    bank_name: str
    bank_accronym: str

    bank_sort_code: str


class WalletTransaction(Transaction):

    receiver_id: int
    receiver_name: str


class BankTransaction(Transaction):

    bank_name: str

    bank_account_no: str
    bank_receiver_name: str


class DashboardData(BaseModel):

    user: User
    balance: float

    recent_transactions: List[
        WalletTransaction |
        BankTransaction   |
        Transaction
    ]

