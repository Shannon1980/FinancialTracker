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
        """Create overview dashboard"""
        st.markdown('<div class="subheader">📊 Project Overview</div>', unsafe_allow_html=True)
        
        # Key metrics with modern styling
        params = st.session_state.project_params
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        non_billable = params['non_billable_hours']
        billable_hours = actual_hours + non_billable
        
        # Modern metric cards with icons and gradients
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-icon">⏱️</div>
                <div class="metric-value">{eac_hours:,.0f}</div>
                <div class="metric-label">EAC Hours</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-icon">📈</div>
                <div class="metric-value">{actual_hours:,.0f}</div>
                <div class="metric-label">Actual Hours</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-icon">💼</div>
                <div class="metric-value">{billable_hours:,.0f}</div>
                <div class="metric-label">Billable Hours</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col4:
            completion_pct = (actual_hours / eac_hours) * 100 if eac_hours > 0 else 0
            progress_color = "#27ae60" if completion_pct >= 75 else "#f39c12" if completion_pct >= 50 else "#e74c3c"
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <div class="metric-icon">🎯</div>
                <div class="metric-value" style="color: {progress_color};">{completion_pct:.1f}%</div>
                <div class="metric-label">Completion</div>
            </div>
            """, unsafe_allow_html=True)

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
        total_transaction_price = params['total_transaction_price']
        recalculated_revenue = (billable_hours / eac_hours) * total_transaction_price if eac_hours > 0 else 0
        
        # Financial summary with modern cards
        st.markdown('<div class="subheader">💰 Financial Summary</div>', unsafe_allow_html=True)
        
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
        """Create direct labor management tab"""
        st.markdown('<div class="subheader">👥 Direct Labor Management</div>', unsafe_allow_html=True)
        
        # QuickBooks-style upload section
        st.markdown("""
        <div class="upload-section">
            <h3>📁 Upload Employee Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Template download section
        st.markdown('<div class="subheader">📋 Download Templates</div>', unsafe_allow_html=True)
        
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
        
        st.markdown("---")
        
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

        # Employee data editor
        st.markdown('<div class="subheader">👤 Employee Data</div>', unsafe_allow_html=True)
        
        # Get employee data
        employees_df = st.session_state.employees
        
        # Employee summary
        if not employees_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Employees", len(employees_df))
            with col2:
                active_employees = len(employees_df[employees_df['Status'] == 'Active'])
                st.metric("Active Employees", active_employees)
            with col3:
                total_salary = employees_df['Current_Salary'].sum()
                st.metric("Total Salary", f"${total_salary:,.0f}")
            with col4:
                avg_salary = employees_df['Current_Salary'].mean()
                st.metric("Avg Salary", f"${avg_salary:,.0f}")
            
            # Employee type and company breakdown
            col1, col2 = st.columns(2)
            with col1:
                employee_type_counts = employees_df['Employee_Type'].value_counts()
                st.markdown("**👥 Employee Type Breakdown**")
                for emp_type, count in employee_type_counts.items():
                    type_icon = "👨‍💼" if emp_type == 'Employee' else "🏢"
                    st.write(f"{type_icon} {emp_type}: {count}")
                
                company_counts = employees_df['Company'].value_counts()
                st.markdown("**🏢 Company Distribution**")
                for company, count in company_counts.items():
                    st.write(f"• {company}: {count}")
            
            with col2:
                status_counts = employees_df['Status'].value_counts()
                st.markdown("**📊 Status Breakdown**")
                for status, count in status_counts.items():
                    status_icon = "🟢" if status == 'Active' else "🔴"
                    st.write(f"{status_icon} {status}: {count}")
                
                lcat_counts = employees_df['LCAT'].value_counts()
                st.markdown("**🎯 LCAT Distribution**")
                for lcat, count in lcat_counts.items():
                    st.write(f"• {lcat}: {count}")
        else:
            st.info("📝 No employees added yet. Use the form below or upload a template to get started.")
        
        # Add new employee
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

        # Display and edit employee data
        
        # Basic employee info
        st.markdown('<div class="subheader">ℹ️ Employee Information</div>', unsafe_allow_html=True)
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
        
        # Employee detail view
        st.markdown('<div class="subheader">👁️ Employee Detail View</div>', unsafe_allow_html=True)
        
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
                        
                        # Create visualization
                        if not period_df.empty:
                            fig = go.Figure()
                            
                            # Add hours bar chart
                            fig.add_trace(go.Bar(
                                x=period_df['Period'],
                                y=period_df['Hours'],
                                name='Hours',
                                yaxis='y',
                                marker_color='#2E5BBA'
                            ))
                            
                            # Add revenue line chart
                            fig.add_trace(go.Scatter(
                                x=period_df['Period'],
                                y=period_df['Revenue'],
                                name='Revenue',
                                yaxis='y2',
                                line=dict(color='#FF6B35', width=3)
                            ))
                            
                            fig.update_layout(
                                title=f'Time Period Data for {selected_employee}',
                                xaxis=dict(title='Period'),
                                yaxis=dict(title='Hours', side='left'),
                                yaxis2=dict(title='Revenue ($)', side='right', overlaying='y'),
                                plot_bgcolor='rgba(0,0,0,0)',
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(size=12),
                                margin=dict(t=50, l=50, r=50, b=50)
                            )
                            
                            st.plotly_chart(fig, width='stretch')
        else:
            st.info("📝 No employees to view. Add employees first to see detailed information.")
        
        # Duplicate detection and management
        st.markdown('<div class="subheader">🔍 Duplicate Detection</div>', unsafe_allow_html=True)
        
        # Check for existing duplicates in current data
        if not employees_df.empty:
            # Find duplicates by name (case-insensitive)
            name_counts = employees_df['Name'].str.lower().value_counts()
            duplicates = name_counts[name_counts > 1]
            
            if not duplicates.empty:
                st.warning(f"⚠️ Found {len(duplicates)} duplicate employee names in current data:")
                
                for dup_name in duplicates.index:
                    dup_employees = employees_df[employees_df['Name'].str.lower() == dup_name]
                    st.write(f"**'{dup_name.title()}':** {len(dup_employees)} entries")
                    
                    # Show duplicate details
                    with st.expander(f"View duplicates for '{dup_name.title()}'"):
                        st.dataframe(dup_employees)
                        
                        # Option to merge duplicates
                        if st.button(f"🔄 Merge Duplicates for '{dup_name.title()}'", key=f"merge_{dup_name}"):
                            # Keep the first entry and remove others
                            first_idx = dup_employees.index[0]
                            duplicate_indices = dup_employees.index[1:]
                            
                            # Remove duplicates
                            st.session_state.employees = st.session_state.employees.drop(duplicate_indices)
                            st.success(f"✅ Merged duplicates for '{dup_name.title()}' - kept first entry, removed {len(duplicate_indices)} duplicates")
                            st.rerun()
            else:
                st.success("✅ No duplicate employee names found in current data")
        
        # Employee removal section
        st.markdown('<div class="subheader">🗑️ Remove Employees</div>', unsafe_allow_html=True)
        
        # Create a more user-friendly employee removal interface
        if not employees_df.empty:
            st.write("Select employees to remove from the project:")
            
            # Create columns for better layout
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                # Employee selection dropdown
                selected_employee = st.selectbox(
                    "Choose employee to remove:",
                    options=employees_df['Name'].tolist(),
                    key="employee_removal_select"
                )
            
            with col2:
                # Show employee details
                if selected_employee:
                    emp_data = employees_df[employees_df['Name'] == selected_employee].iloc[0]
                    st.write(f"**LCAT:** {emp_data['LCAT']}")
                    st.write(f"**Current Salary:** ${emp_data['Current_Salary']:,.2f}")
            
            with col3:
                # Remove button with confirmation
                if selected_employee:
                    if st.button("🗑️ Remove Employee", type="secondary", key="remove_employee_btn"):
                        # Remove the employee
                        st.session_state.employees = st.session_state.employees[
                            st.session_state.employees['Name'] != selected_employee
                        ]
                        st.success(f"✅ {selected_employee} has been removed from the project.")
                        st.rerun()
            
            # Show current employee count
            st.info(f"📊 **Current Employee Count:** {len(st.session_state.employees)}")
            
            # Bulk removal section
            st.markdown("---")
            st.markdown("**Bulk Operations:**")
            
            # Bulk remove by LCAT
            lcat_options = employees_df['LCAT'].unique().tolist()
            if lcat_options:
                col1, col2 = st.columns([2, 1])
                with col1:
                    selected_lcat = st.selectbox(
                        "Remove all employees by Labor Category:",
                        options=lcat_options,
                        key="bulk_lcat_select"
                    )
                with col2:
                    if st.button("🗑️ Remove All by LCAT", type="secondary", key="bulk_remove_lcat_btn"):
                        lcat_count = len(employees_df[employees_df['LCAT'] == selected_lcat])
                        st.session_state.employees = st.session_state.employees[
                            st.session_state.employees['LCAT'] != selected_lcat
                        ]
                        st.success(f"✅ Removed {lcat_count} employees with LCAT: {selected_lcat}")
                        st.rerun()
            
            # Clear all employees (with confirmation)
            if st.button("🗑️ Clear All Employees", type="secondary", key="clear_all_employees_btn"):
                st.warning("⚠️ This will remove ALL employees from the project. This action cannot be undone.")
                if st.button("✅ Confirm Clear All", type="primary", key="confirm_clear_all_btn"):
                    employee_count = len(st.session_state.employees)
                    st.session_state.employees = pd.DataFrame(columns=st.session_state.employees.columns)
                    st.success(f"✅ Cleared all {employee_count} employees from the project.")
                    st.rerun()
        else:
            st.warning("⚠️ No employees to remove. Add some employees first.")
        
        # Update calculations
        self.update_employee_calculations()
        
        # Monthly hours input - show in sections
        st.markdown('<div class="subheader">📅 Monthly Hours (Base Year)</div>', unsafe_allow_html=True)
        base_year_periods = st.session_state.time_periods[:12]
        base_year_columns = [f'Hours_{period}' for period in base_year_periods]
        
        if all(col in employees_df.columns for col in base_year_columns):
            base_year_data = employees_df[["Name"] + base_year_columns].copy()
            
            edited_base_year = st.data_editor(
                base_year_data,
                column_config={col: st.column_config.NumberColumn(period, format="%.1f") 
                              for col, period in zip(base_year_columns, base_year_periods)},
                width='stretch',
                key="base_year_hours"
            )
            
            # Update main dataframe
            for col in base_year_columns:
                st.session_state.employees[col] = edited_base_year[col]
        
        # Option Year 1 hours
        if len(st.session_state.time_periods) > 12:
            st.subheader("Monthly Hours (Option Year 1)")
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
        st.markdown('<div class="subheader">💾 Data Management</div>', unsafe_allow_html=True)
        
        # Export functionality
        st.markdown("**📤 Export Data:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Download Employee Data (Excel)"):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.employees.to_excel(writer, index=False, sheet_name='Employees')
                output.seek(0)
                
                st.download_button(
                    label="📥 Download Excel",
                    data=output.getvalue(),
                    file_name="seas_employee_data.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        
        with col2:
            if st.button("Download Employee Data (CSV)"):
                csv = st.session_state.employees.to_csv(index=False)
                st.download_button(
                    label="📥 Download CSV",
                    data=csv,
                    file_name="seas_employee_data.csv",
                    mime="text/csv"
                )
        
        # Backup and Restore functionality
        st.markdown("**🔄 Backup & Restore:**")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Create Backup"):
                # Create a comprehensive backup of all data
                backup_data = {
                    'employees': st.session_state.employees.to_dict('records'),
                    'subcontractors': st.session_state.subcontractors.to_dict('records'),
                    'odc_costs': st.session_state.odc_costs.to_dict('records'),
                    'tasks': st.session_state.tasks.to_dict('records'),
                    'project_params': st.session_state.project_params,
                    'time_periods': st.session_state.time_periods,
                    'backup_timestamp': datetime.now().isoformat()
                }
                
                backup_json = json.dumps(backup_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download Backup",
                    data=backup_json,
                    file_name=f"seas_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.success("✅ Backup created successfully!")
        
        with col2:
            # File upload for restore
            uploaded_backup = st.file_uploader("Upload backup file to restore", type=['json'], key="backup_restore")
            if uploaded_backup is not None:
                if st.button("🔄 Restore from Backup"):
                    try:
                        backup_data = json.load(uploaded_backup)
                        
                        # Restore all data
                        if 'employees' in backup_data:
                            st.session_state.employees = pd.DataFrame(backup_data['employees'])
                        if 'subcontractors' in backup_data:
                            st.session_state.subcontractors = pd.DataFrame(backup_data['subcontractors'])
                        if 'odc_costs' in backup_data:
                            st.session_state.odc_costs = pd.DataFrame(backup_data['odc_costs'])
                        if 'tasks' in backup_data:
                            st.session_state.tasks = pd.DataFrame(backup_data['tasks'])
                        if 'project_params' in backup_data:
                            st.session_state.project_params = backup_data['project_params']
                        if 'time_periods' in backup_data:
                            st.session_state.time_periods = backup_data['time_periods']
                        
                        st.success("✅ Data restored successfully from backup!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error restoring backup: {str(e)}")

    def create_subcontractor_tab(self):
        """Create subcontractor management tab"""
        st.markdown('<div class="subheader">🏢 Subcontractor Management</div>', unsafe_allow_html=True)
        
        # Add new subcontractor
        with st.expander("➕ Add New Subcontractor", expanded=False):
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

        # Subcontractor data editor
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            st.markdown('<div class="subheader">ℹ️ Subcontractor Information</div>', unsafe_allow_html=True)
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
            st.markdown('<div class="subheader">🗑️ Remove Subcontractors</div>', unsafe_allow_html=True)
            
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
            
            # Monthly hours for subcontractors
            st.markdown('<div class="subheader">📅 Subcontractor Monthly Hours</div>', unsafe_allow_html=True)
            
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

        # ODC Management
        st.markdown('<div class="subheader">🏗️ Other Direct Costs (ODC)</div>', unsafe_allow_html=True)
        
        odc_df = st.session_state.odc_costs
        
        edited_odc = st.data_editor(
            odc_df,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            },
            width='stretch',
            key="odc_data"
        )
        
        st.session_state.odc_costs = edited_odc
        
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