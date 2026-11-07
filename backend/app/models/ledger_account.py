
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import mapped_column

from app.database import Base


class LedgerAccount(Base):
    __tablename__ = "ledger_accounts"

    __table_args__ = (
        CheckConstraint(
            "category IN ('asset', 'liability', 'equity', 'income', 'expense')",
            name="check_valid_ledger_category"
        ),
        CheckConstraint(
            "(is_system = 1 AND account_id IS NULL) OR "
            "(is_system = 0 AND account_id IS NOT NULL)",
            name="check_ledger_account_owner"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    code = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )

    name = mapped_column(
        String(100),
        nullable=False
    )

    category = mapped_column(
        String(20),
        nullable=False
    )

    account_id = mapped_column(
        Integer,
        ForeignKey("accounts.id"),
        unique=True,
        nullable=True
    )

    is_system = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
