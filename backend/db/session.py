"""
Database session management and connection setup
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
from config.settings import settings

# Create database engine
# For Supabase, we'll use NullPool to avoid connection pool issues
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Use with FastAPI's Depends() for automatic session management.

    Usage:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables.
    Call this on application startup.
    """
    from db.base import Base
    # Import all models here to ensure they're registered with Base
    import models.job
    import models.application
    import models.resume
    import models.user

    Base.metadata.create_all(bind=engine)
