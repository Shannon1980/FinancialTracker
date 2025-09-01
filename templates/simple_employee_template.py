#!/usr/bin/env python3
"""
Simple Employee Data Upload Template Generator
Creates Excel template with all required fields for SEAS Financial Tracker
"""

import pandas as pd
from pathlib import Path

def create_employee_template():
    """Create Excel template for employee data uploads"""
    
    # Create templates directory if it doesn't exist
    templates_dir = Path(__file__).parent
    templates_dir.mkdir(exist_ok=True)
    
    # Define the template structure with all required fields
    template_data = {
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
    df = pd.DataFrame(template_data)
    
    # Create Excel file
    template_path = templates_dir / 'employee_upload_template.xlsx'
    
    with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
        # Main data sheet
        df.to_excel(writer, sheet_name='Employee_Data', index=False)
        
        # Instructions sheet
        instructions_data = {
            'Field': ['Name', 'LCAT', 'Priced_Salary', 'Current_Salary', 'Hours_Per_Month', 'Department', 'Start_Date', 'Location', 'Manager', 'Skills'],
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
            ],
            'Required': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'No'],
            'Example': ['John Smith', 'PM', '150000', '160000', '173', 'Management', '2024-01-15', 'Remote', 'Program Director', 'Leadership, Project Management']
        }
        
        instructions_df = pd.DataFrame(instructions_data)
        instructions_df.to_excel(writer, sheet_name='Field_Instructions', index=False)
        
        # Validation sheet
        validation_data = {
            'LCAT_Options': ['PM', 'SA/Eng Lead', 'AI Lead', 'HCD Lead', 'Scrum Master', 'Cloud Data Engineer', 'SRE', 'Full Stack Dev'],
            'Department_Options': ['Management', 'Engineering', 'AI/ML', 'Design', 'Agile', 'Data Engineering', 'DevOps', 'Business'],
            'Location_Options': ['Remote', 'On-site', 'Hybrid', 'Travel']
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
