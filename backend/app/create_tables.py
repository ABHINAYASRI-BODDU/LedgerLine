from app.database import Base, engine

from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry
from app.models.transaction_attempt import TransactionAttempt

from app.services.ledger_protection import install_ledger_immutability_triggers


def create_tables():
    Base.metadata.create_all(bind=engine)

    install_ledger_immutability_triggers(engine)

    print("Database tables created successfully!")
    print("Ledger immutability triggers installed successfully!")


if __name__ == "__main__":
    create_tables()