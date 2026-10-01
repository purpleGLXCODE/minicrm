"""PostgreSQL database foundation for MiniCRM."""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://minicrm:password@127.0.0.1:5432/minicrm",
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db():
    from .models import Lead, Tag, LeadTag  # noqa: F401
    Base.metadata.create_all(bind=engine)
