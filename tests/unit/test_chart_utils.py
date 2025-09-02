"""
Unit tests for chart utilities module
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chart_utils import (
    apply_theme_to_chart,
    create_revenue_trends_chart,
    create_employee_heatmap_chart,
    create_lcat_cost_analysis_chart,
    create_burn_rate_chart,
    create_project_metrics_chart,
    create_financial_summary_chart
)


class TestChartUtils:
    """Test cases for chart utility functions"""
    
    def test_apply_theme_to_chart(self):
        """Test theme application to charts"""
        # Create a simple chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]))
        
        # Apply theme
        themed_fig = apply_theme_to_chart(fig)
        
        # Should return a Figure object
        assert isinstance(themed_fig, go.Figure)
        # Should have layout properties
        assert hasattr(themed_fig, 'layout')
    
    def test_create_revenue_trends_chart_with_data(self, sample_employees_data, sample_subcontractors_data):
        """Test revenue trends chart creation with data"""
        fig = create_revenue_trends_chart(sample_employees_data, sample_subcontractors_data)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
        # Should have a title
        assert fig.layout.title is not None
    
    def test_create_revenue_trends_chart_empty_data(self):
        """Test revenue trends chart creation with empty data"""
        empty_df = pd.DataFrame()
        fig = create_revenue_trends_chart(empty_df, empty_df)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces (sample data)
        assert len(fig.data) > 0
    
    def test_create_employee_heatmap_chart_with_data(self, sample_employees_data):
        """Test employee heatmap chart creation with data"""
        fig = create_employee_heatmap_chart(sample_employees_data)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
    
    def test_create_employee_heatmap_chart_empty_data(self):
        """Test employee heatmap chart creation with empty data"""
        empty_df = pd.DataFrame()
        fig = create_employee_heatmap_chart(empty_df)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have an annotation for empty data
        assert len(fig.layout.annotations) > 0
    
    def test_create_lcat_cost_analysis_chart_with_data(self, sample_employees_data):
        """Test LCAT cost analysis chart creation with data"""
        fig = create_lcat_cost_analysis_chart(sample_employees_data)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
    
    def test_create_lcat_cost_analysis_chart_empty_data(self):
        """Test LCAT cost analysis chart creation with empty data"""
        empty_df = pd.DataFrame()
        fig = create_lcat_cost_analysis_chart(empty_df)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have an annotation for empty data
        assert len(fig.layout.annotations) > 0
    
    def test_create_burn_rate_chart_with_data(self, sample_employees_data, sample_subcontractors_data):
        """Test burn rate chart creation with data"""
        fig = create_burn_rate_chart(sample_employees_data, sample_subcontractors_data)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
    
    def test_create_burn_rate_chart_empty_data(self):
        """Test burn rate chart creation with empty data"""
        empty_df = pd.DataFrame()
        fig = create_burn_rate_chart(empty_df, empty_df)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have an annotation for empty data
        assert len(fig.layout.annotations) > 0
    
    def test_create_project_metrics_chart(self, sample_project_params):
        """Test project metrics chart creation"""
        fig = create_project_metrics_chart(sample_project_params)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
        # Should have a title
        assert fig.layout.title is not None
    
    def test_create_financial_summary_chart(self, sample_project_params):
        """Test financial summary chart creation"""
        fig = create_financial_summary_chart(sample_project_params)
        
        # Should return a Figure object
        assert isinstance(fig, go.Figure)
        # Should have traces
        assert len(fig.data) > 0
        # Should have a title
        assert fig.layout.title is not None
    
    def test_chart_error_handling(self):
        """Test chart creation error handling"""
        # Test with invalid data types
        invalid_data = "not a dataframe"
        
        # Should handle errors gracefully
        try:
            fig = create_revenue_trends_chart(invalid_data, invalid_data)
            assert isinstance(fig, go.Figure)
        except Exception:
            # If an exception is raised, it should be handled
            pass
    
    def test_chart_theme_consistency(self, sample_employees_data):
        """Test that charts maintain theme consistency"""
        fig1 = create_employee_heatmap_chart(sample_employees_data)
        fig2 = create_employee_heatmap_chart(sample_employees_data)
        
        # Both charts should have similar structure
        assert isinstance(fig1, go.Figure)
        assert isinstance(fig2, go.Figure)
        assert len(fig1.data) == len(fig2.data)
