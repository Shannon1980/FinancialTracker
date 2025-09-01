#!/usr/bin/env python3
"""
Create Comprehensive Employee Upload Template
Includes all fields for SEAS Financial Tracker
"""

import pandas as pd
from pathlib import Path

def main():
    """Create comprehensive employee upload template"""
    
    print("🚀 Creating Comprehensive Employee Upload Template...")
    
    # Create templates directory
    templates_dir = Path(__file__).parent
    templates_dir.mkdir(exist_ok=True)
    
    # Comprehensive template data
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
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Add monthly hours columns for base year and option year one
    # Base Year: March 2024 - March 2025 (12 periods)
    base_year_periods = [
        '03/13-04/11/24', '04/12-05/11/24', '05/12-06/10/24', '06/11-07/10/24',
        '07/11-08/09/24', '08/10-09/08/24', '09/09-10/08/24', '10/09-11/07/24',
        '11/08-12/07/24', '12/08-01/06/25', '01/07-02/05/25', '02/06-03/07/25'
    ]
    
    # Option Year 1: March 2025 - March 2026 (12 periods)
    option_year_periods = [
        '03/08-04/07/25', '04/08-05/07/25', '05/08-06/06/25', '06/07-07/06/25',
        '07/07-08/05/25', '08/06-09/04/25', '09/05-10/04/25', '10/05-11/03/25',
        '11/04-12/03/25', '12/04-01/02/26', '01/03-02/01/26', '02/02-03/03/26'
    ]
    
    # Add Hours columns for all periods
    for period in base_year_periods + option_year_periods:
        df[f'Hours_{period}'] = 0.0
    
    # Add Revenue columns for all periods
    for period in base_year_periods + option_year_periods:
        df[f'Revenue_{period}'] = 0.0
    
    # Save as Excel with multiple sheets
    excel_path = templates_dir / 'comprehensive_employee_template.xlsx'
    
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
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
        
        # Validation options - pad arrays to same length
        max_length = max(
            len(['PM', 'SA/Eng Lead', 'AI Lead', 'HCD Lead', 'Scrum Master', 'Cloud Data Engineer', 'SRE', 'Full Stack Dev']),
            len(['Management', 'Engineering', 'AI/ML', 'Design', 'Agile', 'Data Engineering', 'DevOps', 'Business']),
            len(['Remote', 'On-site', 'Hybrid', 'Travel'])
        )
        
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
    
    # Save as CSV
    csv_path = templates_dir / 'comprehensive_employee_template.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Comprehensive Excel template: {excel_path}")
    print(f"✅ Comprehensive CSV template: {csv_path}")
    print(f"📊 Template has {len(df)} sample employees")
    print(f"📋 Template has {len(df.columns)} columns")
    
    print("\n📋 All Fields:")
    for col in df.columns:
        print(f"  - {col}")
    
    print("\n💡 How to use:")
    print("1. Open template in Excel/Google Sheets")
    print("2. Replace sample data with your employee data")
    print("3. Keep column headers exactly as shown")
    print("4. Upload to SEAS Financial Tracker")
    
    print("\n⚠️  Important notes:")
    print("- Required fields: Name, LCAT, Priced_Salary, Current_Salary, Hours_Per_Month")
    print("- Dates should be in YYYY-MM-DD format")
    print("- Salary amounts should be numbers (no $ or commas)")
    print("- LCAT should match one of the validation options")

if __name__ == "__main__":
    main()
