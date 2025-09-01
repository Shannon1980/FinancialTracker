"""
Database package for SEAS Financial Tracker
"""

# Core database components
from .config import DatabaseConfig, get_db, init_database
from .simple_models import (
    Base, Category, Transaction, Account, Budget, Goal, ImportExportHistory
)
from .simple_operations import SimpleDatabaseOperations
from .service import DatabaseService, db_service, DatabaseServiceError, DatabaseConnectionError, DatabaseValidationError

# Database management
from .init_db import reset_database

# Export main components
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
    "ImportExportHistory",
    
    # Operations
    "SimpleDatabaseOperations",
    
    # Service Layer
    "DatabaseService",
    "db_service",
    "DatabaseServiceError",
    "DatabaseConnectionError", 
    "DatabaseValidationError",
    
    # Management
    "reset_database"
]

# Version info
__version__ = "1.0.0"
