# Streamlit Cloud Deployment Guide

## 🚀 Deploy to Streamlit Cloud

### Prerequisites
1. GitHub repository with your code
2. Streamlit Cloud account (free at share.streamlit.io)

### Step 1: Prepare Your Repository
- ✅ `requirements.txt` - Contains all Python dependencies
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `seas-financial-tracker.py` - Main application file
- ✅ `static/custom.css` - Custom styling
- ✅ All supporting files (styling.py, data_utils.py, etc.)

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)

2. **Sign in with GitHub**: Use your GitHub account

3. **New App**: Click "New app"

4. **Repository Settings**:
   - **Repository**: `your-username/FinancialTracker`
   - **Branch**: `main`
   - **Main file path**: `seas-financial-tracker.py`

5. **App URL**: Choose your app URL (e.g., `seas-financial-tracker`)

6. **Deploy**: Click "Deploy!"

### Step 3: Configuration

The app will automatically:
- Install dependencies from `requirements.txt`
- Use configuration from `.streamlit/config.toml`
- Load custom CSS from `static/custom.css`

### Step 4: Access Your App

Your app will be available at:
`https://seas-financial-tracker.streamlit.app`

## 🔧 Troubleshooting

### Common Issues:

1. **CSS Not Loading**: Ensure `static/custom.css` is in the repository
2. **Import Errors**: Check all Python files are included
3. **Database Issues**: SQLite database will be created automatically
4. **Styling Issues**: Verify `.streamlit/config.toml` is present

### File Structure Required:
```
FinancialTracker/
├── seas-financial-tracker.py
├── requirements.txt
├── .streamlit/
│   └── config.toml
├── static/
│   └── custom.css
├── styling.py
├── data_utils.py
├── chart_utils.py
├── config.py
└── database/
    └── (all database files)
```

## 🎯 Features Included

- ✅ Section 508 compliant design
- ✅ QuickBooks-inspired UI
- ✅ Enhanced section contrast
- ✅ Interactive charts and visualizations
- ✅ Employee and subcontractor management
- ✅ Financial tracking and analysis
- ✅ Template downloads
- ✅ Data upload functionality

## 📱 Mobile Responsive

The app is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

## 🔒 Security

- No sensitive data in the repository
- Database created locally per session
- All data processing happens client-side
