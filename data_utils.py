"""
Data processing utilities for SEAS Financial Tracker
Handles data validation, processing, and calculations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import streamlit as st


def generate_time_periods() -> List[str]:
    """Generate monthly time periods for Base Year and Option Year 1"""
    periods = []
    
    # Base Year periods (March 2024 - March 2025)
    base_year_periods = [
        "03/13/2024-04/11/2024", "04/12/2024-05/11/2024", "05/12/2024-06/10/2024", "06/11/2024-07/10/2024",
        "07/11/2024-08/09/2024", "08/10/2024-09/08/2024", "09/09/2024-10/08/2024", "10/09/2024-11/07/2024",
        "11/08/2024-12/07/2024", "12/08/2024-01/06/2025", "01/07/2025-02/05/2025", "02/06/2025-03/07/2025"
    ]
    
    # Option Year 1 periods (March 2025 - March 2026)
    option_year_periods = [
        "03/08/2025-04/07/2025", "04/08/2025-05/07/2025", "05/08/2025-06/06/2025", "06/07/2025-07/06/2025",
        "07/07/2025-08/05/2025", "08/06/2025-09/04/2025", "09/05/2025-10/04/2025", "10/05/2025-11/03/2025",
        "11/04/2025-12/03/2025", "12/04/2025-01/02/2026", "01/03/2026-02/01/2026", "02/02/2026-03/03/2026"
    ]
    
    periods.extend(base_year_periods)
    periods.extend(option_year_periods)
    
    return periods


def create_sample_employees() -> pd.DataFrame:
    """Create sample employee data with all required fields"""
    sample_data = [
        {"Name": "Shannon Gueringer", "LCAT": "PM", "Priced_Salary": 160000, "Current_Salary": 200000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Drew Hynes", "LCAT": "PM", "Priced_Salary": 0, "Current_Salary": 0, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Uyen Tran", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 175000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Leo Khan", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 190000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Vitaliy Baklikov", "LCAT": "AI Lead", "Priced_Salary": 200000, "Current_Salary": 250000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Kenny Tran/Lynn Stahl", "LCAT": "HCD Lead", "Priced_Salary": 130000, "Current_Salary": 150000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Emilio Crocco", "LCAT": "Scrum Master", "Priced_Salary": 110000, "Current_Salary": 110000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Robert Melton", "LCAT": "SA/Eng Lead", "Priced_Salary": 230000, "Current_Salary": 225000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Nayeema Nageen", "LCAT": "Scrum Master", "Priced_Salary": 140000, "Current_Salary": 140000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
        {"Name": "Daniil Goryachev", "LCAT": "Cloud Data Engineer", "Priced_Salary": 90000, "Current_Salary": 90000, 
         "Hours_Per_Month": 173, "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active"},
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Add time period columns
    time_periods = generate_time_periods()
    for period in time_periods:
        df[f'Hours_{period}'] = 0.0
        df[f'Revenue_{period}'] = 0.0
    
    # Calculate hourly rates
    df['Hourly_Rate'] = df['Current_Salary'] / (df['Hours_Per_Month'] * 12)
    
    return df


def create_sample_subcontractors() -> pd.DataFrame:
    """Create sample subcontractor data"""
    sample_data = [
        {"Name": "Adrien Adams", "Company": "BEELINE", "LCAT": "Data Systems SME", "Hourly_Rate": 250.0},
        {"Name": "Paulina Fisher", "Company": "FFtC", "LCAT": "HCD Researcher", "Hourly_Rate": 116.0},
        {"Name": "Andrew Sung", "Company": "FFtC", "LCAT": "Full Stack Dev", "Hourly_Rate": 130.0},
    ]
    
    df = pd.DataFrame(sample_data)
    
    # Add time period columns
    time_periods = generate_time_periods()
    for period in time_periods:
        df[f'Hours_{period}'] = 0.0
        df[f'Revenue_{period}'] = 0.0
    
    return df


def create_sample_odc() -> pd.DataFrame:
    """Create sample Other Direct Costs data"""
    # Generate time periods for ODC data
    time_periods = generate_time_periods()
    odc_data = []
    
    for i, period in enumerate(time_periods):
        amount = 472855.83 if i == 6 else 0.0  # Large ODC in 7th month as per spreadsheet
        odc_data.append({"Period": period, "Amount": amount, "Description": "Infrastructure Costs"})
        
    return pd.DataFrame(odc_data)


def create_sample_tasks() -> pd.DataFrame:
    """Create sample tasks data"""
    sample_data = [
        {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "AI Lead (KEY)", 
         "Person_Org": "OPERATIONS", "Person": "Baklikov, Vitaliy", "Hours": 984, "Cost": 118292.52},
        {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Cloud Data Engineers", 
         "Person_Org": "PROGRAM", "Person": "Anton, Jason", "Hours": 734.75, "Cost": 74832.42},
        {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Infrastructure Lead/SRE", 
         "Person_Org": "V-AQUIA", "Person": "Hardison, William", "Hours": 831, "Cost": 136901.52},
    ]
    
    return pd.DataFrame(sample_data)


def validate_employee_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate employee data for required fields and data types"""
    errors = []
    required_fields = ['Name', 'LCAT', 'Current_Salary', 'Hours_Per_Month', 'Employee_Type', 'Company', 'Status']
    
    # Check required fields
    for field in required_fields:
        if field not in df.columns:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Check for empty names
    if df['Name'].isna().any() or (df['Name'] == '').any():
        errors.append("Employee names cannot be empty")
    
    # Check for valid salary values
    if df['Current_Salary'].isna().any() or (df['Current_Salary'] < 0).any():
        errors.append("Current salary must be non-negative numbers")
    
    # Check for valid hours
    if df['Hours_Per_Month'].isna().any() or (df['Hours_Per_Month'] <= 0).any():
        errors.append("Hours per month must be positive numbers")
    
    return len(errors) == 0, errors


