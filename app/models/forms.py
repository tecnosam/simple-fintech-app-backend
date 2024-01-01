from pydantic import BaseModel, Field


class CreateAccountForm(BaseModel):

    first_name: str
    last_name: str
    email: str

    phone_no: str
    password: str


class LoginForm(BaseModel):

    email: str
    password: str


class UpdateProfileForm(BaseModel):

    first_name: str = Field(default=None)
    last_name: str = Field(default=None)

    email: str = Field(default=None)
    phone_no: str = Field(default=None)

    username: str = Field(default=None)

    password: str = Field(default=None)


class DepositForm(BaseModel):

    transaction_reference: str

    transaction_type: str = 'CREDIT'

    amount: float


class WithdrawalForm(BaseModel):

    bank_id: int

    bank_account_no: str

    bank_receiver_name: str

    transaction_type: str = 'DEBIT'

    amount: float


class TransferForm(BaseModel):

    receiver_id: int

    transaction_type: str = 'DEBIT'

    amount: float

