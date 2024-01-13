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

    phone_no: str = Field(default=None)

    username: str = Field(default=None)

    password: str = Field(default=None)


class DepositForm(BaseModel):

    amount: float


class WithdrawalForm(BaseModel):

    bank_id: int

    bank_account_no: str

    bank_receiver_name: str

    amount: float


class TransferForm(BaseModel):

    receiver_id: int

    amount: float


class WebHookPayload(BaseModel):

    event: str
    data: dict

