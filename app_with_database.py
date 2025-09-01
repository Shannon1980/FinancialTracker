"""
SEAS Financial Tracker with Database Integration
Persistent data storage using SQLite database
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from typing import Dict, List, Optional

# Import database components
from database import (
    init_database, SimpleDatabaseOperations, get_db,
    Category, Transaction, Account, Budget, Goal
)

# Import existing modules
from models import DataManager, ProjectParameters
from business_logic import FinancialCalculator, DataValidator, ReportGenerator
from ui_components import (
    MetricCard, FinancialCard, RemovalInterface, DataTable, 
    ChartContainer, FormSection, SuccessMessage, ErrorMessage, 
    WarningMessage, InfoMessage
)
from config import APP_CONFIG, COLORS, CSS_CLASSES, DEFAULT_PROJECT_PARAMS, LCAT_OPTIONS, CHART_CONFIG

class SEASFinancialTrackerWithDatabase:
    """SEAS Financial Tracker with database integration"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.financial_calculator = FinancialCalculator()
        self.data_validator = DataValidator()
        self.report_generator = ReportGenerator()
        self.db_ops = None
        self.initialize_database()
        self.initialize_session_state()
    
    def initialize_database(self):
        """Initialize database connection and ensure tables exist"""
        try:
            # Initialize database if it doesn't exist
            init_database()
            
            # Get database operations instance
            db = next(get_db())
            self.db_ops = SimpleDatabaseOperations(db)
            db.close()
            
            st.success("✅ Database connected successfully!")
            
        except Exception as e:
            st.error(f"❌ Database connection failed: {e}")
            st.info("Falling back to in-memory data storage")
            self.db_ops = None
    
    def initialize_session_state(self):
        """Initialize session state with database data when available"""
        if 'time_periods' not in st.session_state:
            st.session_state.time_periods = self.generate_time_periods()
        
        if 'project_params' not in st.session_state:
            st.session_state.project_params = DEFAULT_PROJECT_PARAMS.copy()
        
        # Initialize database-backed data
        if self.db_ops:
            self.initialize_database_data()
        else:
            self.initialize_sample_data()
    
    def initialize_database_data(self):
        """Initialize session state with data from database"""
        try:
            # Get categories
            if 'categories' not in st.session_state:
                categories = self.db_ops.get_categories()
                st.session_state.categories = [cat.name for cat in categories]
            
            # Get accounts
            if 'accounts' not in st.session_state:
                accounts = self.db_ops.get_accounts()
                st.session_state.accounts = [acc.name for acc in accounts]
            
            # Get recent transactions
            if 'recent_transactions' not in st.session_state:
                transactions = self.db_ops.get_transactions(limit=50)
                st.session_state.recent_transactions = transactions
            
            # Get budgets
            if 'budgets' not in st.session_state:
                budgets = self.db_ops.get_budgets()
                st.session_state.budgets = budgets
            
            # Get goals
            if 'goals' not in st.session_state:
                goals = self.db_ops.get_goals()
                st.session_state.goals = goals
                
        except Exception as e:
            st.warning(f"Could not load database data: {e}")
            self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize with sample data when database is not available"""
        if 'employees' not in st.session_state:
            st.session_state.employees = self.create_sample_employees()
        
        if 'subcontractors' not in st.session_state:
            st.session_state.subcontractors = self.create_sample_subcontractors()
        
        if 'odc_costs' not in st.session_state:
            st.session_state.odc_costs = self.create_sample_odc()
        
        if 'tasks' not in st.session_state:
            st.session_state.tasks = self.create_sample_tasks()
    
    def generate_time_periods(self) -> list:
        """Generate time periods for the project"""
        periods = []
        start_date = datetime(2024, 3, 13)
        
        # Base Year: March 2024 - March 2025
        for i in range(12):
            period_start = start_date + timedelta(days=30*i)
            period_end = period_start + timedelta(days=29)
            periods.append(f"{period_start.strftime('%m/%d')}-{period_end.strftime('%m/%d/%y')}")
        
        # Option Year 1: March 2025 - March 2026
        for i in range(12):
            period_start = start_date + timedelta(days=30*(i+12))
            period_end = period_start + timedelta(days=29)
            periods.append(f"{period_start.strftime('%m/%d')}-{period_end.strftime('%m/%d/%y')}")
        
        return periods
    
    def create_sample_employees(self) -> pd.DataFrame:
        """Create sample employee data"""
        from config import SAMPLE_EMPLOYEES
        
        df = pd.DataFrame(SAMPLE_EMPLOYEES)
        
        # Calculate hourly rates
        df['Hourly_Rate'] = df.apply(
            lambda row: self.financial_calculator.calculate_hourly_rate(
                row['Current_Salary'], row['Hours_Per_Month']
            ), axis=1
        )
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
        
        return df
    
    def create_sample_subcontractors(self) -> pd.DataFrame:
        """Create sample subcontractor data"""
        from config import SAMPLE_SUBCONTRACTORS
        
        df = pd.DataFrame(SAMPLE_SUBCONTRACTORS)
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
        
        return df
    
    def create_sample_odc(self) -> pd.DataFrame:
        """Create sample ODC costs data"""
        from config import SAMPLE_ODC_COSTS
        
        df = pd.DataFrame(SAMPLE_ODC_COSTS)
        
        # Add monthly cost columns
        for period in st.session_state.time_periods:
            df[f'Cost_{period}'] = 0.0
        
        return df
    
    def create_sample_tasks(self) -> pd.DataFrame:
        """Create sample tasks data"""
        from config import SAMPLE_TASKS
        
        df = pd.DataFrame(SAMPLE_TASKS)
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
        
        return df
    
    def render_database_dashboard(self):
        """Render database-driven financial dashboard"""
        st.header("🗄️ Database Financial Dashboard")
        
        if not self.db_ops:
            st.warning("Database not available. Using sample data.")
            return
        
        try:
            # Get database statistics
            stats = self.db_ops.get_database_stats()
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Transactions", stats.get('total_transactions', 0))
            
            with col2:
                st.metric("Total Categories", stats.get('total_categories', 0))
            
            with col3:
                st.metric("Total Accounts", stats.get('total_accounts', 0))
            
            with col4:
                st.metric("Total Goals", stats.get('total_goals', 0))
            
            # Financial Summary
            st.subheader("📊 Financial Summary")
            
            # Date range selector
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
            with col2:
                end_date = st.date_input("End Date", value=date.today())
            
            if start_date and end_date:
                summary = self.db_ops.get_financial_summary(start_date, end_date)
                
                # Display summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Income", f"${summary['income']:,.2f}")
                with col2:
                    st.metric("Expenses", f"${summary['expenses']:,.2f}")
                with col3:
                    st.metric("Net Income", f"${summary['net_income']:,.2f}")
                
                # Create income vs expenses chart
                fig = go.Figure(data=[
                    go.Bar(name='Income', x=['Income'], y=[summary['income']], marker_color='green'),
                    go.Bar(name='Expenses', x=['Expenses'], y=[summary['expenses']], marker_color='red')
                ])
                fig.update_layout(title="Income vs Expenses", barmode='group')
                st.plotly_chart(fig, use_container_width=True)
            
            # Recent Transactions
            st.subheader("💳 Recent Transactions")
            transactions = self.db_ops.get_transactions(limit=20)
            
            if transactions:
                # Convert to DataFrame for display
                trans_data = []
                for trans in transactions:
                    trans_data.append({
                        'Date': trans.date,
                        'Description': trans.description,
                        'Amount': trans.amount,
                        'Type': trans.transaction_type,
                        'Category': trans.category.name if trans.category else 'N/A',
                        'Account': trans.account.name if trans.account else 'N/A'
                    })
                
                df = pd.DataFrame(trans_data)
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No transactions found.")
                
        except Exception as e:
            st.error(f"Error loading database dashboard: {e}")
    
    def render_transaction_form(self):
        """Render form for adding new transactions"""
        st.subheader("➕ Add New Transaction")
        
        if not self.db_ops:
            st.warning("Database not available.")
            return
        
        with st.form("transaction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                transaction_date = st.date_input("Date", value=date.today())
                description = st.text_input("Description")
                amount = st.number_input("Amount", min_value=0.01, step=0.01)
                transaction_type = st.selectbox("Type", ["expense", "income", "transfer"])
            
            with col2:
                # Get categories and accounts for selection
                categories = self.db_ops.get_categories()
                accounts = self.db_ops.get_accounts()
                
                category_names = [cat.name for cat in categories]
                account_names = [acc.name for acc in accounts]
                
                category_name = st.selectbox("Category", category_names)
                account_name = st.selectbox("Account", account_names)
                notes = st.text_area("Notes")
            
            submitted = st.form_submit_button("Add Transaction")
            
            if submitted:
                try:
                    # Find category and account IDs
                    category = next(cat for cat in categories if cat.name == category_name)
                    account = next(acc for acc in accounts if acc.name == account_name)
                    
                    # Create transaction
                    transaction_data = {
                        "date": transaction_date,
                        "description": description,
                        "amount": amount,
                        "transaction_type": transaction_type,
                        "category_id": category.id,
                        "account_id": account.id,
                        "notes": notes
                    }
                    
                    # Add to database
                    db = next(get_db())
                    db_ops = SimpleDatabaseOperations(db)
                    new_transaction = db_ops.create_transaction(transaction_data)
                    db.close()
                    
                    st.success(f"✅ Transaction added: {description} - ${amount:,.2f}")
                    
                    # Refresh session state
                    if 'recent_transactions' in st.session_state:
                        del st.session_state.recent_transactions
                    
                except Exception as e:
                    st.error(f"❌ Error adding transaction: {e}")
    
    def render_categories_management(self):
        """Render categories management interface"""
        st.subheader("🏷️ Categories Management")
        
        if not self.db_ops:
            st.warning("Database not available.")
            return
        
        try:
            categories = self.db_ops.get_categories()
            
            # Display existing categories
            st.write("**Existing Categories:**")
            for category in categories:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                with col1:
                    st.write(f"{category.icon} {category.name}")
                with col2:
                    st.write(category.description or "No description")
                with col3:
                    st.write(f"Type: {'Expense' if category.is_expense else 'Income'}")
                with col4:
                    if st.button("Edit", key=f"edit_{category.id}"):
                        st.session_state.editing_category = category.id
            
            # Add new category form
            st.write("**Add New Category:**")
            with st.form("category_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Category Name")
                    description = st.text_area("Description")
                    color = st.color_picker("Color", value="#1f77b4")
                
                with col2:
                    icon = st.text_input("Icon (emoji)", value="💰")
                    is_expense = st.checkbox("Is Expense Category", value=True)
                    is_income = st.checkbox("Is Income Category", value=False)
                
                submitted = st.form_submit_button("Add Category")
                
                if submitted and name:
                    try:
                        category_data = {
                            "name": name,
                            "description": description,
                            "color": color,
                            "icon": icon,
                            "is_expense": is_expense,
                            "is_income": is_income
                        }
                        
                        db = next(get_db())
                        db_ops = SimpleDatabaseOperations(db)
                        new_category = db_ops.create_category(category_data)
                        db.close()
                        
                        st.success(f"✅ Category added: {name}")
                        
                        # Refresh categories
                        if 'categories' in st.session_state:
                            del st.session_state.categories
                        
                    except Exception as e:
                        st.error(f"❌ Error adding category: {e}")
                        
        except Exception as e:
            st.error(f"Error loading categories: {e}")
    
    def render_main_app(self):
        """Render the main SEAS Financial Tracker application"""
        st.title("🚀 SEAS Financial Tracker")
        st.markdown("**Professional Financial Management with Database Integration**")
        
        # Navigation tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Database Dashboard", 
            "➕ Add Transaction", 
            "🏷️ Categories", 
            "📈 Financial Analysis",
            "⚙️ Settings"
        ])
        
        with tab1:
            self.render_database_dashboard()
        
        with tab2:
            self.render_transaction_form()
        
        with tab3:
            self.render_categories_management()
        
        with tab4:
            st.subheader("📈 Financial Analysis")
            st.info("Advanced financial analysis features coming soon!")
            
            # Placeholder for future features
            if self.db_ops:
                try:
                    # Show account balances
                    st.write("**Account Balances:**")
                    accounts = self.db_ops.get_accounts()
                    
                    for account in accounts:
                        st.write(f"🏦 {account.name}: ${account.balance:,.2f} ({account.currency})")
                        
                except Exception as e:
                    st.error(f"Error loading account data: {e}")
        
        with tab5:
            st.subheader("⚙️ Settings")
            st.write("**Database Status:**")
            
            if self.db_ops:
                st.success("✅ Database connected and operational")
                
                # Database statistics
                try:
                    stats = self.db_ops.get_database_stats()
                    st.write(f"**Total Records:** {stats.get('total_transactions', 0)} transactions")
                    st.write(f"**Data Range:** {stats.get('date_range', {}).get('earliest', 'N/A')} to {stats.get('date_range', {}).get('latest', 'N/A')}")
                except Exception as e:
                    st.error(f"Error getting database stats: {e}")
            else:
                st.error("❌ Database not available")
    
    def run(self):
        """Run the application"""
        try:
            self.render_main_app()
        except Exception as e:
            st.error(f"Application error: {e}")
            st.exception(e)

def main():
    """Main application entry point"""
    st.set_page_config(
        page_title="SEAS Financial Tracker",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize and run app
    app = SEASFinancialTrackerWithDatabase()
    app.run()

if __name__ == "__main__":
    main()
