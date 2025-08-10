#!/usr/bin/env python3
"""
Test Railway PostgreSQL Database Connection
Run this script to verify your database connection before deploying.
"""

import os
import sys
from sqlalchemy import create_engine, text

# Set the database URL for testing
DATABASE_URL = "postgresql://postgres:VPzlvfYNNmRSpxWukjeUIuGDsSFHwKOc@postgres.railway.internal:5432/railway"

def test_railway_connection():
    """Test connection to Railway PostgreSQL database"""
    print("🔌 Testing Railway PostgreSQL Connection...")
    print(f"Database URL: postgres.railway.internal:5432/railway")
    
    try:
        # Create engine with Railway PostgreSQL configuration
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            pool_timeout=30,
            connect_args={
                "connect_timeout": 10,
                "application_name": "art_app_test",
                "options": "-c timezone=UTC -c statement_timeout=30000"
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test, version() as pg_version"))
            row = result.fetchone()
            print(f"✅ Connection successful!")
            print(f"   Test query result: {row[0]}")
            print(f"   PostgreSQL version: {row[1]}")
            
            # Test if we can create tables
            print("\n📋 Testing table creation...")
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS connection_test (
                    id SERIAL PRIMARY KEY,
                    test_name VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            print("✅ Table creation successful!")
            
            # Test insert
            conn.execute(text("""
                INSERT INTO connection_test (test_name) VALUES ('railway_connection_test')
            """))
            print("✅ Insert operation successful!")
            
            # Test select
            result = conn.execute(text("SELECT COUNT(*) FROM connection_test"))
            count = result.fetchone()[0]
            print(f"✅ Select operation successful! Row count: {count}")
            
            # Clean up test table
            conn.execute(text("DROP TABLE connection_test"))
            print("✅ Cleanup successful!")
            
            conn.commit()
            
        print("\n🎉 All database operations successful!")
        print("   Your Railway PostgreSQL database is ready!")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n🔍 Troubleshooting tips:")
        print("   1. Make sure your Railway project is running")
        print("   2. Check if the database service is active")
        print("   3. Verify the database URL is correct")
        print("   4. Ensure your IP is allowed (if using external access)")
        return False

if __name__ == "__main__":
    success = test_railway_connection()
    sys.exit(0 if success else 1)
