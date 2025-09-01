"""
Template Download Utility for SEAS Financial Tracker
Provides functions to generate and serve templates for download
"""

import pandas as pd
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Tuple

def generate_employee_template(template_type: str = "comprehensive") -> Tuple[bytes, str, str]:
    """
    Generate employee template for download
    
    Args:
        template_type: "basic" or "comprehensive"
    
    Returns:
        Tuple of (file_bytes, filename, mime_type)
    """
    
    if template_type == "basic":
        return _generate_basic_template()
    else:
        return _generate_comprehensive_template()

def _generate_basic_template() -> Tuple[bytes, str, str]:
    """Generate basic employee template"""
    
    # Core employee data
    data = {
        'Name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
        'LCAT': ['PM', 'SA/Eng Lead', 'AI Lead'],
        'Priced_Salary': [150000, 180000, 200000],
        'Current_Salary': [160000, 175000, 250000],
        'Hours_Per_Month': [173, 173, 173]
    }
    
    df = pd.DataFrame(data)
    
    # Add monthly hours columns for base year and option year one
    base_year_periods = [
        '03/13-04/11/24', '04/12-05/11/24', '05/12-06/10/24', '06/11-07/10/24',
        '07/11-08/09/24', '08/10-09/08/24', '09/09-10/08/24', '10/09-11/07/24',
        '11/08-12/07/24', '12/08-01/06/25', '01/07-02/05/25', '02/06-03/07/25'
    ]
    
    option_year_periods = [
        '03/08-04/07/25', '04/08-05/07/25', '05/08-06/06/25', '06/07-07/06/25',
        '07/07-08/05/25', '08/06-09/04/25', '09/05-10/04/25', '10/05-11/03/25',
        '11/04-12/03/25', '12/04-01/02/26', '01/03-02/01/26', '02/02-03/03/26'
    ]
    
    # Add Hours and Revenue columns for all periods
    for period in base_year_periods + option_year_periods:
        df[f'Hours_{period}'] = 0.0
        df[f'Revenue_{period}'] = 0.0
    
    # Generate Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Employee_Data', index=False)
        
        # Add instructions sheet
        instructions = {
            'Field': ['Name', 'LCAT', 'Priced_Salary', 'Current_Salary', 'Hours_Per_Month'],
            'Required': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
            'Description': [
                'Full name of the employee',
                'Labor Category (PM, SA/Eng Lead, AI Lead, etc.)',
                'Original budgeted salary for the project',
                'Current actual salary being paid',
                'Standard hours worked per month (typically 173)'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
    
    output.seek(0)
    file_bytes = output.getvalue()
    filename = f"employee_template_basic_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return file_bytes, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def _generate_comprehensive_template() -> Tuple[bytes, str, str]:
    """Generate comprehensive employee template"""
    
    # Comprehensive employee data
    data = {
        'Name': ['Shannon Gueringer', 'Drew Hynes', 'Uyen Tran', 'Leo Khan', 'Vitaliy Baklikov'],
        'LCAT': ['PM', 'PM', 'SA/Eng Lead', 'SA/Eng Lead', 'AI Lead'],
        'Priced_Salary': [160000, 0, 180000, 180000, 200000],
        'Current_Salary': [200000, 0, 175000, 190000, 250000],
        'Hours_Per_Month': [173, 173, 173, 173, 173],
        'Department': ['Management', 'Management', 'Engineering', 'Engineering', 'AI/ML'],
        'Start_Date': ['2024-01-15', '2024-02-01', '2024-01-20', '2024-01-25', '2024-01-10'],
        'Location': ['Remote', 'Remote', 'Remote', 'Remote', 'Remote'],
        'Manager': ['Program Director', 'Program Director', 'Technical Lead', 'Technical Lead', 'Technical Lead'],
        'Skills': ['Project Management, Leadership', 'Project Management', 'Software Architecture', 'Software Architecture', 'AI/ML, Data Science']
    }
    
    df = pd.DataFrame(data)
    
    # Add monthly hours columns for base year and option year one
    base_year_periods = [
        '03/13-04/11/24', '04/12-05/11/24', '05/12-06/10/24', '06/11-07/10/24',
        '07/11-08/09/24', '08/10-09/08/24', '09/09-10/08/24', '10/09-11/07/24',
        '11/08-12/07/24', '12/08-01/06/25', '01/07-02/05/25', '02/06-03/07/25'
    ]
    
    option_year_periods = [
        '03/08-04/07/25', '04/08-05/07/25', '05/08-06/06/25', '06/07-07/06/25',
        '07/07-08/05/25', '08/06-09/04/25', '09/05-10/04/25', '10/05-11/03/25',
        '11/04-12/03/25', '12/04-01/02/26', '01/03-02/01/26', '02/02-03/03/26'
    ]
    
    # Add Hours and Revenue columns for all periods
    for period in base_year_periods + option_year_periods:
        df[f'Hours_{period}'] = 0.0
        df[f'Revenue_{period}'] = 0.0
    
    # Generate Excel file with multiple sheets
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Employee_Data', index=False)
        
        # Instructions sheet
        instructions = {
            'Field': ['Name', 'LCAT', 'Priced_Salary', 'Current_Salary', 'Hours_Per_Month', 'Department', 'Start_Date', 'Location', 'Manager', 'Skills'],
            'Required': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'No'],
            'Description': [
                'Full name of the employee',
                'Labor Category (PM, SA/Eng Lead, AI Lead, etc.)',
                'Original budgeted salary for the project',
                'Current actual salary being paid',
                'Standard hours worked per month (typically 173)',
                'Department or team assignment',
                'Employee start date (YYYY-MM-DD format)',
                'Work location (Remote, On-site, Hybrid)',
                'Direct manager or supervisor',
                'Key skills and competencies (comma-separated)'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions)
        instructions_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        # Validation options sheet
        max_length = max(8, 8, 4)  # Max length of the arrays
        
        lcat_options = ['PM', 'SA/Eng Lead', 'AI Lead', 'HCD Lead', 'Scrum Master', 'Cloud Data Engineer', 'SRE', 'Full Stack Dev'] + [''] * (max_length - 8)
        dept_options = ['Management', 'Engineering', 'AI/ML', 'Design', 'Agile', 'Data Engineering', 'DevOps', 'Business'] + [''] * (max_length - 8)
        loc_options = ['Remote', 'On-site', 'Hybrid', 'Travel'] + [''] * (max_length - 4)
        
        validation = {
            'LCAT_Options': lcat_options,
            'Department_Options': dept_options,
            'Location_Options': loc_options
        }
        
        validation_df = pd.DataFrame(validation)
        validation_df.to_excel(writer, sheet_name='Validation_Options', index=False)
    
    output.seek(0)
    file_bytes = output.getvalue()
    filename = f"employee_template_comprehensive_{datetime.now().strftime('%Y%m%d')}.xlsx"
    
    return file_bytes, filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def get_template_info() -> Dict[str, Any]:
    """Get information about available templates"""
    
    return {
        "basic": {
            "name": "Basic Employee Template",
            "description": "5 required fields + monthly hours/revenue columns",
            "fields": 53,
            "recommended_for": "Quick employee data entry"
        },
        "comprehensive": {
            "name": "Comprehensive Employee Template", 
            "description": "10 fields + monthly hours/revenue columns + instructions",
            "fields": 58,
            "recommended_for": "Detailed employee management"
        }
    }
