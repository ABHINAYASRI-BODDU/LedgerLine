
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


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        CheckConstraint(
            "account_type IN ('savings', 'checking')",
            name="check_valid_account_type"
        ),
        CheckConstraint(
            "status IN ('active', 'frozen', 'closed')",
            name="check_valid_account_status"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    account_number = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False
    )

    user_id = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    account_type = mapped_column(
        String(20),
        nullable=False
    )

    currency = mapped_column(
        String(3),
        default="INR",
        nullable=False
    )

    status = mapped_column(
        String(20),
        default="active",
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
