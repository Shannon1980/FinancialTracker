# 📋 Employee Data Upload Templates

This directory contains templates for uploading employee data to the SEAS Financial Tracker.

## 🎯 Available Templates

### 1. **Basic Template** (`employee_template.xlsx` / `employee_template.csv`)
- **5 required fields** only
- **Simple structure** for quick uploads
- **Perfect for** basic employee data

**Fields:**
- Name
- LCAT
- Priced_Salary
- Current_Salary
- Hours_Per_Month

### 2. **Comprehensive Template** (`comprehensive_employee_template.xlsx` / `comprehensive_employee_template.csv`)
- **10 fields** including optional ones
- **Multiple Excel sheets** with instructions
- **Validation options** for data quality
- **Perfect for** detailed employee management

**Fields:**
- Name (Required)
- LCAT (Required)
- Priced_Salary (Required)
- Current_Salary (Required)
- Hours_Per_Month (Required)
- Department (Optional)
- Start_Date (Optional)
- Location (Optional)
- Manager (Optional)
- Skills (Optional)

## 📊 How to Use

### **Step 1: Download Template**
- Choose either basic or comprehensive template
- Excel format recommended for better formatting
- CSV format for simple text editors

### **Step 2: Fill in Your Data**
- **Replace sample data** with your actual employee information
- **Keep column headers** exactly as shown
- **Use proper formats**:
  - Dates: YYYY-MM-DD (e.g., 2024-01-15)
  - Salaries: Numbers only (e.g., 150000, not $150,000)
  - Hours: Numbers only (e.g., 173)

### **Step 3: Validate Data**
- **LCAT values** should match: PM, SA/Eng Lead, AI Lead, HCD Lead, Scrum Master, Cloud Data Engineer, SRE, Full Stack Dev
- **Department options**: Management, Engineering, AI/ML, Design, Agile, Data Engineering, DevOps, Business
- **Location options**: Remote, On-site, Hybrid, Travel

### **Step 4: Upload to App**
- Save your completed template
- Use the file upload feature in the SEAS Financial Tracker
- The app will automatically:
  - Calculate hourly rates
  - Add time period columns
  - Validate data format
  - Import employee information

## ⚠️ Important Notes

### **Required Fields**
- **Name**: Full employee name
- **LCAT**: Labor Category (must match validation options)
- **Priced_Salary**: Original budgeted salary
- **Current_Salary**: Actual salary being paid
- **Hours_Per_Month**: Standard monthly hours (typically 173)

### **Data Format Requirements**
- **No currency symbols** ($, €, £)
- **No commas** in numbers
- **Dates in YYYY-MM-DD format**
- **Text fields** can include commas for multiple values

### **Common Mistakes to Avoid**
- ❌ Using $150,000 instead of 150000
- ❌ Using 01/15/2024 instead of 2024-01-15
- ❌ Changing column header names
- ❌ Adding extra columns
- ❌ Using invalid LCAT values

## 🔧 Template Generation

If you need to modify the templates:

```bash
# Generate basic template
python templates/create_employee_template.py

# Generate comprehensive template
python templates/create_comprehensive_template.py
```

## 📁 File Structure

```
templates/
├── README.md                           # This file
├── employee_template.xlsx              # Basic Excel template
├── employee_template.csv               # Basic CSV template
├── comprehensive_employee_template.xlsx # Comprehensive Excel template
├── comprehensive_employee_template.csv  # Comprehensive CSV template
├── create_employee_template.py         # Basic template generator
└── create_comprehensive_template.py    # Comprehensive template generator
```

## 💡 Pro Tips

1. **Start with the basic template** if you're new to the system
2. **Use the comprehensive template** for detailed employee management
3. **Validate your data** before uploading
4. **Keep backups** of your original data
5. **Test with a few employees** before uploading large datasets

## 🆘 Need Help?

If you encounter issues:
1. Check that all required fields are filled
2. Verify data formats match requirements
3. Ensure LCAT values are valid
4. Check that column headers haven't been changed
5. Try the basic template first, then upgrade to comprehensive

## 🎉 Success!

Once uploaded successfully, you'll see:
- ✅ Employee data imported
- ✅ Hourly rates calculated automatically
- ✅ Time period columns added
- ✅ Data ready for financial analysis
