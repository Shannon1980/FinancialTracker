"""
Unit tests for authentication module
"""

import pytest
import hashlib
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from auth import AuthManager


class TestAuthManager:
    """Test cases for AuthManager class"""
    
    def test_init(self):
        """Test AuthManager initialization"""
        auth_manager = AuthManager()
        assert auth_manager is not None
        assert hasattr(auth_manager, 'salt')
        assert hasattr(auth_manager, 'users')
    
    def test_hash_password(self):
        """Test password hashing"""
        auth_manager = AuthManager()
        password = "test_password"
        hashed = auth_manager._hash_password(password)
        
        # Should return a string
        assert isinstance(hashed, str)
        # Should be different from original password
        assert hashed != password
        # Should be consistent
        assert hashed == auth_manager._hash_password(password)
    
    def test_verify_password(self):
        """Test password verification"""
        auth_manager = AuthManager()
        password = "test_password"
        hashed = auth_manager._hash_password(password)
        
        # Should verify correct password
        assert auth_manager._verify_password(password, hashed) is True
        # Should reject incorrect password
        assert auth_manager._verify_password("wrong_password", hashed) is False
    
    def test_authenticate_valid_credentials(self):
        """Test authentication with valid credentials"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {}):
            result = auth_manager.authenticate("admin", "admin123")
            assert result is True
            assert auth_manager.is_authenticated() is True
    
    def test_authenticate_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {}):
            result = auth_manager.authenticate("admin", "wrong_password")
            assert result is False
            assert auth_manager.is_authenticated() is False
    
    def test_authenticate_nonexistent_user(self):
        """Test authentication with nonexistent user"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {}):
            result = auth_manager.authenticate("nonexistent", "password")
            assert result is False
            assert auth_manager.is_authenticated() is False
    
    def test_logout(self):
        """Test logout functionality"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': True, 'username': 'admin'}):
            auth_manager.logout()
            assert auth_manager.is_authenticated() is False
    
    def test_get_user_role(self):
        """Test getting user role"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': True, 'username': 'admin'}):
            role = auth_manager.get_user_role()
            assert role == 'admin'
    
    def test_get_user_role_unauthenticated(self):
        """Test getting user role when not authenticated"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': False}):
            role = auth_manager.get_user_role()
            assert role is None
    
    def test_check_permission_admin(self):
        """Test permission checking for admin user"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': True, 'username': 'admin'}):
            # Admin should have all permissions
            assert auth_manager.check_permission('manage_users') is True
            assert auth_manager.check_permission('view') is True
            assert auth_manager.check_permission('edit') is True
            assert auth_manager.check_permission('delete') is True
    
    def test_check_permission_manager(self):
        """Test permission checking for manager user"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': True, 'username': 'manager'}):
            # Manager should have limited permissions
            assert auth_manager.check_permission('view') is True
            assert auth_manager.check_permission('edit') is True
            assert auth_manager.check_permission('manage_users') is False
    
    def test_check_permission_viewer(self):
        """Test permission checking for viewer user"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': True, 'username': 'viewer'}):
            # Viewer should have read-only permissions
            assert auth_manager.check_permission('view') is True
            assert auth_manager.check_permission('edit') is False
            assert auth_manager.check_permission('manage_users') is False
    
    def test_check_permission_unauthenticated(self):
        """Test permission checking when not authenticated"""
        auth_manager = AuthManager()
        
        # Mock session state
        with patch('streamlit.session_state', {'authenticated': False}):
            # Unauthenticated users should have no permissions
            assert auth_manager.check_permission('view') is False
            assert auth_manager.check_permission('edit') is False
            assert auth_manager.check_permission('manage_users') is False
