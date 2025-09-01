#!/usr/bin/env python3
"""
Database Test Script
Tests database connection and basic operations
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import init_database, SimpleDatabaseOperations, get_db
from database.config import db_config

def test_database_connection():
    """Test basic database connection"""
    print("🔍 Testing database connection...")
    
    try:
        # Test connection
        if db_config.test_connection():
            print("✅ Database connection successful!")
            print(f"📊 Database type: {db_config.database_type}")
            print(f"🔗 Database URL: {db_config.database_url}")
            return True
        else:
            print("❌ Database connection failed!")
            return False
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def test_database_operations():
    """Test database operations"""
    print("\n🔍 Testing database operations...")
    
    try:
        # Get database session
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        
        # Test getting categories
        categories = db_ops.get_categories()
        print(f"✅ Retrieved {len(categories)} categories")
        
        # Test getting accounts
        accounts = db_ops.get_accounts()
        print(f"✅ Retrieved {len(accounts)} accounts")
        
        # Test getting transactions
        transactions = db_ops.get_transactions(limit=10)
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        # Test getting database stats
        stats = db_ops.get_database_stats()
        print(f"✅ Retrieved database stats: {stats}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Database operations error: {e}")
        return False

def test_sample_data_creation():
    """Test creating sample data"""
    print("\n🔍 Testing sample data creation...")
    
    try:
        # Initialize database with sample data
        if init_database():
            print("✅ Sample data created successfully!")
            return True
        else:
            print("❌ Sample data creation failed!")
            return False
    except Exception as e:
        print(f"❌ Sample data creation error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 SEAS Financial Tracker - Database Test Suite")
    print("=" * 50)
    
    # Test 1: Database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed. Exiting.")
        return False
    
    # Test 2: Database operations
    if not test_database_operations():
        print("\n❌ Database operations test failed. Exiting.")
        return False
    
    # Test 3: Sample data creation (only if database is empty)
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        stats = db_ops.get_database_stats()
        db.close()
        
        if stats.get('total_transactions', 0) == 0:
            print("\n📊 Database is empty, creating sample data...")
            if not test_sample_data_creation():
                print("\n❌ Sample data creation failed.")
                return False
        else:
            print(f"\n📊 Database already contains data: {stats['total_transactions']} transactions")
    except Exception as e:
        print(f"\n❌ Error checking database status: {e}")
        return False
    
    print("\n🎉 All database tests passed successfully!")
    print("\n📋 Database Summary:")
    print(f"   • Type: {db_config.database_type}")
    print(f"   • Location: {db_config.database_url}")
    print(f"   • Status: Connected and operational")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
