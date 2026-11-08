
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Import all models so SQLAlchemy registers all five tables.
from app.models.user import User
from app.models.account import Account
from app.models.ledger_account import LedgerAccount
from app.models.ledger_entry import LedgerEntry
from app.models.transaction import Transaction

from app.services.ledger_service import create_system_ledger_accounts


@pytest.fixture
def test_db(tmp_path):
    # Create a separate temporary database for each test.
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

    # Create all database tables.
    Base.metadata.create_all(bind=test_engine)

    # Initialize the system ledger account.
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
    # Create a separate temporary database for API tests.
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

    # Create all database tables.
    Base.metadata.create_all(bind=test_engine)

    # Initialize the system ledger account.
    setup_db = TestingSessionLocal()
    try:
        create_system_ledger_accounts(setup_db)
    finally:
        setup_db.close()

    # Override the application's database dependency.
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()
