
from sqlalchemy.orm import Session, sessionmaker

from app.database import SessionLocal
from app.models.transaction_attempt import TransactionAttempt


def record_failed_attempt(
    transaction_type: str,
    amount_paise: int,
    initiated_by: int,
    failure_reason: str,
    source_account_id: int | None = None,
    destination_account_id: int | None = None,
    idempotency_key: str | None = None,
    session_factory: sessionmaker = SessionLocal,
):
    """
    Save a failed transaction attempt using an independent session.

    This record survives rollback of the original transaction.
    A separate session factory can be supplied during testing.
    """

    audit_db: Session = session_factory()

    try:
        attempt = TransactionAttempt(
            transaction_type=transaction_type,
            amount_paise=amount_paise,
            initiated_by=initiated_by,
            failure_reason=failure_reason[:255],
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            idempotency_key=idempotency_key,
        )

        audit_db.add(attempt)
        audit_db.commit()

    except Exception:
        audit_db.rollback()
        raise

    finally:
        audit_db.close()
