
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


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    __table_args__ = (
        CheckConstraint(
            "entry_type IN ('debit', 'credit')",
            name="check_valid_entry_type"
        ),
        CheckConstraint(
            "amount_paise > 0",
            name="check_positive_entry_amount"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_id = mapped_column(
        Integer,
        ForeignKey("transactions.id"),
        nullable=False,
        index=True
    )

    ledger_account_id = mapped_column(
        Integer,
        ForeignKey("ledger_accounts.id"),
        nullable=False,
        index=True
    )

    entry_type = mapped_column(
        String(10),
        nullable=False
    )

    amount_paise = mapped_column(
        Integer,
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
