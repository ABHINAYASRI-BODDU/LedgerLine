import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Import all models so SQLAlchemy registers all tables.
from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.ledger_entry import LedgerEntry
from app.models.transaction import Transaction
from app.models.transaction_attempt import TransactionAttempt

from app.services.ledger_service import create_system_ledger_accounts
from app.services.ledger_protection import install_ledger_immutability_triggers


@pytest.fixture
def test_db(tmp_path):
    test_database_path = tmp_path / "test_ledgerline.db"
    test_database_url = f"sqlite:///{test_database_path.as_posix()}"

    test_engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    Base.metadata.create_all(bind=test_engine)

    # Install database-level ledger protection.
    install_ledger_immutability_triggers(test_engine)

    setup_db = TestingSessionLocal()
    try:
        create_system_ledger_accounts(setup_db)
    finally:
        setup_db.close()

    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture
def client(tmp_path):
    test_database_path = tmp_path / "test_ledgerline.db"
    test_database_url = f"sqlite:///{test_database_path.as_posix()}"

    test_engine = create_engine(
        test_database_url,
        connect_args={"check_same_thread": False}
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    Base.metadata.create_all(bind=test_engine)

    # Install database-level ledger protection.
    install_ledger_immutability_triggers(test_engine)

    setup_db = TestingSessionLocal()
    try:
        create_system_ledger_accounts(setup_db)
    finally:
        setup_db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    # Make the test session factory available to API tests.
    app.state.test_session_factory = TestingSessionLocal

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

        if hasattr(app.state, "test_session_factory"):
            del app.state.test_session_factory

        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()