def validate_subcontractor_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Validate subcontractor data for required fields and data types"""
    errors = []
    required_fields = ['Name', 'Company', 'LCAT', 'Hourly_Rate']
    
    # Check required fields
    for field in required_fields:
        if field not in df.columns:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        return False, errors
    
    # Check for empty names
    if df['Name'].isna().any() or (df['Name'] == '').any():
        errors.append("Subcontractor names cannot be empty")
    
    # Check for valid hourly rates
    if df['Hourly_Rate'].isna().any() or (df['Hourly_Rate'] <= 0).any():
        errors.append("Hourly rate must be positive numbers")
    
    return len(errors) == 0, errors


def calculate_employee_metrics(employees_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key metrics for employees"""
    if employees_df.empty:
        return {
            'total_employees': 0,
            'total_salary': 0,
            'average_salary': 0,
            'active_employees': 0,
            'inactive_employees': 0
        }
    
    total_employees = len(employees_df)
    total_salary = employees_df['Current_Salary'].sum()
    average_salary = employees_df['Current_Salary'].mean()
    active_employees = len(employees_df[employees_df['Status'] == 'Active'])
    inactive_employees = len(employees_df[employees_df['Status'] == 'Inactive'])
    
    return {
        'total_employees': total_employees,
        'total_salary': total_salary,
        'average_salary': average_salary,
        'active_employees': active_employees,
        'inactive_employees': inactive_employees
    }


def calculate_subcontractor_metrics(subcontractors_df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate key metrics for subcontractors"""
    if subcontractors_df.empty:
        return {
            'total_subcontractors': 0,
            'total_hourly_cost': 0,
            'average_hourly_rate': 0,
            'companies': []
        }
    
    total_subcontractors = len(subcontractors_df)
    total_hourly_cost = (subcontractors_df['Hourly_Rate'] * 173).sum()  # Assuming 173 hours/month
    average_hourly_rate = subcontractors_df['Hourly_Rate'].mean()
    companies = subcontractors_df['Company'].unique().tolist()
    
    return {
        'total_subcontractors': total_subcontractors,
        'total_hourly_cost': total_hourly_cost,
        'average_hourly_rate': average_hourly_rate,
        'companies': companies
    }


def detect_duplicate_employees(new_df: pd.DataFrame, existing_df: pd.DataFrame) -> Tuple[List[str], pd.DataFrame]:
    """Detect duplicate employees by name"""
    if existing_df.empty:
        return [], new_df
    
    # Find duplicates by name
    duplicates = new_df[new_df['Name'].isin(existing_df['Name'])]
    unique_new = new_df[~new_df['Name'].isin(existing_df['Name'])]
    
    return duplicates['Name'].tolist(), unique_new


def merge_employee_data(existing_df: pd.DataFrame, new_df: pd.DataFrame, 
                       merge_strategy: str = "replace") -> pd.DataFrame:
    """Merge new employee data with existing data"""
    if merge_strategy == "replace":
        # Remove existing employees that are being replaced
        existing_df = existing_df[~existing_df['Name'].isin(new_df['Name'])]
        # Concatenate with new data
        return pd.concat([existing_df, new_df], ignore_index=True)
    elif merge_strategy == "skip":
        # Only add non-duplicate employees
        unique_new = new_df[~new_df['Name'].isin(existing_df['Name'])]
        return pd.concat([existing_df, unique_new], ignore_index=True)
    else:
        return existing_df
