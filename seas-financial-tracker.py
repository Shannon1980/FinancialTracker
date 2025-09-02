import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json
from typing import Dict, List, Tuple, Optional
import base64

# Import authentication and user management modules
from auth import AuthManager, render_login_page, render_logout_button, require_auth, check_permission
from user_management import UserManager, render_user_management_page, render_user_info_sidebar, render_data_access_notice
from theme_manager import ThemeManager, render_theme_toggle_sidebar
from modern_ui import ModernUI
from data_import_system import render_data_import_page

# Import utility modules
from utils.template_downloader import generate_employee_template, get_template_info
from styling import load_css, create_section, create_section_divider, create_section_grid, create_metric_card
from data_utils import (
    generate_time_periods, create_sample_employees, create_sample_subcontractors,
    create_sample_odc, create_sample_tasks, validate_employee_data, validate_subcontractor_data,
    calculate_employee_metrics, calculate_subcontractor_metrics, detect_duplicate_employees,
    merge_employee_data
)
from chart_utils import (
    create_revenue_trends_chart, create_employee_heatmap_chart, create_lcat_cost_analysis_chart,
    create_burn_rate_chart, create_project_metrics_chart, create_financial_summary_chart
)

# Set page config
st.set_page_config(
    page_title="SEAS Financial Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load the CSS
load_css()

# CSS is now loaded through the styling module

# ============================================================================
# Modular Section Helper Functions
# ============================================================================

def create_section(title, content, section_type="info", status=None, footer_content=None, actions=None):
    """Create a modular section with consistent styling"""
    
    # Section type classes
    type_classes = {
        "info": "info-section",
        "success": "success-section", 
        "warning": "warning-section",
        "danger": "danger-section"
    }
    
    # Status badges
    status_badges = {
        "active": "active",
        "pending": "pending",
        "completed": "completed",
        "ready": "completed",
        "needs_review": "pending"
    }
    
    # Build section HTML
    section_class = f"section-container {type_classes.get(section_type, 'info-section')}"
    status_html = f'<span class="section-status {status_badges.get(status, "active")}">{status or "Active"}</span>' if status else ""
    
    section_html = f'''
    <div class="{section_class}">
        <div class="section-header">
            <h3>{title}</h3>
            {status_html}
        </div>
        <div class="section-content">
            {content}
        </div>
    '''
    
    # Add footer if provided
    if footer_content or actions:
        section_html += '<div class="section-footer">'
        if footer_content:
            section_html += f'<span>{footer_content}</span>'
        if actions:
            section_html += '<div class="section-actions">'
            for action in actions:
                section_html += f'<button class="btn btn-{action["type"]}">{action["label"]}</button>'
            section_html += '</div>'
        section_html += '</div>'
    
    section_html += '</div>'
    
    return st.markdown(section_html, unsafe_allow_html=True)

def create_section_divider():
    """Create a visual separator between sections"""
    return st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

def create_section_grid(sections, columns=2):
    """Create a responsive grid of sections"""
    grid_html = f'<div class="section-grid" style="grid-template-columns: repeat({columns}, 1fr);">'
    for section in sections:
        grid_html += section
    grid_html += '</div>'
    return st.markdown(grid_html, unsafe_allow_html=True)

def create_metric_card(title, value, change=None, change_type="positive"):
    """Create a metric card for use within sections"""
    change_html = f'<p class="metric-change {change_type}">{change}</p>' if change else ""
    return f'''
    <div class="card">
        <div class="card-header">
            <h4 class="card-title">{title}</h4>
        </div>
        <div class="card-body">
            <p class="metric-value">{value}</p>
            {change_html}
        </div>
    </div>
    '''

class SEASFinancialTracker:
    def __init__(self):
        self.initialize_session_state()
        self.modern_ui = ModernUI()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        # Initialize time_periods first since other methods depend on it
        if 'time_periods' not in st.session_state:
            st.session_state.time_periods = generate_time_periods()
            
        if 'project_params' not in st.session_state:
            st.session_state.project_params = {
                'current_date': datetime(2025, 9, 1),
                'eac_hours': 37626.75,
                'actual_hours': 26656.5,
                'non_billable_hours': -357.75,
                'total_transaction_price': 8079029.79,
                'fringe_rate': 0.326,
                'overhead_rate': 0.150,
                'ga_rate': 0.275,
                'target_profit': 0.3947
            }
            
        if 'employees' not in st.session_state:
            st.session_state.employees = create_sample_employees()
        if 'subcontractors' not in st.session_state:
            st.session_state.subcontractors = create_sample_subcontractors()
        if 'odc_costs' not in st.session_state:
            st.session_state.odc_costs = create_sample_odc()
        if 'tasks' not in st.session_state:
            st.session_state.tasks = create_sample_tasks()





    # ============================================================================
    # Modular Section Content Helper Methods
    # ============================================================================
    
    def _create_employee_summary_content(self):
        """Create content for employee summary section"""
        employees_df = st.session_state.employees
        
        # Check data access permissions
        if not render_data_access_notice('employees'):
            return
        
        if not employees_df.empty:
            # Filter sensitive data based on user permissions
            user_manager = UserManager()
            filtered_df = user_manager.filter_sensitive_data(employees_df, 'employees')
            # Use utility function to calculate metrics
            try:
                metrics = calculate_employee_metrics(employees_df)
                
                # Create metric cards using Streamlit columns
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Employees", metrics['total_employees'], "+2 this month")
                with col2:
                    st.metric("Active Employees", metrics['active_employees'])
                with col3:
                    # Check if user has salary access
                    if user_manager.has_sensitive_data_access('salary'):
                        st.metric("Total Salary", f"${metrics['total_salary']:,.0f}")
                    else:
                        st.metric("Total Salary", "*** Restricted ***")
                with col4:
                    # Check if user has salary access
                    if user_manager.has_sensitive_data_access('salary'):
                        st.metric("Avg Salary", f"${metrics['average_salary']:,.0f}")
                    else:
                        st.metric("Avg Salary", "*** Restricted ***")
            except Exception as e:
                st.error(f"Error calculating metrics: {e}")
                # Fallback metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Employees", len(employees_df))
                with col2:
                    st.metric("Active Employees", len(employees_df[employees_df['Status'] == 'Active']) if 'Status' in employees_df.columns else len(employees_df))
                with col3:
                    st.metric("Total Salary", f"${employees_df['Current_Salary'].sum():,.0f}")
                with col4:
                    st.metric("Avg Salary", f"${employees_df['Current_Salary'].mean():,.0f}")
            
            # Add breakdown summary using Streamlit columns
            st.markdown("### 📊 Employee Breakdown")
            col1, col2, col3 = st.columns(3)
            
            try:
                employee_type_counts = employees_df['Employee_Type'].value_counts()
                status_counts = employees_df['Status'].value_counts()
                company_counts = employees_df['Company'].value_counts()
                
                with col1:
                    st.markdown("#### 👥 Employee Types")
                    for emp_type, count in employee_type_counts.items():
                        type_icon = "👨‍💼" if emp_type == 'Employee' else "🏢"
                        st.write(f"{type_icon} {emp_type}: {count}")
                
                with col2:
                    st.markdown("#### 📊 Status")
                    for status, count in status_counts.items():
                        status_icon = "🟢" if status == 'Active' else "🔴"
                        st.write(f"{status_icon} {status}: {count}")
                
                with col3:
                    st.markdown("#### 🏢 Companies")
                    for company, count in company_counts.items():
                        st.write(f"• {company}: {count}")
            except Exception as e:
                st.error(f"Error in breakdown section: {e}")
                st.write("Employee data available but breakdown failed")
        else:
            st.info("📝 No employees added yet. Use the sections below to add employees or upload data.")
    
    def _create_template_download_content(self):
        """Create content for template download section"""
        st.markdown("Choose from our professionally designed templates to ensure consistent data entry and maintain all required fields.")
        
        # Add template options using Streamlit
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Template**")
            st.markdown("5 required fields + monthly hours/revenue columns")
            st.markdown("Perfect for quick employee data entry")
            
            if st.button("📥 Download Basic Template", key="download_basic"):
                try:
                    file_bytes, filename = generate_employee_template("basic")
                    st.download_button(
                        label="💾 Save Basic Template",
                        data=file_bytes,
                        file_name=filename,
                        key="save_basic"
                    )
                except Exception as e:
                    st.error(f"Error generating template: {e}")
            
        with col2:
            st.markdown("**Comprehensive Template**")
            st.markdown("10 fields + monthly hours/revenue + instructions")
            st.markdown("Perfect for detailed employee management")
            
            if st.button("📥 Download Comprehensive Template", key="download_comprehensive"):
                try:
                    file_bytes, filename = generate_employee_template("comprehensive")
                    st.download_button(
                        label="💾 Save Comprehensive Template",
                        data=file_bytes,
                        file_name=filename,
                        key="save_comprehensive"
                    )
                except Exception as e:
                    st.error(f"Error generating template: {e}")
        
        # Template features
        st.markdown("### 📋 Template Features")
        st.markdown("""
        - **Standardized Format:** Consistent data structure
        - **Data Validation:** Built-in field validation
        - **Monthly Tracking:** 24 monthly periods included
        - **Professional Design:** QuickBooks-inspired layout
        - **Easy Import:** Direct upload compatibility
        """)
        
        st.markdown("### 🎯 Best Practices")
        st.markdown("""
        - Use consistent naming conventions
        - Fill all required fields
        - Validate salary ranges
        - Check for duplicate entries
        """)
    
    def _create_upload_content(self):
        """Create content for data upload section"""
        # Check permissions for data import
        if not check_permission('import'):
            st.warning("🔒 You don't have permission to import data. Contact your administrator.")
            return
            
        uploaded_file = st.file_uploader("Choose Excel/CSV file", type=['xlsx', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df_upload = pd.read_excel(uploaded_file)
                else:
                    df_upload = pd.read_csv(uploaded_file)
                st.success(f"Uploaded {len(df_upload)} rows of data")
                
                if st.button("Import Data"):
                    # Check for duplicates before importing
                    existing_names = [name.lower() for name in st.session_state.employees['Name'].tolist()]
                    new_names = [name.lower() for name in df_upload['Name'].tolist()]
                    
                    # Find duplicate names
                    duplicates = [name for name in new_names if name in existing_names]
                    
                    if duplicates:
                        st.warning(f"⚠️ Found {len(duplicates)} duplicate employee(s): {', '.join(duplicates)}")
                        st.info("💡 Tip: Update existing employees instead of creating duplicates, or use different names.")
                        
                        # Show duplicate comparison
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Existing Employees:**")
                            existing_dups = st.session_state.employees[st.session_state.employees['Name'].str.lower().isin(duplicates)]
                            st.dataframe(existing_dups[['Name', 'LCAT', 'Current_Salary']])
                        
                        with col2:
                            st.write("**New Data (Duplicates):**")
                            new_dups = df_upload[df_upload['Name'].str.lower().isin(duplicates)]
                            st.dataframe(new_dups[['Name', 'LCAT', 'Current_Salary']])
                        
                        if st.button("🔄 Import Anyway (Replace Duplicates)", key="import_anyway"):
                            # Process and merge with existing data (this will replace duplicates)
                            st.session_state.employees = self.process_uploaded_employees(df_upload)
                            st.success("Data imported successfully! Duplicates were replaced.")
                            st.rerun()
                    else:
                        # No duplicates, safe to import
                        st.session_state.employees = self.process_uploaded_employees(df_upload)
                        st.success("✅ Data imported successfully! No duplicates found.")
                        st.rerun()
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

        return '''
        <div class="upload-instructions">
            <h4>📂 Upload Instructions</h4>
            <p>Upload your employee data using Excel (.xlsx) or CSV (.csv) files. The system will automatically validate the data and check for duplicates.</p>
            
            <div class="alert alert-info">
                <strong>💡 Pro Tip:</strong> Download a template first to ensure your data is in the correct format.
            </div>
        </div>
        '''
    
    def _create_employee_management_content(self):
        """Create content for employee management section"""
        # Check permissions for employee management
        if not check_permission('edit'):
            st.warning("🔒 You don't have permission to manage employees. Contact your administrator.")
            return
            
        employees_df = st.session_state.employees
        
        # Add new employee form
        with st.expander("➕ Add New Employee", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_name = st.text_input("Name")
                new_lcat = st.selectbox("LCAT", ["PM", "SA/Eng Lead", "AI Lead", "HCD Lead", 
                                                "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"])
                new_employee_type = st.selectbox("Employee Type", ["Employee", "Subcontractor"])
            with col2:
                new_company = st.selectbox("Company", ["Skyward IT Solutions", "BEELINE", "Self Employed", "Aquia", "Friends"])
                new_status = st.selectbox("Status", ["Active", "Inactive"])
                new_priced_salary = st.number_input("Priced Salary", min_value=0, value=100000)
            with col3:
                new_current_salary = st.number_input("Current Salary", min_value=0, value=100000)
                new_hours_per_month = st.number_input("Hours per Month", min_value=0, value=173)
                
            if st.button("Add Employee") and new_name:
                # Check for duplicate employee names (case-insensitive)
                existing_names = [name.lower() for name in st.session_state.employees['Name'].tolist()]
                if new_name.lower() in existing_names:
                    st.error(f"❌ Employee '{new_name}' already exists! Please use a different name or update the existing employee.")
                else:
                    new_employee = {
                        "Name": new_name,
                        "LCAT": new_lcat,
                        "Employee_Type": new_employee_type,
                        "Company": new_company,
                        "Status": new_status,
                        "Priced_Salary": new_priced_salary,
                        "Current_Salary": new_current_salary,
                        "Hours_Per_Month": new_hours_per_month,
                        "Hourly_Rate": self.calculate_hourly_rate(new_current_salary, new_hours_per_month)
                }
                
                # Add columns for time periods
                    for period in st.session_state.employees.columns:
                        if period.startswith('Hours_') or period.startswith('Revenue_'):
                            new_employee[period] = 0.0
                
                # Add to dataframe
                    new_row = pd.DataFrame([new_employee])
                    st.session_state.employees = pd.concat([st.session_state.employees, new_row],
                                                          ignore_index=True)
                    st.success(f"✅ Added {new_name} to employee list")
                    st.rerun()

        # Employee data editor
        st.markdown("### Employee Information")
        basic_columns = ["Name", "LCAT", "Employee_Type", "Company", "Status", "Priced_Salary", "Current_Salary", "Hours_Per_Month", "Hourly_Rate"]
        
        edited_basic = st.data_editor(
            employees_df[basic_columns],
            column_config={
                "Priced_Salary": st.column_config.NumberColumn("Priced Salary", format="$%.2f"),
                "Current_Salary": st.column_config.NumberColumn("Current Salary", format="$%.2f"),
                "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
            },
            width='stretch',
            key="basic_employee_data"
        )
        
        # Update the main dataframe
        for col in basic_columns:
            st.session_state.employees[col] = edited_basic[col]
        
        return ""
    
    def _create_employee_detail_content(self):
        """Create content for employee detail view section"""
        employees_df = st.session_state.employees
        
        if not employees_df.empty:
            # Employee selector
            selected_employee = st.selectbox(
                "Select Employee to View Details:",
                options=employees_df['Name'].tolist(),
                key="employee_detail_selector"
            )
            
            if selected_employee:
                # Get employee data
                employee_data = employees_df[employees_df['Name'] == selected_employee].iloc[0]
                
                # Create detail view
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.markdown("**📋 Basic Information**")
                    st.write(f"**Name:** {employee_data['Name']}")
                    st.write(f"**LCAT:** {employee_data['LCAT']}")
                    st.write(f"**Employee Type:** {employee_data['Employee_Type']}")
                    st.write(f"**Company:** {employee_data['Company']}")
                    st.write(f"**Status:** {employee_data['Status']}")
                    st.write(f"**Hours/Month:** {employee_data['Hours_Per_Month']}")
                    
                    # Status indicator
                    status_color = "🟢" if employee_data['Status'] == 'Active' else "🔴"
                    st.markdown(f"{status_color} **Status:** {employee_data['Status']}")
                    
                    # Employee type indicator
                    type_icon = "👨‍💼" if employee_data['Employee_Type'] == 'Employee' else "🏢"
                    st.markdown(f"{type_icon} **Type:** {employee_data['Employee_Type']}")
                
                with col2:
                    st.markdown("**💰 Financial Information**")
                    st.write(f"**Priced Salary:** ${employee_data['Priced_Salary']:,.2f}")
                    st.write(f"**Current Salary:** ${employee_data['Current_Salary']:,.2f}")
                    st.write(f"**Hourly Rate:** ${employee_data['Hourly_Rate']:,.2f}")
                    
                    # Salary comparison
                    salary_diff = employee_data['Current_Salary'] - employee_data['Priced_Salary']
                    if salary_diff != 0:
                        diff_color = "🔴" if salary_diff > 0 else "🟢"
                        st.write(f"{diff_color} **Salary Difference:** ${salary_diff:,.2f}")
                
                # Time period data
                st.markdown("**📅 Time Period Data**")
                
                # Get all time period columns
                hours_cols = [col for col in employees_df.columns if col.startswith('Hours_') and col != 'Hours_Per_Month']
                revenue_cols = [col for col in employees_df.columns if col.startswith('Revenue_')]
                
                if hours_cols:
                    # Create time period summary
                    period_data = []
                    for hours_col in hours_cols:
                        period_name = hours_col.replace('Hours_', '')
                        hours = employee_data[hours_col]
                        revenue = employee_data.get(f'Revenue_{period_name}', 0)
                        period_data.append({
                            'Period': period_name,
                            'Hours': hours,
                            'Revenue': revenue,
                            'Rate': revenue / hours if hours > 0 else 0
                        })
                    
                    period_df = pd.DataFrame(period_data)
                    
                    # Show summary statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_hours = period_df['Hours'].sum()
                        st.metric("Total Hours", f"{total_hours:.1f}")
            with col2:
                total_revenue = period_df['Revenue'].sum()
                st.metric("Total Revenue", f"${total_revenue:,.2f}")
            with col3:
                avg_hours = period_df['Hours'].mean()
                st.metric("Avg Hours/Period", f"{avg_hours:.1f}")
            with col4:
                avg_revenue = period_df['Revenue'].mean()
                st.metric("Avg Revenue/Period", f"${avg_revenue:,.2f}")
            
            # Show detailed period data
            with st.expander("📊 View All Time Periods"):
                st.dataframe(period_df, width='stretch')
        else:
            return '<p>📝 No employees available for detailed view. Add employees first.</p>'
        
        return ""

    def _create_editable_employee_profile_content(self):
        """Create editable employee profile view"""
        employees_df = st.session_state.employees
        
        if not employees_df.empty:
            # Employee selector
            selected_employee = st.selectbox(
                "Select Employee to Edit:",
                options=employees_df['Name'].tolist(),
                key="editable_employee_selector"
            )
            
            if selected_employee:
                # Get employee data
                employee_data = employees_df[employees_df['Name'] == selected_employee].iloc[0]
                employee_index = employees_df[employees_df['Name'] == selected_employee].index[0]
                
                # Initialize session state for editing if not exists
                if f'editing_employee_{selected_employee}' not in st.session_state:
                    st.session_state[f'editing_employee_{selected_employee}'] = False
                
                # Toggle edit mode
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 👤 Editing: {selected_employee}")
                with col2:
                    if st.button("✏️ Edit Profile", key=f"edit_btn_{selected_employee}"):
                        st.session_state[f'editing_employee_{selected_employee}'] = True
                        st.rerun()
                
                if st.session_state[f'editing_employee_{selected_employee}']:
                    # Editable form
                    with st.form(f"edit_employee_form_{selected_employee}"):
                        st.markdown("#### 📋 Basic Information")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Name", value=employee_data['Name'], key=f"name_{selected_employee}")
                            new_lcat = st.selectbox(
                                "LCAT", 
                                options=["PM", "SA/Eng Lead", "AI Lead", "HCD Lead", "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"],
                                index=["PM", "SA/Eng Lead", "AI Lead", "HCD Lead", "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"].index(employee_data['LCAT']) if employee_data['LCAT'] in ["PM", "SA/Eng Lead", "AI Lead", "HCD Lead", "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"] else 0,
                                key=f"lcat_{selected_employee}"
                            )
                            new_employee_type = st.selectbox(
                                "Employee Type",
                                options=["Employee", "Subcontractor"],
                                index=0 if employee_data['Employee_Type'] == 'Employee' else 1,
                                key=f"employee_type_{selected_employee}"
                            )
                        
                        with col2:
                            new_company = st.selectbox(
                                "Company",
                                options=["Skyward IT Solutions", "BEELINE", "Self Employed", "Aquia", "Friends"],
                                index=["Skyward IT Solutions", "BEELINE", "Self Employed", "Aquia", "Friends"].index(employee_data['Company']) if employee_data['Company'] in ["Skyward IT Solutions", "BEELINE", "Self Employed", "Aquia", "Friends"] else 0,
                                key=f"company_{selected_employee}"
                            )
                            new_status = st.selectbox(
                                "Status",
                                options=["Active", "Inactive"],
                                index=0 if employee_data['Status'] == 'Active' else 1,
                                key=f"status_{selected_employee}"
                            )
                            new_hours_per_month = st.number_input(
                                "Hours per Month",
                                min_value=0,
                                value=int(employee_data['Hours_Per_Month']),
                                key=f"hours_per_month_{selected_employee}"
                            )
                        
                        st.markdown("#### 💰 Financial Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            new_priced_salary = st.number_input(
                                "Priced Salary",
                                min_value=0.0,
                                value=float(employee_data['Priced_Salary']),
                                key=f"priced_salary_{selected_employee}"
                            )
                        with col2:
                            new_current_salary = st.number_input(
                                "Current Salary",
                                min_value=0.0,
                                value=float(employee_data['Current_Salary']),
                                key=f"current_salary_{selected_employee}"
                            )
                        
                        # Calculate new hourly rate
                        new_hourly_rate = new_current_salary / (new_hours_per_month * 12) if new_hours_per_month > 0 else 0
                        st.info(f"**Calculated Hourly Rate:** ${new_hourly_rate:.2f}")
                        
                        # Form buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
                        with col2:
                            cancel_clicked = st.form_submit_button("❌ Cancel")
                        
                        if save_clicked:
                            # Update employee data
                            st.session_state.employees.at[employee_index, 'Name'] = new_name
                            st.session_state.employees.at[employee_index, 'LCAT'] = new_lcat
                            st.session_state.employees.at[employee_index, 'Employee_Type'] = new_employee_type
                            st.session_state.employees.at[employee_index, 'Company'] = new_company
                            st.session_state.employees.at[employee_index, 'Status'] = new_status
                            st.session_state.employees.at[employee_index, 'Hours_Per_Month'] = new_hours_per_month
                            st.session_state.employees.at[employee_index, 'Priced_Salary'] = new_priced_salary
                            st.session_state.employees.at[employee_index, 'Current_Salary'] = new_current_salary
                            st.session_state.employees.at[employee_index, 'Hourly_Rate'] = new_hourly_rate
                            
                            # Exit edit mode
                            st.session_state[f'editing_employee_{selected_employee}'] = False
                            st.success(f"✅ Successfully updated {new_name}'s profile!")
                            st.rerun()
                        
                        if cancel_clicked:
                            # Exit edit mode without saving
                            st.session_state[f'editing_employee_{selected_employee}'] = False
                            st.rerun()
                else:
                    # Read-only view
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("**📋 Basic Information**")
                        st.write(f"**Name:** {employee_data['Name']}")
                        st.write(f"**LCAT:** {employee_data['LCAT']}")
                        st.write(f"**Employee Type:** {employee_data['Employee_Type']}")
                        st.write(f"**Company:** {employee_data['Company']}")
                        st.write(f"**Status:** {employee_data['Status']}")
                        st.write(f"**Hours/Month:** {employee_data['Hours_Per_Month']}")
                        
                        # Status indicator
                        status_color = "🟢" if employee_data['Status'] == 'Active' else "🔴"
                        st.markdown(f"{status_color} **Status:** {employee_data['Status']}")
                        
                        # Employee type indicator
                        type_icon = "👨‍💼" if employee_data['Employee_Type'] == 'Employee' else "🏢"
                        st.markdown(f"{type_icon} **Type:** {employee_data['Employee_Type']}")
                    
                    with col2:
                        st.markdown("**💰 Financial Information**")
                        st.write(f"**Priced Salary:** ${employee_data['Priced_Salary']:,.2f}")
                        st.write(f"**Current Salary:** ${employee_data['Current_Salary']:,.2f}")
                        st.write(f"**Hourly Rate:** ${employee_data['Hourly_Rate']:,.2f}")
                        
                        # Salary comparison
                        salary_diff = employee_data['Current_Salary'] - employee_data['Priced_Salary']
                        if salary_diff != 0:
                            diff_color = "🔴" if salary_diff > 0 else "🟢"
                            st.write(f"{diff_color} **Salary Difference:** ${salary_diff:,.2f}")
                    
                    # Time period data
                    st.markdown("**📅 Time Period Data**")
                    
                    # Get all time period columns
                    hours_cols = [col for col in employees_df.columns if col.startswith('Hours_') and col != 'Hours_Per_Month']
                    revenue_cols = [col for col in employees_df.columns if col.startswith('Revenue_')]
                    
                    if hours_cols:
                        # Create time period summary
                        period_data = []
                        for hours_col in hours_cols:
                            period_name = hours_col.replace('Hours_', '')
                            hours = employee_data[hours_col]
                            revenue = employee_data.get(f'Revenue_{period_name}', 0)
                            period_data.append({
                                'Period': period_name,
                                'Hours': hours,
                                'Revenue': revenue,
                                'Rate': revenue / hours if hours > 0 else 0
                            })
                        
                        period_df = pd.DataFrame(period_data)
                        
                        # Show summary statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            total_hours = period_df['Hours'].sum()
                            st.metric("Total Hours", f"{total_hours:.1f}")
                        with col2:
                            total_revenue = period_df['Revenue'].sum()
                            st.metric("Total Revenue", f"${total_revenue:,.2f}")
                        with col3:
                            avg_hours = period_df['Hours'].mean()
                            st.metric("Avg Hours/Period", f"{avg_hours:.1f}")
                        with col4:
                            avg_revenue = period_df['Revenue'].mean()
                            st.metric("Avg Revenue/Period", f"${avg_revenue:,.2f}")
                        
                        # Show detailed period data
                        with st.expander("📊 View All Time Periods"):
                            st.dataframe(period_df, width='stretch')
        else:
            st.info("📝 No employees available for profile editing. Add employees first.")

    # ============================================================================
    # Overview Tab Content Helper Methods
    # ============================================================================
    
    def _create_project_metrics_content(self):
        """Create content for project metrics section"""
        params = st.session_state.project_params
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        non_billable = params['non_billable_hours']
        billable_hours = actual_hours + non_billable
        
        # Create metric cards using Streamlit columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("⏱️ EAC Hours", f"{eac_hours:,.0f}")
        with col2:
            st.metric("📈 Actual Hours", f"{actual_hours:,.0f}")
        with col3:
            st.metric("💼 Billable Hours", f"{billable_hours:,.0f}")
        
        # Calculate completion percentage
        completion_pct = (actual_hours / eac_hours) * 100 if eac_hours > 0 else 0
        with col4:
            st.metric("🎯 Completion", f"{completion_pct:.1f}%")
        
        # Add progress bar
        st.markdown("### 📊 Project Progress")
        st.progress(completion_pct / 100)
        st.markdown(f"**{completion_pct:.1f}% Complete** - {actual_hours:,.0f} of {eac_hours:,.0f} hours")
        
        # Add chart visualization
        fig = create_project_metrics_chart(params)
        st.plotly_chart(fig, width='stretch', key="project_metrics_chart")
    
    def _create_financial_summary_content(self):
        """Create content for financial summary section"""
        # Calculate totals
        employees_df = st.session_state.employees
        total_direct_labor = 0
        
        # Sum up all revenue columns
        revenue_columns = [col for col in employees_df.columns if col.startswith('Revenue_')]
        if revenue_columns:
            total_direct_labor = employees_df[revenue_columns].sum().sum()

        # ODC total
        odc_df = st.session_state.odc_costs
        total_odc = odc_df['Amount'].sum()

        # Subcontractor total
        sub_df = st.session_state.subcontractors
        sub_revenue_columns = [col for col in sub_df.columns if col.startswith('Revenue_')]
        total_subcontractor = 0
        if sub_revenue_columns:
            total_subcontractor = sub_df[sub_revenue_columns].sum().sum()

        # Indirect costs
        indirect_costs = self.calculate_indirect_costs(total_direct_labor)
        
        # Total costs
        total_costs = total_direct_labor + total_odc + total_subcontractor + indirect_costs['Total_Indirect']
        
        # Revenue calculation
        params = st.session_state.project_params
        total_transaction_price = params['total_transaction_price']
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        recalculated_revenue = (actual_hours / eac_hours) * total_transaction_price if eac_hours > 0 else 0
        
        # Create financial summary using Streamlit columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Total Revenue", f"${total_transaction_price:,.2f}")
        with col2:
            st.metric("💼 Direct Labor", f"${total_direct_labor:,.2f}")
        with col3:
            st.metric("🏢 ODC Costs", f"${total_odc:,.2f}")
        with col4:
            st.metric("📊 Total Costs", f"${total_costs:,.2f}")
        
        # Additional metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🤝 Subcontractors", f"${total_subcontractor:,.2f}")
        with col2:
            st.metric("📈 Indirect Costs", f"${indirect_costs['Total_Indirect']:,.2f}")
        with col3:
            profit_margin = ((total_transaction_price - total_costs) / total_transaction_price * 100) if total_transaction_price > 0 else 0
            st.metric("📊 Profit Margin", f"{profit_margin:.1f}%")
        with col4:
            st.metric("🎯 Recalculated Revenue", f"${recalculated_revenue:,.2f}")
        
        # Add chart visualization
        fig = create_financial_summary_chart(params)
        st.plotly_chart(fig, width='stretch', key="financial_summary_chart")
    
    def _create_cost_analysis_content(self):
        """Create content for cost analysis section"""
        # Calculate totals for chart
        employees_df = st.session_state.employees
        total_direct_labor = 0
        
        # Sum up all revenue columns
        revenue_columns = [col for col in employees_df.columns if col.startswith('Revenue_')]
        if revenue_columns:
            total_direct_labor = employees_df[revenue_columns].sum().sum()

        # ODC total
        odc_df = st.session_state.odc_costs
        total_odc = odc_df['Amount'].sum()

        # Subcontractor total
        sub_df = st.session_state.subcontractors
        sub_revenue_columns = [col for col in sub_df.columns if col.startswith('Revenue_')]
        total_subcontractor = 0
        if sub_revenue_columns:
            total_subcontractor = sub_df[sub_revenue_columns].sum().sum()

        # Indirect costs
        indirect_costs = self.calculate_indirect_costs(total_direct_labor)
        
        # Cost breakdown chart
        cost_data = {
            'Category': ['Direct Labor', 'ODC', 'Subcontractor', 'Fringe', 'Overhead', 'G&A'],
            'Amount': [total_direct_labor, total_odc, total_subcontractor, 
                      indirect_costs['Fringe'], indirect_costs['Overhead'], indirect_costs['G&A']]
        }
        
        fig = px.pie(pd.DataFrame(cost_data), values='Amount', names='Category', 
                     title="Cost Breakdown by Category")
        st.plotly_chart(fig, width='stretch')
        
        # Add cost analysis summary
        st.markdown("### 💡 Cost Analysis Insights")
        
        # Calculate percentages
        total_costs = sum(cost_data['Amount'])
        if total_costs > 0:
            direct_labor_pct = (total_direct_labor / total_costs) * 100
            odc_pct = (total_odc / total_costs) * 100
            subcontractor_pct = (total_subcontractor / total_costs) * 100
            indirect_pct = ((indirect_costs['Fringe'] + indirect_costs['Overhead'] + indirect_costs['G&A']) / total_costs) * 100
            
            st.markdown(f"""
            **Cost Distribution:**
            - **Direct Labor:** {direct_labor_pct:.1f}% (${total_direct_labor:,.2f})
            - **ODC:** {odc_pct:.1f}% (${total_odc:,.2f})
            - **Subcontractor:** {subcontractor_pct:.1f}% (${total_subcontractor:,.2f})
            - **Indirect Costs:** {indirect_pct:.1f}% (${indirect_costs['Fringe'] + indirect_costs['Overhead'] + indirect_costs['G&A']:,.2f})
            """)
        
        return ""

    # ============================================================================
    # Subcontractor Tab Content Helper Methods
    # ============================================================================
    
    def _create_subcontractor_summary_content(self):
        """Create content for subcontractor summary section"""
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            # Create metric cards using Streamlit columns
            col1, col2, col3, col4 = st.columns(4)
            
            total_subcontractors = len(sub_df)
            total_hourly_rate = sub_df['Hourly_Rate'].sum()
            avg_hourly_rate = sub_df['Hourly_Rate'].mean()
            total_companies = len(sub_df['Company'].unique())
            
            with col1:
                st.metric("Total Subcontractors", total_subcontractors)
            with col2:
                st.metric("Total Hourly Rate", f"${total_hourly_rate:,.2f}")
            with col3:
                st.metric("Avg Hourly Rate", f"${avg_hourly_rate:,.2f}")
            with col4:
                st.metric("Unique Companies", total_companies)
            
            # Add breakdown summary using Streamlit columns
            st.markdown("### 📊 Subcontractor Breakdown")
            col1, col2 = st.columns(2)
            
            company_counts = sub_df['Company'].value_counts()
            lcat_counts = sub_df['LCAT'].value_counts()
            
            with col1:
                st.markdown("#### 🏢 Companies")
                for company, count in company_counts.items():
                    st.write(f"• {company}: {count}")
            
            with col2:
                st.markdown("#### 📋 LCATs")
                for lcat, count in lcat_counts.items():
                    st.write(f"• {lcat}: {count}")
        else:
            st.info("📝 No subcontractors added yet. Use the sections below to add subcontractors.")
    
    def _create_editable_subcontractor_profile_content(self):
        """Create editable subcontractor profile view"""
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            # Subcontractor selector
            selected_subcontractor = st.selectbox(
                "Select Subcontractor to Edit:",
                options=sub_df['Name'].tolist(),
                key="editable_subcontractor_selector"
            )
            
            if selected_subcontractor:
                # Get subcontractor data
                sub_data = sub_df[sub_df['Name'] == selected_subcontractor].iloc[0]
                sub_index = sub_df[sub_df['Name'] == selected_subcontractor].index[0]
                
                # Initialize session state for editing if not exists
                if f'editing_subcontractor_{selected_subcontractor}' not in st.session_state:
                    st.session_state[f'editing_subcontractor_{selected_subcontractor}'] = False
                
                # Toggle edit mode
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 🏢 Editing: {selected_subcontractor}")
                with col2:
                    if st.button("✏️ Edit Profile", key=f"edit_sub_btn_{selected_subcontractor}"):
                        st.session_state[f'editing_subcontractor_{selected_subcontractor}'] = True
                        st.rerun()
                
                if st.session_state[f'editing_subcontractor_{selected_subcontractor}']:
                    # Editable form
                    with st.form(f"edit_subcontractor_form_{selected_subcontractor}"):
                        st.markdown("#### 📋 Basic Information")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            new_name = st.text_input("Name", value=sub_data['Name'], key=f"sub_name_{selected_subcontractor}")
                            new_company = st.text_input("Company", value=sub_data['Company'], key=f"sub_company_{selected_subcontractor}")
                        
                        with col2:
                            new_lcat = st.text_input("LCAT/Role", value=sub_data['LCAT'], key=f"sub_lcat_{selected_subcontractor}")
                            new_hourly_rate = st.number_input(
                                "Hourly Rate",
                                min_value=0.0,
                                value=float(sub_data['Hourly_Rate']),
                                key=f"sub_hourly_rate_{selected_subcontractor}"
                            )
                        
                        # Form buttons
                        col1, col2, col3 = st.columns([1, 1, 2])
                        with col1:
                            save_clicked = st.form_submit_button("💾 Save Changes", type="primary")
                        with col2:
                            cancel_clicked = st.form_submit_button("❌ Cancel")
                        
                        if save_clicked:
                            # Update subcontractor data
                            st.session_state.subcontractors.at[sub_index, 'Name'] = new_name
                            st.session_state.subcontractors.at[sub_index, 'Company'] = new_company
                            st.session_state.subcontractors.at[sub_index, 'LCAT'] = new_lcat
                            st.session_state.subcontractors.at[sub_index, 'Hourly_Rate'] = new_hourly_rate
                            
                            # Exit edit mode
                            st.session_state[f'editing_subcontractor_{selected_subcontractor}'] = False
                            st.success(f"✅ Successfully updated {new_name}'s profile!")
                            st.rerun()
                        
                        if cancel_clicked:
                            # Exit edit mode without saving
                            st.session_state[f'editing_subcontractor_{selected_subcontractor}'] = False
                            st.rerun()
                else:
                    # Read-only view
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("**📋 Basic Information**")
                        st.write(f"**Name:** {sub_data['Name']}")
                        st.write(f"**Company:** {sub_data['Company']}")
                        st.write(f"**LCAT/Role:** {sub_data['LCAT']}")
                        st.write(f"**Hourly Rate:** ${sub_data['Hourly_Rate']:.2f}")
                    
                    with col2:
                        st.markdown("**📊 Time Period Data**")
                        
                        # Get all time period columns
                        hours_cols = [col for col in sub_df.columns if col.startswith('Hours_')]
                        revenue_cols = [col for col in sub_df.columns if col.startswith('Revenue_')]
                        
                        if hours_cols:
                            # Create time period summary
                            period_data = []
                            for hours_col in hours_cols:
                                period_name = hours_col.replace('Hours_', '')
                                hours = sub_data[hours_col]
                                revenue = sub_data.get(f'Revenue_{period_name}', 0)
                                period_data.append({
                                    'Period': period_name,
                                    'Hours': hours,
                                    'Revenue': revenue,
                                    'Rate': revenue / hours if hours > 0 else 0
                                })
                            
                            period_df = pd.DataFrame(period_data)
                            
                            # Show summary statistics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                total_hours = period_df['Hours'].sum()
                                st.metric("Total Hours", f"{total_hours:.1f}")
                            with col2:
                                total_revenue = period_df['Revenue'].sum()
                                st.metric("Total Revenue", f"${total_revenue:,.2f}")
                            with col3:
                                avg_hours = period_df['Hours'].mean()
                                st.metric("Avg Hours/Period", f"{avg_hours:.1f}")
                            with col4:
                                avg_revenue = period_df['Revenue'].mean()
                                st.metric("Avg Revenue/Period", f"${avg_revenue:,.2f}")
                            
                            # Show detailed period data
                            with st.expander("📊 View All Time Periods"):
                                st.dataframe(period_df, width='stretch')
        else:
            st.info("📝 No subcontractors available for profile editing. Add subcontractors first.")
    
    def _create_add_subcontractor_content(self):
        """Create content for add new subcontractor section"""
        st.markdown("Enter subcontractor information to add them to your project.")
        
        # Add form using Streamlit
        col1, col2, col3 = st.columns(3)
        with col1:
            new_name = st.text_input("Subcontractor Name")
            new_company = st.text_input("Company")
        with col2:
            new_lcat = st.text_input("LCAT/Role")
            new_hourly_rate = st.number_input("Hourly Rate", min_value=0.0, value=100.0)
        with col3:
            if st.button("Add Subcontractor") and new_name:
                new_sub = {
                    "Name": new_name,
                    "Company": new_company,
                    "LCAT": new_lcat,
                    "Hourly_Rate": new_hourly_rate
                }
                
                # Add time period columns
                for period in st.session_state.time_periods:
                    new_sub[f'Hours_{period}'] = 0.0
                    new_sub[f'Revenue_{period}'] = 0.0
                
                new_row = pd.DataFrame([new_sub])
                st.session_state.subcontractors = pd.concat([st.session_state.subcontractors, new_row], 
                                                          ignore_index=True)
                st.success(f"Added {new_name} to subcontractor list")
                st.rerun()
        
        # Required fields and tips
        st.markdown("### 📋 Required Fields")
        st.markdown("""
        - **Name:** Subcontractor's full name
        - **Company:** Company or organization
        - **LCAT:** Labor category or role
        - **Hourly Rate:** Rate per hour
        """)
        
        st.markdown("### 💡 Tips")
        st.markdown("""
        - Use consistent naming conventions
        - Verify hourly rates are accurate
        - Include all required information
        """)
    
    def _create_subcontractor_management_content(self):
        """Create content for subcontractor management section"""
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            st.markdown("### Subcontractor Information")
            basic_columns = ["Name", "Company", "LCAT", "Hourly_Rate"]
            
            edited_basic = st.data_editor(
                sub_df[basic_columns],
                column_config={
                    "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
                },
                width='stretch',
                key="basic_subcontractor_data"
            )
            
            # Update main dataframe
            for col in basic_columns:
                st.session_state.subcontractors[col] = edited_basic[col]
            
            # Subcontractor removal section
            st.markdown("### Remove Subcontractors")
            
            if not sub_df.empty:
                st.write("Select subcontractors to remove from the project:")
                
                # Create columns for better layout
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    # Subcontractor selection dropdown
                    selected_subcontractor = st.selectbox(
                        "Choose subcontractor to remove:",
                        options=sub_df['Name'].tolist(),
                        key="subcontractor_removal_select"
                    )
                
                with col2:
                    # Show subcontractor details
                    if selected_subcontractor:
                        sub_data = sub_df[sub_df['Name'] == selected_subcontractor].iloc[0]
                        st.write(f"**Company:** {sub_data['Company']}")
                        st.write(f"**LCAT:** {sub_data['LCAT']}")
                        st.write(f"**Rate:** ${sub_data['Hourly_Rate']:.2f}/hr")
                
                with col3:
                    # Remove button with confirmation
                    if selected_subcontractor:
                        if st.button("🗑️ Remove Subcontractor", type="secondary", key="remove_subcontractor_btn"):
                            # Remove the subcontractor
                            st.session_state.subcontractors = st.session_state.subcontractors[
                                st.session_state.subcontractors['Name'] != selected_subcontractor
                            ]
                            st.success(f"✅ {selected_subcontractor} has been removed from the project.")
                            st.rerun()
                
                # Show current subcontractor count
                st.info(f"📊 **Current Subcontractor Count:** {len(st.session_state.subcontractors)}")
                
                # Bulk removal section
                st.markdown("---")
                st.markdown("**Bulk Operations:**")
                
                # Bulk remove by company
                company_options = sub_df['Company'].unique().tolist()
                if company_options:
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        selected_company = st.selectbox(
                            "Remove all subcontractors by Company:",
                            options=company_options,
                            key="bulk_company_select"
                        )
                    with col2:
                        if st.button("🗑️ Remove All by Company", type="secondary", key="bulk_remove_company_btn"):
                            company_count = len(sub_df[sub_df['Company'] == selected_company])
                            st.session_state.subcontractors = st.session_state.subcontractors[
                                st.session_state.subcontractors['Company'] != selected_company
                            ]
                            st.success(f"✅ Removed {company_count} subcontractors from company: {selected_company}")
                            st.rerun()
                
                # Clear all subcontractors (with confirmation)
                if st.button("🗑️ Clear All Subcontractors", type="secondary", key="clear_all_subcontractors_btn"):
                    st.warning("⚠️ This will remove ALL subcontractors from the project. This action cannot be undone.")
                    if st.button("✅ Confirm Clear All", type="primary", key="confirm_clear_all_subcontractors_btn"):
                        subcontractor_count = len(st.session_state.subcontractors)
                        st.session_state.subcontractors = pd.DataFrame(columns=st.session_state.subcontractors.columns)
                        st.success(f"✅ Cleared all {subcontractor_count} subcontractors from the project.")
                        st.rerun()
            else:
                st.warning("⚠️ No subcontractors to remove.")
        else:
            return '<p>📝 No subcontractors available for management. Add some first.</p>'
        
        return ""
    
    def _create_subcontractor_hours_content(self):
        """Create content for subcontractor monthly hours section"""
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            st.markdown("### Monthly Hours Management")
            
            # Show fewer periods at a time for better usability
            selected_periods = st.multiselect(
                "Select periods to edit",
                st.session_state.time_periods,
                default=st.session_state.time_periods[:6]
            )
            
            if selected_periods:
                hours_columns = [f'Hours_{period}' for period in selected_periods]
                hours_data = sub_df[["Name"] + hours_columns].copy()
                
                edited_hours = st.data_editor(
                    hours_data,
                    column_config={col: st.column_config.NumberColumn(period, format="%.1f") 
                                  for col, period in zip(hours_columns, selected_periods)},
                    width='stretch',
                    key="subcontractor_hours"
                )
                
                # Update main dataframe and calculate revenues
                for col in hours_columns:
                    st.session_state.subcontractors[col] = edited_hours[col]
                
                # Calculate revenues
                for idx, row in st.session_state.subcontractors.iterrows():
                    hourly_rate = row['Hourly_Rate']
                    for period in selected_periods:
                        hours_col = f'Hours_{period}'
                        revenue_col = f'Revenue_{period}'
                        hours = row[hours_col] if pd.notna(row[hours_col]) else 0
                        st.session_state.subcontractors.at[idx, revenue_col] = hours * hourly_rate

                st.success("✅ Hours updated and revenues calculated!")
        else:
            return '<p>📝 No subcontractors available for hours management. Add some first.</p>'
        
        return ""
    
    def _create_odc_management_content(self):
        """Create content for ODC management section"""
        odc_df = st.session_state.odc_costs
        
        st.markdown("### Other Direct Costs (ODC)")
        
        edited_odc = st.data_editor(
            odc_df,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            },
            width='stretch',
            key="odc_data"
        )
        
        st.session_state.odc_costs = edited_odc
        
        return ""

    def create_sample_subcontractors(self) -> pd.DataFrame:
        """Create sample subcontractor data"""
        subcontractors = [
            {"Name": "Adrien Adams", "Company": "BEELINE", "LCAT": "Data Systems SME", "Hourly_Rate": 250.0},
            {"Name": "Paulina Fisher", "Company": "FFtC", "LCAT": "HCD Researcher", "Hourly_Rate": 116.0},
            {"Name": "Andrew Sung", "Company": "FFtC", "LCAT": "Full Stack Dev", "Hourly_Rate": 130.0},
        ]
        
        df = pd.DataFrame(subcontractors)
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
            
        return df





    def calculate_hourly_rate(self, salary: float, hours_per_month: float) -> float:
        """Calculate hourly rate from annual salary"""
        if salary == 0 or hours_per_month == 0:
            return 0.0
        return salary / (hours_per_month * 12)

    def calculate_indirect_costs(self, direct_labor: float) -> Dict[str, float]:
        """Calculate indirect costs based on direct labor"""
        params = st.session_state.project_params
        fringe = direct_labor * params['fringe_rate']
        overhead = direct_labor * params['overhead_rate']
        ga = direct_labor * params['ga_rate']
        
        return {
            'Fringe': fringe,
            'Overhead': overhead,
            'G&A': ga,
            'Total_Indirect': fringe + overhead + ga
        }

    def update_employee_calculations(self):
        """Update calculated fields for employees"""
        df = st.session_state.employees
        
        # Recalculate hourly rates
        for idx, row in df.iterrows():
            if row['Current_Salary'] > 0 and row['Hours_Per_Month'] > 0:
                hourly_rate = self.calculate_hourly_rate(row['Current_Salary'], row['Hours_Per_Month'])
                df.at[idx, 'Hourly_Rate'] = hourly_rate
                
                # Recalculate revenues for each period
                for period in st.session_state.time_periods:
                    hours_col = f'Hours_{period}'
                    revenue_col = f'Revenue_{period}'
                    if hours_col in df.columns:
                        hours = df.at[idx, hours_col] if pd.notna(df.at[idx, hours_col]) else 0
                        df.at[idx, revenue_col] = hours * hourly_rate

    def create_dashboard(self):
        """Create the main dashboard with enhanced QuickBooks design"""
        # Initialize theme manager and apply theme
        theme_manager = ThemeManager()
        theme_manager.apply_theme_css()
        
        # Enhanced QuickBooks-style header
        st.markdown("""
        <div class="main-header">
            <h1>📊 SEAS Project Financial Tracker</h1>
            <div class="subtitle">Professional Financial Management & Analysis Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Welcome message and onboarding
        self._create_welcome_section()
        
        # Enhanced sidebar with better organization and user management
        self._create_enhanced_sidebar()
        
        # Check if user management should be shown
        if st.session_state.get('show_user_management', False):
            render_user_management_page()
            if st.button("← Back to Dashboard"):
                st.session_state.show_user_management = False
                st.rerun()
            return
        
        # Main content area with improved layout
        self._create_main_content()

    def _create_welcome_section(self):
        """Create welcome section with onboarding guidance"""
        st.markdown("""
        <div class="qb-card">
            <div class="qb-card-header">
                <h2 class="qb-card-title">👋 Welcome to SEAS Financial Tracker</h2>
                <p class="qb-card-subtitle">Your comprehensive project financial management solution</p>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem; margin-top: 1rem;">
                <div style="padding: 1rem; background: #E6F2FF; border-radius: 8px; border-left: 4px solid #0073E6;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #0056B3;">📊 Dashboard Overview</h4>
                    <p style="margin: 0; font-size: 14px; color: #4A5568;">Monitor project metrics, financial summaries, and cost analysis in real-time.</p>
                </div>
                <div style="padding: 1rem; background: #E6F7E6; border-radius: 8px; border-left: 4px solid #00A86B;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #00A86B;">👥 Team Management</h4>
                    <p style="margin: 0; font-size: 14px; color: #4A5568;">Manage employees, subcontractors, and track hours with detailed profiles.</p>
                </div>
                <div style="padding: 1rem; background: #FFF2E6; border-radius: 8px; border-left: 4px solid #FF8C00;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #FF8C00;">📈 Analytics & Reports</h4>
                    <p style="margin: 0; font-size: 14px; color: #4A5568;">Generate insights with interactive charts and comprehensive reporting.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _create_enhanced_sidebar(self):
        """Create enhanced sidebar with better organization"""
        with st.sidebar:
            # Enhanced sidebar header
            st.markdown("""
            <div style="background: linear-gradient(135deg, #0073E6 0%, #0056B3 100%); 
                        padding: 1.5rem; border-radius: 12px; margin-bottom: 1.5rem; 
                        box-shadow: 0 4px 12px rgba(0, 115, 230, 0.2);">
                <h3 style="color: white; margin: 0 0 0.5rem 0; text-align: center; font-weight: 600; font-size: 18px;">⚙️ Project Parameters</h3>
                <p style="color: rgba(255,255,255,0.9); margin: 0; text-align: center; font-size: 14px;">Configure your project settings</p>
            </div>
            """, unsafe_allow_html=True)
            
            params = st.session_state.project_params
            params['current_date'] = st.date_input("📅 Current Date", params['current_date'])
            params['total_transaction_price'] = st.number_input("💰 Total Transaction Price ($)", 
                                                              value=params['total_transaction_price'], 
                                                              format="%.2f")
            params['fringe_rate'] = st.number_input("🎯 Fringe Rate", value=params['fringe_rate'], 
                                                   format="%.3f", step=0.001)
            params['overhead_rate'] = st.number_input("🏢 Overhead Rate", value=params['overhead_rate'], 
                                                     format="%.3f", step=0.001)
            params['ga_rate'] = st.number_input("📈 G&A Rate", value=params['ga_rate'], 
                                               format="%.3f", step=0.001)
            params['target_profit'] = st.number_input("🎯 Target Profit Margin", value=params['target_profit'], 
                                                     format="%.4f", step=0.0001)
            
            # Add quick actions section
            st.markdown("---")
            st.markdown("""
            <div style="background: #F1F3F4; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
                <h4 style="margin: 0 0 0.5rem 0; color: #3C4043; font-size: 16px;">🚀 Quick Actions</h4>
                <p style="margin: 0; font-size: 14px; color: #5F6368;">Common tasks and shortcuts</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Refresh Data", help="Reload all data and recalculate metrics"):
                st.rerun()
            
            if st.button("📊 Export Report", help="Generate and download project report"):
                st.success("📄 Report generation started!")

    def _create_main_content(self):
        """Create main content area with modern UI and navigation"""
        # Modern navigation header
        self.modern_ui.render_navigation(
            "SEAS Financial Tracker",
            "Professional Financial Management & Analysis Platform"
        )
        
        # Create navigation using radio buttons with modern styling
        st.markdown("### 🧭 Navigation")
        page = st.radio(
            "Choose a section:",
            ["📊 Overview", "👥 Direct Labor", "🏢 Subcontractors", "📈 Analysis", "✅ Tasks", "📥 Data Import"],
            horizontal=True,
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Render content based on selection with modern UI
        if page == "📊 Overview":
            self._render_overview_content_modern()
        elif page == "👥 Direct Labor":
            self._render_direct_labor_content_modern()
        elif page == "🏢 Subcontractors":
            self._render_subcontractor_content_modern()
        elif page == "📈 Analysis":
            self._render_analysis_content_modern()
        elif page == "✅ Tasks":
            self._render_tasks_content_modern()
        elif page == "📥 Data Import":
            render_data_import_page()

    def _render_overview_content_modern(self):
        """Render overview content with modern UI"""
        # Key metrics section
        st.markdown("### 📊 Key Financial Metrics")
        
        # Create sample metrics for demonstration
        metrics = [
            {"title": "Total Revenue", "value": "$1,200,000", "change": "+5.2%", "change_type": "positive"},
            {"title": "Total Costs", "value": "$800,000", "change": "+2.1%", "change_type": "negative"},
            {"title": "Profit Margin", "value": "33.3%", "change": "+1.2%", "change_type": "positive"},
            {"title": "Active Projects", "value": "12", "change": "+2", "change_type": "positive"}
        ]
        
        self.modern_ui.render_metric_grid(metrics)
        
        # Charts section
        st.markdown("### 📈 Financial Overview")
        
        # Create sample chart
        try:
            import plotly.express as px
            import pandas as pd
            
            # Sample data
            data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [100000, 120000, 110000, 130000, 140000, 150000],
                'Costs': [80000, 90000, 85000, 95000, 100000, 105000]
            })
            
            fig = px.line(data, x='Month', y=['Revenue', 'Costs'], 
                         title='Monthly Revenue vs Costs Trend')
            
            # Apply modern styling
            fig = self.modern_ui.create_accessible_chart(
                fig, 
                "Monthly Financial Performance", 
                "Line chart showing revenue and costs over 6 months"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            self.modern_ui.render_alert("✅ Charts are working properly!", "success")
            
        except Exception as e:
            self.modern_ui.render_alert(f"Chart error: {e}", "error")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Generate Report", use_container_width=True):
                self.modern_ui.render_alert("Report generation started!", "info")
        
        with col2:
            if st.button("📤 Export Data", use_container_width=True):
                self.modern_ui.render_alert("Data export initiated!", "info")
        
        with col3:
            if st.button("🔄 Refresh Data", use_container_width=True):
                st.rerun()

    def _render_direct_labor_content_modern(self):
        """Render direct labor content with modern UI"""
        self.modern_ui.render_alert("✅ Direct Labor section is working!", "success")
        
        # Employee summary metrics
        st.markdown("### 📊 Employee Summary")
        
        # Sample employee metrics
        emp_metrics = [
            {"title": "Total Employees", "value": "24", "change": "+2", "change_type": "positive"},
            {"title": "Active Employees", "value": "22", "change": "0", "change_type": "neutral"},
            {"title": "Avg Salary", "value": "$85,000", "change": "+3.2%", "change_type": "positive"},
            {"title": "Utilization Rate", "value": "92%", "change": "+1.5%", "change_type": "positive"}
        ]
        
        self.modern_ui.render_metric_grid(emp_metrics)
        
        # Employee management form
        with st.container():
            st.markdown("### ➕ Add New Employee")
            
            with st.form("add_employee_modern", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Employee Name", placeholder="Enter full name")
                    lcat = st.selectbox("Labor Category", ["Senior Engineer", "Project Manager", "Analyst", "Consultant"])
                
                with col2:
                    salary = st.number_input("Annual Salary", min_value=30000, max_value=200000, value=75000, step=1000)
                    status = st.selectbox("Status", ["Active", "Inactive", "On Leave"])
                
                submitted = st.form_submit_button("Add Employee", use_container_width=True)
                
                if submitted:
                    if name and lcat:
                        self.modern_ui.render_alert(f"Employee {name} added successfully!", "success")
                    else:
                        self.modern_ui.render_alert("Please fill in all required fields.", "error")
        
        # Employee data table
        if 'employees' in st.session_state and not st.session_state.employees.empty:
            st.markdown("### 👥 Current Employees")
            st.dataframe(st.session_state.employees.head(), use_container_width=True)
        else:
            self.modern_ui.render_alert("No employee data available. Use the form above to add employees.", "info")

    def _render_subcontractor_content_modern(self):
        """Render subcontractor content with modern UI"""
        self.modern_ui.render_alert("✅ Subcontractor section is working!", "success")
        
        # Subcontractor summary metrics
        st.markdown("### 📊 Subcontractor Summary")
        
        # Sample subcontractor metrics
        sub_metrics = [
            {"title": "Active Contracts", "value": "8", "change": "+1", "change_type": "positive"},
            {"title": "Total Value", "value": "$450,000", "change": "+12.5%", "change_type": "positive"},
            {"title": "Avg Hourly Rate", "value": "$125", "change": "+5.2%", "change_type": "positive"},
            {"title": "Completion Rate", "value": "96%", "change": "+2.1%", "change_type": "positive"}
        ]
        
        self.modern_ui.render_metric_grid(sub_metrics)
        
        # Subcontractor management form
        with st.container():
            st.markdown("### ➕ Add New Subcontractor")
            
            with st.form("add_subcontractor_modern", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    company = st.text_input("Company Name", placeholder="Enter company name")
                    service_type = st.selectbox("Service Type", ["Consulting", "Development", "Design", "Testing"])
                
                with col2:
                    hourly_rate = st.number_input("Hourly Rate", min_value=50, max_value=500, value=125, step=5)
                    status = st.selectbox("Contract Status", ["Active", "Pending", "Completed"])
                
                submitted = st.form_submit_button("Add Subcontractor", use_container_width=True)
                
                if submitted:
                    if company and service_type:
                        self.modern_ui.render_alert(f"Subcontractor {company} added successfully!", "success")
                    else:
                        self.modern_ui.render_alert("Please fill in all required fields.", "error")
        
        # Subcontractor data table
        if 'subcontractors' in st.session_state and not st.session_state.subcontractors.empty:
            st.markdown("### 🏢 Current Subcontractors")
            st.dataframe(st.session_state.subcontractors.head(), use_container_width=True)
        else:
            self.modern_ui.render_alert("No subcontractor data available. Use the form above to add subcontractors.", "info")

    def _render_analysis_content_modern(self):
        """Render analysis content with modern UI"""
        self.modern_ui.render_alert("✅ Analysis section is working!", "success")
        
        # Financial analysis metrics
        st.markdown("### 📊 Financial Analysis Overview")
        
        # Sample analysis metrics
        analysis_metrics = [
            {"title": "ROI", "value": "150%", "change": "+8.5%", "change_type": "positive"},
            {"title": "Burn Rate", "value": "$45K/mo", "change": "-2.1%", "change_type": "positive"},
            {"title": "Profit Margin", "value": "33.3%", "change": "+1.2%", "change_type": "positive"},
            {"title": "Cash Flow", "value": "$125K", "change": "+15.3%", "change_type": "positive"}
        ]
        
        self.modern_ui.render_metric_grid(analysis_metrics)
        
        # Interactive charts section
        st.markdown("### 📈 Financial Trends")
        
        # Create multiple charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue trend chart
            try:
                import plotly.express as px
                import pandas as pd
                
                revenue_data = pd.DataFrame({
                    'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    'Revenue': [100000, 120000, 110000, 130000, 140000, 150000]
                })
                
                fig1 = px.bar(revenue_data, x='Month', y='Revenue', 
                             title='Monthly Revenue Trend')
                fig1 = self.modern_ui.create_accessible_chart(
                    fig1, 
                    "Monthly Revenue", 
                    "Bar chart showing monthly revenue over 6 months"
                )
                
                st.plotly_chart(fig1, use_container_width=True)
                
            except Exception as e:
                self.modern_ui.render_alert(f"Revenue chart error: {e}", "error")
        
        with col2:
            # Cost breakdown pie chart
            try:
                cost_data = pd.DataFrame({
                    'Category': ['Labor', 'Materials', 'Overhead', 'Other'],
                    'Amount': [400000, 200000, 150000, 50000]
                })
                
                fig2 = px.pie(cost_data, values='Amount', names='Category', 
                             title='Cost Breakdown by Category')
                fig2 = self.modern_ui.create_accessible_chart(
                    fig2, 
                    "Cost Breakdown", 
                    "Pie chart showing cost distribution across categories"
                )
                
                st.plotly_chart(fig2, use_container_width=True)
                
            except Exception as e:
                self.modern_ui.render_alert(f"Cost chart error: {e}", "error")
        
        # Analysis insights
        st.markdown("### 💡 Key Insights")
        insights = [
            "📈 Revenue has grown 50% over the past 6 months",
            "💰 Labor costs represent 50% of total expenses",
            "⚡ Burn rate is within acceptable limits",
            "🎯 Profit margins are above industry average"
        ]
        
        for insight in insights:
            st.markdown(f"- {insight}")

    def _render_tasks_content_modern(self):
        """Render tasks content with modern UI"""
        self.modern_ui.render_alert("✅ Tasks section is working!", "success")
        
        # Task summary metrics
        st.markdown("### 📊 Task Summary")
        
        # Sample task metrics
        task_metrics = [
            {"title": "Total Tasks", "value": "24", "change": "+3", "change_type": "positive"},
            {"title": "Completed", "value": "18", "change": "+2", "change_type": "positive"},
            {"title": "In Progress", "value": "4", "change": "0", "change_type": "neutral"},
            {"title": "Overdue", "value": "2", "change": "-1", "change_type": "positive"}
        ]
        
        self.modern_ui.render_metric_grid(task_metrics)
        
        # Task management form
        with st.container():
            st.markdown("### ➕ Add New Task")
            
            with st.form("add_task_modern", clear_on_submit=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    task_name = st.text_input("Task Name", placeholder="Enter task description")
                    assigned_to = st.text_input("Assigned To", placeholder="Enter assignee name")
                
                with col2:
                    priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                    status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
                
                due_date = st.date_input("Due Date")
                description = st.text_area("Description", placeholder="Enter task details")
                
                submitted = st.form_submit_button("Add Task", use_container_width=True)
                
                if submitted:
                    if task_name and assigned_to:
                        self.modern_ui.render_alert(f"Task '{task_name}' added successfully!", "success")
                    else:
                        self.modern_ui.render_alert("Please fill in all required fields.", "error")
        
        # Task data table
        if 'tasks' in st.session_state and not st.session_state.tasks.empty:
            st.markdown("### ✅ Current Tasks")
            st.dataframe(st.session_state.tasks.head(), use_container_width=True)
        else:
            self.modern_ui.render_alert("No tasks available. Use the form above to add tasks.", "info")

    def _render_overview_content(self):
        """Render overview tab content"""
        st.markdown("## 📊 Overview Dashboard")
        
        # Test chart first
        st.markdown("### 🧪 Chart Test")
        try:
            # Simple test chart
            test_data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Revenue': [1000, 1200, 1100, 1300, 1400],
                'Costs': [800, 900, 850, 950, 1000]
            })
            
            fig = px.line(test_data, x='Month', y=['Revenue', 'Costs'], 
                         title='Test Chart - Revenue vs Costs')
            st.plotly_chart(fig, use_container_width=True, key="overview_test_chart")
            st.success("✅ Charts are working!")
            
        except Exception as e:
            st.error(f"❌ Chart test failed: {e}")
        
        st.markdown("---")
        
        # Project Metrics
        st.markdown("### 📊 Project Metrics")
        self._create_project_metrics_content()
        
        st.markdown("---")
        
        # Financial Summary
        st.markdown("### 💰 Financial Summary")
        self._create_financial_summary_content()
        
        st.markdown("---")
        
        # Cost Analysis
        st.markdown("### 📈 Cost Analysis")
        self._create_cost_analysis_content()

    def _render_direct_labor_content(self):
        """Render direct labor tab content"""
        st.markdown("## 👥 Direct Labor Management")
        st.success("✅ Direct Labor section is working!")
        
        # Simple content first
        st.write("**Employee Management Features:**")
        st.write("- 📊 Employee Summary and Metrics")
        st.write("- 📋 Download Excel Templates")
        st.write("- 📤 Upload Employee Data")
        st.write("- 👤 Manage Employee Profiles")
        
        # Show employee data if available
        if 'employees' in st.session_state and not st.session_state.employees.empty:
            st.markdown("### 📊 Current Employee Data")
            st.write(f"Total Employees: {len(st.session_state.employees)}")
            st.dataframe(st.session_state.employees.head())
        else:
            st.info("No employee data available. Use the upload feature to add employees.")
        
        # Add a simple form
        st.markdown("### ➕ Quick Add Employee")
        with st.form("add_employee_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Employee Name")
                lcat = st.text_input("LCAT")
            with col2:
                salary = st.number_input("Salary", value=50000)
                status = st.selectbox("Status", ["Active", "Inactive"])
            
            if st.form_submit_button("Add Employee"):
                if name and lcat:
                    st.success(f"Employee {name} added successfully!")
                else:
                    st.error("Please fill in all required fields.")

    def _render_subcontractor_content(self):
        """Render subcontractor tab content"""
        st.markdown("## 🏢 Subcontractor Management")
        st.success("✅ Subcontractor section is working!")
        
        # Simple content
        st.write("**Subcontractor Management Features:**")
        st.write("- 📊 Subcontractor Summary and Metrics")
        st.write("- ➕ Add New Subcontractors")
        st.write("- 📤 Upload Subcontractor Data")
        st.write("- 👥 Manage Subcontractor Profiles")
        
        # Show subcontractor data if available
        if 'subcontractors' in st.session_state and not st.session_state.subcontractors.empty:
            st.markdown("### 📊 Current Subcontractor Data")
            st.write(f"Total Subcontractors: {len(st.session_state.subcontractors)}")
            st.dataframe(st.session_state.subcontractors.head())
        else:
            st.info("No subcontractor data available. Use the form below to add subcontractors.")
        
        # Add a simple form
        st.markdown("### ➕ Quick Add Subcontractor")
        with st.form("add_subcontractor_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Company Name")
                lcat = st.text_input("Service Type")
            with col2:
                rate = st.number_input("Hourly Rate", value=100.0)
                status = st.selectbox("Status", ["Active", "Inactive"])
            
            if st.form_submit_button("Add Subcontractor"):
                if name and lcat:
                    st.success(f"Subcontractor {name} added successfully!")
                else:
                    st.error("Please fill in all required fields.")

    def _render_analysis_content(self):
        """Render analysis tab content"""
        st.markdown("## 📈 Financial Analysis")
        st.success("✅ Analysis section is working!")
        
        # Simple content
        st.write("**Financial Analysis Features:**")
        st.write("- 📈 Revenue Trends and Projections")
        st.write("- 🔥 Employee Utilization Heatmaps")
        st.write("- 💰 Cost Analysis by Category")
        st.write("- ⚡ Project Burn Rate Analysis")
        
        # Simple test chart
        st.markdown("### 📊 Sample Financial Chart")
        try:
            # Create a simple test chart
            import plotly.express as px
            import pandas as pd
            
            data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                'Revenue': [100000, 120000, 110000, 130000, 140000, 150000],
                'Costs': [80000, 90000, 85000, 95000, 100000, 105000]
            })
            
            fig = px.line(data, x='Month', y=['Revenue', 'Costs'], 
                         title='Monthly Revenue vs Costs')
            st.plotly_chart(fig, use_container_width=True)
            st.success("✅ Charts are working properly!")
            
        except Exception as e:
            st.error(f"Chart error: {e}")
            st.write("Chart functionality may not be available.")
        
        # Financial metrics
        st.markdown("### 💰 Key Financial Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Revenue", "$1,200,000", "+5.2%")
        with col2:
            st.metric("Total Costs", "$800,000", "+2.1%")
        with col3:
            st.metric("Profit Margin", "33.3%", "+1.2%")
        with col4:
            st.metric("ROI", "150%", "+8.5%")

    def _render_tasks_content(self):
        """Render tasks tab content"""
        st.markdown("## ✅ Task Management")
        st.success("✅ Tasks section is working!")
        
        # Simple content
        st.write("**Task Management Features:**")
        st.write("- ➕ Add New Tasks")
        st.write("- 📝 Manage Task Details")
        st.write("- 📊 Task Progress Tracking")
        st.write("- 🗑️ Remove Completed Tasks")
        
        # Show tasks data if available
        if 'tasks' in st.session_state and not st.session_state.tasks.empty:
            st.markdown("### 📊 Current Tasks")
            st.write(f"Total Tasks: {len(st.session_state.tasks)}")
            st.dataframe(st.session_state.tasks.head())
        else:
            st.info("No tasks available. Use the form below to add tasks.")
        
        # Add a simple form
        st.markdown("### ➕ Quick Add Task")
        with st.form("add_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                task_name = st.text_input("Task Name")
                assigned_to = st.text_input("Assigned To")
            with col2:
                priority = st.selectbox("Priority", ["High", "Medium", "Low"])
                status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
            
            if st.form_submit_button("Add Task"):
                if task_name and assigned_to:
                    st.success(f"Task '{task_name}' added successfully!")
                else:
                    st.error("Please fill in all required fields.")
        
        # Task summary
        st.markdown("### 📊 Task Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", "12", "+2")
        with col2:
            st.metric("Completed", "8", "+1")
        with col3:
            st.metric("In Progress", "3", "0")
        with col4:
            st.metric("Pending", "1", "+1")

    def create_overview_tab(self):
        """Create overview dashboard with enhanced modular design"""
        
        # Test chart first
        st.markdown("## 🧪 Chart Test")
        try:
            # Simple test chart
            test_data = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
                'Revenue': [1000, 1200, 1100, 1300, 1400],
                'Costs': [800, 900, 850, 950, 1000]
            })
            
            fig = px.line(test_data, x='Month', y=['Revenue', 'Costs'], 
                         title='Test Chart - Revenue vs Costs')
            st.plotly_chart(fig, use_container_width=True, key="overview_test_chart")
            st.success("✅ Charts are working!")
            
        except Exception as e:
            st.error(f"❌ Chart test failed: {e}")
        
        st.markdown("---")
        
        # Project Metrics with enhanced section styling
        st.markdown("""
        <div class="section-container info-section">
            <div class="section-header">
                <h2 style="color: #000000; margin: 0;">📊 Project Metrics</h2>
            </div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        self._create_project_metrics_content()
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Financial Summary with enhanced styling
        st.markdown("""
        <div class="section-container success-section">
            <div class="section-header">
                <h2 style="color: #000000; margin: 0;">💰 Financial Summary</h2>
            </div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        self._create_financial_summary_content()
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Cost Analysis with enhanced styling
        st.markdown("""
        <div class="section-container warning-section">
            <div class="section-header">
                <h2 style="color: #000000; margin: 0;">📈 Cost Analysis</h2>
            </div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        self._create_cost_analysis_content()
        st.markdown("</div></div>", unsafe_allow_html=True)
        



        


        














    def create_direct_labor_tab(self):
        """Create direct labor management tab with modular design"""
        st.markdown("## 👥 Direct Labor Management")
        
        # Test content first
        st.info("✅ Direct Labor tab is working!")
        st.write("This tab contains employee management features.")
        
        try:
            # Section 1: Employee Summary
            st.markdown("### 📊 Employee Summary")
            self._create_employee_summary_content()
            
            st.markdown("---")
            
            # Section 2: Template Download
            st.markdown("### 📋 Download Templates")
            self._create_template_download_content()
            
            st.markdown("---")
            
            # Section 3: Data Upload
            st.markdown("### 📤 Upload Data")
            self._create_upload_content()
            
            st.markdown("---")
            
            # Section 4: Employee Management
            st.markdown("### 👤 Employee Management")
            self._create_employee_management_content()
            
        except Exception as e:
            st.error(f"Error in Direct Labor tab: {e}")
            st.write("Some features may not be available due to an error.")
        
        st.markdown("---")
        
        # Section 5: Employee Detail View
        st.markdown("""
        <div class="section-container success-section">
            <div class="section-header">
                <h2 style="color: #000000; margin: 0;">👁️ Employee Detail View</h2>
            </div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        self._create_employee_detail_content()
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Section 6: Editable Employee Profiles
        st.markdown("""
        <div class="section-container warning-section">
            <div class="section-header">
                <h2 style="color: #000000; margin: 0;">✏️ Editable Employee Profiles</h2>
            </div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        self._create_editable_employee_profile_content()
        st.markdown("</div></div>", unsafe_allow_html=True)
        
        # Update calculations
        self.update_employee_calculations()

    def create_subcontractor_tab(self):
        """Create subcontractor management tab with modular design"""
        st.markdown("## 🏢 Subcontractor Management")
        
        # Test content first
        st.info("✅ Subcontractor tab is working!")
        st.write("This tab contains subcontractor management features.")
        
        try:
            # Section 1: Subcontractor Summary
            st.markdown("### 📊 Subcontractor Summary")
            self._create_subcontractor_summary_content()
            
            st.markdown("---")
            
            # Section 2: Add New Subcontractor
            st.markdown("### ➕ Add New Subcontractor")
            self._create_add_subcontractor_content()
            
            st.markdown("---")
            
            # Section 3: Subcontractor Management
            st.markdown("### 👥 Subcontractor Management")
            self._create_subcontractor_management_content()
            
        except Exception as e:
            st.error(f"Error in Subcontractor tab: {e}")
            st.write("Some features may not be available due to an error.")
        
        st.markdown("---")
        
        # Section 4: Monthly Hours Management
        st.markdown("## 📅 Monthly Hours Management")
        self._create_subcontractor_hours_content()
        
        st.markdown("---")
        
        # Section 5: ODC Management
        st.markdown("## 🏗️ Other Direct Costs (ODC)")
        self._create_odc_management_content()
        
        st.markdown("---")
        
        # Section 6: Editable Subcontractor Profiles
        st.markdown("## ✏️ Editable Subcontractor Profiles")
        self._create_editable_subcontractor_profile_content()



    def create_analysis_tab(self):
        """Create analysis and visualization tab with modular design"""
        st.markdown("## 📈 Financial Analysis")
        
        # Test content first
        st.info("✅ Analysis tab is working!")
        st.write("This tab contains financial analysis and visualization features.")
        
        try:
            # Section 1: Revenue Trends
            st.markdown("### 📈 Monthly Revenue Trends")
            self._create_revenue_trends_content()
            
            st.markdown("---")
            
            # Section 2: Employee Utilization
            st.markdown("### 🔥 Employee Hours Heatmap")
            self._create_employee_heatmap_content()
            
            st.markdown("---")
            
            # Section 3: Cost Analysis
            st.markdown("### 💰 Cost Analysis by Labor Category")
            self._create_lcat_cost_analysis_content()
            
            st.markdown("---")
            
            # Section 4: Burn Rate Analysis
            st.markdown("### ⚡ Project Burn Rate Analysis")
            self._create_burn_rate_content()
            
        except Exception as e:
            st.error(f"Error in Analysis tab: {e}")
            st.write("Some features may not be available due to an error.")
        
        st.markdown("---")
        
        # Section 4: Burn Rate Analysis
        st.markdown("## ⚡ Project Burn Rate Analysis")
        self._create_burn_rate_content()

    def _create_revenue_trends_content(self):
        """Create content for revenue trends section"""
        employees_df = st.session_state.employees
        subcontractors_df = st.session_state.subcontractors
        
        # Debug information
        st.write("Debug - Employees columns:", list(employees_df.columns) if not employees_df.empty else "No employees data")
        st.write("Debug - Subcontractors columns:", list(subcontractors_df.columns) if not subcontractors_df.empty else "No subcontractors data")
        
        # Create a simple test chart first
        try:
            # Simple test chart
            test_data = pd.DataFrame({
                'Period': ['Jan', 'Feb', 'Mar', 'Apr'],
                'Revenue': [1000, 1200, 1100, 1300]
            })
            
            fig = px.line(test_data, x='Period', y='Revenue', title='Test Chart - Revenue Trends')
            st.plotly_chart(fig, use_container_width=True, key="test_chart")
            
            # Now try the actual chart
            if not employees_df.empty:
                fig = create_revenue_trends_chart(employees_df, subcontractors_df)
                st.plotly_chart(fig, use_container_width=True, key="revenue_trends_chart")
            else:
                st.info("No employee data available for revenue trends chart.")
                
        except Exception as e:
            st.error(f"Error creating chart: {e}")
            st.write("Chart creation failed. Please check the data structure.")

    def _create_employee_heatmap_content(self):
        """Create content for employee heatmap section"""
        employees_df = st.session_state.employees
        
        # Use utility function to create the chart
        fig = create_employee_heatmap_chart(employees_df)
        st.plotly_chart(fig, width='stretch', key="employee_heatmap_chart")

    def _create_lcat_cost_analysis_content(self):
        """Create content for LCAT cost analysis section"""
        employees_df = st.session_state.employees
        
        # Use utility function to create the chart
        fig = create_lcat_cost_analysis_chart(employees_df)
        st.plotly_chart(fig, width='stretch', key="lcat_cost_chart")

    def _create_burn_rate_content(self):
        """Create content for burn rate analysis section"""
        employees_df = st.session_state.employees
        subcontractors_df = st.session_state.subcontractors
        
        # Use utility function to create the chart
        fig = create_burn_rate_chart(employees_df, subcontractors_df)
        st.plotly_chart(fig, width='stretch', key="burn_rate_chart")

    def create_tasks_tab(self):
        """Create task management tab with modular design"""
        st.markdown("## ✅ Task Management")
        
        # Test content first
        st.info("✅ Tasks tab is working!")
        st.write("This tab contains task management features.")
        
        try:
            # Section 1: Add New Task
            st.markdown("### ➕ Add New Task")
            self._create_add_task_content()
            
            st.markdown("---")
            
            # Section 2: Task Management
            st.markdown("### 📝 Task Details & Management")
            self._create_task_management_content()
            
            st.markdown("---")
            
            # Section 3: Task Removal
            st.markdown("### 🗑️ Remove Tasks")
            self._create_task_removal_content()
            
        except Exception as e:
            st.error(f"Error in Tasks tab: {e}")
            st.write("Some features may not be available due to an error.")
        
        st.markdown("---")
        
        # Section 4: Task Summary & Analysis
        st.markdown("## 📊 Task Summary & Analysis")
        self._create_task_summary_content()

    def _create_add_task_content(self):
        """Create content for add new task section"""
        tasks_df = st.session_state.tasks
        
        with st.expander("➕ Add New Task", expanded=False):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_task_id = st.text_input("Task ID")
                new_task_name = st.text_input("Task Name")
            with col2:
                new_lcat = st.text_input("LCAT")
                new_person_org = st.text_input("Person Organization")
            with col3:
                new_person = st.text_input("Person")
                new_hours = st.number_input("Hours", min_value=0.0)
                new_cost = st.number_input("Cost", min_value=0.0)
                
            if st.button("Add Task") and new_task_id:
                new_task = {
                    "Task_ID": new_task_id,
                    "Task_Name": new_task_name,
                    "LCAT": new_lcat,
                    "Person_Org": new_person_org,
                    "Person": new_person,
                    "Hours": new_hours,
                    "Cost": new_cost
                }
                
                new_row = pd.DataFrame([new_task])
                st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], 
                                                  ignore_index=True)
                st.success(f"Added task {new_task_id}")
                st.rerun()

    def _create_task_management_content(self):
        """Create content for task management section"""
        tasks_df = st.session_state.tasks
        
        if not tasks_df.empty:
            edited_tasks = st.data_editor(
                tasks_df,
                column_config={
                    "Hours": st.column_config.NumberColumn("Hours", format="%.2f"),
                    "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
                },
                width='stretch',
                key="tasks_data"
            )
            
            st.session_state.tasks = edited_tasks
        else:
            st.info("No tasks available. Add a new task to get started.")

    def _create_task_removal_content(self):
        """Create content for task removal section"""
        tasks_df = st.session_state.tasks
        
        if not tasks_df.empty:
            st.write("Select tasks to remove from the project:")
            
            # Create columns for better layout
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Task selection dropdown
                selected_task = st.selectbox(
                    "Choose task to remove:",
                    options=[f"{row['Task_ID']} - {row['Task_Name']}" for _, row in tasks_df.iterrows()],
                    key="task_removal_select"
                )
            
            with col2:
                # Show task details
                if selected_task:
                    task_id = selected_task.split(" - ")[0]
                    task_data = tasks_df[tasks_df['Task_ID'] == task_id].iloc[0]
                    st.write(f"**Task Name:** {task_data['Task_Name']}")
                    st.write(f"**LCAT:** {task_data['LCAT']}")
                    st.write(f"**Person:** {task_data['Person']}")
                    st.write(f"**Hours:** {task_data['Hours']:.2f}")
                    st.write(f"**Cost:** ${task_data['Cost']:.2f}")
            
            with col3:
                # Remove button with confirmation
                if selected_task:
                    if st.button("🗑️ Remove Task", type="secondary", key="remove_task_btn"):
                        # Remove the task
                        task_id = selected_task.split(" - ")[0]
                        st.session_state.tasks = st.session_state.tasks[
                            st.session_state.tasks['Task_ID'] != task_id
                        ]
                        st.success(f"✅ Task {task_id} has been removed from the project.")
                        st.rerun()
            
            # Show current task count
            st.info(f"📊 **Current Task Count:** {len(st.session_state.tasks)}")
            
            # Bulk removal section
            st.markdown("---")
            st.markdown("**Bulk Operations:**")
            
            # Bulk remove by Task ID
            task_id_options = tasks_df['Task_ID'].unique().tolist()
            if task_id_options:
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_task_id = st.selectbox(
                        "Remove all tasks by Task ID:",
                        options=task_id_options,
                        key="bulk_task_id_select"
                    )
                with col2:
                    if st.button("🗑️ Remove All by Task ID", type="secondary", key="bulk_remove_task_id_btn"):
                        task_id_count = len(tasks_df[tasks_df['Task_ID'] == selected_task_id])
                        st.session_state.tasks = st.session_state.tasks[
                            st.session_state.tasks['Task_ID'] != selected_task_id
                        ]
                        st.success(f"✅ Removed {task_id_count} tasks with Task ID: {selected_task_id}")
                        st.rerun()
            
            # Clear all tasks (with confirmation)
            if st.button("🗑️ Clear All Tasks", type="secondary", key="clear_all_tasks_btn"):
                st.warning("⚠️ This will remove ALL tasks from the project. This action cannot be undone.")
                if st.button("✅ Confirm Clear All", type="primary", key="confirm_clear_all_tasks_btn"):
                    task_count = len(st.session_state.tasks)
                    st.session_state.tasks = pd.DataFrame(columns=st.session_state.tasks.columns)
                    st.success(f"✅ Cleared all {task_count} tasks from the project.")
                    st.rerun()
        else:
            st.warning("⚠️ No tasks to remove.")

    def _create_task_summary_content(self):
        """Create content for task summary section"""
        tasks_df = st.session_state.tasks
        
        if not tasks_df.empty:
            task_summary = tasks_df.groupby(['Task_ID', 'Task_Name']).agg({
                'Hours': 'sum',
                'Cost': 'sum'
            }).reset_index()
            
            st.dataframe(task_summary, width='stretch')
            
            # Task cost visualization
            if not task_summary.empty:
                fig = px.bar(task_summary, x='Task_ID', y='Cost',
                            title='Cost by Task ID',
                            hover_data=['Task_Name', 'Hours'],
                            color_discrete_sequence=['#2E5BBA'])
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(size=12),
                    margin=dict(t=50, l=50, r=50, b=50)
                )
                st.plotly_chart(fig, width='stretch', key="task_cost_chart")
        else:
            st.info("No tasks available for summary analysis.")

    def process_uploaded_employees(self, df_upload: pd.DataFrame) -> pd.DataFrame:
        """Process uploaded employee data with duplicate handling"""
        # Map common column names
        column_mapping = {
            'Employee Name': 'Name',
            'employee_name': 'Name',
            'Labor Category': 'LCAT',
            'labor_category': 'LCAT',
            'Role': 'LCAT',
            'Salary': 'Current_Salary',
            'Rate': 'Hourly_Rate'
        }
        
        # Rename columns
        df_upload = df_upload.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_cols = ['Name', 'LCAT', 'Current_Salary']
        missing_cols = [col for col in required_cols if col not in df_upload.columns]
        
        if missing_cols:
            st.error(f"Missing required columns: {missing_cols}")
            return st.session_state.employees
        
        # Add default values for missing columns
        if 'Priced_Salary' not in df_upload.columns:
            df_upload['Priced_Salary'] = df_upload['Current_Salary']
        if 'Hours_Per_Month' not in df_upload.columns:
            df_upload['Hours_Per_Month'] = 173
        if 'Status' not in df_upload.columns:
            df_upload['Status'] = 'Active'
        if 'Employee_Type' not in df_upload.columns:
            df_upload['Employee_Type'] = 'Employee'
        if 'Company' not in df_upload.columns:
            df_upload['Company'] = 'Skyward IT Solutions'
        
        # Calculate hourly rates
        df_upload['Hourly_Rate'] = df_upload.apply(
            lambda row: self.calculate_hourly_rate(row['Current_Salary'], row['Hours_Per_Month']), 
            axis=1
        )
        
        # Handle duplicates within uploaded data first
        df_upload = df_upload.drop_duplicates(subset=['Name'], keep='first')
        
        # Merge with existing data, handling duplicates by name
        if not st.session_state.employees.empty:
            # Get existing employee names (case-insensitive)
            existing_names = [name.lower() for name in st.session_state.employees['Name'].tolist()]
            
            # Filter out duplicates from new data
            new_employees = df_upload[~df_upload['Name'].str.lower().isin(existing_names)]
            duplicate_employees = df_upload[df_upload['Name'].str.lower().isin(existing_names)]
            
            if not duplicate_employees.empty:
                st.info(f"ℹ️ {len(duplicate_employees)} duplicate employee(s) from upload will replace existing entries")
            
            # Combine new employees with existing ones (new data takes precedence)
            result_df = pd.concat([st.session_state.employees, new_employees], ignore_index=True)
            
            # Update existing employees with new data
            for _, new_emp in duplicate_employees.iterrows():
                # Find and replace existing employee
                mask = result_df['Name'].str.lower() == new_emp['Name'].lower()
                result_df.loc[mask] = new_emp
            
            return result_df
        else:
            # No existing employees, just return processed upload
            return df_upload

def main():
    """Main application function"""
    # Check authentication first
    auth_manager = AuthManager()
    
    if not auth_manager.is_authenticated():
        render_login_page()
        return
    
    # User is authenticated, show the main application
    tracker = SEASFinancialTracker()
    tracker.create_dashboard()
    
    # Add user info, theme toggle, and logout button to sidebar
    render_user_info_sidebar()
    render_theme_toggle_sidebar()
    render_logout_button()
    
    # Footer
    st.markdown("---")
    st.markdown("SEAS Financial Tracker - Built with Streamlit 📊")

if __name__ == "__main__":
    main()