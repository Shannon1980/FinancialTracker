"""
Refactored SEAS Financial Tracker Application
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import json

# Import our refactored modules
from models import DataManager, ProjectParameters
from business_logic import FinancialCalculator, DataValidator, ReportGenerator
from ui_components import (
    MetricCard, FinancialCard, RemovalInterface, DataTable, 
    ChartContainer, FormSection, SuccessMessage, ErrorMessage, 
    WarningMessage, InfoMessage
)
from config import APP_CONFIG, COLORS, CSS_CLASSES, DEFAULT_PROJECT_PARAMS, LCAT_OPTIONS, CHART_CONFIG

class SEASFinancialTrackerRefactored:
    """Refactored SEAS Financial Tracker with better separation of concerns"""
    
    def __init__(self):
        self.data_manager = DataManager()
        self.financial_calculator = FinancialCalculator()
        self.data_validator = DataValidator()
        self.report_generator = ReportGenerator()
        self.initialize_session_state()
    
    def initialize_session_state(self):
        """Initialize session state with proper separation"""
        if 'time_periods' not in st.session_state:
            st.session_state.time_periods = self.generate_time_periods()
        
        if 'project_params' not in st.session_state:
            st.session_state.project_params = DEFAULT_PROJECT_PARAMS.copy()
        
        if 'employees' not in st.session_state:
            st.session_state.employees = self.create_sample_employees()
        
        if 'subcontractors' not in st.session_state:
            st.session_state.subcontractors = self.create_sample_subcontractors()
        
        if 'odc_costs' not in st.session_state:
            st.session_state.odc_costs = self.create_sample_odc()
        
        if 'tasks' not in st.session_state:
            st.session_state.tasks = self.create_sample_tasks()
    
    def generate_time_periods(self) -> list:
        """Generate time periods for the project"""
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
        """Create sample employee data"""
        from config import SAMPLE_EMPLOYEES
        
        df = pd.DataFrame(SAMPLE_EMPLOYEES)
        
        # Calculate hourly rates
        df['Hourly_Rate'] = df.apply(
            lambda row: self.financial_calculator.calculate_hourly_rate(
                row['Current_Salary'], row['Hours_Per_Month']
            ), axis=1
        )
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
        
        return df
    
    def create_sample_subcontractors(self) -> pd.DataFrame:
        """Create sample subcontractor data"""
        from config import SAMPLE_SUBCONTRACTORS
        
        df = pd.DataFrame(SAMPLE_SUBCONTRACTORS)
        
        # Add monthly hours columns
        for period in st.session_state.time_periods:
            df[f'Hours_{period}'] = 0.0
            df[f'Revenue_{period}'] = 0.0
        
        return df
    
    def create_sample_odc(self) -> pd.DataFrame:
        """Create sample ODC data"""
        from config import DEFAULT_PROJECT_PARAMS
        
        odc_data = []
        for i, period in enumerate(st.session_state.time_periods):
            amount = 472855.83 if i == 6 else 0.0
            odc_data.append({
                "Period": period, 
                "Amount": amount, 
                "Description": "Infrastructure Costs"
            })
        
        return pd.DataFrame(odc_data)
    
    def create_sample_tasks(self) -> pd.DataFrame:
        """Create sample task data"""
        from config import SAMPLE_TASKS
        
        return pd.DataFrame(SAMPLE_TASKS)
    
    def create_dashboard(self):
        """Create the main dashboard with refactored components"""
        self.render_header()
        self.render_sidebar()
        self.render_main_tabs()
    
    def render_header(self):
        """Render the application header"""
        st.markdown(f"""
        <div class="{CSS_CLASSES['main_header']}">
            <h1>{APP_CONFIG['icon']} {APP_CONFIG['title']}</h1>
            <div class="subtitle">{APP_CONFIG['subtitle']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """Render the sidebar with project parameters"""
        with st.sidebar:
            st.markdown(f"""
            <div style="background: {COLORS['primary']}; 
                        padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; 
                        box-shadow: 0 4px 12px rgba(46, 91, 186, 0.2);">
                <h3 style="color: white; margin: 0 0 1rem 0; text-align: center; font-weight: 600;">
                    ⚙️ Project Parameters
                </h3>
            </div>
            """, unsafe_allow_html=True)
            
            params = st.session_state.project_params
            # Handle current_date properly - it might be a string or datetime object
            if isinstance(params['current_date'], str):
                current_date_value = datetime.strptime(params['current_date'], '%Y-%m-%d').date()
            else:
                current_date_value = params['current_date']
            
            params['current_date'] = st.date_input("📅 Current Date", value=current_date_value)
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
    
    def render_main_tabs(self):
        """Render the main application tabs"""
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Overview", "👥 Direct Labor", "🏢 Subcontractors", "📊 Analysis", "📋 Tasks"
        ])
        
        with tab1:
            self.render_overview_tab()
        with tab2:
            self.render_direct_labor_tab()
        with tab3:
            self.render_subcontractor_tab()
        with tab4:
            self.render_analysis_tab()
        with tab5:
            self.render_tasks_tab()
    
    def render_overview_tab(self):
        """Render the overview tab with refactored components"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📊 Project Overview</div>', 
                   unsafe_allow_html=True)
        
        # Render metric cards
        self.render_overview_metrics()
        
        # Render financial summary
        self.render_financial_summary()
    
    def render_overview_metrics(self):
        """Render overview metric cards"""
        params = st.session_state.project_params
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        non_billable = params['non_billable_hours']
        billable_hours = actual_hours + non_billable
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            MetricCard.render("⏱️", f"{eac_hours:,.0f}", "EAC Hours")
        
        with col2:
            MetricCard.render("📈", f"{actual_hours:,.0f}", "Actual Hours")
        
        with col3:
            MetricCard.render("💼", f"{billable_hours:,.0f}", "Billable Hours")
        
        with col4:
            completion_pct = self.financial_calculator.calculate_completion_percentage(actual_hours, eac_hours)
            progress_color = COLORS['success'] if completion_pct >= 75 else COLORS['warning'] if completion_pct >= 50 else COLORS['danger']
            MetricCard.render("🎯", f"{completion_pct:.1f}%", "Completion", progress_color)
    
    def render_financial_summary(self):
        """Render financial summary cards"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">💰 Financial Summary</div>', 
                   unsafe_allow_html=True)
        
        # Calculate financial data
        financial_data = self.calculate_financial_summary()
        
        col1, col2 = st.columns(2)
        
        with col1:
            FinancialCard.render("💸 Costs Breakdown", financial_data['costs'])
        
        with col2:
            FinancialCard.render("📊 Revenue Analysis", financial_data['revenue'])
    
    def calculate_financial_summary(self) -> dict:
        """Calculate financial summary data"""
        employees_df = st.session_state.employees
        params = st.session_state.project_params
        
        # Calculate totals
        revenue_columns = [col for col in employees_df.columns if col.startswith('Revenue_')]
        total_direct_labor = employees_df[revenue_columns].sum().sum() if revenue_columns else 0
        
        total_odc = st.session_state.odc_costs['Amount'].sum()
        total_subcontractor = st.session_state.subcontractors[revenue_columns].sum().sum() if revenue_columns else 0
        
        # Create ProjectParameters object for calculations
        project_params = ProjectParameters(
            current_date=params['current_date'],
            eac_hours=params['eac_hours'],
            actual_hours=params['actual_hours'],
            non_billable_hours=params['non_billable_hours'],
            total_transaction_price=params['total_transaction_price'],
            fringe_rate=params['fringe_rate'],
            overhead_rate=params['overhead_rate'],
            ga_rate=params['ga_rate'],
            target_profit=params['target_profit']
        )
        
        indirect_costs = self.financial_calculator.calculate_indirect_costs(
            total_direct_labor, 
            project_params
        )
        
        total_costs = total_direct_labor + total_odc + total_subcontractor + indirect_costs['Total_Indirect']
        
        # Revenue calculation
        total_transaction_price = params['total_transaction_price']
        recalculated_revenue = (params['actual_hours'] / params['eac_hours']) * total_transaction_price if params['eac_hours'] > 0 else 0
        
        profit_loss = self.financial_calculator.calculate_profit_loss(recalculated_revenue, total_costs)
        profit_color = COLORS['success'] if profit_loss >= 0 else COLORS['danger']
        
        return {
            'costs': [
                {'label': '👥 Direct Labor', 'value': f"${total_direct_labor:,.2f}"},
                {'label': '🏗️ ODC', 'value': f"${total_odc:,.2f}"},
                {'label': '🤝 Subcontractor', 'value': f"${total_subcontractor:,.2f}"},
                {'label': '🎯 Fringe', 'value': f"${indirect_costs['Fringe']:,.2f}"},
                {'label': '🏢 Overhead', 'value': f"${indirect_costs['Overhead']:,.2f}"},
                {'label': '📈 G&A', 'value': f"${indirect_costs['G&A']:,.2f}"},
                {'label': 'Total Costs', 'value': f"${total_costs:,.2f}"}
            ],
            'revenue': [
                {'label': '💰 Total Transaction Price', 'value': f"${total_transaction_price:,.2f}"},
                {'label': '📈 Recalculated Revenue', 'value': f"${recalculated_revenue:,.2f}"},
                {'label': 'Profit/Loss', 'value': f"${profit_loss:,.2f}", 'color': profit_color}
            ]
        }
    
    def render_direct_labor_tab(self):
        """Render the direct labor tab"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">👥 Direct Labor Management</div>', 
                   unsafe_allow_html=True)
        
        # File upload section
        self.render_upload_section()
        
        # Employee management
        self.render_employee_management()
    
    def render_upload_section(self):
        """Render file upload section"""
        st.markdown(f"""
        <div class="{CSS_CLASSES['upload_section']}">
            <h3>📁 Upload Employee Data</h3>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose Excel/CSV file", type=['xlsx', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df_upload = pd.read_excel(uploaded_file)
                else:
                    df_upload = pd.read_csv(uploaded_file)
                
                SuccessMessage.render(f"Uploaded {len(df_upload)} rows of data")
                
                if st.button("Import Data"):
                    # Process and merge with existing data
                    st.session_state.employees = self.process_uploaded_employees(df_upload)
                    SuccessMessage.render("Data imported successfully!")
                    st.rerun()
                    
            except Exception as e:
                ErrorMessage.render(f"Error reading file: {str(e)}")
    
    def render_employee_management(self):
        """Render employee management interface"""
        # Add new employee
        col1, col2, col3 = FormSection.create_expandable("Add New Employee", 3)
        with col1:
            new_name = st.text_input("Name")
            new_lcat = st.selectbox("LCAT", options=LCAT_OPTIONS)
        with col2:
            new_priced_salary = st.number_input("Priced Salary", min_value=0, value=100000)
            new_current_salary = st.number_input("Current Salary", min_value=0, value=100000)
        with col3:
            new_hours_per_month = st.number_input("Hours per Month", min_value=0, value=173)
            
        if st.button("Add Employee") and new_name:
            self.add_new_employee(new_name, new_lcat, new_priced_salary, new_current_salary, new_hours_per_month)
        
        # Employee data editor
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">ℹ️ Employee Information</div>', 
                   unsafe_allow_html=True)
        
        basic_columns = ["Name", "LCAT", "Priced_Salary", "Current_Salary", "Hours_Per_Month", "Hourly_Rate"]
        column_configs = {
            "Priced_Salary": st.column_config.NumberColumn("Priced Salary", format="$%.2f"),
            "Current_Salary": st.column_config.NumberColumn("Current Salary", format="$%.2f"),
            "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
        }
        
        edited_basic = DataTable.render(
            st.session_state.employees,
            basic_columns,
            column_configs,
            "basic_employee_data",
            'stretch'
        )
        
        # Update the main dataframe
        for col in basic_columns:
            st.session_state.employees[col] = edited_basic[col]
        
        # Employee removal interface
        self.render_employee_removal()
    
    def render_employee_removal(self):
        """Render employee removal interface"""
        employees_df = st.session_state.employees
        
        def employee_display(emp):
            return emp['Name']
        
        def employee_details(emp):
            return {
                'LCAT': emp['LCAT'],
                'Current Salary': f"${emp['Current_Salary']:,.2f}",
                'Hours/Month': f"{emp['Hours_Per_Month']}"
            }
        
        def remove_employee(emp):
            st.session_state.employees = st.session_state.employees[
                st.session_state.employees['Name'] != emp['Name']
            ]
        
        bulk_operations = [
            {
                'type': 'select',
                'label': 'Remove all employees by Labor Category:',
                'options': employees_df['LCAT'].unique().tolist(),
                'key': 'lcat_select',
                'button_text': '🗑️ Remove All by LCAT',
                'action': lambda lcat: self.bulk_remove_employees_by_lcat(lcat)
            },
            {
                'type': 'button',
                'key': 'clear_all',
                'button_text': '🗑️ Clear All Employees',
                'action': lambda _: self.clear_all_employees()
            }
        ]
        
        RemovalInterface.render(
            "Remove Employees",
            employees_df.to_dict('records'),
            employee_display,
            employee_details,
            remove_employee,
            len(employees_df),
            bulk_operations
        )
    
    def add_new_employee(self, name, lcat, priced_salary, current_salary, hours_per_month):
        """Add a new employee"""
        new_employee = {
            "Name": name,
            "LCAT": lcat,
            "Priced_Salary": priced_salary,
            "Current_Salary": current_salary,
            "Hours_Per_Month": hours_per_month,
            "Hourly_Rate": self.financial_calculator.calculate_hourly_rate(current_salary, hours_per_month)
        }
        
        # Add columns for time periods
        for period in st.session_state.time_periods:
            new_employee[f'Hours_{period}'] = 0.0
            new_employee[f'Revenue_{period}'] = 0.0
        
        # Add to dataframe
        new_row = pd.DataFrame([new_employee])
        st.session_state.employees = pd.concat([st.session_state.employees, new_row], ignore_index=True)
        SuccessMessage.render(f"Added {name} to employee list")
        st.rerun()
    
    def bulk_remove_employees_by_lcat(self, lcat):
        """Remove all employees by LCAT"""
        lcat_count = len(st.session_state.employees[st.session_state.employees['LCAT'] == lcat])
        st.session_state.employees = st.session_state.employees[
            st.session_state.employees['LCAT'] != lcat
        ]
        SuccessMessage.render(f"Removed {lcat_count} employees with LCAT: {lcat}")
    
    def clear_all_employees(self):
        """Clear all employees"""
        employee_count = len(st.session_state.employees)
        st.session_state.employees = pd.DataFrame(columns=st.session_state.employees.columns)
        SuccessMessage.render(f"Cleared all {employee_count} employees from the project")
    
    def process_uploaded_employees(self, df_upload: pd.DataFrame) -> pd.DataFrame:
        """Process uploaded employee data"""
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
            ErrorMessage.render(f"Missing required columns: {missing_cols}")
            return st.session_state.employees
        
        # Add default values for missing columns
        if 'Priced_Salary' not in df_upload.columns:
            df_upload['Priced_Salary'] = df_upload['Current_Salary']
        if 'Hours_Per_Month' not in df_upload.columns:
            df_upload['Hours_Per_Month'] = 173
        
        # Calculate hourly rates
        df_upload['Hourly_Rate'] = df_upload.apply(
            lambda row: self.financial_calculator.calculate_hourly_rate(
                row['Current_Salary'], row['Hours_Per_Month']
            ), axis=1
        )
        
        # Add time period columns
        for period in st.session_state.time_periods:
            df_upload[f'Hours_{period}'] = 0.0
            df_upload[f'Revenue_{period}'] = 0.0
        
        return df_upload
    
    def render_subcontractor_tab(self):
        """Render the subcontractor tab"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">🏢 Subcontractor Management</div>', 
                   unsafe_allow_html=True)
        
        # Add new subcontractor
        col1, col2, col3 = FormSection.create_expandable("Add New Subcontractor", 3)
        with col1:
            new_name = st.text_input("Subcontractor Name")
            new_company = st.text_input("Company")
        with col2:
            new_lcat = st.text_input("LCAT/Role")
            new_hourly_rate = st.number_input("Hourly Rate", min_value=0.0, value=100.0)
        with col3:
            if st.button("Add Subcontractor") and new_name:
                self.add_new_subcontractor(new_name, new_company, new_lcat, new_hourly_rate)
        
        # Subcontractor data editor
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">ℹ️ Subcontractor Information</div>', 
                       unsafe_allow_html=True)
            
            basic_columns = ["Name", "Company", "LCAT", "Hourly_Rate"]
            column_configs = {
                "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
            }
            
            edited_basic = DataTable.render(
                sub_df,
                basic_columns,
                column_configs,
                "basic_subcontractor_data",
                'stretch'
            )
            
            # Update main dataframe
            for col in basic_columns:
                st.session_state.subcontractors[col] = edited_basic[col]
            
            # Subcontractor removal interface
            self.render_subcontractor_removal()
            
            # Monthly hours for subcontractors
            st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📅 Subcontractor Monthly Hours</div>', 
                       unsafe_allow_html=True)
            
            # Show fewer periods at a time for better usability
            selected_periods = st.multiselect(
                "Select periods to edit",
                st.session_state.time_periods,
                default=st.session_state.time_periods[:6]
            )
            
            if selected_periods:
                hours_columns = [f'Hours_{period}' for period in selected_periods]
                hours_data = sub_df[["Name"] + hours_columns].copy()
                
                edited_hours = DataTable.render(
                    hours_data,
                    ["Name"] + hours_columns,
                    {col: st.column_config.NumberColumn(period, format="%.1f") 
                     for col, period in zip(hours_columns, selected_periods)},
                    "subcontractor_hours",
                    'stretch'
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
    
    def render_subcontractor_removal(self):
        """Render subcontractor removal interface"""
        sub_df = st.session_state.subcontractors
        
        def subcontractor_display(sub):
            return sub['Name']
        
        def subcontractor_details(sub):
            return {
                'Company': sub['Company'],
                'LCAT': sub['LCAT'],
                'Rate': f"${sub['Hourly_Rate']:.2f}/hr"
            }
        
        def remove_subcontractor(sub):
            st.session_state.subcontractors = st.session_state.subcontractors[
                st.session_state.subcontractors['Name'] != sub['Name']
            ]
        
        bulk_operations = [
            {
                'type': 'select',
                'label': 'Remove all subcontractors by Company:',
                'options': sub_df['Company'].unique().tolist(),
                'key': 'company_select',
                'button_text': '🗑️ Remove All by Company',
                'action': lambda company: self.bulk_remove_subcontractors_by_company(company)
            },
            {
                'type': 'button',
                'key': 'clear_all_subcontractors',
                'button_text': '🗑️ Clear All Subcontractors',
                'action': lambda _: self.clear_all_subcontractors()
            }
        ]
        
        RemovalInterface.render(
            "Remove Subcontractors",
            sub_df.to_dict('records'),
            subcontractor_display,
            subcontractor_details,
            remove_subcontractor,
            len(sub_df),
            bulk_operations
        )
    
    def add_new_subcontractor(self, name, company, lcat, hourly_rate):
        """Add a new subcontractor"""
        new_sub = {
            "Name": name,
            "Company": company,
            "LCAT": lcat,
            "Hourly_Rate": hourly_rate
        }
        
        # Add time period columns
        for period in st.session_state.time_periods:
            new_sub[f'Hours_{period}'] = 0.0
            new_sub[f'Revenue_{period}'] = 0.0
        
        new_row = pd.DataFrame([new_sub])
        st.session_state.subcontractors = pd.concat([st.session_state.subcontractors, new_row], ignore_index=True)
        SuccessMessage.render(f"Added {name} to subcontractor list")
        st.rerun()
    
    def bulk_remove_subcontractors_by_company(self, company):
        """Remove all subcontractors by company"""
        company_count = len(st.session_state.subcontractors[st.session_state.subcontractors['Company'] == company])
        st.session_state.subcontractors = st.session_state.subcontractors[
            st.session_state.subcontractors['Company'] != company
        ]
        SuccessMessage.render(f"Removed {company_count} subcontractors from company: {company}")
    
    def clear_all_subcontractors(self):
        """Clear all subcontractors"""
        subcontractor_count = len(st.session_state.subcontractors)
        st.session_state.subcontractors = pd.DataFrame(columns=st.session_state.subcontractors.columns)
        SuccessMessage.render(f"Cleared all {subcontractor_count} subcontractors from the project")
    
    def render_analysis_tab(self):
        """Render the analysis tab"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📊 Financial Analysis & Visualizations</div>', 
                   unsafe_allow_html=True)
        
        # Monthly revenue trends
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📈 Monthly Revenue Trends</div>', 
                   unsafe_allow_html=True)
        
        revenue_df = self.report_generator.generate_monthly_revenue_report(
            st.session_state.employees, 
            st.session_state.time_periods
        )
        
        if not revenue_df.empty:
            fig = px.line(revenue_df, x='Period', y='Revenue', 
                         title='Direct Labor Revenue by Month',
                         color_discrete_sequence=[COLORS['primary']])
            fig.update_layout(
                xaxis_tickangle=45,
                plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
                paper_bgcolor=CHART_CONFIG['paper_bgcolor'],
                font=dict(size=CHART_CONFIG['font_size']),
                margin=CHART_CONFIG['margin']
            )
            st.plotly_chart(fig, width='stretch')
        
        # Employee utilization heatmap
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">🔥 Employee Hours Heatmap</div>', 
                   unsafe_allow_html=True)
        
        hours_columns = [col for col in st.session_state.employees.columns if col.startswith('Hours_')]
        if hours_columns:
            heatmap_data = st.session_state.employees[['Name'] + hours_columns].set_index('Name')
            
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
                plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
                paper_bgcolor=CHART_CONFIG['paper_bgcolor'],
                font=dict(size=CHART_CONFIG['font_size']),
                margin=CHART_CONFIG['margin']
            )
            st.plotly_chart(fig, width='stretch')
        
        # Cost analysis by LCAT
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">💰 Cost Analysis by Labor Category</div>', 
                   unsafe_allow_html=True)
        
        lcat_revenue = self.report_generator.generate_lcat_summary(st.session_state.employees)
        
        if not lcat_revenue.empty:
            fig = px.bar(lcat_revenue, x='LCAT', y='Total_Revenue',
                        title='Total Revenue by Labor Category',
                        color_discrete_sequence=[COLORS['primary']])
            fig.update_layout(
                xaxis_tickangle=45,
                plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
                paper_bgcolor=CHART_CONFIG['paper_bgcolor'],
                font=dict(size=CHART_CONFIG['font_size']),
                margin=CHART_CONFIG['margin']
            )
            st.plotly_chart(fig, width='stretch')
        
        # Burn rate analysis
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">⚡ Project Burn Rate Analysis</div>', 
                   unsafe_allow_html=True)
        
        burn_rate_data = self.report_generator.generate_burn_rate_analysis(
            st.session_state.employees, 
            st.session_state.time_periods
        )
        
        if burn_rate_data['periods']:
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=burn_rate_data['periods'], y=burn_rate_data['cumulative_hours'], 
                           name="Cumulative Hours"),
                secondary_y=False,
            )
            
            fig.add_trace(
                go.Scatter(x=burn_rate_data['periods'], y=burn_rate_data['cumulative_costs'], 
                           name="Cumulative Costs"),
                secondary_y=True,
            )
            
            fig.update_xaxes(title_text="Period", tickangle=45)
            fig.update_yaxes(title_text="Hours", secondary_y=False)
            fig.update_yaxes(title_text="Costs ($)", secondary_y=True)
            fig.update_layout(
                title_text="Cumulative Hours and Costs",
                plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
                paper_bgcolor=CHART_CONFIG['paper_bgcolor'],
                font=dict(size=CHART_CONFIG['font_size']),
                margin=CHART_CONFIG['margin']
            )
            
            st.plotly_chart(fig, width='stretch')
    
    def render_tasks_tab(self):
        """Render the tasks tab"""
        st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📋 Task Breakdown Management</div>', 
                   unsafe_allow_html=True)
        
        # Add new task
        col1, col2, col3 = FormSection.create_expandable("Add New Task", 3)
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
            self.add_new_task(new_task_id, new_task_name, new_lcat, new_person_org, new_person, new_hours, new_cost)
        
        # Display and edit tasks
        tasks_df = st.session_state.tasks
        
        if not tasks_df.empty:
            st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📝 Task Details</div>', 
                       unsafe_allow_html=True)
            
            column_configs = {
                "Hours": st.column_config.NumberColumn("Hours", format="%.2f"),
                "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
            }
            
            edited_tasks = DataTable.render(
                tasks_df,
                list(tasks_df.columns),
                column_configs,
                "tasks_data",
                'stretch'
            )
            
            st.session_state.tasks = edited_tasks
            
            # Task removal interface
            self.render_task_removal()
            
            # Task summary by ID
            st.markdown(f'<div class="{CSS_CLASSES["subheader"]}">📊 Task Summary</div>', 
                       unsafe_allow_html=True)
            
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
                            color_discrete_sequence=[COLORS['primary']])
                fig.update_layout(
                    plot_bgcolor=CHART_CONFIG['plot_bgcolor'],
                    paper_bgcolor=CHART_CONFIG['paper_bgcolor'],
                    font=dict(size=CHART_CONFIG['font_size']),
                    margin=CHART_CONFIG['margin']
                )
                st.plotly_chart(fig, width='stretch')
    
    def render_task_removal(self):
        """Render task removal interface"""
        tasks_df = st.session_state.tasks
        
        def task_display(task):
            return f"{task['Task_ID']} - {task['Task_Name']}"
        
        def task_details(task):
            return {
                'Task Name': task['Task_Name'],
                'LCAT': task['LCAT'],
                'Person': task['Person'],
                'Hours': f"{task['Hours']:.2f}",
                'Cost': f"${task['Cost']:.2f}"
            }
        
        def remove_task(task):
            st.session_state.tasks = st.session_state.tasks[
                st.session_state.tasks['Task_ID'] != task['Task_ID']
            ]
        
        bulk_operations = [
            {
                'type': 'select',
                'label': 'Remove all tasks by Task ID:',
                'options': tasks_df['Task_ID'].unique().tolist(),
                'key': 'task_id_select',
                'button_text': '🗑️ Remove All by Task ID',
                'action': lambda task_id: self.bulk_remove_tasks_by_id(task_id)
            },
            {
                'type': 'button',
                'key': 'clear_all_tasks',
                'button_text': '🗑️ Clear All Tasks',
                'action': lambda _: self.clear_all_tasks()
            }
        ]
        
        RemovalInterface.render(
            "Remove Tasks",
            tasks_df.to_dict('records'),
            task_display,
            task_details,
            remove_task,
            len(tasks_df),
            bulk_operations
        )
    
    def add_new_task(self, task_id, task_name, lcat, person_org, person, hours, cost):
        """Add a new task"""
        new_task = {
            "Task_ID": task_id,
            "Task_Name": task_name,
            "LCAT": lcat,
            "Person_Org": person_org,
            "Person": person,
            "Hours": hours,
            "Cost": cost
        }
        
        new_row = pd.DataFrame([new_task])
        st.session_state.tasks = pd.concat([st.session_state.tasks, new_row], ignore_index=True)
        SuccessMessage.render(f"Added task {task_id}")
        st.rerun()
    
    def bulk_remove_tasks_by_id(self, task_id):
        """Remove all tasks by task ID"""
        task_id_count = len(st.session_state.tasks[st.session_state.tasks['Task_ID'] == task_id])
        st.session_state.tasks = st.session_state.tasks[
            st.session_state.tasks['Task_ID'] != task_id
        ]
        SuccessMessage.render(f"Removed {task_id_count} tasks with Task ID: {task_id}")
    
    def clear_all_tasks(self):
        """Clear all tasks"""
        task_count = len(st.session_state.tasks)
        st.session_state.tasks = pd.DataFrame(columns=st.session_state.tasks.columns)
        SuccessMessage.render(f"Cleared all {task_count} tasks from the project")

def main():
    """Main application function"""
    tracker = SEASFinancialTrackerRefactored()
    tracker.create_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown("SEAS Financial Tracker - Built with Streamlit 📊")

if __name__ == "__main__":
    main()
