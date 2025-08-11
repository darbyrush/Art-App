from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Simple database configuration - minimal and working
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./art_explorer.db")

# Create engine with minimal configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    logger.info("Using SQLite database")
else:
    # Simple PostgreSQL configuration - no complex pooling
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info("Using PostgreSQL database")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Defer import to avoid circular import issues
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except ImportError as e:
        logger.warning(f"Could not import database models: {e}")
        logger.info("Database initialization skipped - models not available")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.info("Database initialization failed - continuing anyway")

def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
