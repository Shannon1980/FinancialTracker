# 🚀 Streamlit Cloud Deployment Guide

## Quick Deployment Steps

### 1. Go to Streamlit Cloud
1. Visit [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**

### 2. Configure Your App
- **Repository**: `Shannon1980/FinancialTracker`
- **Branch**: `main`
- **Main file path**: `seas-financial-tracker.py`
- **App URL**: `seas-financial-tracker` (optional, but recommended)

### 3. Set Up Secrets
In the Streamlit Cloud dashboard, go to your app settings and add these secrets:

```toml
# Authentication Settings
AUTH_SALT = "your_secure_salt_here_change_this"
ADMIN_PASSWORD = "secure_admin_password_change_this"
MANAGER_PASSWORD = "secure_manager_password_change_this"
VIEWER_PASSWORD = "secure_viewer_password_change_this"

# Security Settings
SESSION_TIMEOUT = 3600
MAX_LOGIN_ATTEMPTS = 3
LOCKOUT_DURATION = 300
```

### 4. Deploy
Click **"Deploy!"** and wait 2-5 minutes for deployment to complete.

## 🔑 Default Login Credentials

| Role | Username | Password | Access Level |
|------|----------|----------|--------------|
| Admin | admin | admin123 | Full system access |
| Manager | manager | manager123 | Limited sensitive data access |
| Viewer | viewer | viewer123 | Read-only, no sensitive data |

**⚠️ IMPORTANT: Change these passwords immediately after deployment!**

## 🎯 Your App Will Be Available At:
`https://seas-financial-tracker.streamlit.app`

## ✨ Features Available After Deployment

### 🔐 Authentication & Security
- Secure login system with role-based access
- Session management with automatic timeout
- Password protection for all data access
- Audit logging for compliance

### 👥 User Management
- Role-based permissions (Admin, Manager, Viewer)
- User management interface for administrators
- Data access logging and monitoring
- Sensitive data filtering based on user role

### 🎨 Theme System
- Light and dark mode switching
- Professional QuickBooks-inspired design
- Responsive layout for all devices
- Theme persistence across sessions

### 📊 Data Management
- Employee data management with salary protection
- Subcontractor tracking
- Project cost analysis
- Financial reporting and analytics

### 📈 Charts & Visualizations
- Interactive Plotly charts
- Revenue trend analysis
- Cost breakdown visualizations
- Project burn rate monitoring
- Theme-aware chart styling

## 🔧 Post-Deployment Configuration

### 1. Update Passwords
1. Log in as admin
2. Go to User Management (👥 Manage Users button in sidebar)
3. Update default passwords for all users
4. Consider adding new users with appropriate roles

### 2. Test All Features
1. **Authentication**: Test login/logout with all user types
2. **Data Access**: Verify role-based data filtering
3. **Charts**: Ensure all visualizations display correctly
4. **Theme Switching**: Test light/dark mode toggle
5. **User Management**: Test user creation and permission management

### 3. Import Your Data
1. Use the template download feature to get the correct format
2. Upload your employee and subcontractor data
3. Verify data is properly loaded and filtered based on user roles

## 🚨 Troubleshooting

### Common Issues

#### App Won't Start
- Check that `seas-financial-tracker.py` is the main file
- Verify all dependencies are in `requirements.txt`
- Check Streamlit Cloud logs for error messages

#### Authentication Not Working
- Verify secrets are properly configured
- Check that AUTH_SALT is set
- Ensure passwords are properly configured

#### Charts Not Displaying
- Check that Plotly is in requirements.txt
- Verify data is properly loaded
- Check browser console for JavaScript errors

#### Theme Not Switching
- Clear browser cache
- Check that theme_manager.py is properly imported
- Verify CSS is loading correctly

### Getting Help
1. Check Streamlit Cloud logs in the dashboard
2. Review the application logs in the browser console
3. Test locally first: `streamlit run seas-financial-tracker.py`
4. Check GitHub issues or create a new one

## 🔄 Updates and Maintenance

### Updating the App
1. Push changes to your GitHub repository
2. Streamlit Cloud will automatically redeploy
3. Monitor the deployment status in the dashboard

### Monitoring
1. Check Streamlit Cloud dashboard for app health
2. Monitor user access logs in the application
3. Review error logs for any issues
4. Update dependencies regularly

## 📊 Performance Optimization

### For Large Datasets
1. Consider implementing data pagination
2. Use data caching for frequently accessed information
3. Optimize chart rendering for large datasets
4. Implement lazy loading for better performance

### Security Best Practices
1. Regularly update passwords
2. Monitor access logs for suspicious activity
3. Keep dependencies updated
4. Use HTTPS (enabled by default on Streamlit Cloud)

## 🎯 Next Steps

After successful deployment:
1. **Train Users**: Provide training on the new system
2. **Data Migration**: Import existing data using templates
3. **Customization**: Adjust themes and styling as needed
4. **Integration**: Consider integrating with other systems
5. **Monitoring**: Set up regular monitoring and maintenance

---

**🎉 Congratulations!** Your SEAS Financial Tracker is now live and ready for use. The application provides enterprise-level security, professional design, and comprehensive financial management capabilities.

For support or questions, refer to the documentation or contact your system administrator.