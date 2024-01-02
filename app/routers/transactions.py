from fastapi import APIRouter, Path, Depends

from app.dependencies import (
    get_user_id
)

from app.models.forms import (
    DepositForm,
    WithdrawalForm,
    TransferForm,
    WebHookPayload
)

from app.models.responses import (
    Response,
    TransactionResponse,
    TransactionListResponse
)

from app.controllers.transactions import (
    get_transactions,
    get_transaction,

    register_deposit_via_paystack,
    register_withdrawal_via_bank,
    register_transfer,

    update_transaction_status_from_webhook
)


router = APIRouter(prefix='/api', tags=['Transactions'])


@router.get("/transactions", response_model=TransactionListResponse)
def get_transactions_route(
    user_id: int = Depends(get_user_id)
):

    # TODO: paginate
    transactions = get_transactions(user_id)
    print(transactions, user_id, type(user_id))
    return TransactionResponse.cook(data=transactions)


@router.get(
    "/transactions/{transaction_type}/{transaction_id}",
    response_model=TransactionResponse
)
def get_transaction_route(
    user_id: int = Depends(get_user_id),
    transaction_type: str = Path(),
    transaction_id: int = Path()
):

    transaction = get_transaction(
        user_id,
        transaction_id,
        transaction_namespace=transaction_type
    )
    return TransactionResponse.cook(data=transaction)


@router.post("/deposit", response_model=Response)
def deposit_route(
    data: DepositForm,
    user_id: int = Depends(get_user_id)
):

    data = data.model_dump()

    deposit = register_deposit_via_paystack(
        user_id=user_id,
        **data
    )

    return TransactionResponse.cook(data=deposit)


@router.post("/withdraw", response_model=Response)
def withdraw_route(
    data: WithdrawalForm,
    user_id: int = Depends(get_user_id)
):

    data = data.model_dump()

    withdrawal = register_withdrawal_via_bank(
        user_id=user_id,
        bank_transaction=data
    )

    return TransactionResponse.cook()


@router.post("/transfer", response_model=Response)
def wallet_transfer_route(
    data: TransferForm,
    user_id: int = Depends(get_user_id)
):

    data = data.model_dump()

    transfer = register_transfer(
        sender_id=user_id,
        **data
    )
    return TransactionResponse.cook()


@router.post("/paystack/webhook")
def paystack_webhook(payload: WebHookPayload):

    webhook_data = payload.model_dump()

    return update_transaction_status_from_webhook(
        webhook_data
    )

