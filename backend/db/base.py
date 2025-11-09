"""
Database base class and common mixins
"""
from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.orm import declarative_base, declared_attr
import uuid
from sqlalchemy.dialects.postgresql import UUID

# Base class for all models
Base = declarative_base()


class TimestampMixin:
    """Mixin to add created_at and updated_at timestamps to models"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )


class UUIDMixin:
    """Mixin to add UUID primary key to models"""

    @declared_attr
    def id(cls):
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False
        )
