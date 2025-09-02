"""
Pytest configuration and fixtures for SEAS Financial Tracker tests
"""

import pytest
import pandas as pd
import streamlit as st
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_employees_data():
    """Sample employee data for testing"""
    return pd.DataFrame({
        'Name': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'LCAT': ['Senior Engineer', 'Project Manager', 'Analyst'],
        'Current_Salary': [85000, 95000, 65000],
        'Priced_Salary': [100000, 110000, 75000],
        'Status': ['Active', 'Active', 'Active'],
        'Hours_Jan': [160, 160, 160],
        'Hours_Feb': [160, 160, 160],
        'Revenue_Jan': [10000, 11000, 7500],
        'Revenue_Feb': [10000, 11000, 7500]
    })


@pytest.fixture
def sample_subcontractors_data():
    """Sample subcontractor data for testing"""
    return pd.DataFrame({
        'Name': ['ABC Corp', 'XYZ Ltd', 'DEF Inc'],
        'LCAT': ['Consultant', 'Specialist', 'Advisor'],
        'Hourly_Rate': [150, 200, 125],
        'Status': ['Active', 'Active', 'Active'],
        'Hours_Jan': [80, 60, 100],
        'Hours_Feb': [80, 60, 100],
        'Revenue_Jan': [12000, 12000, 12500],
        'Revenue_Feb': [12000, 12000, 12500]
    })


@pytest.fixture
def sample_project_params():
    """Sample project parameters for testing"""
    return {
        'total_transaction_price': 1000000,
        'actual_hours': 2000,
        'eac_hours': 2500,
        'target_profit': 0.15,
        'indirect_rate': 0.25
    }


@pytest.fixture
def mock_session_state():
    """Mock Streamlit session state"""
    with patch.object(st, 'session_state', {}):
        yield st.session_state


@pytest.fixture
def mock_streamlit():
    """Mock Streamlit components"""
    with patch.multiple(
        st,
        markdown=Mock(),
        write=Mock(),
        error=Mock(),
        success=Mock(),
        warning=Mock(),
        info=Mock(),
        button=Mock(return_value=False),
        selectbox=Mock(return_value='test'),
        text_input=Mock(return_value='test'),
        number_input=Mock(return_value=100),
        columns=Mock(return_value=[Mock(), Mock()]),
        tabs=Mock(return_value=[Mock(), Mock(), Mock()]),
        plotly_chart=Mock(),
        dataframe=Mock(),
        metric=Mock()
    ):
        yield st


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Set up test environment before each test"""
    # Clear any existing session state
    if hasattr(st, 'session_state'):
        st.session_state.clear()
    
    # Set up basic session state
    st.session_state.update({
        'authenticated': True,
        'username': 'test_user',
        'role': 'admin'
    })
    
    yield
    
    # Cleanup after test
    if hasattr(st, 'session_state'):
        st.session_state.clear()


@pytest.fixture
def sample_time_periods():
    """Sample time periods for testing"""
    return [
        'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
    ]


@pytest.fixture
def sample_tasks_data():
    """Sample tasks data for testing"""
    return pd.DataFrame({
        'Task_ID': ['T001', 'T002', 'T003'],
        'Task_Name': ['Design', 'Development', 'Testing'],
        'Assigned_To': ['John Doe', 'Jane Smith', 'Bob Johnson'],
        'Status': ['In Progress', 'Completed', 'Pending'],
        'Hours_Estimated': [40, 80, 20],
        'Hours_Actual': [35, 85, 0],
        'Cost_Estimated': [4000, 8000, 2000],
        'Cost_Actual': [3500, 8500, 0]
    })


@pytest.fixture
def sample_odc_data():
    """Sample ODC (Other Direct Costs) data for testing"""
    return pd.DataFrame({
        'Category': ['Travel', 'Equipment', 'Software'],
        'Description': ['Business travel', 'Hardware purchase', 'License fees'],
        'Amount': [5000, 10000, 3000],
        'Period': ['Jan', 'Jan', 'Feb'],
        'Status': ['Approved', 'Approved', 'Pending']
    })
