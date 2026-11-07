
from app.database import Base, engine

from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.transaction import Transaction
from app.models.ledger_entry import LedgerEntry


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
