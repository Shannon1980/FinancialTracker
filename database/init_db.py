"""
Database Initialization Script
Creates tables and populates with sample data
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel

from .config import DatabaseConfig
from .simple_models import (
    Base, Category, Transaction, Account, Budget, Goal, 
    ImportExportHistory
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and sample data"""
    
    # Create database configuration
    db_config = DatabaseConfig()
    database_url = db_config.get_database_url()
    
    logger.info(f"Initializing database: {database_url}")
    
    try:
        # Create engine
        engine = db_config.create_engine()
        
        # Create all tables
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        
        # Create indexes
        logger.info("Creating database indexes...")
        # Indexes will be created automatically by SQLAlchemy
        
        # Create session
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        # Check if database is empty
        if _is_database_empty(db):
            logger.info("Database is empty, creating sample data...")
            _create_sample_data(db)
        else:
            logger.info("Database already contains data, skipping sample data creation")
        
        db.close()
        
        logger.info("✅ Database initialization completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

def _is_database_empty(db):
    """Check if database has any data"""
    try:
        # Check if categories table has data
        result = db.execute(text("SELECT COUNT(*) FROM categories")).scalar()
        return result == 0
    except Exception:
        return True

def _create_sample_data(db):
    """Create sample data for the application"""
    
    # Sample Categories
    sample_categories = [
        {
            "name": "Food & Dining",
            "description": "Restaurants, groceries, and dining out",
            "color": "#FF6B6B",
            "icon": "🍽️",
            "is_expense": True,
            "is_income": False
        },
        {
            "name": "Transportation",
            "description": "Gas, public transit, rideshare",
            "color": "#4ECDC4",
            "icon": "🚗",
            "is_expense": True,
            "is_income": False
        },
        {
            "name": "Shopping",
            "description": "Clothing, electronics, household items",
            "color": "#45B7D1",
            "icon": "🛍️",
            "is_expense": True,
            "is_income": False
        },
        {
            "name": "Entertainment",
            "description": "Movies, games, hobbies",
            "color": "#96CEB4",
            "icon": "🎬",
            "is_expense": True,
            "is_income": False
        },
        {
            "name": "Healthcare",
            "description": "Medical expenses, prescriptions",
            "color": "#FFEAA7",
            "icon": "🏥",
            "is_expense": True,
            "is_income": False
        },
        {
            "name": "Salary",
            "description": "Regular employment income",
            "color": "#DDA0DD",
            "icon": "💰",
            "is_expense": False,
            "is_income": True
        },
        {
            "name": "Freelance",
            "description": "Contract and freelance work",
            "color": "#98D8C8",
            "icon": "💼",
            "is_expense": False,
            "is_income": True
        },
        {
            "name": "Investment",
            "description": "Dividends, interest, capital gains",
            "color": "#F7DC6F",
            "icon": "📈",
            "is_expense": False,
            "is_income": True
        }
    ]
    
    # Create categories
    categories = []
    for cat_data in sample_categories:
        category = Category(**cat_data)
        db.add(category)
        db.flush()  # Get the ID
        categories.append(category)
    
    # Sample Accounts
    sample_accounts = [
        {
            "name": "Main Checking",
            "account_type": "checking",
            "balance": 5000.00,
            "currency": "USD",
            "institution": "Local Bank"
        },
        {
            "name": "Savings Account",
            "account_type": "savings",
            "balance": 15000.00,
            "currency": "USD",
            "institution": "Local Bank"
        },
        {
            "name": "Credit Card",
            "account_type": "credit",
            "balance": -2500.00,
            "currency": "USD",
            "institution": "Credit Union",
            "credit_limit": 10000.00
        },
        {
            "name": "Investment Portfolio",
            "account_type": "investment",
            "balance": 50000.00,
            "currency": "USD",
            "institution": "Investment Firm"
        }
    ]
    
    # Create accounts
    accounts = []
    for acc_data in sample_accounts:
        account = Account(**acc_data)
        db.add(account)
        db.flush()  # Get the ID
        accounts.append(account)
    
    # Sample Transactions (last 30 days)
    from datetime import datetime, timedelta
    import random
    
    today = datetime.now().date()
    transaction_types = ["expense", "income"]
    
    # Get category IDs for expenses and income
    expense_categories = [c for c in categories if c.is_expense]
    income_categories = [c for c in categories if c.is_income]
    
    sample_transactions = []
    
    # Generate random transactions for the last 30 days
    for i in range(50):  # 50 sample transactions
        # Random date in last 30 days
        days_ago = random.randint(0, 30)
        transaction_date = today - timedelta(days=days_ago)
        
        # Random transaction type
        transaction_type = random.choice(transaction_types)
        
        if transaction_type == "expense":
            # Expense transaction
            category = random.choice(expense_categories)
            amount = round(random.uniform(10.0, 200.0), 2)
            descriptions = [
                "Grocery shopping", "Restaurant meal", "Gas station",
                "Online purchase", "Coffee shop", "Movie tickets",
                "Clothing store", "Pharmacy", "Hardware store"
            ]
        else:
            # Income transaction
            category = random.choice(income_categories)
            amount = round(random.uniform(100.0, 2000.0), 2)
            descriptions = [
                "Salary payment", "Freelance work", "Investment dividend",
                "Bonus payment", "Side hustle", "Refund"
            ]
        
        transaction_data = {
            "date": transaction_date,
            "description": random.choice(descriptions),
            "amount": amount,
            "transaction_type": transaction_type,
            "category_id": category.id,
            "account_id": random.choice(accounts).id,
            "notes": f"Sample transaction {i+1}"
        }
        
        sample_transactions.append(transaction_data)
    
    # Create transactions
    for trans_data in sample_transactions:
        transaction = Transaction(**trans_data)
        db.add(transaction)
    
    # Sample Budgets
    sample_budgets = [
        {
            "name": "Monthly Food Budget",
            "category_id": next(c.id for c in categories if c.name == "Food & Dining"),
            "amount": 600.00,
            "period": "monthly",
            "start_date": today.replace(day=1)
        },
        {
            "name": "Monthly Transportation Budget",
            "category_id": next(c.id for c in categories if c.name == "Transportation"),
            "amount": 300.00,
            "period": "monthly",
            "start_date": today.replace(day=1)
        },
        {
            "name": "Monthly Entertainment Budget",
            "category_id": next(c.id for c in categories if c.name == "Entertainment"),
            "amount": 200.00,
            "period": "monthly",
            "start_date": today.replace(day=1)
        }
    ]
    
    # Create budgets
    for budget_data in sample_budgets:
        budget = Budget(**budget_data)
        db.add(budget)
    
    # Sample Goals
    sample_goals = [
        {
            "name": "Emergency Fund",
            "description": "Build 6-month emergency fund",
            "target_amount": 30000.00,
            "current_amount": 15000.00,
            "target_date": today + timedelta(days=365),
            "priority": "high",
            "status": "active"
        },
        {
            "name": "Vacation Fund",
            "description": "Save for summer vacation",
            "target_amount": 5000.00,
            "current_amount": 2000.00,
            "target_date": today + timedelta(days=180),
            "priority": "medium",
            "status": "active"
        },
        {
            "name": "New Car",
            "description": "Save for down payment on new car",
            "target_amount": 10000.00,
            "current_amount": 5000.00,
            "target_date": today + timedelta(days=730),
            "priority": "medium",
            "status": "active"
        }
    ]
    
    # Create goals
    for goal_data in sample_goals:
        goal = Goal(**goal_data)
        db.add(goal)
    
    # Commit all changes
    db.commit()
    
    logger.info(f"✅ Created {len(categories)} categories")
    logger.info(f"✅ Created {len(accounts)} accounts")
    logger.info(f"✅ Created {len(sample_transactions)} transactions")
    logger.info(f"✅ Created {len(sample_budgets)} budgets")
    logger.info(f"✅ Created {len(sample_goals)} goals")

def reset_database():
    """Reset database (drop all tables and recreate)"""
    
    db_config = DatabaseConfig()
    engine = db_config.create_engine()
    
    logger.warning("⚠️ This will delete ALL data! Are you sure?")
    response = input("Type 'YES' to confirm: ")
    
    if response == "YES":
        logger.info("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        logger.info("Recreating tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Creating sample data...")
        _create_sample_data(db_config.get_session())
        
        logger.info("✅ Database reset completed!")
    else:
        logger.info("Database reset cancelled.")

if __name__ == "__main__":
    # Initialize database when run directly
    init_database()
