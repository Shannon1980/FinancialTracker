"""
Data Models for SEAS Financial Tracker
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

@dataclass
class ProjectParameters:
    """Project configuration parameters"""
    current_date: datetime
    eac_hours: float
    actual_hours: float
    non_billable_hours: float
    total_transaction_price: float
    fringe_rate: float
    overhead_rate: float
    ga_rate: float
    target_profit: float

@dataclass
class Employee:
    """Employee data model"""
    name: str
    lcat: str
    priced_salary: float
    current_salary: float
    hours_per_month: float
    hourly_rate: float
    hours_by_period: Dict[str, float]
    revenue_by_period: Dict[str, float]

@dataclass
class Subcontractor:
    """Subcontractor data model"""
    name: str
    company: str
    lcat: str
    hourly_rate: float
    hours_by_period: Dict[str, float]
    revenue_by_period: Dict[str, float]

@dataclass
class ODCCost:
    """Other Direct Cost data model"""
    period: str
    amount: float
    description: str

@dataclass
class Task:
    """Task breakdown data model"""
    task_id: str
    task_name: str
    lcat: str
    person_org: str
    person: str
    hours: float
    cost: float

class DataManager:
    """Centralized data management"""
    
    def __init__(self):
        self.employees: pd.DataFrame = pd.DataFrame()
        self.subcontractors: pd.DataFrame = pd.DataFrame()
        self.odc_costs: pd.DataFrame = pd.DataFrame()
        self.tasks: pd.DataFrame = pd.DataFrame()
        self.project_params: ProjectParameters = None
        self.time_periods: List[str] = []
    
    def add_employee(self, employee: Employee) -> None:
        """Add new employee"""
        # Implementation here
    
    def remove_employee(self, name: str) -> bool:
        """Remove employee by name"""
        # Implementation here
    
    def get_employee_count(self) -> int:
        """Get total employee count"""
        return len(self.employees)
    
    def export_data(self, format: str = 'excel') -> bytes:
        """Export data in specified format"""
        # Implementation here
    
    def create_backup(self) -> Dict:
        """Create comprehensive backup"""
        # Implementation here
    
    def restore_backup(self, backup_data: Dict) -> bool:
        """Restore from backup"""
        # Implementation here
