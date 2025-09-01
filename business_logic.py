"""
Business Logic for SEAS Financial Tracker
"""
from typing import Dict, List, Tuple
import pandas as pd
from models import ProjectParameters

class FinancialCalculator:
    """Handles all financial calculations"""
    
    @staticmethod
    def calculate_hourly_rate(salary: float, hours_per_month: float) -> float:
        """Calculate hourly rate from annual salary"""
        if salary == 0 or hours_per_month == 0:
            return 0.0
        return salary / (hours_per_month * 12)
    
    @staticmethod
    def calculate_indirect_costs(direct_labor: float, params: ProjectParameters) -> Dict[str, float]:
        """Calculate indirect costs based on direct labor"""
        fringe = direct_labor * params.fringe_rate
        overhead = direct_labor * params.overhead_rate
        ga = direct_labor * params.ga_rate
        
        return {
            'Fringe': fringe,
            'Overhead': overhead,
            'G&A': ga,
            'Total_Indirect': fringe + overhead + ga
        }
    
    @staticmethod
    def calculate_completion_percentage(actual_hours: float, eac_hours: float) -> float:
        """Calculate project completion percentage"""
        if eac_hours <= 0:
            return 0.0
        return (actual_hours / eac_hours) * 100
    
    @staticmethod
    def calculate_profit_loss(revenue: float, total_costs: float) -> float:
        """Calculate profit/loss"""
        return revenue - total_costs
    
    @staticmethod
    def calculate_profit_margin(profit_loss: float, revenue: float) -> float:
        """Calculate profit margin percentage"""
        if revenue <= 0:
            return 0.0
        return (profit_loss / revenue) * 100

class DataValidator:
    """Handles data validation"""
    
    @staticmethod
    def validate_employee_data(employee_data: Dict) -> Tuple[bool, List[str]]:
        """Validate employee data"""
        errors = []
        required_fields = ['name', 'lcat', 'current_salary', 'hours_per_month']
        
        for field in required_fields:
            if field not in employee_data or not employee_data[field]:
                errors.append(f"Missing required field: {field}")
        
        if 'current_salary' in employee_data and employee_data['current_salary'] < 0:
            errors.append("Salary cannot be negative")
        
        if 'hours_per_month' in employee_data and employee_data['hours_per_month'] <= 0:
            errors.append("Hours per month must be positive")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_project_params(params: Dict) -> Tuple[bool, List[str]]:
        """Validate project parameters"""
        errors = []
        
        if 'eac_hours' in params and params['eac_hours'] <= 0:
            errors.append("EAC hours must be positive")
        
        if 'total_transaction_price' in params and params['total_transaction_price'] < 0:
            errors.append("Total transaction price cannot be negative")
        
        return len(errors) == 0, errors

class ReportGenerator:
    """Generates various financial reports"""
    
    @staticmethod
    def generate_monthly_revenue_report(employees_df: pd.DataFrame, time_periods: List[str]) -> pd.DataFrame:
        """Generate monthly revenue report"""
        revenue_by_month = {}
        
        for period in time_periods:
            revenue_col = f'Revenue_{period}'
            if revenue_col in employees_df.columns:
                revenue_by_month[period] = employees_df[revenue_col].sum()
        
        return pd.DataFrame(list(revenue_by_month.items()), columns=['Period', 'Revenue'])
    
    @staticmethod
    def generate_lcat_summary(employees_df: pd.DataFrame) -> pd.DataFrame:
        """Generate summary by labor category"""
        revenue_columns = [col for col in employees_df.columns if col.startswith('Revenue_')]
        
        if not revenue_columns:
            return pd.DataFrame()
        
        lcat_revenue = employees_df.groupby('LCAT').agg({
            col: 'sum' for col in revenue_columns
        }).sum(axis=1).reset_index()
        
        lcat_revenue.columns = ['LCAT', 'Total_Revenue']
        return lcat_revenue
    
    @staticmethod
    def generate_burn_rate_analysis(employees_df: pd.DataFrame, time_periods: List[str]) -> Dict:
        """Generate burn rate analysis"""
        cumulative_hours = []
        cumulative_costs = []
        periods = []
        
        running_hours = 0
        running_costs = 0
        
        for period in time_periods:
            hours_col = f'Hours_{period}'
            revenue_col = f'Revenue_{period}'
            
            if hours_col in employees_df.columns:
                period_hours = employees_df[hours_col].sum()
                period_revenue = employees_df[revenue_col].sum()
                
                running_hours += period_hours
                running_costs += period_revenue
                
                periods.append(period)
                cumulative_hours.append(running_hours)
                cumulative_costs.append(running_costs)
        
        return {
            'periods': periods,
            'cumulative_hours': cumulative_hours,
            'cumulative_costs': cumulative_costs
        }
