"""
Database Operations Module
Handles all CRUD operations for financial data
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
from .config import get_db

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Main database operations class"""
    
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
    
    def get_categories(self, include_inactive: bool = False) -> List[Category]:
        """Get all categories"""
        query = self.db.query(Category)
        if not include_inactive:
            query = query.filter(Category.is_active == True)
        return query.order_by(Category.name).all()
    
    def get_category_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        return self.db.query(Category).filter(Category.id == category_id).first()
    
    def update_category(self, category_id: int, update_data: Dict[str, Any]) -> Optional[Category]:
        """Update category"""
        try:
            category = self.get_category_by_id(category_id)
            if category:
                for key, value in update_data.items():
                    if hasattr(category, key):
                        setattr(category, key, value)
                category.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(category)
                logger.info(f"Updated category: {category.name}")
                return category
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating category: {e}")
            raise
    
    def delete_category(self, category_id: int) -> bool:
        """Delete category (soft delete)"""
        try:
            category = self.get_category_by_id(category_id)
            if category:
                # Check if category has transactions
                transaction_count = self.db.query(Transaction).filter(
                    Transaction.category_id == category_id
                ).count()
                
                if transaction_count > 0:
                    logger.warning(f"Cannot delete category {category.name} - has {transaction_count} transactions")
                    return False
                
                self.db.delete(category)
                self.db.commit()
                logger.info(f"Deleted category: {category.name}")
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting category: {e}")
            raise
    
    # Transaction Operations
    def create_transaction(self, transaction_data: Dict[str, Any]) -> Transaction:
        """Create a new transaction"""
        try:
            transaction = Transaction(**transaction_data)
            self.db.add(transaction)
            self.db.commit()
            self.db.refresh(transaction)
            
            # Update account balance
            if transaction.account_id:
                self._update_account_balance(transaction.account_id)
            
            logger.info(f"Created transaction: {transaction.description} - ${transaction.amount}")
            return transaction
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error creating transaction: {e}")
            raise
    
    def get_transactions(
        self, 
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[int] = None,
        account_id: Optional[int] = None,
        transaction_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Transaction]:
        """Get transactions with filters"""
        query = self.db.query(Transaction)
        
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)
        if category_id:
            query = query.filter(Transaction.category_id == category_id)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)
        if transaction_type:
            query = query.filter(Transaction.transaction_type == transaction_type)
        
        return query.order_by(desc(Transaction.date)).offset(offset).limit(limit).all()
    
    def get_transaction_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Get transaction by ID"""
        return self.db.query(Transaction).filter(Transaction.id == transaction_id).first()
    
    def update_transaction(self, transaction_id: int, update_data: Dict[str, Any]) -> Optional[Transaction]:
        """Update transaction"""
        try:
            transaction = self.get_transaction_by_id(transaction_id)
            if transaction:
                old_amount = transaction.amount
                old_account_id = transaction.account_id
                
                for key, value in update_data.items():
                    if hasattr(transaction, key):
                        setattr(transaction, key, value)
                
                transaction.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(transaction)
                
                # Update account balances if needed
                if old_account_id:
                    self._update_account_balance(old_account_id)
                if transaction.account_id:
                    self._update_account_balance(transaction.account_id)
                
                logger.info(f"Updated transaction: {transaction.description}")
                return transaction
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating transaction: {e}")
            raise
    
    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete transaction"""
        try:
            transaction = self.get_transaction_by_id(transaction_id)
            if transaction:
                account_id = transaction.account_id
                self.db.delete(transaction)
                self.db.commit()
                
                # Update account balance
                if account_id:
                    self._update_account_balance(account_id)
                
                logger.info(f"Deleted transaction: {transaction.description}")
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting transaction: {e}")
            raise
    
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
    
    def get_accounts(self, include_inactive: bool = False) -> List[Account]:
        """Get all accounts"""
        query = self.db.query(Account)
        if not include_inactive:
            query = query.filter(Account.is_active == True)
        return query.order_by(Account.name).all()
    
    def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """Get account by ID"""
        return self.db.query(Account).filter(Account.id == account_id).first()
    
    def update_account(self, account_id: int, update_data: Dict[str, Any]) -> Optional[Account]:
        """Update account"""
        try:
            account = self.get_account_by_id(account_id)
            if account:
                for key, value in update_data.items():
                    if hasattr(account, key):
                        setattr(account, key, value)
                account.updated_at = datetime.utcnow()
                self.db.commit()
                self.db.refresh(account)
                logger.info(f"Updated account: {account.name}")
                return account
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating account: {e}")
            raise
    
    def delete_account(self, account_id: int) -> bool:
        """Delete account (soft delete)"""
        try:
            account = self.get_account_by_id(account_id)
            if account:
                # Check if account has transactions
                transaction_count = self.db.query(Transaction).filter(
                    Transaction.account_id == account_id
                ).count()
                
                if transaction_count > 0:
                    logger.warning(f"Cannot delete account {account.name} - has {transaction_count} transactions")
                    return False
                
                account.is_active = False
                self.db.commit()
                logger.info(f"Deactivated account: {account.name}")
                return True
            return False
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error deleting account: {e}")
            raise
    
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
    
    def get_budgets(self, period: Optional[str] = None, active_only: bool = True) -> List[Budget]:
        """Get budgets with filters"""
        query = self.db.query(Budget)
        
        if period:
            query = query.filter(Budget.period == period)
        if active_only:
            query = query.filter(Budget.is_active == True)
        
        return query.order_by(Budget.start_date).all()
    
    def get_budget_progress(self, budget_id: int) -> Dict[str, Any]:
        """Get budget progress and spending"""
        budget = self.db.query(Budget).filter(Budget.id == budget_id).first()
        if not budget:
            return {}
        
        # Calculate spending for the budget period
        start_date = budget.start_date
        end_date = budget.end_date or date.today()
        
        spending = self.db.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.category_id == budget.category_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.transaction_type == "expense"
            )
        ).scalar() or 0.0
        
        remaining = budget.amount - spending
        progress = (spending / budget.amount) * 100 if budget.amount > 0 else 0
        
        return {
            "budget": budget,
            "spending": spending,
            "remaining": remaining,
            "progress": progress,
            "is_over_budget": spending > budget.amount
        }
    
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
    
    def get_goals(self, status: Optional[str] = None) -> List[Goal]:
        """Get goals with optional status filter"""
        query = self.db.query(Goal)
        if status:
            query = query.filter(Goal.status == status)
        return query.order_by(Goal.priority, Goal.target_date).all()
    
    def update_goal_progress(self, goal_id: int, amount: float) -> Optional[Goal]:
        """Update goal progress"""
        try:
            goal = self.db.query(Goal).filter(Goal.id == goal_id).first()
            if goal:
                goal.current_amount += amount
                goal.updated_at = datetime.utcnow()
                
                # Check if goal is completed
                if goal.current_amount >= goal.target_amount:
                    goal.status = "completed"
                
                self.db.commit()
                self.db.refresh(goal)
                logger.info(f"Updated goal progress: {goal.name} - ${goal.current_amount}/${goal.target_amount}")
                return goal
            return None
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Error updating goal progress: {e}")
            raise
    
    # Analytics and Reporting
    def get_financial_summary(
        self, 
        start_date: date, 
        end_date: date,
        account_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get financial summary for a date range"""
        query_filters = [
            Transaction.date >= start_date,
            Transaction.date <= end_date
        ]
        
        if account_id:
            query_filters.append(Transaction.account_id == account_id)
        
        # Income
        income = self.db.query(func.sum(Transaction.amount)).filter(
            and_(*query_filters, Transaction.transaction_type == "income")
        ).scalar() or 0.0
        
        # Expenses
        expenses = self.db.query(func.sum(Transaction.amount)).filter(
            and_(*query_filters, Transaction.transaction_type == "expense")
        ).scalar() or 0.0
        
        # Net income
        net_income = income - expenses
        
        # Category breakdown
        category_breakdown = self.db.query(
            Category.name,
            func.sum(Transaction.amount).label('total')
        ).join(Transaction).filter(
            and_(*query_filters, Transaction.transaction_type == "expense")
        ).group_by(Category.name).all()
        
        return {
            "period": {"start": start_date, "end": end_date},
            "income": income,
            "expenses": expenses,
            "net_income": net_income,
            "category_breakdown": [
                {"category": cat.name, "amount": float(total)} 
                for cat, total in category_breakdown
            ]
        }
    
    def get_account_balances(self) -> List[Dict[str, Any]]:
        """Get current balances for all active accounts"""
        accounts = self.get_accounts(include_inactive=False)
        balances = []
        
        for account in accounts:
            # Get latest balance from transactions
            latest_balance = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.account_id == account.id
            ).scalar() or 0.0
            
            balances.append({
                "account_id": account.id,
                "account_name": account.name,
                "account_type": account.account_type,
                "balance": latest_balance,
                "currency": account.currency,
                "institution": account.institution
            })
        
        return balances
    
    # Utility Methods
    def _update_account_balance(self, account_id: int):
        """Update account balance based on transactions"""
        try:
            # Calculate balance from all transactions
            balance = self.db.query(func.sum(Transaction.amount)).filter(
                Transaction.account_id == account_id
            ).scalar() or 0.0
            
            # Update account
            account = self.get_account_by_id(account_id)
            if account:
                account.balance = balance
                account.updated_at = datetime.utcnow()
                self.db.commit()
                
        except SQLAlchemyError as e:
            logger.error(f"Error updating account balance: {e}")
            self.db.rollback()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {
                "total_transactions": self.db.query(Transaction).count(),
                "total_categories": self.db.query(Category).count(),
                "total_accounts": self.db.query(Account).count(),
                "total_budgets": self.db.query(Budget).count(),
                "total_goals": self.db.query(Goal).count(),
                "total_recurring": self.db.query(RecurringTransaction).count(),
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
__all__ = ["DatabaseOperations"]
