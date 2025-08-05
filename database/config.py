from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - try multiple Railway environment variables
DATABASE_URL = (
    os.getenv("DATABASE_URL") or 
    os.getenv("POSTGRES_URL") or 
    os.getenv("RAILWAY_DATABASE_URL") or 
    "postgresql://darbyrush@localhost/art_explorer"
)

# Debug database URL (without password for security)
if DATABASE_URL:
    debug_url = DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL
    print(f"Database URL: {debug_url}")
else:
    print("Warning: DATABASE_URL environment variable not found")
    print("Available environment variables:")
    for key, value in os.environ.items():
        if 'DATABASE' in key or 'POSTGRES' in key:
            print(f"  {key}: {value[:20]}..." if len(value) > 20 else f"  {key}: {value}")

# Handle Railway's PostgreSQL URL format
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create engine with better error handling
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False,  # Set to True for SQL debugging
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
        print(f"Database URL available: {bool(DATABASE_URL)}")
        if DATABASE_URL:
            print(f"Database URL format: {DATABASE_URL[:20]}...")
        # Don't raise the error in production, just log it
        if os.getenv("ENVIRONMENT") == "production":
            print("Continuing without database initialization in production")
        else:
            raise 