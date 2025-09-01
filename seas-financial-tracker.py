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
from utils.template_downloader import generate_employee_template, get_template_info

# Set page config
st.set_page_config(
    page_title="SEAS Financial Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load comprehensive Section 508 compliant QuickBooks design CSS
def load_css():
    """Load the comprehensive CSS for Section 508 compliance and QuickBooks design"""
    try:
        with open('static/custom.css', 'r') as f:
            css_content = f.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        st.success("✅ Section 508 compliant QuickBooks design loaded successfully!")
    except FileNotFoundError:
        st.warning("⚠️ CSS file not found. Using default Streamlit styling.")
        # Fallback to basic QuickBooks-inspired styling
        st.markdown("""
        <style>
            .stApp { background: #f7fafc; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
            .stButton > button { background: #2C7BE5; color: white; border-radius: 8px; padding: 0.75rem 1.5rem; }
            .stButton > button:hover { background: #2D3748; transform: translateY(-1px); }
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error loading CSS: {e}")

# Load the CSS
load_css()

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
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        # Initialize time_periods first since other methods depend on it
        if 'time_periods' not in st.session_state:
            st.session_state.time_periods = self.generate_time_periods()
            
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
            st.session_state.employees = self.create_sample_employees()
        if 'subcontractors' not in st.session_state:
            st.session_state.subcontractors = self.create_sample_subcontractors()
        if 'odc_costs' not in st.session_state:
            st.session_state.odc_costs = self.create_sample_odc()
        if 'tasks' not in st.session_state:
            st.session_state.tasks = self.create_sample_tasks()

    def generate_time_periods(self) -> List[str]:
        """Generate monthly time periods for Base Year and Option Year 1"""
        periods = []
        start_date = datetime(2024, 3, 13)
        
        # Base Year: March 2024 - March 2025
        for i in range(12):
            period_start = start_date + timedelta(days=30*i)
            period_end = period_start + timedelta(days=29)
            periods.append(f"{period_start.strftime('%m/%d')}-{period_end.strftime('%m/%d/%y')}")
        
        # Option Year 1: March 2025 - March 2026
        for i in range(12):
            period_start = start_date + timedelta(days=30*(i+12))
            period_end = period_start + timedelta(days=29)
            periods.append(f"{period_start.strftime('%m/%d')}-{period_end.strftime('%m/%d/%y')}")
            
        return periods

    def create_sample_employees(self) -> pd.DataFrame:
        """Create sample employee data based on SEAS spreadsheet"""
        employees = [
            {"Name": "Shannon Gueringer", "LCAT": "PM", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 160000, "Current_Salary": 200000, "Hours_Per_Month": 173},
            {"Name": "Drew Hynes", "LCAT": "PM", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Inactive", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
            {"Name": "Uyen Tran", "LCAT": "SA/Eng Lead", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 180000, "Current_Salary": 175000, "Hours_Per_Month": 173},
            {"Name": "Leo Khan", "LCAT": "SA/Eng Lead", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 180000, "Current_Salary": 190000, "Hours_Per_Month": 173},
            {"Name": "Vitaliy Baklikov", "LCAT": "AI Lead", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 200000, "Current_Salary": 250000, "Hours_Per_Month": 173},
            {"Name": "Kenny Tran/Lynn Stahl", "LCAT": "HCD Lead", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 130000, "Current_Salary": 150000, "Hours_Per_Month": 173},
            {"Name": "Emilio Crocco", "LCAT": "Scrum Master", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 110000, "Current_Salary": 110000, "Hours_Per_Month": 173},
            {"Name": "Robert Melton", "LCAT": "SA/Eng Lead", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 230000, "Current_Salary": 225000, "Hours_Per_Month": 173},
            {"Name": "Nayeema Nageen", "LCAT": "Scrum Master", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 140000, "Current_Salary": 140000, "Hours_Per_Month": 173},
            {"Name": "Daniil Goryachev", "LCAT": "Cloud Data Engineer", "Employee_Type": "Employee", "Company": "Skyward IT Solutions", "Status": "Active", "Priced_Salary": 90000, "Current_Salary": 90000, "Hours_Per_Month": 173},
            {"Name": "Adrien Adams", "LCAT": "Data Systems SME", "Employee_Type": "Subcontractor", "Company": "BEELINE", "Status": "Active", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
            {"Name": "Paulina Fisher", "LCAT": "HCD Researcher", "Employee_Type": "Subcontractor", "Company": "Self Employed", "Status": "Active", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
            {"Name": "Andrew Sung", "LCAT": "Full Stack Dev", "Employee_Type": "Subcontractor", "Company": "Friends", "Status": "Active", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
        ]
        
        df = pd.DataFrame(employees)
        
        # Calculate hourly rates
        df['Hourly_Rate'] = df['Current_Salary'] / (df['Hours_Per_Month'] * 12 / 12)  # Annual to monthly rate
        df['Hourly_Rate'] = df['Hourly_Rate'] / df['Hours_Per_Month'] * 40 * 4.33  # Approximate monthly hourly rate
        
        # Add monthly hours columns (initialize with zeros)
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
            
        return df

    # ============================================================================
    # Modular Section Content Helper Methods
    # ============================================================================
    
    def _create_employee_summary_content(self):
        """Create content for employee summary section"""
        employees_df = st.session_state.employees
        
        if not employees_df.empty:
            # Create metric cards
            metric_cards = []
            
            total_employees = len(employees_df)
            active_employees = len(employees_df[employees_df['Status'] == 'Active'])
            total_salary = employees_df['Current_Salary'].sum()
            avg_salary = employees_df['Current_Salary'].mean()
            
            metric_cards.append(create_metric_card("Total Employees", total_employees, "+2 this month"))
            metric_cards.append(create_metric_card("Active Employees", active_employees))
            metric_cards.append(create_metric_card("Total Salary", f"${total_salary:,.0f}"))
            metric_cards.append(create_metric_card("Avg Salary", f"${avg_salary:,.0f}"))
            
            # Create grid of metric cards
            grid_html = f'''
            <div class="section-grid">
                {''.join(metric_cards)}
            </div>
            '''
            
            # Add breakdown summary
            employee_type_counts = employees_df['Employee_Type'].value_counts()
            status_counts = employees_df['Status'].value_counts()
            company_counts = employees_df['Company'].value_counts()
            
            breakdown_html = '''
            <div style="margin-top: 1.5rem;">
                <div class="section-grid" style="grid-template-columns: repeat(3, 1fr);">
                    <div>
                        <h4>👥 Employee Types</h4>
            '''
            
            for emp_type, count in employee_type_counts.items():
                type_icon = "👨‍💼" if emp_type == 'Employee' else "🏢"
                breakdown_html += f'<p>{type_icon} {emp_type}: {count}</p>'
            
            breakdown_html += '''
                    </div>
                    <div>
                        <h4>📊 Status</h4>
            '''
            
            for status, count in status_counts.items():
                status_icon = "🟢" if status == 'Active' else "🔴"
                breakdown_html += f'<p>{status_icon} {status}: {count}</p>'
            
            breakdown_html += '''
                    </div>
                    <div>
                        <h4>🏢 Companies</h4>
            '''
            
            for company, count in company_counts.items():
                breakdown_html += f'<p>• {company}: {count}</p>'
            
            breakdown_html += '''
                    </div>
                </div>
            </div>
            '''
            
            return grid_html + breakdown_html
        else:
            return '<p>📝 No employees added yet. Use the sections below to add employees or upload data.</p>'
    
    def _create_template_download_content(self):
        """Create content for template download section"""
        content_html = '''
        <div class="section-with-sidebar">
            <div class="section-main">
                <h4>📥 Download Employee Templates</h4>
                <p>Choose from our professionally designed templates to ensure consistent data entry and maintain all required fields.</p>
        '''
        
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
        
        return '''
            </div>
            <div class="section-sidebar">
                <h4>📋 Template Features</h4>
                <ul>
                    <li><strong>Standardized Format:</strong> Consistent data structure</li>
                    <li><strong>Data Validation:</strong> Built-in field validation</li>
                    <li><strong>Monthly Tracking:</strong> 24 monthly periods included</li>
                    <li><strong>Professional Design:</strong> QuickBooks-inspired layout</li>
                    <li><strong>Easy Import:</strong> Direct upload compatibility</li>
                </ul>
                
                <h4>🎯 Best Practices</h4>
                <ul>
                    <li>Use consistent naming conventions</li>
                    <li>Fill all required fields</li>
                    <li>Validate salary ranges</li>
                    <li>Check for duplicate entries</li>
                </ul>
            </div>
        </div>
        '''
    
    def _create_upload_content(self):
        """Create content for data upload section"""
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
        
        # Create metric cards
        metric_cards = []
        
        metric_cards.append(create_metric_card("⏱️ EAC Hours", f"{eac_hours:,.0f}"))
        metric_cards.append(create_metric_card("📈 Actual Hours", f"{actual_hours:,.0f}"))
        metric_cards.append(create_metric_card("💼 Billable Hours", f"{billable_hours:,.0f}"))
        
        # Calculate completion percentage
        completion_pct = (actual_hours / eac_hours) * 100 if eac_hours > 0 else 0
        progress_color = "#27ae60" if completion_pct >= 75 else "#f39c12" if completion_pct >= 50 else "#e74c3c"
        metric_cards.append(create_metric_card("🎯 Completion", f"{completion_pct:.1f}%"))
        
        # Create grid of metric cards
        grid_html = f'''
        <div class="section-grid">
            {''.join(metric_cards)}
        </div>
        '''
        
        # Add progress bar
        progress_html = f'''
        <div style="margin-top: 1.5rem;">
            <h4>📊 Project Progress</h4>
            <div style="background: #e9ecef; border-radius: 8px; height: 20px; overflow: hidden;">
                <div style="background: {progress_color}; height: 100%; width: {min(completion_pct, 100)}%; transition: width 0.3s ease;"></div>
            </div>
            <p style="text-align: center; margin-top: 0.5rem; color: {progress_color}; font-weight: 600;">
                {completion_pct:.1f}% Complete
            </p>
        </div>
        '''
        
        return grid_html + progress_html
    
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
        
        # Create financial summary

        
        return ""
    
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
            # Create metric cards
            metric_cards = []
            
            total_subcontractors = len(sub_df)
            total_hourly_rate = sub_df['Hourly_Rate'].sum()
            avg_hourly_rate = sub_df['Hourly_Rate'].mean()
            total_companies = len(sub_df['Company'].unique())
            
            metric_cards.append(create_metric_card("Total Subcontractors", total_subcontractors))
            metric_cards.append(create_metric_card("Total Hourly Rate", f"${total_hourly_rate:,.2f}"))
            metric_cards.append(create_metric_card("Avg Hourly Rate", f"${avg_hourly_rate:,.2f}"))
            metric_cards.append(create_metric_card("Unique Companies", total_companies))
            
            # Create grid of metric cards
            grid_html = f'''
            <div class="section-grid">
                {''.join(metric_cards)}
            </div>
            '''
            
            # Add breakdown summary
            company_counts = sub_df['Company'].value_counts()
            lcat_counts = sub_df['LCAT'].value_counts()
            
            breakdown_html = '''
            <div style="margin-top: 1.5rem;">
                <div class="section-grid" style="grid-template-columns: repeat(2, 1fr);">
                    <div>
                        <h4>🏢 Companies</h4>
            '''
            
            for company, count in company_counts.items():
                breakdown_html += f'<p>• {company}: {count}</p>'
            
            breakdown_html += '''
                    </div>
                    <div>
                        <h4>🎯 LCATs</h4>
            '''
            
            for lcat, count in lcat_counts.items():
                breakdown_html += f'<p>• {lcat}: {count}</p>'
            
            breakdown_html += '''
                    </div>
                </div>
            </div>
            '''
            
            return grid_html + breakdown_html
        else:
            return '<p>📝 No subcontractors added yet. Use the sections below to add subcontractors.</p>'
    
    def _create_add_subcontractor_content(self):
        """Create content for add new subcontractor section"""
        content_html = '''
        <div class="section-with-sidebar">
            <div class="section-main">
                <h4>➕ Add New Subcontractor</h4>
                <p>Enter subcontractor information to add them to your project.</p>
        '''
        
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
        
        return '''
            </div>
            <div class="section-sidebar">
                <h4>📋 Required Fields</h4>
                <ul>
                    <li><strong>Name:</strong> Subcontractor's full name</li>
                    <li><strong>Company:</strong> Company or organization</li>
                    <li><strong>LCAT:</strong> Labor category or role</li>
                    <li><strong>Hourly Rate:</strong> Rate per hour</li>
                </ul>
                
                <h4>💡 Tips</h4>
                <ul>
                    <li>Use consistent naming conventions</li>
                    <li>Verify hourly rates are accurate</li>
                    <li>Include all required information</li>
                </ul>
            </div>
        </div>
        '''
    
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

    def create_sample_odc(self) -> pd.DataFrame:
        """Create sample ODC (Other Direct Costs) data"""
        odc_data = []
        for i, period in enumerate(st.session_state.time_periods):
            amount = 472855.83 if i == 6 else 0.0  # Large ODC in 7th month as per spreadsheet
            odc_data.append({"Period": period, "Amount": amount, "Description": "Infrastructure Costs"})
            
        return pd.DataFrame(odc_data)

    def create_sample_tasks(self) -> pd.DataFrame:
        """Create sample task breakdown data"""
        tasks = [
            {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "AI Lead (KEY)", 
             "Person_Org": "OPERATIONS", "Person": "Baklikov, Vitaliy", "Hours": 984, "Cost": 118292.52},
            {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Cloud Data Engineers", 
             "Person_Org": "PROGRAM", "Person": "Anton, Jason", "Hours": 734.75, "Cost": 74832.42},
            {"Task_ID": "0001AA", "Task_Name": "CEDAR and KMP Transition", "LCAT": "Infrastructure Lead/SRE", 
             "Person_Org": "V-AQUIA", "Person": "Hardison, William", "Hours": 831, "Cost": 136901.52},
        ]
        
        return pd.DataFrame(tasks)

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
        """Create the main dashboard"""
        # QuickBooks-style header with subtitle
        st.markdown("""
        <div class="main-header">
            <h1>📊 SEAS Project Financial Tracker</h1>
            <div class="subtitle">Professional Financial Management & Analysis Platform</div>
        </div>
        """, unsafe_allow_html=True)
        
        # QuickBooks-style sidebar for project parameters
        with st.sidebar:
            st.markdown("""
            <div style="background: #2E5BBA; 
                        padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 4px 12px rgba(46, 91, 186, 0.2);">
                <h3 style="color: white; margin: 0 0 1rem 0; text-align: center; font-weight: 600;">⚙️ Project Parameters</h3>
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

        # Main tabs with modern styling
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Overview", "👥 Direct Labor", "🏢 Subcontractors", "📊 Analysis", "📋 Tasks"])

        with tab1:
            self.create_overview_tab()
            
        with tab2:
            self.create_direct_labor_tab()
            
        with tab3:
            self.create_subcontractor_tab()
            
        with tab4:
            self.create_analysis_tab()
            
        with tab5:
            self.create_tasks_tab()

    def create_overview_tab(self):
        """Create overview dashboard with modular design"""
        
        # Section 1: Project Metrics - Info Section
        create_section(
            title="📊 Project Metrics",
            content=self._create_project_metrics_content(),
            section_type="info",
            status="active",
            footer_content="Real-time project tracking",
            actions=[
                {"type": "primary", "label": "Refresh Metrics"},
                {"type": "secondary", "label": "Export Report"}
            ]
        )
        
        create_section_divider()
        
        # Section 2: Financial Summary - Success Section
        create_section(
            title="💰 Financial Summary",
            content=self._create_financial_summary_content(),
            section_type="success",
            status="complete",
            footer_content="Financial calculations updated",
            actions=[
                {"type": "primary", "label": "View Details"},
                {"type": "secondary", "label": "Download Report"}
            ]
        )
        
        create_section_divider()
        
        # Section 3: Cost Analysis - Warning Section
        create_section(
            title="📈 Cost Analysis",
            content=self._create_cost_analysis_content(),
            section_type="warning",
            status="needs_review",
            footer_content="Review cost breakdowns",
            actions=[
                {"type": "primary", "label": "Analyze Trends"},
                {"type": "secondary", "label": "Compare Periods"}
            ]
        )
        



        


        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="financial-card">
                <h3>💸 Costs Breakdown</h3>
                <div class="financial-item">
                    <span>👥 Direct Labor</span>
                    <strong>${total_direct_labor:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>🏗️ ODC</span>
                    <strong>${total_odc:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>🤝 Subcontractor</span>
                    <strong>${total_subcontractor:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>🎯 Fringe</span>
                    <strong>${indirect_costs['Fringe']:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>🏢 Overhead</span>
                    <strong>${indirect_costs['Overhead']:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>📈 G&A</span>
                    <strong>${indirect_costs['G&A']:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>Total Costs</span>
                    <strong>${total_costs:,.2f}</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            profit_loss = recalculated_revenue - total_costs
            profit_color = "#27ae60" if profit_loss >= 0 else "#e74c3c"
            st.markdown(f"""
            <div class="financial-card">
                <h3>📊 Revenue Analysis</h3>
                <div class="financial-item">
                    <span>💰 Total Transaction Price</span>
                    <strong>${total_transaction_price:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>📈 Recalculated Revenue</span>
                    <strong>${recalculated_revenue:,.2f}</strong>
                </div>
                <div class="financial-item">
                    <span>Profit/Loss</span>
                    <strong style="color: {profit_color};">${profit_loss:,.2f}</strong>
                </div>
            """, unsafe_allow_html=True)
            
            if recalculated_revenue > 0:
                margin = (profit_loss / recalculated_revenue) * 100
                margin_color = "#27ae60" if margin >= 0 else "#e74c3c"
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1.2rem; border-radius: 8px; margin-top: 1rem; text-align: center; border: 1px solid #e9ecef;">
                    <div style="font-size: 1.1rem; font-weight: 600; color: {margin_color};">Profit Margin: {margin:.2f}%</div>
                </div>
                """, unsafe_allow_html=True)

        # Cost breakdown chart
        cost_data = {
            'Category': ['Direct Labor', 'ODC', 'Subcontractor', 'Fringe', 'Overhead', 'G&A'],
            'Amount': [total_direct_labor, total_odc, total_subcontractor, 
                      indirect_costs['Fringe'], indirect_costs['Overhead'], indirect_costs['G&A']]
        }
        
        fig = px.pie(pd.DataFrame(cost_data), values='Amount', names='Category', 
                     title="Cost Breakdown by Category")
        st.plotly_chart(fig, width='stretch')

    def create_direct_labor_tab(self):
        """Create direct labor management tab with modular design"""
        
        # Section 1: Employee Summary - Info Section
        create_section(
            title="📊 Employee Summary",
            content=self._create_employee_summary_content(),
            section_type="info",
            status="active",
            footer_content="Data refreshes automatically",
            actions=[
                {"type": "primary", "label": "Refresh Data"},
                {"type": "secondary", "label": "Export Report"}
            ]
        )
        
        create_section_divider()
        
        # Section 2: Template Download - Success Section
        create_section(
            title="📋 Download Templates",
            content=self._create_template_download_content(),
            section_type="success",
            status="ready"
        )
        
        create_section_divider()
        
        # Section 3: Data Upload - Warning Section
        create_section(
            title="📁 Data Upload",
            content=self._create_upload_content(),
            section_type="warning",
            status="needs_review"
        )
        
        create_section_divider()
        
        # Section 4: Employee Management - Info Section
        create_section(
            title="👥 Employee Management",
            content=self._create_employee_management_content(),
            section_type="info",
            status="active",
            actions=[
                {"type": "primary", "label": "Add Employee"},
                {"type": "secondary", "label": "Bulk Edit"}
            ]
        )
        
        create_section_divider()
        
        # Section 5: Employee Detail View - Info Section
        create_section(
            title="👁️ Employee Detail View",
            content=self._create_employee_detail_content(),
            section_type="info",
            status="active"
        )
        
        # Duplicate detection and management

        

        

        
        # Update calculations
        self.update_employee_calculations()
        
        # Monthly hours input - show in sections


        
        # Option Year 1 hours
        if len(st.session_state.time_periods) > 12:
    
            oy1_periods = st.session_state.time_periods[12:]
            oy1_columns = [f'Hours_{period}' for period in oy1_periods]
            
            if all(col in employees_df.columns for col in oy1_columns):
                oy1_data = employees_df[["Name"] + oy1_columns].copy()
                
                edited_oy1 = st.data_editor(
                    oy1_data,
                    column_config={col: st.column_config.NumberColumn(period, format="%.1f") 
                                  for col, period in zip(oy1_columns, oy1_periods)},
                    width='stretch',
                    key="oy1_hours"
                )
                
                # Update main dataframe
                for col in oy1_columns:
                    st.session_state.employees[col] = edited_oy1[col]
        
        # Final calculations update
        self.update_employee_calculations()
        
        # Data Management section

        

        


    def create_subcontractor_tab(self):
        """Create subcontractor management tab with modular design"""
        
        # Section 1: Subcontractor Summary - Info Section
        create_section(
            title="📊 Subcontractor Summary",
            content=self._create_subcontractor_summary_content(),
            section_type="info",
            status="active",
            footer_content="Data refreshes automatically",
            actions=[
                {"type": "primary", "label": "Refresh Data"},
                {"type": "secondary", "label": "Export Report"}
            ]
        )
        
        create_section_divider()
        
        # Section 2: Add New Subcontractor - Success Section
        create_section(
            title="➕ Add New Subcontractor",
            content=self._create_add_subcontractor_content(),
            section_type="success",
            status="ready"
        )
        
        create_section_divider()
        
        # Section 3: Subcontractor Management - Info Section
        create_section(
            title="👥 Subcontractor Management",
            content=self._create_subcontractor_management_content(),
            section_type="info",
            status="active",
            actions=[
                {"type": "primary", "label": "Edit Data"},
                {"type": "secondary", "label": "Bulk Operations"}
            ]
        )
        
        create_section_divider()
        
        # Section 4: Monthly Hours - Warning Section
        create_section(
            title="📅 Monthly Hours Management",
            content=self._create_subcontractor_hours_content(),
            section_type="warning",
            status="needs_review"
        )
        
        create_section_divider()
        
        # Section 5: ODC Management - Info Section
        create_section(
            title="🏗️ Other Direct Costs (ODC)",
            content=self._create_odc_management_content(),
            section_type="info",
            status="active"
        )
        
        # ODC removal section
        st.markdown('<div class="subheader">🗑️ Remove ODC Entries</div>', unsafe_allow_html=True)
        
        if not odc_df.empty:
            st.write("Select ODC entries to remove from the project:")
            
            # Create columns for better layout
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # ODC selection dropdown
                selected_odc = st.selectbox(
                    "Choose ODC entry to remove:",
                    options=[f"{row['Period']} - ${row['Amount']:,.2f}" for _, row in odc_df.iterrows()],
                    key="odc_removal_select"
                )
            
            with col2:
                # Show ODC details
                if selected_odc:
                    period = selected_odc.split(" - ")[0]
                    odc_data = odc_df[odc_df['Period'] == period].iloc[0]
                    st.write(f"**Period:** {odc_data['Period']}")
                    st.write(f"**Amount:** ${odc_data['Amount']:,.2f}")
                    st.write(f"**Description:** {odc_data['Description']}")
            
            with col3:
                # Remove button with confirmation
                if selected_odc:
                    if st.button("🗑️ Remove ODC", type="secondary", key="remove_odc_btn"):
                        # Remove the ODC entry
                        period = selected_odc.split(" - ")[0]
                        st.session_state.odc_costs = st.session_state.odc_costs[
                            st.session_state.odc_costs['Period'] != period
                        ]
                        st.success(f"✅ ODC entry for {period} has been removed from the project.")
                        st.rerun()
            
            # Show current ODC count
            st.info(f"📊 **Current ODC Entries:** {len(st.session_state.odc_costs)}")
            
            # Bulk removal section
            st.markdown("---")
            st.markdown("**Bulk Operations:**")
            
            # Clear all ODC entries (with confirmation)
            if st.button("🗑️ Clear All ODC Entries", type="secondary", key="clear_all_odc_btn"):
                st.warning("⚠️ This will remove ALL ODC entries from the project. This action cannot be undone.")
                if st.button("✅ Confirm Clear All", type="primary", key="confirm_clear_all_odc_btn"):
                    odc_count = len(st.session_state.odc_costs)
                    st.session_state.odc_costs = pd.DataFrame(columns=st.session_state.odc_costs.columns)
                    st.success(f"✅ Cleared all {odc_count} ODC entries from the project.")
                    st.rerun()
        else:
            st.warning("⚠️ No ODC entries to remove.")

    def create_analysis_tab(self):
        """Create analysis and visualization tab"""
        st.markdown('<div class="subheader">📊 Financial Analysis & Visualizations</div>', unsafe_allow_html=True)
        
        # Monthly revenue trends
        st.markdown('<div class="subheader">📈 Monthly Revenue Trends</div>', unsafe_allow_html=True)
        
        employees_df = st.session_state.employees
        revenue_by_month = {}
        
        for period in st.session_state.time_periods:
            revenue_col = f'Revenue_{period}'
            if revenue_col in employees_df.columns:
                revenue_by_month[period] = employees_df[revenue_col].sum()
        
        if revenue_by_month:
            revenue_df = pd.DataFrame(list(revenue_by_month.items()), 
                                    columns=['Period', 'Revenue'])
            
            fig = px.line(revenue_df, x='Period', y='Revenue', 
                         title='Direct Labor Revenue by Month',
                         color_discrete_sequence=['#2E5BBA'])
            fig.update_layout(
                xaxis_tickangle=45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(t=50, l=50, r=50, b=50)
            )
            st.plotly_chart(fig, width='stretch')
        
        # Employee utilization heatmap
        st.markdown('<div class="subheader">🔥 Employee Hours Heatmap</div>', unsafe_allow_html=True)
        
        hours_columns = [col for col in employees_df.columns if col.startswith('Hours_')]
        if hours_columns:
            heatmap_data = employees_df[['Name'] + hours_columns].set_index('Name')
            
            # Rename columns for better display
            period_names = [col.replace('Hours_', '') for col in hours_columns]
            heatmap_data.columns = period_names
            
            fig = px.imshow(heatmap_data.values, 
                           x=period_names,
                           y=heatmap_data.index,
                           aspect="auto",
                           title="Employee Hours by Month",
                           color_continuous_scale='Viridis')
            fig.update_layout(
                xaxis_tickangle=45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(t=50, l=50, r=50, b=50)
            )
            st.plotly_chart(fig, width='stretch')
        
        # Cost analysis by LCAT
        st.markdown('<div class="subheader">💰 Cost Analysis by Labor Category</div>', unsafe_allow_html=True)
        
        lcat_revenue = employees_df.groupby('LCAT').agg({
            col: 'sum' for col in employees_df.columns if col.startswith('Revenue_')
        }).sum(axis=1).reset_index()
        lcat_revenue.columns = ['LCAT', 'Total_Revenue']
        
        if not lcat_revenue.empty:
            fig = px.bar(lcat_revenue, x='LCAT', y='Total_Revenue',
                        title='Total Revenue by Labor Category',
                        color_discrete_sequence=['#2E5BBA'])
            fig.update_layout(
                xaxis_tickangle=45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(t=50, l=50, r=50, b=50)
            )
            st.plotly_chart(fig, width='stretch')
        
        # Burn rate analysis
        st.markdown('<div class="subheader">⚡ Project Burn Rate Analysis</div>', unsafe_allow_html=True)
        
        params = st.session_state.project_params
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        
        # Calculate cumulative hours and costs over time
        cumulative_hours = []
        cumulative_costs = []
        periods = []
        
        running_hours = 0
        running_costs = 0
        
        for period in st.session_state.time_periods:
            hours_col = f'Hours_{period}'
            revenue_col = f'Revenue_{period}'
            
            if hours_col in employees_df.columns:
                period_hours = employees_df[hours_col].sum()
                period_revenue = employees_df[revenue_col].sum()
                
                running_hours += period_hours
                running_costs += period_revenue
                
                periods.append(period)
                cumulative_hours.append(running_hours)
                cumulative_costs.append(running_costs)
        
        if periods:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=periods, y=cumulative_hours, name="Cumulative Hours"),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=periods, y=cumulative_costs, name="Cumulative Costs"),
                secondary_y=True,
            )
            
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
            
            st.plotly_chart(fig, width='stretch')

    def create_tasks_tab(self):
        """Create task management tab"""
        st.markdown('<div class="subheader">📋 Task Breakdown Management</div>', unsafe_allow_html=True)
        
        # Task data editor
        tasks_df = st.session_state.tasks
        
        # Add new task
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

        # Display and edit tasks
        if not tasks_df.empty:
            st.markdown('<div class="subheader">📝 Task Details</div>', unsafe_allow_html=True)
            
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
            
            # Task removal section
            st.markdown('<div class="subheader">🗑️ Remove Tasks</div>', unsafe_allow_html=True)
            
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
            
            # Task summary by ID
            st.markdown('<div class="subheader">📊 Task Summary</div>', unsafe_allow_html=True)
            
            task_summary = edited_tasks.groupby(['Task_ID', 'Task_Name']).agg({
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
                st.plotly_chart(fig, width='stretch')

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
    tracker = SEASFinancialTracker()
    tracker.create_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("SEAS Financial Tracker - Built with Streamlit 📊")

if __name__ == "__main__":
    main()