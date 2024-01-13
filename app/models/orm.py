from datetime import datetime

from sqlalchemy import (
    Column,
    Text,
    Boolean,
    String,
    DateTime,
    Integer,
    ForeignKey
)

from sqlalchemy.orm import (
    declarative_base,
    relationship,
    sessionmaker
)

from sqlalchemy.engine import create_engine

from app.utils.settings import DATABASE_URI


engine = create_engine(DATABASE_URI, echo=False)

Session = sessionmaker(bind=engine)

Base = declarative_base()


class OurBase(Base):

    __abstract__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class User(OurBase):

    __tablename__ = "users"

    # Firstname and Lastname merge together
    name = Column(String(200), nullable=False)

    email = Column(String(100), nullable=False, unique=True)

    username = Column(String(50), nullable=True, unique=True)

    phone_no = Column(String(50), nullable=True, unique=False)

    password = Column(Text, nullable=False)


class SavedCard(OurBase):

    __tablename__ = 'cards'

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # VISA, MASTERCARD, or VERVE
    card_type = Column(String(50))

    last_4_digits = Column(String(5), nullable=False)
    cvv = Column(String(5), nullable=False)
    expiring_date = Column(DateTime, nullable=False)


class Bank(OurBase):

    __tablename__ = 'banks'

    bank_name = Column(Text, nullable=False)

    bank_accronym = Column(String(5), nullable=False)

    bank_sort_code = Column(Text, nullable=False)


# ========== Transactions ==========

class BaseTransaction(OurBase):

    __abstract__ = True

    user_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    # DEBIT or CREDIT
    transaction_type = Column(String(10), nullable=False)

    # TODO: change to decimal or float
    amount = Column(Integer, nullable=False)

    # PENDING, SUCCESS, FAILURE, CANCELLED
    transaction_status = Column(
        String(20),
        nullable=False,
        default='PENDING'
    )

    @property
    def narration(self):
        return "Transaction Performed"


class WalletTransaction(BaseTransaction):

    __tablename__ = 'transactions'

    receiver_id = Column(
        Integer,
        ForeignKey('users.id', ondelete='SET NULL'),
        nullable=True
    )

    @property
    def narration(self):

        return f"Transfer to {self.receiver_id}"


class BankTransaction(BaseTransaction):

    """
        This will be typically used to store payouts
        or withdrawals to user's or third party's local
        bank account.
    """

    __tablename__ = 'bank_transactions'

    bank_id = Column(
        Integer,
        ForeignKey('banks.id')
    )

    bank_account_no = Column(String(11), nullable=False)

    bank_receiver_name = Column(String(100), nullable=False)

    transaction_reference = Column(Text, nullable=False, unique=True)

    @property
    def narration(self):

        return f"Bank Transfer to {self.bank_receiver_name}"


class PaystackTransaction(BaseTransaction):

    """
        Paystack or Payment Gateway transactions
        We use this typically for storing deposit
        transactions

    """

    __tablename__ = "paystack_transactions"

    # Transaction reference from Paystack
    transaction_reference = Column(
        Text,
        nullable=False,
        unique=True
    )

    @property
    def narration(self):

        return "Deposit to Wallet"


Base.metadata.create_all(bind=engine)

