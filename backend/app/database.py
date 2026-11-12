
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Get the backend folder location
BASE_DIR = Path(__file__).resolve().parent.parent

# Local SQLite database location
DATABASE_PATH = BASE_DIR / "ledgerline.db"

# Use PostgreSQL when DATABASE_URL is provided.
# Otherwise, use SQLite for local development.
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Render/Neon PostgreSQL connection
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql+psycopg://",
        1
    )

    DATABASE_URL = DATABASE_URL.replace(
        "postgresql://",
        "postgresql+psycopg://",
        1
    )

    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )

else:
    # Local SQLite connection
    DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

    engine = create_engine(
        DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 30
        }
    )


# Create database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Base class for database models
class Base(DeclarativeBase):
    pass


# Function to provide database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
