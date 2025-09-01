import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
from typing import Dict, List, Tuple, Optional
import base64

# Set page config
st.set_page_config(
    page_title="SEAS Financial Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SEASFinancialTracker:
    def __init__(self):
        self.initialize_session_state()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'employees' not in st.session_state:
            st.session_state.employees = self.create_sample_employees()
        if 'subcontractors' not in st.session_state:
            st.session_state.subcontractors = self.create_sample_subcontractors()
        if 'odc_costs' not in st.session_state:
            st.session_state.odc_costs = self.create_sample_odc()
        if 'tasks' not in st.session_state:
            st.session_state.tasks = self.create_sample_tasks()
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
        if 'time_periods' not in st.session_state:
            st.session_state.time_periods = self.generate_time_periods()

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
            {"Name": "Shannon Gueringer", "LCAT": "PM", "Priced_Salary": 160000, "Current_Salary": 200000, "Hours_Per_Month": 173},
            {"Name": "Drew Hynes", "LCAT": "PM", "Priced_Salary": 0, "Current_Salary": 0, "Hours_Per_Month": 173},
            {"Name": "Uyen Tran", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 175000, "Hours_Per_Month": 173},
            {"Name": "Leo Khan", "LCAT": "SA/Eng Lead", "Priced_Salary": 180000, "Current_Salary": 190000, "Hours_Per_Month": 173},
            {"Name": "Vitaliy Baklikov", "LCAT": "AI Lead", "Priced_Salary": 200000, "Current_Salary": 250000, "Hours_Per_Month": 173},
            {"Name": "Kenny Tran/Lynn Stahl", "LCAT": "HCD Lead", "Priced_Salary": 130000, "Current_Salary": 150000, "Hours_Per_Month": 173},
            {"Name": "Emilio Crocco", "LCAT": "Scrum Master", "Priced_Salary": 110000, "Current_Salary": 110000, "Hours_Per_Month": 173},
            {"Name": "Robert Melton", "LCAT": "SA/Eng Lead", "Priced_Salary": 230000, "Current_Salary": 225000, "Hours_Per_Month": 173},
            {"Name": "Nayeema Nageen", "LCAT": "Scrum Master", "Priced_Salary": 140000, "Current_Salary": 140000, "Hours_Per_Month": 173},
            {"Name": "Daniil Goryachev", "LCAT": "Cloud Data Engineer", "Priced_Salary": 90000, "Current_Salary": 90000, "Hours_Per_Month": 173},
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
        st.title("📊 SEAS Project Financial Tracker")
        
        # Sidebar for project parameters
        with st.sidebar:
            st.header("Project Parameters")
            
            params = st.session_state.project_params
            params['current_date'] = st.date_input("Current Date", params['current_date'])
            params['total_transaction_price'] = st.number_input("Total Transaction Price ($)", 
                                                              value=params['total_transaction_price'], 
                                                              format="%.2f")
            params['fringe_rate'] = st.number_input("Fringe Rate", value=params['fringe_rate'], 
                                                   format="%.3f", step=0.001)
            params['overhead_rate'] = st.number_input("Overhead Rate", value=params['overhead_rate'], 
                                                     format="%.3f", step=0.001)
            params['ga_rate'] = st.number_input("G&A Rate", value=params['ga_rate'], 
                                               format="%.3f", step=0.001)
            params['target_profit'] = st.number_input("Target Profit Margin", value=params['target_profit'], 
                                                     format="%.4f", step=0.0001)

        # Main tabs
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
        st.header("Project Overview")
        
        # Key metrics
        params = st.session_state.project_params
        actual_hours = params['actual_hours']
        eac_hours = params['eac_hours']
        non_billable = params['non_billable_hours']
        billable_hours = actual_hours + non_billable
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("EAC Hours", f"{eac_hours:,.2f}")
            
        with col2:
            st.metric("Actual Hours to Date", f"{actual_hours:,.2f}")
            
        with col3:
            st.metric("Billable Hours", f"{billable_hours:,.2f}")
            
        with col4:
            completion_pct = (actual_hours / eac_hours) * 100 if eac_hours > 0 else 0
            st.metric("Completion %", f"{completion_pct:.1f}%")

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
        
        # Financial summary
        st.subheader("Financial Summary")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Costs Breakdown:**")
            st.write(f"Direct Labor: ${total_direct_labor:,.2f}")
            st.write(f"ODC: ${total_odc:,.2f}")
            st.write(f"Subcontractor: ${total_subcontractor:,.2f}")
            st.write(f"Fringe: ${indirect_costs['Fringe']:,.2f}")
            st.write(f"Overhead: ${indirect_costs['Overhead']:,.2f}")
            st.write(f"G&A: ${indirect_costs['G&A']:,.2f}")
            st.write(f"**Total Costs: ${total_costs:,.2f}**")
            
        with col2:
            st.write("**Revenue Analysis:**")
            st.write(f"Total Transaction Price: ${total_transaction_price:,.2f}")
            st.write(f"Recalculated Revenue: ${recalculated_revenue:,.2f}")
            profit_loss = recalculated_revenue - total_costs
            st.write(f"**Profit/Loss: ${profit_loss:,.2f}**")
            
            if recalculated_revenue > 0:
                margin = (profit_loss / recalculated_revenue) * 100
                st.write(f"Profit Margin: {margin:.2f}%")

        # Cost breakdown chart
        cost_data = {
            'Category': ['Direct Labor', 'ODC', 'Subcontractor', 'Fringe', 'Overhead', 'G&A'],
            'Amount': [total_direct_labor, total_odc, total_subcontractor, 
                      indirect_costs['Fringe'], indirect_costs['Overhead'], indirect_costs['G&A']]
        }
        
        fig = px.pie(pd.DataFrame(cost_data), values='Amount', names='Category', 
                     title="Cost Breakdown by Category")
        st.plotly_chart(fig, use_container_width=True)

    def create_direct_labor_tab(self):
        """Create direct labor management tab"""
        st.header("Direct Labor Management")
        
        # File upload
        st.subheader("Upload Employee Data")
        uploaded_file = st.file_uploader("Choose Excel/CSV file", type=['xlsx', 'csv'])
        
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith('.xlsx'):
                    df_upload = pd.read_excel(uploaded_file)
                else:
                    df_upload = pd.read_csv(uploaded_file)
                st.success(f"Uploaded {len(df_upload)} rows of data")
                
                if st.button("Import Data"):
                    # Process and merge with existing data
                    st.session_state.employees = self.process_uploaded_employees(df_upload)
                    st.success("Data imported successfully!")
                    st.experimental_rerun()
                    
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")

        # Employee data editor
        st.subheader("Employee Data")
        
        # Add new employee
        with st.expander("Add New Employee"):
            col1, col2, col3 = st.columns(3)
            with col1:
                new_name = st.text_input("Name")
                new_lcat = st.selectbox("LCAT", ["PM", "SA/Eng Lead", "AI Lead", "HCD Lead", 
                                                "Scrum Master", "Cloud Data Engineer", "SRE", "Full Stack Dev"])
            with col2:
                new_priced_salary = st.number_input("Priced Salary", min_value=0, value=100000)
                new_current_salary = st.number_input("Current Salary", min_value=0, value=100000)
            with col3:
                new_hours_per_month = st.number_input("Hours per Month", min_value=0, value=173)
                
            if st.button("Add Employee") and new_name:
                new_employee = {
                    "Name": new_name,
                    "LCAT": new_lcat,
                    "Priced_Salary": new_priced_salary,
                    "Current_Salary": new_current_salary,
                    "Hours_Per_Month": new_hours_per_month,
                    "Hourly_Rate": self.calculate_hourly_rate(new_current_salary, new_hours_per_month)
                }
                
                # Add columns for time periods
                for period in st.session_state.time_periods:
                    new_employee[f'Hours_{period}'] = 0.0
                    new_employee[f'Revenue_{period}'] = 0.0
                
                # Add to dataframe
                new_row = pd.DataFrame([new_employee])
                st.session_state.employees = pd.concat([st.session_state.employees, new_row], 
                                                      ignore_index=True)
                st.success(f"Added {new_name} to employee list")
                st.experimental_rerun()

        # Display and edit employee data
        employees_df = st.session_state.employees
        
        # Basic employee info
        st.subheader("Employee Information")
        basic_columns = ["Name", "LCAT", "Priced_Salary", "Current_Salary", "Hours_Per_Month", "Hourly_Rate"]
        
        edited_basic = st.data_editor(
            employees_df[basic_columns],
            column_config={
                "Priced_Salary": st.column_config.NumberColumn("Priced Salary", format="$%.2f"),
                "Current_Salary": st.column_config.NumberColumn("Current Salary", format="$%.2f"),
                "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
            },
            use_container_width=True,
            key="basic_employee_data"
        )
        
        # Update the main dataframe
        for col in basic_columns:
            st.session_state.employees[col] = edited_basic[col]
        
        # Update calculations
        self.update_employee_calculations()
        
        # Monthly hours input - show in sections
        st.subheader("Monthly Hours (Base Year)")
        base_year_periods = st.session_state.time_periods[:12]
        base_year_columns = [f'Hours_{period}' for period in base_year_periods]
        
        if all(col in employees_df.columns for col in base_year_columns):
            base_year_data = employees_df[["Name"] + base_year_columns].copy()
            
            edited_base_year = st.data_editor(
                base_year_data,
                column_config={col: st.column_config.NumberColumn(period, format="%.1f") 
                              for col, period in zip(base_year_columns, base_year_periods)},
                use_container_width=True,
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
                    use_container_width=True,
                    key="oy1_hours"
                )
                
                # Update main dataframe
                for col in oy1_columns:
                    st.session_state.employees[col] = edited_oy1[col]
        
        # Final calculations update
        self.update_employee_calculations()
        
        # Export functionality
        st.subheader("Export Data")
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

    def create_subcontractor_tab(self):
        """Create subcontractor management tab"""
        st.header("Subcontractor Management")
        
        # Add new subcontractor
        with st.expander("Add New Subcontractor"):
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
                    st.experimental_rerun()

        # Subcontractor data editor
        sub_df = st.session_state.subcontractors
        
        if not sub_df.empty:
            st.subheader("Subcontractor Information")
            basic_columns = ["Name", "Company", "LCAT", "Hourly_Rate"]
            
            edited_basic = st.data_editor(
                sub_df[basic_columns],
                column_config={
                    "Hourly_Rate": st.column_config.NumberColumn("Hourly Rate", format="$%.2f"),
                },
                use_container_width=True,
                key="basic_subcontractor_data"
            )
            
            # Update main dataframe
            for col in basic_columns:
                st.session_state.subcontractors[col] = edited_basic[col]
            
            # Monthly hours for subcontractors
            st.subheader("Subcontractor Monthly Hours")
            
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
                    use_container_width=True,
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
        st.subheader("Other Direct Costs (ODC)")
        
        odc_df = st.session_state.odc_costs
        
        edited_odc = st.data_editor(
            odc_df,
            column_config={
                "Amount": st.column_config.NumberColumn("Amount", format="$%.2f"),
            },
            use_container_width=True,
            key="odc_data"
        )
        
        st.session_state.odc_costs = edited_odc

    def create_analysis_tab(self):
        """Create analysis and visualization tab"""
        st.header("Financial Analysis & Visualizations")
        
        # Monthly revenue trends
        st.subheader("Monthly Revenue Trends")
        
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
                         title='Direct Labor Revenue by Month')
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Employee utilization heatmap
        st.subheader("Employee Hours Heatmap")
        
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
                           title="Employee Hours by Month")
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Cost analysis by LCAT
        st.subheader("Cost Analysis by Labor Category")
        
        lcat_revenue = employees_df.groupby('LCAT').agg({
            col: 'sum' for col in employees_df.columns if col.startswith('Revenue_')
        }).sum(axis=1).reset_index()
        lcat_revenue.columns = ['LCAT', 'Total_Revenue']
        
        if not lcat_revenue.empty:
            fig = px.bar(lcat_revenue, x='LCAT', y='Total_Revenue',
                        title='Total Revenue by Labor Category')
            fig.update_xaxis(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        # Burn rate analysis
        st.subheader("Project Burn Rate Analysis")
        
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
            fig.update_layout(title_text="Cumulative Hours and Costs")
            
            st.plotly_chart(fig, use_container_width=True)

    def create_tasks_tab(self):
        """Create task management tab"""
        st.header("Task Breakdown Management")
        
        # Task data editor
        tasks_df = st.session_state.tasks
        
        # Add new task
        with st.expander("Add New Task"):
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
                st.experimental_rerun()

        # Display and edit tasks
        if not tasks_df.empty:
            st.subheader("Task Details")
            
            edited_tasks = st.data_editor(
                tasks_df,
                column_config={
                    "Hours": st.column_config.NumberColumn("Hours", format="%.2f"),
                    "Cost": st.column_config.NumberColumn("Cost", format="$%.2f"),
                },
                use_container_width=True,
                key="tasks_data"
            )
            
            st.session_state.tasks = edited_tasks
            
            # Task summary by ID
            st.subheader("Task Summary")
            
            task_summary = edited_tasks.groupby(['Task_ID', 'Task_Name']).agg({
                'Hours': 'sum',
                'Cost': 'sum'
            }).reset_index()
            
            st.dataframe(task_summary, use_container_width=True)
            
            # Task cost visualization
            if not task_summary.empty:
                fig = px.bar(task_summary, x='Task_ID', y='Cost',
                            title='Cost by Task ID',
                            hover_data=['Task_Name', 'Hours'])
                st.plotly_chart(fig, use_container_width=True)

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
            st.error(f"Missing required columns: {missing_cols}")
            return st.session_state.employees
        
        # Add default values for missing columns
        if 'Priced_Salary' not in df_upload.columns:
            df_upload['Priced_Salary'] = df_upload['Current_Salary']
        if 'Hours_Per_Month' not in df_upload.columns:
            df_upload['Hours_Per_Month'] = 173
        
        # Calculate hourly rates
        df_upload['Hourly_Rate'] = df_upload.apply(
            lambda row: self.calculate_hourly_rate(row['Current_Salary'], row['Hours_Per_Month']), 
            axis=1
        )
        
        # Add time period columns
        for period in st.session_state.time_periods:
            df_upload[f'Hours_{period}'] = 0.0
            df_upload[f'Revenue_{period}'] = 0.0
        
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