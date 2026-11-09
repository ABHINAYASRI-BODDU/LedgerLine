
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.orm import mapped_column

from app.database import Base


class TransactionAttempt(Base):
    __tablename__ = "transaction_attempts"

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('deposit', 'withdrawal', 'transfer')",
            name="check_valid_attempt_type"
        ),
        CheckConstraint(
            "amount_paise > 0",
            name="check_positive_attempt_amount"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_type = mapped_column(
        String(20),
        nullable=False
    )

    amount_paise = mapped_column(
        Integer,
        nullable=False
    )

    source_account_id = mapped_column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True
    )

    destination_account_id = mapped_column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=True
    )

    initiated_by = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    idempotency_key = mapped_column(
        String(100),
        nullable=True
    )

    failure_reason = mapped_column(
        String(255),
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

