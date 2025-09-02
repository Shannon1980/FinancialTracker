"""
Authentication module for SEAS Financial Tracker
Provides secure login functionality to protect financial data
"""

import streamlit as st
import hashlib
import os
from typing import Optional, Dict, Any
import time


class AuthManager:
    """Manages user authentication and session security"""
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour in seconds
        self.max_login_attempts = 3
        self.lockout_duration = 300  # 5 minutes in seconds
        
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256 with salt"""
        salt = os.getenv('AUTH_SALT', 'seas_financial_tracker_2024')
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def get_credentials(self) -> Dict[str, str]:
        """Get valid credentials from environment variables"""
        return {
            'admin': os.getenv('ADMIN_PASSWORD', 'admin123'),
            'manager': os.getenv('MANAGER_PASSWORD', 'manager123'),
            'viewer': os.getenv('VIEWER_PASSWORD', 'viewer123')
        }
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if 'authenticated' not in st.session_state:
            return False
        
        if not st.session_state.authenticated:
            return False
            
        # Check session timeout
        if 'login_time' in st.session_state:
            if time.time() - st.session_state.login_time > self.session_timeout:
                self.logout()
                return False
                
        return True
    
    def login(self, username: str, password: str) -> bool:
        """Authenticate user with username and password"""
        # Check for lockout
        if self.is_locked_out():
            st.error("🔒 Account temporarily locked due to too many failed attempts. Please try again later.")
            return False
            
        credentials = self.get_credentials()
        hashed_password = self.hash_password(password)
        
        if username in credentials and self.hash_password(credentials[username]) == hashed_password:
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.login_time = time.time()
            st.session_state.login_attempts = 0
            st.session_state.last_failed_attempt = None
            return True
        else:
            self.record_failed_attempt()
            return False
    
    def logout(self):
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.login_time = None
        st.session_state.login_attempts = 0
        st.session_state.last_failed_attempt = None
        st.rerun()
    
    def record_failed_attempt(self):
        """Record a failed login attempt"""
        if 'login_attempts' not in st.session_state:
            st.session_state.login_attempts = 0
        if 'last_failed_attempt' not in st.session_state:
            st.session_state.last_failed_attempt = None
            
        st.session_state.login_attempts += 1
        st.session_state.last_failed_attempt = time.time()
    
    def is_locked_out(self) -> bool:
        """Check if account is locked due to too many failed attempts"""
        if 'login_attempts' not in st.session_state or 'last_failed_attempt' not in st.session_state:
            return False
            
        if st.session_state.login_attempts >= self.max_login_attempts:
            if time.time() - st.session_state.last_failed_attempt < self.lockout_duration:
                return True
            else:
                # Reset attempts after lockout period
                st.session_state.login_attempts = 0
                st.session_state.last_failed_attempt = None
                
        return False
    
    def get_user_role(self) -> str:
        """Get the role of the current user"""
        if not self.is_authenticated():
            return 'guest'
        return st.session_state.get('username', 'guest')
    
    def has_permission(self, action: str) -> bool:
        """Check if current user has permission for specific action"""
        if not self.is_authenticated():
            return False
            
        role = self.get_user_role()
        
        # Define permissions by role
        permissions = {
            'admin': ['view', 'edit', 'delete', 'export', 'import', 'manage_users'],
            'manager': ['view', 'edit', 'export', 'import'],
            'viewer': ['view', 'export']
        }
        
        return action in permissions.get(role, [])


def render_login_page() -> bool:
    """Render the login page and return True if authentication is successful"""
    
    # Custom CSS for login page
    st.markdown("""
    <style>
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    .login-header h1 {
        color: #0073E6;
        margin-bottom: 0.5rem;
    }
    .login-header p {
        color: #666;
        margin: 0;
    }
    .stButton > button {
        width: 100%;
        background-color: #0073E6;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.75rem;
        font-size: 1rem;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #0056B3;
    }
    .security-notice {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 1rem;
        margin-top: 1rem;
        font-size: 0.9rem;
        color: #495057;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Login form
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    
    # Header with Logo
    st.markdown("""
    <div class="login-header">
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjYwIiB2aWV3Qm94PSIwIDAgMjAwIDYwIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPgogIDxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iNjAiIGZpbGw9IiNGRkZGRkYiIHJ4PSI4Ii8+CiAgPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMTAsIDgpIj4KICAgIDxyZWN0IHg9IjAiIHk9IjIwIiB3aWR0aD0iNDQiIGhlaWdodD0iMjQiIGZpbGw9IiNGMEY4RkYiIHJ4PSIyIi8+CiAgICA8cmVjdCB4PSI0IiB5PSIzMiIgd2lkdGg9IjYiIGhlaWdodD0iMTIiIGZpbGw9IiMwMDczRTYiLz4KICAgIDxyZWN0IHg9IjEyIiB5PSIyOCIgd2lkdGg9IjYiIGhlaWdodD0iMTYiIGZpbGw9IiMwMEE4NkIiLz4KICAgIDxyZWN0IHg9IjIwIiB5PSIyNCIgd2lkdGg9IjYiIGhlaWdodD0iMjAiIGZpbGw9IiNGRjhDMDAiLz4KICAgIDxyZWN0IHg9IjI4IiB5PSIzMCIgd2lkdGg9IjYiIGhlaWdodD0iMTQiIGZpbGw9IiNFNTNFM0UiLz4KICAgIDxyZWN0IHg9IjM2IiB5PSIyNiIgd2lkdGg9IjYiIGhlaWdodD0iMTgiIGZpbGw9IiM5QzI3QjAiLz4KICAgIDxwYXRoIGQ9Ik00LDM2IEwxMiwzMiBMMjAsMjggTDI4LDM0IEwzNiwzMCIgc3Ryb2tlPSIjMDA3M0U2IiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiLz4KICAgIDxjaXJjbGUgY3g9IjIyIiBjeT0iMTIiIHI9IjgiIGZpbGw9IiMwMDczRTYiLz4KICAgIDx0ZXh0IHg9IjIyIiB5PSIxNyIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZmlsbD0id2hpdGUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMCIgZm9udC13ZWlnaHQ9ImJvbGQiPiQ8L3RleHQ+CiAgPC9nPgogIDxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDY1LCAxNSkiPgogICAgPHRleHQgeD0iMCIgeT0iMTIiIGZpbGw9IiMwMDczRTYiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZm9udC13ZWlnaHQ9ImJvbGQiPlNFQVM8L3RleHQ+CiAgICA8dGV4dCB4PSIwIiB5PSIyOCIgZmlsbD0iIzRBNTU2OCIgZm9udC1mYW1pbHk9IkFyaWFsLCBzYW5zLXNlcmlmIiBmb250LXNpemU9IjEwIiBmb250LXdlaWdodD0iNTAwIj5GaW5hbmNpYWwgVHJhY2tlcjwvdGV4dD4KICA8L2c+CiAgPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoNjUsIDQwKSI+CiAgICA8dGV4dCB4PSIwIiB5PSI4IiBmaWxsPSIjOUFBMEE2IiBmb250LWZhbWlseT0iQXJpYWwsIHNhbnMtc2VyaWYiIGZvbnQtc2l6ZT0iOCI+U2VjdXJlIEFjY2VzcyBSZXF1aXJlZDwvdGV4dD4KICA8L2c+Cjwvc3ZnPg==" alt="SEAS Financial Tracker Logo" style="max-width: 200px; margin-bottom: 1rem;">
        <h1>🔐 Secure Access</h1>
        <p>Professional Financial Management Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form"):
        st.markdown("### Please sign in to continue")
        
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            login_button = st.form_submit_button("🔑 Login", use_container_width=True)
        with col2:
            if st.form_submit_button("❓ Help", use_container_width=True):
                st.info("""
                **Default Credentials:**
                - **Admin**: admin / admin123
                - **Manager**: manager / manager123  
                - **Viewer**: viewer / viewer123
                
                **Note**: Change these passwords in production by setting environment variables.
                """)
        
        if login_button:
            auth_manager = AuthManager()
            
            if not username or not password:
                st.error("⚠️ Please enter both username and password")
            else:
                if auth_manager.login(username, password):
                    st.success("✅ Login successful! Redirecting...")
                    time.sleep(1)
                    st.rerun()
                else:
                    remaining_attempts = auth_manager.max_login_attempts - st.session_state.get('login_attempts', 0)
                    if remaining_attempts > 0:
                        st.error(f"❌ Invalid credentials. {remaining_attempts} attempts remaining.")
                    else:
                        st.error("🔒 Account locked. Please try again later.")
    
    # Security notice
    st.markdown("""
    <div class="security-notice">
        <strong>🔒 Security Notice:</strong><br>
        This application contains sensitive financial data. Access is logged and monitored. 
        Please ensure you are authorized to access this system.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return False


def render_logout_button():
    """Render logout button in sidebar"""
    if st.session_state.get('authenticated', False):
        with st.sidebar:
            st.markdown("---")
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"👤 **{st.session_state.get('username', 'User')}**")
            with col2:
                if st.button("🚪 Logout", key="logout_btn"):
                    auth_manager = AuthManager()
                    auth_manager.logout()
                    st.rerun()


def require_auth(func):
    """Decorator to require authentication for specific functions"""
    def wrapper(*args, **kwargs):
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            render_login_page()
            return None
        return func(*args, **kwargs)
    return wrapper


def check_permission(action: str) -> bool:
    """Check if current user has permission for specific action"""
    auth_manager = AuthManager()
    return auth_manager.has_permission(action)
