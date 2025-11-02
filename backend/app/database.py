"""
Database Connection and Session Management
SQLAlchemy setup for MySQL connection
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Generator

from app.config import settings

# SQLAlchemy Engine
engine = create_engine(
    settings.mysql_url_sync,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database - create all tables if they don't exist
    Note: In production, use migrations (Alembic) instead
    """
    Base.metadata.create_all(bind=engine)


def check_db_connection() -> bool:
    """
    Check if database connection is healthy
    Returns True if connection successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


# Event listeners for connection pool debugging (optional, for development)
if settings.debug:
    @event.listens_for(engine, "connect")
    def receive_connect(dbapi_conn, connection_record):
        """Log when new connection is created"""
        print(f"[DB] New connection created: {id(dbapi_conn)}")
    
    @event.listens_for(engine, "checkin")
    def receive_checkin(dbapi_conn, connection_record):
        """Log when connection is returned to pool"""
        print(f"[DB] Connection returned to pool: {id(dbapi_conn)}")

