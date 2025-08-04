#!/usr/bin/env python3
"""
Database setup script for Art Explorer
"""

import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path
sys.path.append('.')

from database.config import init_db, engine
from database.models import Base
from sqlalchemy import text

def setup_database():
    """Initialize the database and create all tables"""
    print("🚀 Setting up Art Explorer Database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Test database connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check your DATABASE_URL in .env file")
        print("3. Ensure database exists: CREATE DATABASE art_explorer;")
        return False
    
    return True

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        
        env_content = """# Database Configuration
DATABASE_URL=postgresql://art_user:art_password@localhost:5432/art_explorer

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys (optional)
SMITHSONIAN_API_KEY=your_smithsonian_api_key_here
HARVARD_API_KEY=your_harvard_api_key_here
EUROPEANA_API_KEY=your_europeana_api_key_here

# Application Settings
DEBUG=True
API_URL=http://localhost:8000
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created!")
        print("⚠️  Please update the API keys in .env file")

if __name__ == "__main__":
    print("🎨 Art Explorer Database Setup")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Create .env file if needed
    create_env_file()
    
    # Setup database
    if setup_database():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start the FastAPI backend: uvicorn api.main:app --reload")
        print("2. Start the Streamlit frontend: streamlit run app.py")
        print("3. Or use Docker: docker-compose up")
    else:
        print("\n❌ Setup failed. Please check the error messages above.")
        sys.exit(1) 