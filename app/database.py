"""
AegisShare — Database Configuration

Sets up the SQLAlchemy engine, session factory, and declarative base.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Load variables from .env into os.environ.
load_dotenv()

# Database URL — configurable via environment variable.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# Engine — ``check_same_thread=False`` is required for SQLite when used
# with FastAPI's async concurrency model.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory — each request gets its own session via ``get_db()``.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Modern declarative base (replaces deprecated ``declarative_base()``).
class Base(DeclarativeBase):
    """Shared base class for all ORM models."""