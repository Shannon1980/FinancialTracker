# 🔐 Authentication Setup Guide

## Overview
The SEAS Financial Tracker now includes secure authentication to protect your financial data. This guide explains how to set up and configure the authentication system.

## 🔑 Default Credentials

**⚠️ IMPORTANT: Change these passwords in production!**

| Role | Username | Default Password | Permissions |
|------|----------|------------------|-------------|
| **Admin** | admin | admin123 | Full access (view, edit, delete, export, import, manage users) |
| **Manager** | manager | manager123 | Management access (view, edit, export, import) |
| **Viewer** | viewer | viewer123 | Read-only access (view, export) |

## 🚀 Streamlit Cloud Deployment

### Option 1: Environment Variables (Recommended)
Set these environment variables in your Streamlit Cloud app settings:

1. Go to your Streamlit Cloud app dashboard
2. Click "Settings" → "Secrets"
3. Add the following secrets:

```toml
[secrets]
AUTH_SALT = "your_secure_random_salt_here_change_this_in_production"
ADMIN_PASSWORD = "your_secure_admin_password_here"
MANAGER_PASSWORD = "your_secure_manager_password_here"
VIEWER_PASSWORD = "your_secure_viewer_password_here"
```

### Option 2: Secrets File
Create a `.streamlit/secrets.toml` file in your repository:

```toml
[secrets]
AUTH_SALT = "your_secure_random_salt_here_change_this_in_production"
ADMIN_PASSWORD = "your_secure_admin_password_here"
MANAGER_PASSWORD = "your_secure_manager_password_here"
VIEWER_PASSWORD = "your_secure_viewer_password_here"
```

## 🔒 Security Features

### Authentication Features:
- ✅ **Secure Password Hashing**: SHA-256 with salt
- ✅ **Session Management**: 1-hour timeout with automatic logout
- ✅ **Login Attempt Limiting**: 3 attempts before 5-minute lockout
- ✅ **Role-Based Access Control**: Different permission levels
- ✅ **Session Security**: Automatic timeout and logout

### Permission Levels:

#### Admin (Full Access)
- View all data
- Edit employees and subcontractors
- Delete records
- Export data
- Import data
- Manage users (future feature)

#### Manager (Management Access)
- View all data
- Edit employees and subcontractors
- Export data
- Import data

#### Viewer (Read-Only Access)
- View all data
- Export data

## 🛡️ Security Best Practices

### For Production Deployment:

1. **Change Default Passwords**:
   ```bash
   # Generate secure passwords
   openssl rand -base64 32
   ```

2. **Use Strong Salt**:
   ```bash
   # Generate secure salt
   openssl rand -hex 32
   ```

3. **Environment Variables**:
   - Never commit passwords to version control
   - Use environment variables or secrets management
   - Rotate passwords regularly

4. **Access Control**:
   - Limit admin accounts to essential personnel only
   - Use viewer accounts for most users
   - Monitor login attempts and sessions

## 🔧 Local Development

For local development, you can use the default credentials or set environment variables:

```bash
export AUTH_SALT="dev_salt_2024"
export ADMIN_PASSWORD="admin123"
export MANAGER_PASSWORD="manager123"
export VIEWER_PASSWORD="viewer123"
```

## 📱 User Experience

### Login Page Features:
- Clean, professional design
- Help button with default credentials
- Security notice
- Account lockout protection
- Session timeout warnings

### Main Application:
- Logout button in sidebar
- User role display
- Permission-based feature access
- Automatic session management

## 🚨 Troubleshooting

### Common Issues:

1. **Can't Login**:
   - Check username/password spelling
   - Verify environment variables are set
   - Check if account is locked out

2. **Permission Denied**:
   - Verify user role has required permissions
   - Check if session has expired

3. **Session Timeout**:
   - Sessions expire after 1 hour
   - Re-login to continue

### Reset Authentication:
If you need to reset authentication:
1. Clear browser cookies/session storage
2. Restart the Streamlit app
3. Use default credentials to login

## 🔄 Updates and Maintenance

### Regular Security Tasks:
- [ ] Rotate passwords quarterly
- [ ] Review user access levels
- [ ] Monitor login attempts
- [ ] Update authentication salt annually
- [ ] Review and update permissions as needed

## 📞 Support

For authentication issues:
1. Check this guide first
2. Verify environment variables
3. Check Streamlit Cloud logs
4. Contact system administrator

---

**Remember**: Always use strong, unique passwords in production and never share credentials in plain text!
