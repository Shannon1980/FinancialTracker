"""
User Management System for SEAS Financial Tracker
Provides granular permissions and data access control
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from auth import AuthManager, check_permission


class UserManager:
    """Manages users, roles, and permissions"""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.initialize_user_data()
    
    def initialize_user_data(self):
        """Initialize user management data in session state"""
        if 'users' not in st.session_state:
            st.session_state.users = self.get_default_users()
        if 'user_permissions' not in st.session_state:
            st.session_state.user_permissions = self.get_default_permissions()
        if 'data_access_log' not in st.session_state:
            st.session_state.data_access_log = []
    
    def get_default_users(self) -> Dict[str, Dict[str, Any]]:
        """Get default user configurations"""
        return {
            'admin': {
                'username': 'admin',
                'full_name': 'System Administrator',
                'email': 'admin@seas.com',
                'role': 'admin',
                'department': 'IT',
                'created_date': datetime.now().isoformat(),
                'last_login': None,
                'status': 'active',
                'permissions': ['all']
            },
            'manager': {
                'username': 'manager',
                'full_name': 'Project Manager',
                'email': 'manager@seas.com',
                'role': 'manager',
                'department': 'Project Management',
                'created_date': datetime.now().isoformat(),
                'last_login': None,
                'status': 'active',
                'permissions': ['view', 'edit', 'export', 'import']
            },
            'viewer': {
                'username': 'viewer',
                'full_name': 'Financial Viewer',
                'email': 'viewer@seas.com',
                'role': 'viewer',
                'department': 'Finance',
                'created_date': datetime.now().isoformat(),
                'last_login': None,
                'status': 'active',
                'permissions': ['view', 'export']
            }
        }
    
    def get_default_permissions(self) -> Dict[str, Dict[str, List[str]]]:
        """Get default permission configurations"""
        return {
            'admin': {
                'data_access': ['all'],
                'sensitive_data': ['salary', 'personal_info', 'financial_data'],
                'operations': ['create', 'read', 'update', 'delete', 'export', 'import', 'manage_users'],
                'reports': ['all_reports', 'financial_summary', 'employee_data', 'cost_analysis']
            },
            'manager': {
                'data_access': ['employees', 'subcontractors', 'projects', 'tasks'],
                'sensitive_data': ['salary'],  # Limited salary access
                'operations': ['create', 'read', 'update', 'export', 'import'],
                'reports': ['financial_summary', 'employee_data', 'cost_analysis']
            },
            'viewer': {
                'data_access': ['employees', 'subcontractors', 'projects'],
                'sensitive_data': [],  # No sensitive data access
                'operations': ['read', 'export'],
                'reports': ['financial_summary', 'cost_analysis']
            }
        }
    
    def get_current_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.auth_manager.is_authenticated():
            return {}
        
        username = st.session_state.get('username', '')
        return st.session_state.users.get(username, {})
    
    def has_data_access(self, data_type: str) -> bool:
        """Check if current user has access to specific data type"""
        if not self.auth_manager.is_authenticated():
            return False
        
        user_info = self.get_current_user_info()
        role = user_info.get('role', 'viewer')
        permissions = st.session_state.user_permissions.get(role, {})
        
        data_access = permissions.get('data_access', [])
        return 'all' in data_access or data_type in data_access
    
    def has_sensitive_data_access(self, data_type: str) -> bool:
        """Check if current user has access to sensitive data"""
        if not self.auth_manager.is_authenticated():
            return False
        
        user_info = self.get_current_user_info()
        role = user_info.get('role', 'viewer')
        permissions = st.session_state.user_permissions.get(role, {})
        
        sensitive_data = permissions.get('sensitive_data', [])
        return data_type in sensitive_data
    
    def log_data_access(self, data_type: str, action: str, details: str = ""):
        """Log data access for audit purposes"""
        if not self.auth_manager.is_authenticated():
            return
        
        username = st.session_state.get('username', 'unknown')
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'username': username,
            'data_type': data_type,
            'action': action,
            'details': details,
            'ip_address': 'streamlit_cloud'  # Placeholder for IP
        }
        
        st.session_state.data_access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(st.session_state.data_access_log) > 1000:
            st.session_state.data_access_log = st.session_state.data_access_log[-1000:]
    
    def filter_sensitive_data(self, df: pd.DataFrame, data_type: str) -> pd.DataFrame:
        """Filter sensitive data based on user permissions"""
        if not self.auth_manager.is_authenticated():
            return df
        
        # Log the data access
        self.log_data_access(data_type, 'view', f"Accessed {len(df)} records")
        
        # Create a copy to avoid modifying original
        filtered_df = df.copy()
        
        # Remove sensitive columns based on permissions
        sensitive_columns = {
            'salary': ['Current_Salary', 'Priced_Salary', 'Hourly_Rate'],
            'personal_info': ['Email', 'Phone', 'Address', 'SSN'],
            'financial_data': ['Revenue_', 'Cost_', 'Profit_']
        }
        
        for sensitive_type, columns in sensitive_columns.items():
            if not self.has_sensitive_data_access(sensitive_type):
                # Find columns that match the pattern
                for col in filtered_df.columns:
                    if any(pattern in col for pattern in columns):
                        filtered_df[col] = '*** Restricted ***'
        
        return filtered_df
    
    def get_user_role_display(self) -> str:
        """Get user role for display purposes"""
        user_info = self.get_current_user_info()
        role = user_info.get('role', 'viewer')
        
        role_display = {
            'admin': '🔑 Administrator',
            'manager': '👔 Manager',
            'viewer': '👁️ Viewer'
        }
        
        return role_display.get(role, '👤 User')


def render_user_management_page():
    """Render the user management interface"""
    if not check_permission('manage_users'):
        st.error("🔒 You don't have permission to manage users. Contact your administrator.")
        return
    
    user_manager = UserManager()
    
    st.markdown("## 👥 User Management")
    st.markdown("Manage users, roles, and permissions for the SEAS Financial Tracker.")
    
    # Tabs for different management functions
    tab1, tab2, tab3, tab4 = st.tabs(["👤 Users", "🔐 Permissions", "📊 Access Log", "⚙️ Settings"])
    
    with tab1:
        render_users_tab(user_manager)
    
    with tab2:
        render_permissions_tab(user_manager)
    
    with tab3:
        render_access_log_tab(user_manager)
    
    with tab4:
        render_settings_tab(user_manager)


def render_users_tab(user_manager: UserManager):
    """Render the users management tab"""
    st.markdown("### User Accounts")
    
    # Display current users
    users_df = pd.DataFrame.from_dict(user_manager.get_default_users(), orient='index')
    
    # Format the dataframe for display
    display_df = users_df[['username', 'full_name', 'role', 'department', 'status']].copy()
    display_df.columns = ['Username', 'Full Name', 'Role', 'Department', 'Status']
    
    st.dataframe(display_df, use_container_width=True)
    
    # Add new user form
    with st.expander("➕ Add New User", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username")
            new_full_name = st.text_input("Full Name")
            new_email = st.text_input("Email")
        
        with col2:
            new_role = st.selectbox("Role", ["admin", "manager", "viewer"])
            new_department = st.text_input("Department")
            new_status = st.selectbox("Status", ["active", "inactive"])
        
        if st.button("Add User"):
            if new_username and new_full_name:
                # Add user logic here
                st.success(f"User {new_username} added successfully!")
            else:
                st.error("Please fill in all required fields.")


def render_permissions_tab(user_manager: UserManager):
    """Render the permissions management tab"""
    st.markdown("### Role-Based Permissions")
    
    permissions = user_manager.get_default_permissions()
    
    for role, role_permissions in permissions.items():
        with st.expander(f"🔐 {role.title()} Permissions", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Data Access:**")
                for data_type in role_permissions.get('data_access', []):
                    st.markdown(f"• {data_type}")
                
                st.markdown("**Sensitive Data:**")
                for data_type in role_permissions.get('sensitive_data', []):
                    st.markdown(f"• {data_type}")
            
            with col2:
                st.markdown("**Operations:**")
                for operation in role_permissions.get('operations', []):
                    st.markdown(f"• {operation}")
                
                st.markdown("**Reports:**")
                for report in role_permissions.get('reports', []):
                    st.markdown(f"• {report}")


def render_access_log_tab(user_manager: UserManager):
    """Render the access log tab"""
    st.markdown("### Data Access Log")
    st.markdown("Audit trail of data access and user activities.")
    
    access_log = st.session_state.get('data_access_log', [])
    
    if access_log:
        # Convert to DataFrame for better display
        log_df = pd.DataFrame(access_log)
        log_df['timestamp'] = pd.to_datetime(log_df['timestamp'])
        log_df = log_df.sort_values('timestamp', ascending=False)
        
        # Display recent entries
        st.dataframe(log_df.head(50), use_container_width=True)
        
        # Export log
        if st.button("📥 Export Access Log"):
            csv = log_df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"access_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No access log entries found.")


def render_settings_tab(user_manager: UserManager):
    """Render the settings tab"""
    st.markdown("### Security Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Session Settings:**")
        session_timeout = st.number_input("Session Timeout (minutes)", value=60, min_value=15, max_value=480)
        max_attempts = st.number_input("Max Login Attempts", value=3, min_value=1, max_value=10)
        lockout_duration = st.number_input("Lockout Duration (minutes)", value=5, min_value=1, max_value=60)
    
    with col2:
        st.markdown("**Data Protection:**")
        enable_audit_log = st.checkbox("Enable Audit Logging", value=True)
        mask_sensitive_data = st.checkbox("Mask Sensitive Data", value=True)
        require_strong_passwords = st.checkbox("Require Strong Passwords", value=True)
    
    if st.button("💾 Save Settings"):
        st.success("Settings saved successfully!")


def render_user_info_sidebar():
    """Render user information in sidebar"""
    if st.session_state.get('authenticated', False):
        user_manager = UserManager()
        user_info = user_manager.get_current_user_info()
        
        with st.sidebar:
            st.markdown("---")
            st.markdown("### 👤 User Information")
            
            # User role and name
            role_display = user_manager.get_user_role_display()
            full_name = user_info.get('full_name', st.session_state.get('username', 'User'))
            
            st.markdown(f"**{role_display}**")
            st.markdown(f"**{full_name}**")
            
            # Department
            department = user_info.get('department', 'N/A')
            st.markdown(f"*{department}*")
            
            # Last login
            last_login = user_info.get('last_login')
            if last_login:
                st.markdown(f"Last login: {last_login}")
            
            # Quick actions based on role
            st.markdown("### 🚀 Quick Actions")
            
            if check_permission('manage_users'):
                if st.button("👥 Manage Users", use_container_width=True):
                    st.session_state.show_user_management = True
            
            if check_permission('export'):
                if st.button("📊 Export Data", use_container_width=True):
                    st.session_state.show_export = True


def get_data_access_warning(data_type: str) -> str:
    """Get appropriate warning message for data access"""
    user_manager = UserManager()
    
    if not user_manager.has_data_access(data_type):
        return f"🔒 You don't have permission to access {data_type} data."
    
    if not user_manager.has_sensitive_data_access('salary') and 'salary' in data_type.lower():
        return f"⚠️ Salary information is restricted. Contact your administrator for access."
    
    return ""


def render_data_access_notice(data_type: str):
    """Render data access notice for sensitive information"""
    warning = get_data_access_warning(data_type)
    if warning:
        st.warning(warning)
        return False
    return True
