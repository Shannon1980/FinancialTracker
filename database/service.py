"""
Database Service Layer for SEAS Financial Tracker
Provides efficient database operations with connection pooling and context managers
"""

import logging
from contextlib import contextmanager
from typing import Generator, Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError, IntegrityError

from .config import get_db
from .simple_operations import SimpleDatabaseOperations
from .simple_models import Category, Transaction, Account, Budget, Goal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseServiceError(Exception):
    """Custom exception for database service errors"""
    pass

class DatabaseConnectionError(DatabaseServiceError):
    """Exception for database connection issues"""
    pass

class DatabaseValidationError(DatabaseServiceError):
    """Exception for data validation issues"""
    pass

class DatabaseService:
    """Database service with connection pooling and error handling"""
    
    def __init__(self):
        self._operations_cache = {}
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager for database sessions with automatic cleanup"""
        session = None
        try:
            session = next(get_db())
            yield session
        except Exception as e:
            if session:
                session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseConnectionError(f"Failed to establish database session: {e}")
        finally:
            if session:
                try:
                    session.close()
                except Exception as e:
                    logger.warning(f"Error closing session: {e}")
    
    def _get_operations(self, session: Session) -> SimpleDatabaseOperations:
        """Get database operations instance for a session"""
        session_id = id(session)
        if session_id not in self._operations_cache:
            self._operations_cache[session_id] = SimpleDatabaseOperations(session)
        return self._operations_cache[session_id]
    
    def _handle_database_error(self, operation: str, error: Exception) -> None:
        """Handle database errors with appropriate logging and user-friendly messages"""
        if isinstance(error, OperationalError):
            logger.error(f"Database operation failed: {operation} - {error}")
            raise DatabaseConnectionError(f"Database operation failed. Please try again.")
        elif isinstance(error, IntegrityError):
            logger.error(f"Data integrity error: {operation} - {error}")
            raise DatabaseValidationError(f"Invalid data provided. Please check your input.")
        elif isinstance(error, SQLAlchemyError):
            logger.error(f"SQLAlchemy error: {operation} - {error}")
            raise DatabaseServiceError(f"Database error occurred: {error}")
        else:
            logger.error(f"Unexpected error in {operation}: {error}")
            raise DatabaseServiceError(f"An unexpected error occurred: {error}")
    
    # Category Operations
    def get_categories(self) -> List[Category]:
        """Get all categories with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_categories()
        except Exception as e:
            self._handle_database_error("get_categories", e)
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_category_by_id(category_id)
        except Exception as e:
            self._handle_database_error("get_category_by_id", e)
    
    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """Create a new category with validation and error handling"""
        try:
            # Validate required fields
            required_fields = ['name']
            for field in required_fields:
                if not category_data.get(field):
                    raise DatabaseValidationError(f"Missing required field: {field}")
            
            with self.get_session() as session:
                operations = self._get_operations(session)
                category = operations.create_category(category_data)
                session.commit()
                logger.info(f"Category created: {category.name}")
                return category
        except Exception as e:
            self._handle_database_error("create_category", e)
    
    def update_category(self, category_id: int, category_data: Dict[str, Any]) -> Category:
        """Update an existing category with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                category = operations.update_category(category_id, category_data)
                session.commit()
                logger.info(f"Category updated: {category.name}")
                return category
        except Exception as e:
            self._handle_database_error("update_category", e)
    
    def delete_category(self, category_id: int) -> bool:
        """Delete a category with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                success = operations.delete_category(category_id)
                if success:
                    session.commit()
                    logger.info(f"Category deleted: ID {category_id}")
                return success
        except Exception as e:
            self._handle_database_error("delete_category", e)
    
    # Account Operations
    def get_accounts(self) -> List[Account]:
        """Get all accounts with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_accounts()
        except Exception as e:
            self._handle_database_error("get_accounts", e)
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_account_by_id(account_id)
        except Exception as e:
            self._handle_database_error("get_account_by_id", e)
    
    def create_account(self, account_data: Dict[str, Any]) -> Account:
        """Create a new account with validation and error handling"""
        try:
            # Validate required fields
            required_fields = ['name', 'account_type']
            for field in required_fields:
                if not account_data.get(field):
                    raise DatabaseValidationError(f"Missing required field: {field}")
            
            with self.get_session() as session:
                operations = self._get_operations(session)
                account = operations.create_account(account_data)
                session.commit()
                logger.info(f"Account created: {account.name}")
                return account
        except Exception as e:
            self._handle_database_error("create_account", e)
    
    def update_account(self, account_id: int, account_data: Dict[str, Any]) -> Account:
        """Update an existing account with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                account = operations.update_account(account_id, account_data)
                session.commit()
                logger.info(f"Account updated: {account.name}")
                return account
        except Exception as e:
            self._handle_database_error("update_account", e)
    
    # Transaction Operations
    def get_transactions(self, limit: Optional[int] = None, 
                        category_id: Optional[int] = None,
                        account_id: Optional[int] = None,
                        start_date: Optional[str] = None,
                        end_date: Optional[str] = None) -> List[Transaction]:
        """Get transactions with optional filtering and error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_transactions(
                    limit=limit,
                    category_id=category_id,
                    account_id=account_id,
                    start_date=start_date,
                    end_date=end_date
                )
        except Exception as e:
            self._handle_database_error("get_transactions", e)
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_transaction_by_id(transaction_id)
        except Exception as e:
            self._handle_database_error("get_transaction_by_id", e)
    
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction with validation and error handling"""
        try:
            # Validate required fields
            required_fields = ['date', 'description', 'amount', 'transaction_type']
            for field in required_fields:
                if not transaction_data.get(field):
                    raise DatabaseValidationError(f"Missing required field: {field}")
            
            # Validate amount
            if transaction_data['amount'] <= 0:
                raise DatabaseValidationError("Amount must be greater than 0")
            
            with self.get_session() as session:
                operations = self._get_operations(session)
                transaction = operations.create_transaction(transaction_data)
                session.commit()
                logger.info(f"Transaction created: {transaction.description} - ${transaction.amount:,.2f}")
                return transaction
        except Exception as e:
            self._handle_database_error("create_transaction", e)
    
    def update_transaction(self, transaction_id: int, transaction_data: Dict[str, Any]) -> Transaction:
        """Update an existing transaction with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                transaction = operations.update_transaction(transaction_id, transaction_data)
                session.commit()
                logger.info(f"Transaction updated: {transaction.description}")
                return transaction
        except Exception as e:
            self._handle_database_error("update_transaction", e)
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                success = operations.delete_transaction(transaction_id)
                if success:
                    session.commit()
                    logger.info(f"Transaction deleted: ID {transaction_id}")
                return success
        except Exception as e:
            self._handle_database_error("delete_transaction", e)
    
    # Budget Operations
    def get_budgets(self) -> List[Budget]:
        """Get all budgets with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_budgets()
        except Exception as e:
            self._handle_database_error("get_budgets", e)
    
    def create_budget(self, budget_data: Dict[str, Any]) -> Budget:
        """Create a new budget with validation and error handling"""
        try:
            # Validate required fields
            required_fields = ['name', 'amount', 'period']
            for field in required_fields:
                if not budget_data.get(field):
                    raise DatabaseValidationError(f"Missing required field: {field}")
            
            with self.get_session() as session:
                operations = self._get_operations(session)
                budget = operations.create_budget(budget_data)
                session.commit()
                logger.info(f"Budget created: {budget.name}")
                return budget
        except Exception as e:
            self._handle_database_error("create_budget", e)
    
    # Goal Operations
    def get_goals(self) -> List[Goal]:
        """Get all goals with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_goals()
        except Exception as e:
            self._handle_database_error("get_goals", e)
    
    def create_goal(self, goal_data: Dict[str, Any]) -> Goal:
        """Create a new goal with validation and error handling"""
        try:
            # Validate required fields
            required_fields = ['name', 'target_amount']
            for field in required_fields:
                if not goal_data.get(field):
                    raise DatabaseValidationError(f"Missing required field: {field}")
            
            with self.get_session() as session:
                operations = self._get_operations(session)
                goal = operations.create_goal(goal_data)
                session.commit()
                logger.info(f"Goal created: {goal.name}")
                return goal
        except Exception as e:
            self._handle_database_error("create_goal", e)
    
    # Analytics Operations
    def get_financial_summary(self, start_date: str, end_date: str) -> Dict[str, float]:
        """Get financial summary for date range with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_financial_summary(start_date, end_date)
        except Exception as e:
            self._handle_database_error("get_financial_summary", e)
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics with error handling"""
        try:
            with self.get_session() as session:
                operations = self._get_operations(session)
                return operations.get_database_stats()
        except Exception as e:
            self._handle_database_error("get_database_stats", e)
    
    # Utility Methods
    def test_connection(self) -> bool:
        """Test database connection with error handling"""
        try:
            from .config import DatabaseConfig
            db_config = DatabaseConfig()
            return db_config.test_connection()
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def clear_cache(self) -> None:
        """Clear the operations cache"""
        self._operations_cache.clear()
        logger.info("Database operations cache cleared")

# Global instance for easy access
db_service = DatabaseService()
