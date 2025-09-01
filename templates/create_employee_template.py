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
