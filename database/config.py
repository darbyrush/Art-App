from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - use SQLite for local development
# For Railway deployment, use the provided PostgreSQL URL
RAILWAY_DB_URL = "postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway"

# Check if we're in production (Railway) or local development
is_production = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("DATABASE_URL")

if is_production:
    # Use PostgreSQL in production
    DATABASE_URL = (
        os.getenv("DATABASE_URL") or 
        os.getenv("POSTGRES_URL") or 
        os.getenv("RAILWAY_DATABASE_URL") or 
        RAILWAY_DB_URL or
        "postgresql://darbyrush@localhost/art_explorer"
    )
    
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
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        pool_pre_ping=True,
        echo=False,
        connect_args={
            "connect_timeout": 10,
            "application_name": "art_app"
        }
    )

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