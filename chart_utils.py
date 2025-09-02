"""
Chart and visualization utilities for SEAS Financial Tracker
Handles Plotly chart creation and data visualization
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import streamlit as st
from theme_manager import ThemeManager


def apply_theme_to_chart(fig: go.Figure) -> go.Figure:
    """Apply current theme to a Plotly chart"""
    theme_manager = ThemeManager()
    theme_config = theme_manager.get_plotly_theme()
    
    # Apply theme to layout
    fig.update_layout(**theme_config['layout'])
    
    # Update grid and axis styling
    fig.update_xaxes(
        gridcolor=theme_config['layout']['xaxis']['gridcolor'],
        color=theme_config['layout']['xaxis']['color']
    )
    fig.update_yaxes(
        gridcolor=theme_config['layout']['yaxis']['gridcolor'],
        color=theme_config['layout']['yaxis']['color']
    )
    
    return fig


def create_revenue_trends_chart(employees_df: pd.DataFrame, subcontractors_df: pd.DataFrame) -> go.Figure:
    """Create revenue trends chart for employees and subcontractors"""
    # Get time period columns
    time_periods = [col for col in employees_df.columns if col.startswith('Revenue_')]
    
    if not time_periods:
        # Create empty chart if no data
        fig = go.Figure()
        fig.add_annotation(text="No revenue data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    
    # Calculate total revenue by period
    employee_revenue = []
    subcontractor_revenue = []
    period_labels = []
    
    for period_col in time_periods:
        period_name = period_col.replace('Revenue_', '')
        period_labels.append(period_name)
        
        # Employee revenue
        emp_rev = employees_df[period_col].sum() if not employees_df.empty else 0
        employee_revenue.append(emp_rev)
        
        # Subcontractor revenue
        sub_rev = subcontractors_df[period_col].sum() if not subcontractors_df.empty else 0
        subcontractor_revenue.append(sub_rev)
    
    # Create the chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=period_labels,
        y=employee_revenue,
        mode='lines+markers',
        name='Employee Revenue',
        line=dict(color='#2C7BE5', width=3),
        marker=dict(size=8)
    ))
    
    fig.add_trace(go.Scatter(
        x=period_labels,
        y=subcontractor_revenue,
        mode='lines+markers',
        name='Subcontractor Revenue',
        line=dict(color='#E53E3E', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Revenue Trends by Period",
        xaxis_title="Time Period",
        yaxis_title="Revenue ($)",
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50),
        xaxis=dict(tickangle=45)
    )
    
    # Apply theme
    fig = apply_theme_to_chart(fig)
    
    return fig


def create_employee_heatmap_chart(employees_df: pd.DataFrame) -> go.Figure:
    """Create employee hours heatmap chart"""
    if employees_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No employee data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    
    # Get time period columns
    hours_cols = [col for col in employees_df.columns if col.startswith('Hours_') and col != 'Hours_Per_Month']
    
    if not hours_cols:
        fig = go.Figure()
        fig.add_annotation(text="No hours data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    
    # Prepare data for heatmap
    employees = employees_df['Name'].tolist()
    periods = [col.replace('Hours_', '') for col in hours_cols]
    
    # Create matrix of hours
    hours_matrix = []
    for _, employee in employees_df.iterrows():
        row = []
        for col in hours_cols:
            row.append(employee[col])
        hours_matrix.append(row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=hours_matrix,
        x=periods,
        y=employees,
        colorscale='Blues',
        showscale=True,
        colorbar=dict(title="Hours")
    ))
    
    fig.update_layout(
        title="Employee Hours Heatmap",
        xaxis_title="Time Period",
        yaxis_title="Employee",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def create_lcat_cost_analysis_chart(employees_df: pd.DataFrame) -> go.Figure:
    """Create LCAT cost analysis chart"""
    if employees_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No employee data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    
    # Group by LCAT and calculate costs
    lcat_costs = employees_df.groupby('LCAT').agg({
        'Current_Salary': 'sum',
        'Name': 'count'
    }).reset_index()
    
    lcat_costs.columns = ['LCAT', 'Total_Cost', 'Employee_Count']
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=lcat_costs['LCAT'],
            y=lcat_costs['Total_Cost'],
            text=lcat_costs['Employee_Count'],
            textposition='auto',
            marker_color='#2C7BE5'
        )
    ])
    
    fig.update_layout(
        title="Cost Analysis by LCAT",
        xaxis_title="LCAT",
        yaxis_title="Total Cost ($)",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50),
        xaxis=dict(tickangle=45)
    )
    
    return fig


def create_burn_rate_chart(employees_df: pd.DataFrame, subcontractors_df: pd.DataFrame) -> go.Figure:
    """Create burn rate analysis chart"""
    # Get time period columns
    time_periods = [col for col in employees_df.columns if col.startswith('Hours_') and col != 'Hours_Per_Month']
    
    if not time_periods:
        fig = go.Figure()
        fig.add_annotation(text="No time period data available", xref="paper", yref="paper", 
                          x=0.5, y=0.5, showarrow=False, font_size=16)
        return fig
    
    # Calculate cumulative hours and costs
    cumulative_hours = []
    cumulative_costs = []
    period_labels = []
    
    total_hours = 0
    total_costs = 0
    
    for period_col in time_periods:
        period_name = period_col.replace('Hours_', '')
        period_labels.append(period_name)
        
        # Calculate hours for this period
        emp_hours = employees_df[period_col].sum() if not employees_df.empty else 0
        sub_hours = subcontractors_df[period_col].sum() if not subcontractors_df.empty else 0
        period_hours = emp_hours + sub_hours
        
        # Calculate costs for this period
        emp_costs = 0
        if not employees_df.empty:
            for _, emp in employees_df.iterrows():
                emp_costs += emp[period_col] * emp['Hourly_Rate']
        
        sub_costs = 0
        if not subcontractors_df.empty:
            for _, sub in subcontractors_df.iterrows():
                sub_costs += sub[period_col] * sub['Hourly_Rate']
        
        period_costs = emp_costs + sub_costs
        
        # Add to cumulative totals
        total_hours += period_hours
        total_costs += period_costs
        
        cumulative_hours.append(total_hours)
        cumulative_costs.append(total_costs)
    
    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Add hours trace
    fig.add_trace(
        go.Scatter(
            x=period_labels,
            y=cumulative_hours,
            mode='lines+markers',
            name='Cumulative Hours',
            line=dict(color='#2C7BE5', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False,
    )
    
    # Add costs trace
    fig.add_trace(
        go.Scatter(
            x=period_labels,
            y=cumulative_costs,
            mode='lines+markers',
            name='Cumulative Costs',
            line=dict(color='#E53E3E', width=3),
            marker=dict(size=8)
        ),
        secondary_y=True,
    )
    
    # Update layout
    fig.update_xaxes(title_text="Period", tickangle=45)
    fig.update_yaxes(title_text="Hours", secondary_y=False)
    fig.update_yaxes(title_text="Costs ($)", secondary_y=True)
    fig.update_layout(
        title_text="Cumulative Hours and Costs",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    return fig


def create_project_metrics_chart(params: Dict[str, Any]) -> go.Figure:
    """Create project metrics visualization"""
    # Create a simple metrics display chart
    metrics = [
        ("EAC Hours", params.get('eac_hours', 0)),
        ("Actual Hours", params.get('actual_hours', 0)),
        ("Non-Billable Hours", abs(params.get('non_billable_hours', 0))),
    ]
    
    labels = [metric[0] for metric in metrics]
    values = [metric[1] for metric in metrics]
    colors = ['#2C7BE5', '#38A169', '#E53E3E']
    
    fig = go.Figure(data=[
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors,
            text=values,
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Project Hours Overview",
        xaxis_title="Metric",
        yaxis_title="Hours",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    return fig


def create_financial_summary_chart(params: Dict[str, Any]) -> go.Figure:
    """Create financial summary visualization"""
    # Calculate financial metrics
    total_price = params.get('total_transaction_price', 0)
    fringe_rate = params.get('fringe_rate', 0)
    overhead_rate = params.get('overhead_rate', 0)
    ga_rate = params.get('ga_rate', 0)
    target_profit = params.get('target_profit', 0)
    
    # Calculate components
    fringe_cost = total_price * fringe_rate
    overhead_cost = total_price * overhead_rate
    ga_cost = total_price * ga_rate
    profit = total_price * target_profit
    base_cost = total_price - fringe_cost - overhead_cost - ga_cost - profit
    
    # Create pie chart
    labels = ['Base Cost', 'Fringe', 'Overhead', 'G&A', 'Profit']
    values = [base_cost, fringe_cost, overhead_cost, ga_cost, profit]
    colors = ['#2C7BE5', '#38A169', '#D69E2E', '#E53E3E', '#805AD5']
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent+value',
            texttemplate='%{label}<br>%{percent}<br>$%{value:,.0f}'
        )
    ])
    
    fig.update_layout(
        title="Financial Breakdown",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(t=50, l=50, r=50, b=50)
    )
    
    return fig
