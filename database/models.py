"""
Database Models for SEAS Financial Tracker
Defines the structure of financial data tables
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped
from sqlmodel import SQLModel, Field, Relationship
from pydantic import BaseModel, field_validator
import uuid

# SQLAlchemy Base
Base = declarative_base()

# Pydantic Base Models
class FinancialRecordBase(BaseModel):
    """Base model for financial records"""
    
    model_config = {"arbitrary_types_allowed": True}

# Financial Categories
class Category(SQLModel, table=True):
    """Financial transaction categories"""
    __tablename__ = "categories"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    color: Optional[str] = Field(default="#1f77b4", max_length=7)  # Hex color
    icon: Optional[str] = Field(default="💰", max_length=10)
    is_expense: bool = Field(default=True)
    is_income: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transactions: List["Transaction"] = Relationship(back_populates="category")
    
    class Config:
        arbitrary_types_allowed = True

# Financial Transactions
class Transaction(SQLModel, table=True):
    """Financial transactions table"""
    __tablename__ = "transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    transaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    date: date = Field(index=True)
    description: str = Field(max_length=500)
    amount: float = Field()
    transaction_type: str = Field(max_length=20, index=True)  # income, expense, transfer
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    tags: Optional[str] = Field(default=None, max_length=1000)  # JSON string of tags
    notes: Optional[str] = Field(default=None, max_length=2000)
    receipt_path: Optional[str] = Field(default=None, max_length=500)
    is_recurring: bool = Field(default=False)
    recurring_frequency: Optional[str] = Field(default=None, max_length=20)  # daily, weekly, monthly, yearly
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: Optional[Category] = Relationship(back_populates="transactions")
    account: Optional["Account"] = Relationship(back_populates="transactions")
    
    class Config:
        arbitrary_types_allowed = True

# Financial Accounts
class Account(SQLModel, table=True):
    """Financial accounts table"""
    __tablename__ = "accounts"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True, index=True)
    account_type: str = Field(max_length=50, index=True)  # checking, savings, credit, investment
    balance: float = Field(default=0.0)
    currency: str = Field(default="USD", max_length=3)
    institution: Optional[str] = Field(default=None, max_length=100)
    account_number: Optional[str] = Field(default=None, max_length=50)
    routing_number: Optional[str] = Field(default=None, max_length=50)
    interest_rate: Optional[float] = Field(default=None)
    credit_limit: Optional[float] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    transactions: List[Transaction] = Relationship(back_populates="account")
    
    class Config:
        arbitrary_types_allowed = True

# Budgets
class Budget(SQLModel, table=True):
    """Budget planning table"""
    __tablename__ = "budgets"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    amount: float = Field()
    period: str = Field(max_length=20, index=True)  # monthly, yearly
    start_date: date = Field(index=True)
    end_date: Optional[date] = Field(default=None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: Optional[Category] = Relationship()
    
    class Config:
        arbitrary_types_allowed = True

# Goals
class Goal(SQLModel, table=True):
    """Financial goals table"""
    __tablename__ = "goals"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=1000)
    target_amount: float = Field()
    current_amount: float = Field(default=0.0)
    target_date: Optional[date] = Field(default=None)
    priority: str = Field(default="medium", max_length=20)  # low, medium, high
    status: str = Field(default="active", max_length=20)  # active, completed, paused
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True

# Recurring Transactions
class RecurringTransaction(SQLModel, table=True):
    """Recurring transactions table"""
    __tablename__ = "recurring_transactions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str = Field(max_length=500)
    amount: float = Field()
    frequency: str = Field(max_length=20)  # daily, weekly, monthly, yearly
    start_date: date = Field(index=True)
    end_date: Optional[date] = Field(default=None)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    account_id: Optional[int] = Field(default=None, foreign_key="accounts.id")
    is_active: bool = Field(default=True)
    last_generated: Optional[date] = Field(default=None)
    next_generation: Optional[date] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    category: Optional[Category] = Relationship()
    account: Optional[Account] = Relationship()
    
    class Config:
        arbitrary_types_allowed = True

# Import/Export History
class ImportExportHistory(SQLModel, table=True):
    """Track import/export operations"""
    __tablename__ = "import_export_history"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    operation_type: str = Field(max_length=20)  # import, export
    file_name: str = Field(max_length=255)
    file_size: Optional[int] = Field(default=None)
    records_processed: int = Field(default=0)
    records_successful: int = Field(default=0)
    records_failed: int = Field(default=0)
    status: str = Field(max_length=20)  # success, failed, partial
    error_message: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        arbitrary_types_allowed = True

# Database Indexes for Performance
class DatabaseIndexes:
    """Define database indexes for better performance"""
    
    @staticmethod
    def create_indexes(engine):
        """Create database indexes"""
        from sqlalchemy import text
        
        indexes = [
            # Transaction indexes
            "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_category ON transactions(category_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_account ON transactions(account_id)",
            "CREATE INDEX IF NOT EXISTS idx_transactions_amount ON transactions(amount)",
            
            # Account indexes
            "CREATE INDEX IF NOT EXISTS idx_accounts_type ON accounts(account_type)",
            "CREATE INDEX IF NOT EXISTS idx_accounts_active ON accounts(is_active)",
            
            # Budget indexes
            "CREATE INDEX IF NOT EXISTS idx_budgets_period ON budgets(period)",
            "CREATE INDEX IF NOT EXISTS idx_budgets_active ON budgets(is_active)",
            
            # Goal indexes
            "CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)",
            "CREATE INDEX IF NOT EXISTS idx_goals_priority ON goals(priority)",
            
            # Recurring transaction indexes
            "CREATE INDEX IF NOT EXISTS idx_recurring_active ON recurring_transactions(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_recurring_next_gen ON recurring_transactions(next_generation)",
        ]
        
        with engine.connect() as conn:
            for index_sql in indexes:
                try:
                    conn.execute(text(index_sql))
                    conn.commit()
                except Exception as e:
                    print(f"Warning: Could not create index: {e}")

# Pydantic models for API responses
class TransactionResponse(BaseModel):
    """Transaction response model"""
    id: int
    transaction_id: str
    date: date
    description: str
    amount: float
    transaction_type: str
    category_name: Optional[str] = None
    account_name: Optional[str] = None
    tags: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class CategoryResponse(BaseModel):
    """Category response model"""
    id: int
    name: str
    description: Optional[str] = None
    color: str
    icon: str
    is_expense: bool
    is_income: bool
    transaction_count: int = 0
    
    class Config:
        from_attributes = True

class AccountResponse(BaseModel):
    """Account response model"""
    id: int
    name: str
    account_type: str
    balance: float
    currency: str
    institution: Optional[str] = None
    is_active: bool
    transaction_count: int = 0
    
    class Config:
        from_attributes = True

# Export all models
__all__ = [
    "Base",
    "Category",
    "Transaction", 
    "Account",
    "Budget",
    "Goal",
    "RecurringTransaction",
    "ImportExportHistory",
    "TransactionResponse",
    "CategoryResponse",
    "AccountResponse",
    "DatabaseIndexes"
]
