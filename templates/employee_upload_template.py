#!/usr/bin/env python3
"""
Employee Data Upload Template Generator
Creates Excel template with all required fields for SEAS Financial Tracker
"""

import pandas as pd
import os
from pathlib import Path
from datetime import datetime

def create_employee_template():
    """Create Excel template for employee data uploads"""
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent
    templates_dir.mkdir(exist_ok=True)
    
    # Define the template structure with all required fields
    template_data = {
        'Name': [
            'Shannon Gueringer',
            'Drew Hynes', 
            'Uyen Tran',
            'Leo Khan',
            'Vitaliy Baklikov',
            'Kenny Tran/Lynn Stahl',
            'Emilio Crocco',
            'Robert Melton',
            'Nayeema Nageen',
            'Daniil Goryachev'
        ],
        'LCAT': [
            'PM',
            'PM',
            'SA/Eng Lead', 
            'SA/Eng Lead',
            'AI Lead',
            'HCD Lead',
            'Scrum Master',
            'SA/Eng Lead',
            'Scrum Master',
            'Cloud Data Engineer'
        ],
        'Priced_Salary': [
            160000,
            0,
            180000,
            180000,
            200000,
            130000,
            110000,
            230000,
            140000,
            90000
        ],
        'Current_Salary': [
            200000,
            0,
            175000,
            190000,
            250000,
            150000,
            110000,
            225000,
            140000,
            90000
        ],
        'Hours_Per_Month': [
            173,
            173,
            173,
            173,
            173,
            173,
            173,
            173,
            173,
            173
        ],
        'Department': [
            'Management',
            'Management',
            'Engineering',
            'Engineering', 
            'AI/ML',
            'Design',
            'Agile',
            'Engineering',
            'Agile',
            'Data Engineering'
        ],
        'Start_Date': [
            '2024-01-15',
            '2024-02-01',
            '2024-01-20',
            '2024-01-25',
            '2024-01-10',
            '2024-02-15',
            '2024-01-30',
            '2024-01-05',
            '2024-02-10',
            '2024-01-12'
        ],
        'Location': [
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote',
            'Remote'
        ],
        'Manager': [
            'Program Director',
            'Program Director',
            'Technical Lead',
            'Technical Lead',
            'Technical Lead',
            'Design Lead',
            'Agile Lead',
            'Technical Lead',
            'Agile Lead',
            'Data Lead'
        ],
        'Skills': [
            'Project Management, Leadership, Financial Analysis',
            'Project Management, Stakeholder Management',
            'Software Architecture, Engineering Leadership',
            'Software Architecture, System Design',
            'AI/ML, Data Science, Technical Leadership',
            'Human-Centered Design, Research, UX',
            'Agile, Scrum, Team Facilitation',
            'Software Architecture, Technical Leadership',
            'Agile, Scrum, Process Improvement',
            'Data Engineering, Cloud, ETL'
        ]
    }
    
    # Create DataFrame
    df = pd.DataFrame(template_data)
    
    # Calculate hourly rates (this will be done by the app)
    df['Hourly_Rate_Calculated'] = df.apply(
        lambda row: round(row['Current_Salary'] / (row['Hours_Per_Month'] * 12), 2) if row['Current_Salary'] > 0 else 0,
        axis=1
    )
    
    # Add time period columns (these will be populated by the app)
    time_periods = [
        '03/13-04/11/24', '04/12-05/11/24', '05/12-06/10/24', '06/11-07/10/24',
        '07/11-08/09/24', '08/10-09/08/24', '09/09-10/08/24', '10/09-11/07/24',
        '11/08-12/07/24', '12/08-01/06/25', '01/07-02/05/25', '02/06-03/07/25'
    ]
    
    for period in time_periods:
        df[f'Hours_{period}'] = 0.0
        df[f'Revenue_{period}'] = 0.0
    
    # Create Excel file with multiple sheets
    template_path = templates_dir / 'employee_upload_template.xlsx'
    
    with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Employee_Data', index=False)
        
        # Instructions sheet
        instructions_data = {
            'Field': [
                'Name',
                'LCAT',
                'Priced_Salary',
                'Current_Salary', 
                'Hours_Per_Month',
                'Department',
                'Start_Date',
                'Location',
                'Manager',
                'Skills',
                'Hours_[Period]',
                'Revenue_[Period]'
            ],
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
                'Key skills and competencies (comma-separated)',
                'Hours worked in specific time period (populated by app)',
                'Revenue generated in specific time period (populated by app)'
            ],
            'Required': [
                'Yes',
                'Yes',
                'Yes',
                'Yes',
                'Yes',
                'No',
                'No',
                'No',
                'No',
                'No',
                'No (Auto-calculated)',
                'No (Auto-calculated)'
            ],
            'Example': [
                'John Smith',
                'PM',
                '150000',
                '160000',
                '173',
                'Management',
                '2024-01-15',
                'Remote',
                'Program Director',
                'Leadership, Project Management',
                '0.0',
                '0.0'
            ]
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Field_Instructions', index=False)
        
        # Validation sheet
        validation_data = {
            'LCAT_Options': [
                'PM',
                'SA/Eng Lead',
                'AI Lead',
                'HCD Lead',
                'Scrum Master',
                'Cloud Data Engineer',
                'SRE',
                'Full Stack Dev',
                'Data Scientist',
                'UX Designer',
                'DevOps Engineer',
                'Business Analyst'
            ],
            'Department_Options': [
                'Management',
                'Engineering',
                'AI/ML',
                'Design',
                'Agile',
                'Data Engineering',
                'DevOps',
                'Business',
                'Operations',
                'Quality Assurance'
            ],
            'Location_Options': [
                'Remote',
                'On-site',
                'Hybrid',
                'Travel'
            ]
        }
        
        validation_df = pd.DataFrame(validation_data)
        validation_df.to_excel(writer, sheet_name='Validation_Options', index=False)
    
    print(f"✅ Employee template created: {template_path}")
    print(f"📊 Template includes {len(df)} sample employees")
    print(f"📋 Template has {len(df.columns)} columns")
    
    return template_path

