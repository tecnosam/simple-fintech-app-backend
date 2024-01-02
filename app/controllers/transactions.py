from typing import List

from sqlalchemy.exc import IntegrityError

from sqlalchemy import or_

from app.models.orm import (
    Session,

    User,
    BaseTransaction,
    WalletTransaction,
    BankTransaction,
    PaystackTransaction
)

from app.utils.exceptions import AppException


# ========== GET INFORMATION ==========

def get_transactions(
    user_id: int,
    limit: int = 10,
    offset: int = 0
):

    """
        Returns all the transactions a user has made

    """

    with Session() as session:

        wallet = session.query(WalletTransaction).filter(
            or_(
                WalletTransaction.user_id == user_id,
                WalletTransaction.receiver_id == user_id
            )
        ).all()

        paystack = session.query(PaystackTransaction).filter_by(
            user_id=user_id
        ).all()

        print("Paystack", paystack)

        bank = session.query(BankTransaction).filter_by(
            user_id=user_id
        ).all()

        transactions = sorted(
            wallet + paystack + bank,
            key=lambda x: x.created_at,
            reverse=True
        )

        print(offset, limit)
        print("All", transactions, transactions[offset:offset+limit])
        return transactions[offset:offset+limit] 


def get_transaction(
    user_id,
    transaction_id,
    transaction_namespace: str
) -> List[WalletTransaction | BankTransaction | PaystackTransaction]:

    """
        Transaction namespace is one of
        1. WALLET
        2. BANK
        3. GATEWAY

    """

    Model: BaseTransaction = None

    transaction_namespace = transaction_namespace.upper()

    match transaction_namespace:

        case 'WALLET':
            Model = WalletTransaction
        case 'BANK':
            Model = BankTransaction
        case 'GATEWAY':
            Model = PaystackTransaction

    if Model is None:
        raise AppException(
            msg="Transaction Namespace does not exist!",
            code=422
        )

    with Session() as session:

        query = {
            'user_id': user_id,
            'id': transaction_id
        }

        transaction = session.query(Model).filter_by(**query).first()

        return transaction


def get_balance(user_id, session=None) -> float:

    """
        Computes the balance of a user
    """
    
    its_our_session = session is None

    session = Session() if session is None else session

    # We need to get the session started if it's ours
    if its_our_session:
        session.begin()

    transfers_sent = session.query(WalletTransaction).filter_by(
        user_id=user_id,
        transaction_status='SUCCESS'
    ).all()

    transfers_received = session.query(WalletTransaction).filter_by(
        receiver_id=user_id,
        transaction_status='SUCCESS'
    ).all()

    withdrawals = session.query(BankTransaction).filter_by(
        user_id=user_id,
        transaction_status='SUCCESS'
    ).all()

    deposits = session.query(PaystackTransaction).filter_by(
        user_id=user_id,
        transaction_status='SUCCESS'
    ).all()

    outflow = sum(map(lambda x: x.amount, transfers_sent + withdrawals))
    inflow = sum(map(lambda x: x.amount, transfers_received + deposits))

    balance = inflow - outflow

    # If we started the session locally, we shou close it
    if its_our_session:
        session.close()

    return balance


def get_dashboard_data(user_id):

    """
        Get's dashboard data including
        User's name 
        User's balance
        User's last 5 transactions

    """

    transactions: list = get_transactions(user_id, offset=0, limit=5)

    balance: float = get_balance(user_id)

    with Session() as session:

        user: User = session.query(User).filter_by(id=user_id).first()

    return {
        'user': user,
        'balance': balance,
        'recent_transactions': transactions
    }


# ========== PERFORM TRANSACTIONS ==========

def register_deposit_via_paystack(**deposit_data):

    """
        Takes in deposit data

        Calls paystack to validate the transaction amount
        and the status of the transaction.

        After that, it updates the database

    """

    deposit_data['transaction_type'] = 'CREDIT'

    with Session() as session:
        try:
            transaction = PaystackTransaction(**deposit_data)

            session.add(transaction)
            session.commit()

            return {'id': transaction.id, 'amount': transaction.amount}

        except IntegrityError as exc:

            session.rollback()
            print("This transaction has already been recorded before")


def register_withdrawal_via_bank(
    user_id: int,
    bank_transaction: dict
):
    """
        Initiates withdrawal process

        First checks if the user has enough credits in balance

        Then talks to paystack to initiate Bank Transfer from
        our wallet.

        Then register's withdrawal in database
    """

    amount: float = bank_transaction.get('amount')

    with Session() as session:

        if get_balance(user_id, session=session) < amount:
            raise ValueError("Insufficient funds to make this transaction")

        # TODO: Talk to paystack

        bank_transaction['user_id'] = user_id
        bank_transaction['transaction_reference'] = ""
        bank_transaction['transaction_type'] = 'DEBIT'

        transaction = BankTransaction(**bank_transaction)

        session.add(transaction)
        session.commit()

        return {'id': transaction.id, 'amount': transaction.amount}


def register_transfer(sender_id, receiver_id, amount):

    """

        Initiates transfer process

        First check if sender has enough credits in balance
        Then process the transaction
    """

    with Session() as session:

        if get_balance(sender_id, session=session) < amount:

            raise ValueError("Insufficient funds to make this transaction")

        data = {
            'user_id': sender_id,
            'receiver_id': receiver_id,
            'transaction_type': 'DEBIT',
            'amount': amount,
            'transaction_status': 'SUCCESS'
        }

        transaction = WalletTransaction(**data)

        session.add(transaction)
        session.commit()

        return True


def update_transaction_status_from_webhook(webhook_data):

    """
        Process Webhook update from paystack

        In the background we also send things like
        push notifications or emails alerting successful
        transaction

        The webhook data must contain:
            1. User ID 
            2. Transaction Reference 
            3. Transaction Status 
            4. Transaction Type 
            5. User's Email as it is in our DB

    """

    event, _ = webhook_data['event'].split(".")

    data = webhook_data['data']

    transaction_reference = data.get('reference')
    transaction_status = data['status'].upper()

    # Either withdrawal or deposit

    if event == 'charge':
        Model = PaystackTransaction
        metadata = data.get('metadata', {}) 

    elif event == 'transfer':
        Model = BankTransaction
        metadata = data['recipient'].get('metadata', {}) 
    else:
        # Don't care about other responses
        return 0

    user_id = metadata.get('user_id')
    email = metadata.get('email')

    with Session() as session:

        modified_count = session.query(Model).filter_by(
            user_id=user_id,
            transaction_reference=transaction_reference
        ).update({'transaction_status': transaction_status})

        session.commit()

        if modified_count:
            print(f"Sending email to {email}")
            # TODO: Trigger email to client saying transaction is successful
            pass

    return modified_count

