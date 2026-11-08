
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction

from app.services.ledger_service import (
    create_system_ledger_accounts,
    record_deposit,
    record_withdrawal,
    record_transfer,
    get_account_balance,
)


def test_simultaneous_withdrawals_cannot_overspend(tmp_path):
    database_path = tmp_path / "concurrency_test.db"

    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False, "timeout": 30}
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    try:
        Base.metadata.create_all(bind=engine)
        setup_db = TestSessionLocal()

        try:
            create_system_ledger_accounts(setup_db)

            user = User(
                full_name="Concurrency Test User",
                email="concurrency@example.com",
                hashed_password="test-hash",
                role="customer",
                is_active=True
            )
            setup_db.add(user)
            setup_db.flush()
            user_id = user.id

            account = Account(
                account_number="LL0000000001",
                user_id=user_id,
                account_type="savings",
                currency="INR",
                status="active"
            )
            setup_db.add(account)
            setup_db.commit()
            account_id = account.id

            record_deposit(
                db=setup_db,
                account=account,
                amount_paise=10000,
                initiated_by=user_id,
                idempotency_key="concurrency-initial-deposit"
            )
        finally:
            setup_db.close()

        start_barrier = Barrier(2)

        def make_withdrawal(idempotency_key):
            db = TestSessionLocal()
            try:
                account = db.query(Account).filter(
                    Account.id == account_id
                ).first()

                start_barrier.wait()

                record_withdrawal(
                    db=db,
                    account=account,
                    amount_paise=8000,
                    initiated_by=user_id,
                    idempotency_key=idempotency_key
                )
                return "success"

            except ValueError as error:
                if str(error) == "Insufficient balance.":
                    return "insufficient_balance"
                raise
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                make_withdrawal,
                ["concurrent-withdrawal-1", "concurrent-withdrawal-2"]
            ))

        assert results.count("success") == 1
        assert results.count("insufficient_balance") == 1

        final_db = TestSessionLocal()
        try:
            account = final_db.query(Account).filter(
                Account.id == account_id
            ).first()
            assert get_account_balance(final_db, account) == 2000
        finally:
            final_db.close()

    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_simultaneous_duplicate_withdrawals_are_recorded_once(tmp_path):
    database_path = tmp_path / "duplicate_concurrency_test.db"

    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False, "timeout": 30}
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    try:
        Base.metadata.create_all(bind=engine)
        setup_db = TestSessionLocal()

        try:
            create_system_ledger_accounts(setup_db)

            user = User(
                full_name="Duplicate Concurrency User",
                email="duplicate-concurrency@example.com",
                hashed_password="test-hash",
                role="customer",
                is_active=True
            )
            setup_db.add(user)
            setup_db.flush()
            user_id = user.id

            account = Account(
                account_number="LL0000000002",
                user_id=user_id,
                account_type="savings",
                currency="INR",
                status="active"
            )
            setup_db.add(account)
            setup_db.commit()
            account_id = account.id

            record_deposit(
                db=setup_db,
                account=account,
                amount_paise=10000,
                initiated_by=user_id,
                idempotency_key="duplicate-concurrency-deposit"
            )
        finally:
            setup_db.close()

        start_barrier = Barrier(2)

        def make_withdrawal():
            db = TestSessionLocal()
            try:
                account = db.query(Account).filter(
                    Account.id == account_id
                ).first()

                start_barrier.wait()

                transaction = record_withdrawal(
                    db=db,
                    account=account,
                    amount_paise=8000,
                    initiated_by=user_id,
                    idempotency_key="same-concurrent-withdrawal-key"
                )
                return transaction.id
            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            transaction_ids = list(executor.map(
                lambda _: make_withdrawal(),
                range(2)
            ))

        assert transaction_ids[0] == transaction_ids[1]

        final_db = TestSessionLocal()
        try:
            account = final_db.query(Account).filter(
                Account.id == account_id
            ).first()

            assert get_account_balance(final_db, account) == 2000

            withdrawal_count = final_db.query(Transaction).filter(
                Transaction.idempotency_key
                == "same-concurrent-withdrawal-key"
            ).count()

            assert withdrawal_count == 1
        finally:
            final_db.close()

    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_simultaneous_transfers_cannot_overspend(tmp_path):
    database_path = tmp_path / "transfer_concurrency_test.db"

    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False, "timeout": 30}
    )

    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    try:
        Base.metadata.create_all(bind=engine)
        setup_db = TestSessionLocal()

        try:
            create_system_ledger_accounts(setup_db)

            user = User(
                full_name="Transfer Concurrency User",
                email="transfer-concurrency@example.com",
                hashed_password="test-hash",
                role="customer",
                is_active=True
            )
            setup_db.add(user)
            setup_db.flush()
            user_id = user.id

            source_account = Account(
                account_number="LL0000000003",
                user_id=user_id,
                account_type="savings",
                currency="INR",
                status="active"
            )

            destination_account = Account(
                account_number="LL0000000004",
                user_id=user_id,
                account_type="savings",
                currency="INR",
                status="active"
            )

            setup_db.add_all([source_account, destination_account])
            setup_db.commit()

            source_id = source_account.id
            destination_id = destination_account.id

            record_deposit(
                db=setup_db,
                account=source_account,
                amount_paise=10000,
                initiated_by=user_id,
                idempotency_key="transfer-concurrency-deposit"
            )
        finally:
            setup_db.close()

        start_barrier = Barrier(2)

        def make_transfer(idempotency_key):
            db = TestSessionLocal()

            try:
                source = db.query(Account).filter(
                    Account.id == source_id
                ).first()

                destination = db.query(Account).filter(
                    Account.id == destination_id
                ).first()

                start_barrier.wait()

                record_transfer(
                    db=db,
                    source_account=source,
                    destination_account=destination,
                    amount_paise=8000,
                    initiated_by=user_id,
                    idempotency_key=idempotency_key
                )

                return "success"

            except ValueError as error:
                if str(error) == "Insufficient balance.":
                    return "insufficient_balance"
                raise

            finally:
                db.close()

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(
                make_transfer,
                ["concurrent-transfer-1", "concurrent-transfer-2"]
            ))

        assert results.count("success") == 1
        assert results.count("insufficient_balance") == 1

        final_db = TestSessionLocal()

        try:
            source = final_db.query(Account).filter(
                Account.id == source_id
            ).first()

            destination = final_db.query(Account).filter(
                Account.id == destination_id
            ).first()

            assert get_account_balance(final_db, source) == 2000
            assert get_account_balance(final_db, destination) == 8000

        finally:
            final_db.close()

    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
