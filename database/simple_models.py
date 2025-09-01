"""
Simplified Database Models for SEAS Financial Tracker
Compatible with current Python and package versions
"""

from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# SQLAlchemy Base
Base = declarative_base()

# Financial Categories
class Category(Base):
    """Financial transaction categories"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#1f77b4")  # Hex color
    icon = Column(String(10), default="💰")
    is_expense = Column(Boolean, default=True)
    is_income = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="category")

# Financial Transactions
class Transaction(Base):
    """Financial transactions table"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    description = Column(String(500), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(String(20), nullable=False, index=True)  # income, expense, transfer
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    notes = Column(Text, nullable=True)
    receipt_path = Column(String(500), nullable=True)
    is_recurring = Column(Boolean, default=False)
    recurring_frequency = Column(String(20), nullable=True)  # daily, weekly, monthly, yearly
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")

# Financial Accounts
class Account(Base):
    """Financial accounts table"""
    __tablename__ = "accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    account_type = Column(String(50), nullable=False, index=True)  # checking, savings, credit, investment
    balance = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    institution = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=True)
    routing_number = Column(String(50), nullable=True)
    interest_rate = Column(Float, nullable=True)
    credit_limit = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = relationship("Transaction", back_populates="account")

# Budgets
class Budget(Base):
    """Budget planning table"""
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    amount = Column(Float, nullable=False)
    period = Column(String(20), nullable=False, index=True)  # monthly, yearly
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    category = relationship("Category")

# Goals
class Goal(Base):
    """Financial goals table"""
    __tablename__ = "goals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date, nullable=True)
    priority = Column(String(20), default="medium")  # low, medium, high
    status = Column(String(20), default="active")  # active, completed, paused
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Import/Export History
class ImportExportHistory(Base):
    """Track import/export operations"""
    __tablename__ = "import_export_history"
    
    id = Column(Integer, primary_key=True, index=True)
    operation_type = Column(String(20), nullable=False)  # import, export
    file_name = Column(String(255), nullable=False)
    file_size = Column(Integer, nullable=True)
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    status = Column(String(20), nullable=False)  # success, failed, partial
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Export all models
__all__ = [
    "Base",
    "Category",
    "Transaction", 
    "Account",
    "Budget",
    "Goal",
    "ImportExportHistory"
]
