"""
Unit tests for data utilities module
"""

import pytest
import pandas as pd
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data_utils import (
    generate_time_periods,
    create_sample_employees,
    create_sample_subcontractors,
    calculate_employee_metrics,
    calculate_subcontractor_metrics,
    validate_employee_data,
    validate_subcontractor_data
)


class TestDataUtils:
    """Test cases for data utility functions"""
    
    def test_generate_time_periods(self):
        """Test time period generation"""
        periods = generate_time_periods()
        
        # Should return a list
        assert isinstance(periods, list)
        # Should have 24 periods (2 years)
        assert len(periods) == 24
        # Should start with Jan
        assert periods[0] == 'Jan'
        # Should have standard month names
        expected_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        assert periods[:12] == expected_months
    
    def test_create_sample_employees(self):
        """Test sample employee data creation"""
        employees_df = create_sample_employees()
        
        # Should return a DataFrame
        assert isinstance(employees_df, pd.DataFrame)
        # Should not be empty
        assert not employees_df.empty
        # Should have required columns
        required_columns = ['Name', 'LCAT', 'Current_Salary', 'Status']
        for col in required_columns:
            assert col in employees_df.columns
    
    def test_create_sample_subcontractors(self):
        """Test sample subcontractor data creation"""
        subcontractors_df = create_sample_subcontractors()
        
        # Should return a DataFrame
        assert isinstance(subcontractors_df, pd.DataFrame)
        # Should not be empty
        assert not subcontractors_df.empty
        # Should have required columns
        required_columns = ['Name', 'LCAT', 'Hourly_Rate', 'Status']
        for col in required_columns:
            assert col in subcontractors_df.columns
    
    def test_calculate_employee_metrics(self, sample_employees_data):
        """Test employee metrics calculation"""
        metrics = calculate_employee_metrics(sample_employees_data)
        
        # Should return a dictionary
        assert isinstance(metrics, dict)
        # Should have required metrics
        required_metrics = ['total_employees', 'active_employees', 'total_salary', 'average_salary']
        for metric in required_metrics:
            assert metric in metrics
        
        # Should have correct values
        assert metrics['total_employees'] == 3
        assert metrics['active_employees'] == 3
        assert metrics['total_salary'] == 245000  # 85000 + 95000 + 65000
        assert metrics['average_salary'] == 81666.67  # 245000 / 3
    
    def test_calculate_subcontractor_metrics(self, sample_subcontractors_data):
        """Test subcontractor metrics calculation"""
        metrics = calculate_subcontractor_metrics(sample_subcontractors_data)
        
        # Should return a dictionary
        assert isinstance(metrics, dict)
        # Should have required metrics
        required_metrics = ['total_subcontractors', 'active_subcontractors', 'total_hours', 'average_rate']
        for metric in required_metrics:
            assert metric in metrics
        
        # Should have correct values
        assert metrics['total_subcontractors'] == 3
        assert metrics['active_subcontractors'] == 3
    
    def test_validate_employee_data_valid(self, sample_employees_data):
        """Test employee data validation with valid data"""
        is_valid, errors = validate_employee_data(sample_employees_data)
        
        # Should be valid
        assert is_valid is True
        # Should have no errors
        assert len(errors) == 0
    
    def test_validate_employee_data_missing_columns(self):
        """Test employee data validation with missing columns"""
        invalid_df = pd.DataFrame({
            'Name': ['John Doe'],
            'LCAT': ['Engineer']
            # Missing required columns
        })
        
        is_valid, errors = validate_employee_data(invalid_df)
        
        # Should be invalid
        assert is_valid is False
        # Should have errors
        assert len(errors) > 0
    
    def test_validate_employee_data_invalid_salary(self):
        """Test employee data validation with invalid salary"""
        invalid_df = pd.DataFrame({
            'Name': ['John Doe'],
            'LCAT': ['Engineer'],
            'Current_Salary': ['invalid_salary'],  # Should be numeric
            'Status': ['Active']
        })
        
        is_valid, errors = validate_employee_data(invalid_df)
        
        # Should be invalid
        assert is_valid is False
        # Should have errors
        assert len(errors) > 0
    
    def test_validate_subcontractor_data_valid(self, sample_subcontractors_data):
        """Test subcontractor data validation with valid data"""
        is_valid, errors = validate_subcontractor_data(sample_subcontractors_data)
        
        # Should be valid
        assert is_valid is True
        # Should have no errors
        assert len(errors) == 0
    
    def test_validate_subcontractor_data_missing_columns(self):
        """Test subcontractor data validation with missing columns"""
        invalid_df = pd.DataFrame({
            'Name': ['ABC Corp'],
            'LCAT': ['Consultant']
            # Missing required columns
        })
        
        is_valid, errors = validate_subcontractor_data(invalid_df)
        
        # Should be invalid
        assert is_valid is False
        # Should have errors
        assert len(errors) > 0
    
    def test_validate_subcontractor_data_invalid_rate(self):
        """Test subcontractor data validation with invalid hourly rate"""
        invalid_df = pd.DataFrame({
            'Name': ['ABC Corp'],
            'LCAT': ['Consultant'],
            'Hourly_Rate': ['invalid_rate'],  # Should be numeric
            'Status': ['Active']
        })
        
        is_valid, errors = validate_subcontractor_data(invalid_df)
        
        # Should be invalid
        assert is_valid is False
        # Should have errors
        assert len(errors) > 0
