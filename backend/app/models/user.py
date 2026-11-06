from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Integer,
    String,
)
from sqlalchemy.orm import mapped_column

from app.database import Base


class User(Base):

    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('customer', 'admin')",
            name="check_valid_user_role"
        ),
    )

    id = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    full_name = mapped_column(
        String(100),
        nullable=False
    )

    email = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    hashed_password = mapped_column(
        String(255),
        nullable=False
    )

    role = mapped_column(
        String(20),
        default="customer",
        nullable=False
    )

    is_active = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )