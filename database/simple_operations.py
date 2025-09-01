"""
Simplified Database Operations Module
Handles basic CRUD operations for financial data
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from sqlalchemy.exc import SQLAlchemyError
import logging

from .simple_models import (
    Category, Transaction, Account, Budget, Goal, 
    ImportExportHistory
)

logger = logging.getLogger(__name__)

class SimpleDatabaseOperations:
    """Simplified database operations class"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Category Operations
    def create_category(self, category_data: Dict[str, Any]) -> Category:
        """Create a new category"""
        try:
            category = Category(**category_data)
            self.db.add(category)
            self.db.commit()
            self.db.refresh(category)
            logger.info(f"Created category: {category.name}")
            return category
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating category: {e}")
            raise
    
    def get_categories(self) -> List[Category]:
        """Get all categories"""
        return self.db.query(Category).order_by(Category.name).all()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    # Transaction Operations
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        try:
            transaction = Transaction(**transaction_data)
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            logger.info(f"Created transaction: {transaction.description} - ${transaction.amount}")
            return transaction
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise
    
    def get_transactions(self, limit: int = 100) -> List[Transaction]:
        """Get transactions with limit"""
        return self.db.query(Transaction).order_by(desc(Transaction.date)).limit(limit).all()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    # Account Operations
    def create_account(self, account_data: Dict[str, Any]) -> Account:
        """Create a new account"""
        try:
            account = Account(**account_data)
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
            logger.info(f"Created account: {account.name}")
            return account
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating account: {e}")
            raise
    
    def get_accounts(self) -> List[Account]:
        """Get all active accounts"""
        return self.db.query(Account).filter(Account.is_active == True).order_by(Account.name).all()
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    # Budget Operations
    def create_budget(self, budget_data: Dict[str, Any]) -> Budget:
        """Create a new budget"""
        try:
            budget = Budget(**budget_data)
            self.db.add(budget)
            self.db.commit()
            self.db.refresh(budget)
            logger.info(f"Created budget: {budget.name}")
            return budget
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating budget: {e}")
            raise
    
    def get_budgets(self) -> List[Budget]:
        """Get all active budgets"""
        return self.db.query(Budget).filter(Budget.is_active == True).order_by(Budget.start_date).all()
    
    # Goal Operations
    def create_goal(self, goal_data: Dict[str, Any]) -> Goal:
        """Create a new financial goal"""
        try:
            goal = Goal(**goal_data)
            self.db.add(goal)
            self.db.commit()
            self.db.refresh(goal)
            logger.info(f"Created goal: {goal.name}")
            return goal
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating goal: {e}")
            raise
    
    def get_goals(self) -> List[Goal]:
        """Get all goals"""
        return self.db.query(Goal).order_by(Goal.priority, Goal.target_date).all()
    
    # Analytics and Reporting
    def get_financial_summary(self, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get financial summary for a date range"""
        # Income
        income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.transaction_type == "income"
            )
        ).scalar() or 0.0
        
        # Expenses
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.transaction_type == "expense"
            )
        ).scalar() or 0.0
        
        # Net income
        net_income = income - expenses
        
        return {
            "period": {"start": start_date, "end": end_date},
            "income": income,
            "expenses": expenses,
            "net_income": net_income
        }
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {
                "total_transactions": self.db.query(Transaction).count(),
                "total_categories": self.db.query(Category).count(),
                "total_accounts": self.db.query(Account).count(),
                "total_budgets": self.db.query(Budget).count(),
                "total_goals": self.db.query(Goal).count(),
            }
            
            # Date range of transactions
            date_range = self.db.query(
                func.min(Transaction.date),
                func.max(Transaction.date)
            ).first()
            
            if date_range and date_range[0]:
                stats["date_range"] = {
                    "earliest": date_range[0],
                    "latest": date_range[1]
                }
            
            return stats
            
        except SQLAlchemyError as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Export the main class
__all__ = ["SimpleDatabaseOperations"]
