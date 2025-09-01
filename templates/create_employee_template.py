#!/usr/bin/env python3
"""
Create Employee Data Upload Template
Simple and reliable template generator
"""

import pandas as pd
from pathlib import Path

def main():
    """Create employee upload template"""
    
    print("🚀 Creating Employee Upload Template...")
    
    # Create templates directory
    templates_dir = Path(__file__).parent
    templates_dir.mkdir(exist_ok=True)
    
    # Simple template data - all arrays same length
    data = {
        'Name': ['John Smith', 'Jane Doe', 'Bob Johnson'],
        'LCAT': ['PM', 'SA/Eng Lead', 'AI Lead'],
        'Priced_Salary': [150000, 180000, 200000],
        'Current_Salary': [160000, 175000, 250000],
        'Hours_Per_Month': [173, 173, 173]
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Save as Excel
    excel_path = templates_dir / 'employee_template.xlsx'
    df.to_excel(excel_path, index=False, sheet_name='Employee_Data')
    
    # Save as CSV
    csv_path = templates_dir / 'employee_template.csv'
    df.to_csv(csv_path, index=False)
    
    print(f"✅ Excel template: {excel_path}")
    print(f"✅ CSV template: {csv_path}")
    print(f"📊 Template has {len(df)} sample employees")
    print(f"📋 Template has {len(df.columns)} columns")
    
    print("\n📋 Required Fields:")
    for col in df.columns:
        print(f"  - {col}")
    
    print("\n💡 How to use:")
    print("1. Open template in Excel/Google Sheets")
    print("2. Replace sample data with your employee data")
    print("3. Keep column headers exactly as shown")
    print("4. Upload to SEAS Financial Tracker")

if __name__ == "__main__":
    main()
