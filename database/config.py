from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

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
    DATABASE_URL = (
        os.getenv("DATABASE_URL") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("RAILWAY_DATABASE_URL")
    )
    
    if not DATABASE_URL:
        # Build from individual components if available
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        database = os.getenv("POSTGRES_DB", "art_explorer")
        
        if password:
            DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        else:
            print("Warning: No PostgreSQL credentials found. Please set DATABASE_URL or POSTGRES_* environment variables.")
            DATABASE_URL = "postgresql://postgres@localhost/art_explorer"
    
    # Handle Railway's PostgreSQL URL format
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
else:
    # Use SQLite for local development
    DATABASE_URL = "sqlite:///./art_explorer.db"

# Debug database URL (without password for security)
if DATABASE_URL:
    if DATABASE_URL.startswith("sqlite"):
        debug_url = DATABASE_URL
    else:
        debug_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"Database URL: {debug_url}")
else:
    print("Warning: DATABASE_URL environment variable not found")

# Create engine with appropriate configuration
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for local development
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # PostgreSQL configuration for production - optimized
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections every 5 minutes
        pool_size=5,       # Reduced pool size for Railway limits
        max_overflow=10,   # Reduced overflow
        pool_timeout=30,   # Connection timeout
        echo=False,
        connect_args={
            "connect_timeout": 10,
            "application_name": "art_app",
            "options": "-c timezone=UTC"
        }
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
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        if DATABASE_URL.startswith("sqlite"):
            print("SQLite database should be created automatically")
        else:
            print("Continuing without database initialization - Railway PostgreSQL not configured")
            print("To fix: Add PostgreSQL service to Railway project") 