# 👥 User Management & Data Security Guide

## Overview
The SEAS Financial Tracker includes a comprehensive user management system that provides granular permissions and protects sensitive financial data. This system ensures that only authorized users can access specific information based on their role and permissions.

## 🔐 User Roles & Permissions

### Administrator (Admin)
**Full System Access**
- **Data Access**: All data types
- **Sensitive Data**: Salary, Personal Info, Financial Data
- **Operations**: Create, Read, Update, Delete, Export, Import, Manage Users
- **Reports**: All reports including financial summaries and employee data

**Use Cases**:
- System administrators
- IT personnel
- Senior management with full access needs

### Manager
**Management Access**
- **Data Access**: Employees, Subcontractors, Projects, Tasks
- **Sensitive Data**: Limited salary access
- **Operations**: Create, Read, Update, Export, Import
- **Reports**: Financial summaries, employee data, cost analysis

**Use Cases**:
- Project managers
- Department heads
- Team leads

### Viewer
**Read-Only Access**
- **Data Access**: Employees, Subcontractors, Projects
- **Sensitive Data**: No access to sensitive information
- **Operations**: Read, Export
- **Reports**: Financial summaries, cost analysis

**Use Cases**:
- Financial analysts
- External auditors
- Stakeholders who need reporting access

## 🛡️ Data Protection Features

### Sensitive Data Filtering
The system automatically filters sensitive data based on user permissions:

#### Salary Information
- **Current_Salary**: Employee current salary amounts
- **Priced_Salary**: Contract pricing information
- **Hourly_Rate**: Calculated hourly rates

#### Personal Information
- **Email**: Employee email addresses
- **Phone**: Contact phone numbers
- **Address**: Home addresses
- **SSN**: Social Security Numbers

#### Financial Data
- **Revenue_**: Revenue calculations and projections
- **Cost_**: Cost analysis and breakdowns
- **Profit_**: Profit margin calculations

### Data Access Logging
All data access is logged for audit purposes:
- **Timestamp**: When data was accessed
- **User**: Who accessed the data
- **Data Type**: What type of data was accessed
- **Action**: What action was performed
- **Details**: Additional context about the access

## 🚀 User Management Interface

### Accessing User Management
1. Login as an Administrator
2. Look for "👥 Manage Users" button in the sidebar
3. Click to access the user management interface

### User Management Features

#### Users Tab
- **View All Users**: See all registered users and their roles
- **Add New Users**: Create new user accounts
- **User Status**: Active/Inactive user management
- **User Details**: Full name, email, department information

#### Permissions Tab
- **Role-Based Permissions**: View permissions for each role
- **Data Access Levels**: See what data each role can access
- **Operation Permissions**: View allowed operations per role
- **Report Access**: See which reports each role can generate

#### Access Log Tab
- **Audit Trail**: View all data access activities
- **User Activity**: Track what users are doing
- **Export Logs**: Download access logs for compliance
- **Real-time Monitoring**: See recent activities

#### Settings Tab
- **Session Management**: Configure session timeouts
- **Security Settings**: Set login attempt limits
- **Data Protection**: Enable/disable audit logging
- **Password Policies**: Configure password requirements

## 🔒 Security Implementation

### Authentication Flow
1. **Login**: User enters credentials
2. **Verification**: System verifies username/password
3. **Role Assignment**: User role is determined
4. **Permission Loading**: User permissions are loaded
5. **Session Creation**: Secure session is established
6. **Data Filtering**: Sensitive data is filtered based on permissions

### Data Filtering Process
1. **Request**: User requests data
2. **Permission Check**: System checks user permissions
3. **Data Retrieval**: Original data is retrieved
4. **Filtering**: Sensitive fields are masked or removed
5. **Logging**: Access is logged for audit
6. **Display**: Filtered data is shown to user

### Session Security
- **Timeout**: Sessions expire after 1 hour of inactivity
- **Automatic Logout**: Users are logged out when session expires
- **Secure Storage**: Session data is stored securely
- **Activity Logging**: All session activities are logged

## 📊 Data Access Examples

### Administrator View
```
Employee: John Doe
Salary: $85,000
Email: john.doe@company.com
Phone: (555) 123-4567
```

### Manager View
```
Employee: John Doe
Salary: $85,000
Email: *** Restricted ***
Phone: *** Restricted ***
```

### Viewer View
```
Employee: John Doe
Salary: *** Restricted ***
Email: *** Restricted ***
Phone: *** Restricted ***
```

## 🚨 Security Best Practices

### For Administrators
1. **Regular Access Reviews**: Review user access quarterly
2. **Principle of Least Privilege**: Give users minimum required access
3. **Monitor Access Logs**: Regularly review access logs
4. **Strong Passwords**: Enforce strong password policies
5. **Regular Updates**: Keep user roles and permissions updated

### For Users
1. **Secure Login**: Use strong, unique passwords
2. **Logout**: Always logout when finished
3. **Report Issues**: Report any suspicious activity
4. **Data Handling**: Don't share sensitive information
5. **Access Requests**: Request additional access through proper channels

## 🔧 Configuration

### Environment Variables
Set these in your Streamlit Cloud secrets:

```toml
[secrets]
# Authentication
AUTH_SALT = "your_secure_salt_here"
ADMIN_PASSWORD = "secure_admin_password"
MANAGER_PASSWORD = "secure_manager_password"
VIEWER_PASSWORD = "secure_viewer_password"

# Security Settings
SESSION_TIMEOUT = 3600
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300
```

### Customizing Permissions
To modify permissions, edit the `get_default_permissions()` function in `user_management.py`:

```python
def get_default_permissions(self) -> Dict[str, Dict[str, List[str]]]:
    return {
        'admin': {
            'data_access': ['all'],
            'sensitive_data': ['salary', 'personal_info', 'financial_data'],
            'operations': ['create', 'read', 'update', 'delete', 'export', 'import', 'manage_users'],
            'reports': ['all_reports', 'financial_summary', 'employee_data', 'cost_analysis']
        },
        # Add custom roles here
    }
```

## 📈 Monitoring & Compliance

### Access Logs
- **Real-time Monitoring**: View current user activities
- **Historical Data**: Access logs are retained for compliance
- **Export Capability**: Download logs for external analysis
- **Search & Filter**: Find specific activities quickly

### Compliance Features
- **Audit Trail**: Complete record of all data access
- **User Activity**: Track who accessed what and when
- **Data Protection**: Automatic filtering of sensitive information
- **Session Management**: Secure session handling

## 🆘 Troubleshooting

### Common Issues

1. **"Access Denied" Messages**:
   - Check user role and permissions
   - Verify session hasn't expired
   - Contact administrator for access review

2. **Missing Data**:
   - Data may be filtered based on permissions
   - Check if user has access to sensitive data
   - Contact administrator for access request

3. **Login Issues**:
   - Verify username and password
   - Check if account is locked
   - Wait for lockout period to expire

### Getting Help
1. **Check Permissions**: Verify your role and access level
2. **Review Logs**: Check access logs for activity history
3. **Contact Admin**: Reach out to system administrator
4. **Document Issues**: Keep records of any problems

---

**Remember**: This system is designed to protect sensitive financial data while providing appropriate access to authorized users. Always follow security best practices and report any concerns immediately.
