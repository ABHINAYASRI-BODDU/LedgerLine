
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


class Transaction(Base):
    __tablename__ = "transactions"

    __table_args__ = (
        CheckConstraint(
            "transaction_type IN ('deposit', 'withdrawal', 'transfer')",
            name="check_valid_transaction_type"
        ),
        CheckConstraint(
            "amount_paise > 0",
            name="check_positive_transaction_amount"
        ),
        CheckConstraint(
            "status IN ('pending', 'posted', 'failed', 'reversed')",
            name="check_valid_transaction_status"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )
    idempotency_key = mapped_column(
        String(100),
        nullable=True,
        unique=True
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
        nullable=False
    )

    status = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
