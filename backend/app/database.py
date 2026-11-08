from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


# Get the backend folder location
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file location
DATABASE_PATH = BASE_DIR / "ledgerline.db"

# Database connection URL
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# Create database engine
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