"""
Database Package for SEAS Financial Tracker
Provides database configuration, models, and operations
"""

from .config import DatabaseConfig, get_db, init_database
from .simple_models import (
    Base, Category, Transaction, Account, Budget, Goal,
    ImportExportHistory
)
from .simple_operations import SimpleDatabaseOperations
from .init_db import init_database, reset_database

__all__ = [
    # Configuration
    "DatabaseConfig",
    "get_db",
    "init_database",
    
    # Models
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
    "DatabaseIndexes",
    
    # Operations
    "SimpleDatabaseOperations",
    
    # Initialization
    "reset_database"
]

# Version info
__version__ = "1.0.0"
