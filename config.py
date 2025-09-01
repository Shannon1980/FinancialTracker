"""
Configuration for SEAS Financial Tracker
"""
from typing import Dict, Any

# Application Configuration
APP_CONFIG = {
    'title': 'SEAS Project Financial Tracker',
    'subtitle': 'Professional Financial Management & Analysis Platform',
    'icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded'
}

# Color Scheme (QuickBooks-inspired)
COLORS = {
    'primary': '#2E5BBA',
    'secondary': '#1E3A8A',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'info': '#3498db',
    'light': '#f8f9fa',
    'dark': '#495057',
    'border': '#e9ecef',
    'text': '#6c757d'
}

# CSS Classes
CSS_CLASSES = {
    'main_header': 'main-header',
    'subheader': 'subheader',
    'metric_card': 'metric-card',
    'financial_card': 'financial-card',
    'upload_section': 'upload-section'
}

# Default Project Parameters
DEFAULT_PROJECT_PARAMS = {
    'current_date': '2025-09-01',
    'eac_hours': 37626.75,
    'actual_hours': 26656.5,
    'non_billable_hours': -357.75,
    'total_transaction_price': 8079029.79,
    'fringe_rate': 0.326,
    'overhead_rate': 0.150,
    'ga_rate': 0.275,
    'target_profit': 0.3947
}

# Sample Data
SAMPLE_EMPLOYEES = [
    {"Name": "Shannon Gueringer", "LCAT": "PM", "Priced_Salary": 160000, "Current_Salary": 200000, "Hours_Per_Month": 173},
    {"Name": "Drew Hynes", "LCAT": "PM", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
    {"Name": "Uyen Tran", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 175000, "Hours_Per_Month": 173},
    {"Name": "Leo Khan", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 190000, "Hours_Per_Month": 173},
    {"Name": "Vitaliy Baklikov", "LCAT": "AI Lead", "Priced_Salary": 200000, "Current_Salary": 250000, "Hours_Per_Month": 173},
    {"Name": "Kenny Tran/Lynn Stahl", "LCAT": "HCD Lead", "Priced_Salary": 130000, "Current_Salary": 150000, "Hours_Per_Month": 173},
    {"Name": "Emilio Crocco", "LCAT": "Scrum Master", "Priced_Salary": 110000, "Current_Salary": 110000, "Hours_Per_Month": 173},
    {"Name": "Robert Melton", "LCAT": "SA/Eng Lead", "Priced_Salary": 230000, "Current_Salary": 225000, "Hours_Per_Month": 173},
    {"Name": "Nayeema Nageen", "LCAT": "Scrum Master", "Priced_Salary": 140000, "Current_Salary": 140000, "Hours_Per_Month": 173},
    {"Name": "Daniil Goryachev", "LCAT": "Cloud Data Engineer", "Priced_Salary": 90000, "Current_Salary": 90000, "Hours_Per_Month": 173},
]

SAMPLE_SUBCONTRACTORS = [
    {"Name": "Adrien Adams", "Company": "BEELINE", "LCAT": "Data Systems SME", "Hourly_Rate": 250.0},
    {"Name": "Paulina Fisher", "Company": "FFtC", "LCAT": "HCD Researcher", "Hourly_Rate": 116.0},
    {"Name": "Andrew Sung", "Company": "FFtC", "LCAT": "Full Stack Dev", "Hourly_Rate": 130.0},
]

SAMPLE_ODC_COSTS = [
    {"Name": "Office Space", "Category": "Facilities", "Monthly_Cost": 5000.0, "Description": "Office rent and utilities"},
    {"Name": "Software Licenses", "Category": "Technology", "Monthly_Cost": 2500.0, "Description": "Development tools and software"},
    {"Name": "Internet & Phone", "Category": "Technology", "Monthly_Cost": 800.0, "Description": "High-speed internet and phone services"},
    {"Name": "Insurance", "Category": "Business", "Monthly_Cost": 1200.0, "Description": "Business liability and property insurance"},
    {"Name": "Marketing", "Category": "Business", "Monthly_Cost": 1500.0, "Description": "Marketing materials and advertising"},
]

SAMPLE_TASKS = [
    {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "AI Lead (KEY)", 
     "Person_Org": "OPERATIONS", "Person": "Baklikov, Vitaliy", "Hours": 984, "Cost": 118292.52},
    {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Cloud Data Engineers", 
     "Person_Org": "PROGRAM", "Person": "Anton, Jason", "Hours": 734.75, "Cost": 74832.42},
    {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Infrastructure Lead/SRE", 
     "Person_Org": "V-AQUIA", "Person": "Hardison, William", "Hours": 831, "Cost": 136901.52},
]

# LCAT Options
LCAT_OPTIONS = [
    "PM", "SA/Eng Lead", "AI Lead", "HCD Lead", 
    "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"
]

# Chart Configuration
CHART_CONFIG = {
    'default_colors': ['#2E5BBA', '#1E3A8A', '#3498db', '#e74c3c', '#9b59b6'],
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font_size': 12,
    'margin': {'t': 50, 'l': 50, 'r': 50, 'b': 50}
}

# File Upload Configuration
FILE_UPLOAD_CONFIG = {
    'allowed_types': ['xlsx', 'csv', 'json'],
    'max_size': 200 * 1024 * 1024,  # 200MB
}

# Chart Configuration
CHART_CONFIG = {
    'default_colors': ['#2E5BBA', '#1E3A8A', '#3498db', '#e74c3c', '#9b59b6'],
    'plot_bgcolor': 'rgba(0,0,0,0)',
    'paper_bgcolor': 'rgba(0,0,0,0)',
    'font_size': 12,
    'margin': {'t': 50, 'l': 50, 'r': 50, 'b': 50}
}

# Validation Rules
VALIDATION_RULES = {
    'salary_min': 0,
    'hours_min': 0,
    'rate_min': 0,
    'percentage_min': 0,
    'percentage_max': 100
}

# Export Configuration
EXPORT_CONFIG = {
    'excel_engine': 'openpyxl',
    'csv_encoding': 'utf-8',
    'json_indent': 2
}
