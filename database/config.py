from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv
import logging
import re

load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

def clean_database_url(url_string):
    """
    Clean and validate database URL from environment variable.
    Handles cases where the entire 'KEY=value' string is passed.
    """
    if not url_string:
        return None
    
    # Remove any leading/trailing whitespace
    url_string = url_string.strip()
    
    # Check if it's in the format 'KEY=value' and extract just the value
    if '=' in url_string and not url_string.startswith(('postgresql://', 'postgres://', 'sqlite://')):
        # Split on first '=' and take the value part
        parts = url_string.split('=', 1)
        if len(parts) == 2:
            url_string = parts[1].strip()
            logger.info(f"Extracted database URL from environment variable format")
    
    # Validate the URL format
    if url_string.startswith(('postgresql://', 'postgres://')):
        # Ensure it's a valid PostgreSQL URL
        if not re.match(r'^postgres(ql)?://[^:]+:[^@]+@[^:]+:\d+/[^?]+', url_string):
            logger.error(f"Invalid PostgreSQL URL format: {url_string}")
            return None
        return url_string
    elif url_string.startswith('sqlite://'):
        return url_string
    else:
        logger.error(f"Unsupported database URL format: {url_string}")
        return None

# Database configuration
# Use PostgreSQL if DATABASE_URL is provided (Railway or other), otherwise SQLite for local development

# Check if we should use PostgreSQL
use_postgres = (
    os.getenv("DATABASE_URL") or 
    os.getenv("POSTGRES_URL") or 
    os.getenv("RAILWAY_DATABASE_URL") or
    os.getenv("DEVELOPMENT_MODE", "true").lower() == "false"
)

if use_postgres:
    # Use PostgreSQL (Railway or other PostgreSQL database)
    raw_database_url = (
        os.getenv("DATABASE_URL") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("RAILWAY_DATABASE_URL")
    )
    
    # Clean and validate the database URL
    DATABASE_URL = clean_database_url(raw_database_url)
    
    if not DATABASE_URL:
        # Build from individual components if available
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        database = os.getenv("POSTGRES_DB", "art_explorer")
        
        if password:
            DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            logger.info("Built database URL from individual components")
        else:
            logger.warning("No PostgreSQL credentials found. Please set DATABASE_URL or POSTGRES_* environment variables.")
            DATABASE_URL = "postgresql://postgres@localhost/art_explorer"
    
    # Handle Railway's PostgreSQL URL format
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
        logger.info("Converted postgres:// to postgresql://")
else:
    # Use SQLite for local development
    DATABASE_URL = "sqlite:///./art_explorer.db"

# Debug database URL (without password for security)
if DATABASE_URL:
    if DATABASE_URL.startswith("sqlite"):
        debug_url = DATABASE_URL
    else:
        debug_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    logger.info(f"Database URL: {debug_url}")
else:
    logger.warning("DATABASE_URL environment variable not found")

# Create engine with appropriate configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for local development
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    logger.info("Using SQLite database for development")
else:
    # PostgreSQL configuration for production - Railway optimized
    try:
        # Railway-specific optimizations
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=600,      # Recycle connections every 10 minutes (Railway friendly)
            pool_size=5,           # Reduced pool size for Railway (more conservative)
            max_overflow=10,       # Reduced overflow for Railway
            pool_timeout=60,       # Increased connection timeout for Railway
            echo=False,
            connect_args={
                "connect_timeout": 30,        # Increased from 10s to 30s for Railway
                "application_name": "art_app_railway",
                "options": "-c timezone=UTC -c statement_timeout=60000 -c idle_in_transaction_session_timeout=600000"
            }
        )
        logger.info("Using PostgreSQL database for Railway production")
        
        # Test the connection immediately to catch issues early
        try:
            from sqlalchemy import text
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
            logger.info("✅ Initial database connection test successful")
        except Exception as e:
            logger.warning(f"⚠️ Initial connection test failed: {e}")
            # Continue anyway - connection might work later
            
    except Exception as e:
        logger.error(f"Failed to create PostgreSQL engine: {e}")
        logger.info("Falling back to SQLite for development")
        DATABASE_URL = "sqlite:///./art_explorer.db"
        engine = create_engine(
            DATABASE_URL,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=False
        )

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine,
    expire_on_commit=False
)

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
        from database.models import Base
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        if DATABASE_URL.startswith("sqlite"):
            logger.info("SQLite database should be created automatically")
        else:
            logger.warning("Continuing without database initialization - Railway PostgreSQL not configured")
            logger.info("To fix: Add PostgreSQL service to Railway project")

def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            conn.commit()
        logger.info("Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def get_connection_info():
    """Get database connection information"""
    if DATABASE_URL.startswith("sqlite"):
        return {
            "type": "sqlite",
            "url": DATABASE_URL,
            "pool_size": "N/A (StaticPool)",
            "pool_overflow": "N/A (StaticPool)"
        }
    else:
        return {
            "type": "postgresql",
            "url": DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else "hidden",
            "pool_size": engine.pool.size(),
            "pool_overflow": engine.pool.overflow()
        }
