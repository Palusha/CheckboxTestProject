from databases import Database
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    Float,
    LargeBinary,
    MetaData,
    String,
    Table,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.config import settings
from src.constants import DB_NAMING_CONVENTION

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)
metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)

database = Database(DATABASE_URL, force_rollback=settings.ENVIRONMENT.is_testing)


auth_user = Table(
    "auth_user",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("email", String, unique=True, nullable=False),
    Column("first_name", String),
    Column("last_name", String),
    Column("password", LargeBinary, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
    Column("updated_at", DateTime, onupdate=func.now()),
)

receipts = Table(
    "receipts",
    metadata,
    Column("id", Integer, Identity(), primary_key=True),
    Column("user_id", ForeignKey("auth_user.id", ondelete="CASCADE"), nullable=False),
    Column("products", JSONB, nullable=False),
    Column("payment", JSONB, nullable=False),
    Column("total", Float, nullable=False),
    Column("rest", Float, nullable=False),
    Column("created_at", DateTime, server_default=func.now(), nullable=False),
)
