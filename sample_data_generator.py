"""
Sample Data Generator for SEAS Financial Tracker
Generates realistic sample data for employees and subcontractors
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any


class SampleDataGenerator:
    """Generates realistic sample data for testing and demonstration"""
    
    def __init__(self):
        self.names = [
            "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown",
            "Frank Miller", "Grace Lee", "Henry Taylor", "Ivy Chen", "Jack Anderson",
            "Kate Martinez", "Liam Thompson", "Maya Rodriguez", "Noah Garcia", "Olivia White",
            "Paul Harris", "Quinn Clark", "Rachel Lewis", "Sam Walker", "Tina Hall"
        ]
        
        self.managers = [
            "Shannon Gueringer", "Uyen Tran", "Mike Wilson", "Sarah Johnson", "John Smith"
        ]
        
        self.skills_sets = [
            "Python, React, AWS, Docker",
            "SQL, Python, Spark, Azure",
            "JavaScript, Node.js, MongoDB, Git",
            "Java, Spring Boot, PostgreSQL, Kubernetes",
            "C#, .NET, SQL Server, Azure DevOps",
            "Python, Django, PostgreSQL, Docker",
            "React, TypeScript, Node.js, AWS",
            "Python, Machine Learning, TensorFlow, Jupyter",
            "Angular, TypeScript, C#, SQL Server",
            "Vue.js, Node.js, MongoDB, Docker"
        ]
        
        self.departments = [
            "Engineering", "Data Engineering", "DevOps", "Product Management",
            "Design", "Quality Assurance", "Business Analysis", "Management"
        ]
        
        self.locations = ["Remote", "On-site", "Hybrid"]
        
        self.lcats = [
            "Project Manager", "Senior Engineer", "Full Stack Developer",
            "Data Engineer", "Cloud Engineer", "DevOps Engineer",
            "Business Analyst", "UX/UI Designer", "QA Engineer",
            "Technical Lead", "Solution Architect", "Consultant"
        ]
    
    def generate_team_members(self, count: int = 10) -> List[Dict[str, Any]]:
        """Generate sample team member data"""
        team_members = []
        
        for i in range(count):
            name = random.choice(self.names)
            self.names.remove(name)  # Avoid duplicates
            
            # Salary ranges based on LCAT
            lcat = random.choice(self.lcats)
            if "Manager" in lcat or "Lead" in lcat or "Architect" in lcat:
                base_salary = random.randint(120000, 180000)
            elif "Senior" in lcat:
                base_salary = random.randint(100000, 140000)
            else:
                base_salary = random.randint(70000, 120000)
            
            # Add some variation
            current_salary = base_salary + random.randint(-5000, 10000)
            priced_salary = base_salary + random.randint(-2000, 5000)
            
            # Start date within last 2 years
            start_date = datetime.now() - timedelta(days=random.randint(30, 730))
            
            team_member = {
                "Name": name,
                "Type": "Team",
                "LCAT": lcat,
                "Priced_Salary": priced_salary,
                "Current_Salary": current_salary,
                "Hours_Per_Month": 173,  # Full-time
                "Department": random.choice(self.departments),
                "Start_Date": start_date.strftime("%Y-%m-%d"),
                "Location": random.choice(self.locations),
                "Manager": random.choice(self.managers),
                "Skills": random.choice(self.skills_sets),
                "Contract_End_Date": ""  # Empty for team members
            }
            
            team_members.append(team_member)
        
        return team_members
    
    def generate_subcontractors(self, count: int = 5) -> List[Dict[str, Any]]:
        """Generate sample subcontractor data"""
        subcontractors = []
        
        for i in range(count):
            name = random.choice(self.names)
            self.names.remove(name)  # Avoid duplicates
            
            # Subcontractors typically have higher hourly rates but fewer hours
            lcat = random.choice(self.lcats)
            if "Manager" in lcat or "Lead" in lcat or "Architect" in lcat:
                base_salary = random.randint(140000, 200000)
                hours_per_month = random.randint(120, 160)
            elif "Senior" in lcat:
                base_salary = random.randint(120000, 160000)
                hours_per_month = random.randint(100, 140)
            else:
                base_salary = random.randint(80000, 130000)
                hours_per_month = random.randint(80, 120)
            
            # Add some variation
            current_salary = base_salary + random.randint(-5000, 10000)
            priced_salary = base_salary + random.randint(-2000, 5000)
            
            # Start date within last year
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            
            # Contract end date (6-18 months from start)
            contract_duration = random.randint(180, 540)  # days
            end_date = start_date + timedelta(days=contract_duration)
            
            subcontractor = {
                "Name": name,
                "Type": "Subcontractor",
                "LCAT": lcat,
                "Priced_Salary": priced_salary,
                "Current_Salary": current_salary,
                "Hours_Per_Month": hours_per_month,
                "Department": random.choice(self.departments),
                "Start_Date": start_date.strftime("%Y-%m-%d"),
                "Location": random.choice(self.locations),
                "Manager": random.choice(self.managers),
                "Skills": random.choice(self.skills_sets),
                "Contract_End_Date": end_date.strftime("%Y-%m-%d")
            }
            
            subcontractors.append(subcontractor)
        
        return subcontractors
    
    def generate_monthly_data(self, employees: List[Dict[str, Any]], months: int = 12) -> pd.DataFrame:
        """Generate monthly hours and revenue data for employees"""
        df = pd.DataFrame(employees)
        
        # Generate monthly columns
        current_date = datetime.now()
        for i in range(months):
            month_start = current_date + timedelta(days=30*i)
            month_end = month_start + timedelta(days=29)
            date_range = f"{month_start.strftime('%m/%d')}-{month_end.strftime('%m/%d/%y')}"
            
            hours_col = f"Hours_{date_range}"
            revenue_col = f"Revenue_{date_range}"
            
            # Generate hours (with some variation)
            hours_data = []
            revenue_data = []
            
            for _, row in df.iterrows():
                base_hours = row['Hours_Per_Month']
                # Add some variation (±10%)
                variation = random.uniform(0.9, 1.1)
                hours = int(base_hours * variation)
                hours_data.append(hours)
                
                # Calculate revenue
                hourly_rate = row['Current_Salary'] / (row['Hours_Per_Month'] * 12)
                markup = 1.2 if row['Type'] == 'Subcontractor' else 1.0
                revenue = hours * hourly_rate * markup
                revenue_data.append(round(revenue, 2))
            
            df[hours_col] = hours_data
            df[revenue_col] = revenue_data
        
        return df
    
    def generate_complete_dataset(self, team_count: int = 10, subcontractor_count: int = 5) -> pd.DataFrame:
        """Generate complete dataset with team members and subcontractors"""
        # Reset names list
        self.names = [
            "Alice Johnson", "Bob Smith", "Carol Davis", "David Wilson", "Emma Brown",
            "Frank Miller", "Grace Lee", "Henry Taylor", "Ivy Chen", "Jack Anderson",
            "Kate Martinez", "Liam Thompson", "Maya Rodriguez", "Noah Garcia", "Olivia White",
            "Paul Harris", "Quinn Clark", "Rachel Lewis", "Sam Walker", "Tina Hall"
        ]
        
        # Generate team members and subcontractors
        team_members = self.generate_team_members(team_count)
        subcontractors = self.generate_subcontractors(subcontractor_count)
        
        # Combine all employees
        all_employees = team_members + subcontractors
        
        # Generate monthly data
        df = self.generate_monthly_data(all_employees)
        
        return df


def create_sample_data():
    """Create and return sample data for the application"""
    generator = SampleDataGenerator()
    return generator.generate_complete_dataset()


if __name__ == "__main__":
    # Generate sample data for testing
    generator = SampleDataGenerator()
    df = generator.generate_complete_dataset()
    
    print("Generated sample data:")
    print(f"Total employees: {len(df)}")
    print(f"Team members: {len(df[df['Type'] == 'Team'])}")
    print(f"Subcontractors: {len(df[df['Type'] == 'Subcontractor'])}")
    
    # Save to Excel
    df.to_excel("sample_employee_data.xlsx", index=False)
    print("Sample data saved to 'sample_employee_data.xlsx'")
