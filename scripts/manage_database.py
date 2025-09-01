#!/usr/bin/env python3
"""
Database Management Script for SEAS Financial Tracker
Provides administrative functions for database management
"""

import sys
import os
from pathlib import Path
from datetime import datetime, date, timedelta
import argparse
import json

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database import (
    init_database, SimpleDatabaseOperations, get_db,
    Category, Transaction, Account, Budget, Goal
)

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n--- {title} ---")

def show_database_stats():
    """Display database statistics"""
    print_header("Database Statistics")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        stats = db_ops.get_database_stats()
        db.close()
        
        print(f"📊 Total Transactions: {stats.get('total_transactions', 0)}")
        print(f"🏷️ Total Categories: {stats.get('total_categories', 0)}")
        print(f"🏦 Total Accounts: {stats.get('total_accounts', 0)}")
        print(f"💰 Total Budgets: {stats.get('total_budgets', 0)}")
        print(f"🎯 Total Goals: {stats.get('total_goals', 0)}")
        
        if 'date_range' in stats:
            print(f"📅 Data Range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
        
    except Exception as e:
        print(f"❌ Error getting database stats: {e}")

def show_categories():
    """Display all categories"""
    print_header("Categories")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        categories = db_ops.get_categories()
        db.close()
        
        if not categories:
            print("No categories found.")
            return
        
        for i, category in enumerate(categories, 1):
            print(f"{i:2d}. {category.icon} {category.name}")
            print(f"    Description: {category.description or 'No description'}")
            print(f"    Type: {'Expense' if category.is_expense else 'Income'}")
            print(f"    Color: {category.color}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting categories: {e}")

def show_accounts():
    """Display all accounts"""
    print_header("Accounts")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        accounts = db_ops.get_accounts()
        db.close()
        
        if not accounts:
            print("No accounts found.")
            return
        
        for i, account in enumerate(accounts, 1):
            print(f"{i:2d}. 🏦 {account.name}")
            print(f"    Type: {account.account_type}")
            print(f"    Balance: ${account.balance:,.2f} {account.currency}")
            print(f"    Institution: {account.institution or 'N/A'}")
            print(f"    Status: {'Active' if account.is_active else 'Inactive'}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting accounts: {e}")

def show_recent_transactions(limit=20):
    """Display recent transactions"""
    print_header(f"Recent Transactions (Last {limit})")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        transactions = db_ops.get_transactions(limit=limit)
        db.close()
        
        if not transactions:
            print("No transactions found.")
            return
        
        for i, trans in enumerate(transactions, 1):
            category_name = trans.category.name if trans.category else 'N/A'
            account_name = trans.account.name if trans.account else 'N/A'
            
            print(f"{i:2d}. {trans.date} - {trans.description}")
            print(f"    Amount: ${trans.amount:,.2f} ({trans.transaction_type})")
            print(f"    Category: {category_name}")
            print(f"    Account: {account_name}")
            if trans.notes:
                print(f"    Notes: {trans.notes}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting transactions: {e}")

def show_budgets():
    """Display all budgets"""
    print_header("Budgets")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        budgets = db_ops.get_budgets()
        db.close()
        
        if not budgets:
            print("No budgets found.")
            return
        
        for i, budget in enumerate(budgets, 1):
            category_name = budget.category.name if budget.category else 'N/A'
            print(f"{i:2d}. {budget.name}")
            print(f"    Amount: ${budget.amount:,.2f}")
            print(f"    Period: {budget.period}")
            print(f"    Category: {category_name}")
            print(f"    Start Date: {budget.start_date}")
            print(f"    Status: {'Active' if budget.is_active else 'Inactive'}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting budgets: {e}")

def show_goals():
    """Display all goals"""
    print_header("Financial Goals")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        goals = db_ops.get_goals()
        db.close()
        
        if not goals:
            print("No goals found.")
            return
        
        for i, goal in enumerate(goals, 1):
            progress = (goal.current_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
            print(f"{i:2d}. {goal.name}")
            print(f"    Target: ${goal.target_amount:,.2f}")
            print(f"    Current: ${goal.current_amount:,.2f}")
            print(f"    Progress: {progress:.1f}%")
            print(f"    Priority: {goal.priority.title()}")
            print(f"    Status: {goal.status.title()}")
            if goal.target_date:
                print(f"    Target Date: {goal.target_date}")
            print()
        
    except Exception as e:
        print(f"❌ Error getting goals: {e}")

def add_sample_transaction():
    """Add a sample transaction"""
    print_header("Add Sample Transaction")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        
        # Get first category and account
        categories = db_ops.get_categories()
        accounts = db_ops.get_accounts()
        
        if not categories or not accounts:
            print("❌ Need at least one category and account to add transactions.")
            return
        
        # Create sample transaction
        transaction_data = {
            "date": date.today(),
            "description": "Sample transaction from management script",
            "amount": 99.99,
            "transaction_type": "expense",
            "category_id": categories[0].id,
            "account_id": accounts[0].id,
            "notes": "Added via management script"
        }
        
        new_transaction = db_ops.create_transaction(transaction_data)
        db.close()
        
        print(f"✅ Sample transaction added: {new_transaction.description} - ${new_transaction.amount:,.2f}")
        
    except Exception as e:
        print(f"❌ Error adding sample transaction: {e}")

def export_data_to_json(filename="financial_data_export.json"):
    """Export all data to JSON file"""
    print_header(f"Export Data to {filename}")
    
    try:
        db = next(get_db())
        db_ops = SimpleDatabaseOperations(db)
        
        # Collect all data
        export_data = {
            "export_date": datetime.now().isoformat(),
            "categories": [],
            "accounts": [],
            "transactions": [],
            "budgets": [],
            "goals": []
        }
        
        # Export categories
        categories = db_ops.get_categories()
        for cat in categories:
            export_data["categories"].append({
                "name": cat.name,
                "description": cat.description,
                "color": cat.color,
                "icon": cat.icon,
                "is_expense": cat.is_expense,
                "is_income": cat.is_income
            })
        
        # Export accounts
        accounts = db_ops.get_accounts()
        for acc in accounts:
            export_data["accounts"].append({
                "name": acc.name,
                "account_type": acc.account_type,
                "balance": acc.balance,
                "currency": acc.currency,
                "institution": acc.institution
            })
        
        # Export transactions
        transactions = db_ops.get_transactions(limit=1000)
        for trans in transactions:
            export_data["transactions"].append({
                "date": trans.date.isoformat(),
                "description": trans.description,
                "amount": trans.amount,
                "transaction_type": trans.transaction_type,
                "category": trans.category.name if trans.category else None,
                "account": trans.account.name if trans.account else None,
                "notes": trans.notes
            })
        
        # Export budgets
        budgets = db_ops.get_budgets()
        for budget in budgets:
            export_data["budgets"].append({
                "name": budget.name,
                "amount": budget.amount,
                "period": budget.period,
                "category": budget.category.name if budget.category else None
            })
        
        # Export goals
        goals = db_ops.get_goals()
        for goal in goals:
            export_data["goals"].append({
                "name": goal.name,
                "description": goal.description,
                "target_amount": goal.target_amount,
                "current_amount": goal.current_amount,
                "priority": goal.priority,
                "status": goal.status
            })
        
        db.close()
        
        # Write to file
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"✅ Data exported to {filename}")
        print(f"📊 Exported {len(export_data['categories'])} categories")
        print(f"📊 Exported {len(export_data['accounts'])} accounts")
        print(f"📊 Exported {len(export_data['transactions'])} transactions")
        print(f"📊 Exported {len(export_data['budgets'])} budgets")
        print(f"📊 Exported {len(export_data['goals'])} goals")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")

def reset_database():
    """Reset database (drop all data and recreate)"""
    print_header("Reset Database")
    
    print("⚠️  WARNING: This will delete ALL data!")
    response = input("Type 'RESET' to confirm: ")
    
    if response == "RESET":
        try:
            from database.init_db import reset_database as reset_db
            reset_db()
            print("✅ Database reset completed!")
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
    else:
        print("Database reset cancelled.")

def show_menu():
    """Show the main menu"""
    print_header("Database Management Menu")
    print("1. 📊 Show Database Statistics")
    print("2. 🏷️ Show Categories")
    print("3. 🏦 Show Accounts")
    print("4. 💳 Show Recent Transactions")
    print("5. 💰 Show Budgets")
    print("6. 🎯 Show Goals")
    print("7. ➕ Add Sample Transaction")
    print("8. 📤 Export Data to JSON")
    print("9. 🔄 Reset Database")
    print("0. ❌ Exit")
    print("-" * 60)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SEAS Financial Tracker Database Management")
    parser.add_argument("--command", "-c", help="Run specific command and exit")
    parser.add_argument("--export", "-e", help="Export data to specified file")
    parser.add_argument("--stats", "-s", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    # If specific command provided, run it and exit
    if args.command:
        if args.command == "stats":
            show_database_stats()
        elif args.command == "categories":
            show_categories()
        elif args.command == "accounts":
            show_accounts()
        elif args.command == "transactions":
            show_recent_transactions()
        elif args.command == "budgets":
            show_budgets()
        elif args.command == "goals":
            show_goals()
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
        return 0
    
    # If export specified, run export and exit
    if args.export:
        export_data_to_json(args.export)
        return 0
    
    # If stats flag, show stats and exit
    if args.stats:
        show_database_stats()
        return 0
    
    # Interactive mode
    while True:
        show_menu()
        
        try:
            choice = input("Choose an option (0-9): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                show_database_stats()
            elif choice == "2":
                show_categories()
            elif choice == "3":
                show_accounts()
            elif choice == "4":
                limit = input("Number of transactions to show (default 20): ").strip()
                limit = int(limit) if limit.isdigit() else 20
                show_recent_transactions(limit)
            elif choice == "5":
                show_budgets()
            elif choice == "6":
                show_goals()
            elif choice == "7":
                add_sample_transaction()
            elif choice == "8":
                filename = input("Export filename (default: financial_data_export.json): ").strip()
                filename = filename if filename else "financial_data_export.json"
                export_data_to_json(filename)
            elif choice == "9":
                reset_database()
            else:
                print("❌ Invalid option. Please choose 0-9.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            input("\nPress Enter to continue...")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