def create_csv_template():
    """Create CSV template for easier editing"""
    
    templates_dir = Path(__file__).parent
    
    # Create simplified CSV template
    csv_data = {
        'Name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
        'LCAT': ['PM', 'SA/Eng Lead', 'AI Lead'],
        'Priced_Salary': [150000, 180000, 200000],
        'Current_Salary': [160000, 175000, 250000],
        'Hours_Per_Month': [173, 173, 173],
        'Department': ['Management', 'Engineering', 'AI/ML'],
        'Start_Date': ['2024-01-15', '2024-01-20', '2024-01-10'],
        'Location': ['Remote', 'Remote', 'Remote'],
        'Manager': ['Program Director', 'Technical Lead', 'Technical Lead'],
        'Skills': ['Leadership, Project Management', 'Software Architecture, Engineering', 'AI/ML, Data Science']
    }
    
    df = pd.DataFrame(csv_data)
    csv_path = templates_dir / 'employee_upload_template.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"✅ CSV template created: {csv_path}")
    return csv_path

def main():
    """Main function to create all templates"""
    print("🚀 Creating Employee Data Upload Templates...")
    print("=" * 50)
    
    try:
        # Create Excel template
        excel_path = create_employee_template()
        
        # Create CSV template
        csv_path = create_csv_template()
        
        print("\n🎉 Templates created successfully!")
        print(f"📁 Excel template: {excel_path}")
        print(f"📁 CSV template: {csv_path}")
        
        print("\n📋 How to use:")
        print("1. Open the Excel template in Excel/Google Sheets")
        print("2. Replace sample data with your actual employee data")
        print("3. Save and upload to the SEAS Financial Tracker")
        print("4. The app will automatically calculate hourly rates and add time periods")
        
        print("\n⚠️  Important notes:")
        print("- Keep the column headers exactly as shown")
        print("- Required fields: Name, LCAT, Priced_Salary, Current_Salary, Hours_Per_Month")
        print("- Dates should be in YYYY-MM-DD format")
        print("- Salary amounts should be numbers (no $ or commas)")
        
    except Exception as e:
        print(f"❌ Error creating templates: {e}")

if __name__ == "__main__":
    main()
