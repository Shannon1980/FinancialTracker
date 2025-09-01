# SEAS Financial Tracker - Implementation Guide

## 🚀 **Getting Started with Section 508 Compliant QuickBooks Design**

### **1. File Structure**
```
static/
├── custom.css              # Main CSS stylesheet
├── sample_dashboard.html   # Example HTML component
├── color_palette.md        # Color documentation
└── implementation_guide.md # This file
```

### **2. Integration Steps**

#### **Step 1: Add CSS to Streamlit App**
```python
# In your main Streamlit app (seas-financial-tracker.py)
import streamlit as st

# Load custom CSS
def load_css():
    with open('static/custom.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Call this function at the start of your app
if __name__ == "__main__":
    load_css()
    # ... rest of your app code
```

#### **Step 2: Update Streamlit Components**
```python
# Replace existing Streamlit styling with custom classes
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<h3 class="card-title">Employee Management</h3>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# For buttons, use custom styling
st.markdown('<button class="btn btn-primary">Add Employee</button>', unsafe_allow_html=True)
```

#### **Step 3: Add ARIA Labels and Semantic HTML**
```python
# Add accessibility attributes to Streamlit components
st.markdown('''
<div class="card" role="region" aria-labelledby="employee-heading">
    <h3 id="employee-heading" class="card-title">Employee Management</h3>
    <div class="card-body">
        <!-- Your content here -->
    </div>
</div>
''', unsafe_allow_html=True)
```

## 🎨 **CSS Class Reference**

### **Layout Classes**
```css
.container          /* Responsive container with max-width */
.dashboard-grid    /* Grid layout for dashboard components */
.summary-cards     /* Card layout for summary information */
```

### **Component Classes**
```css
.card              /* QuickBooks-style card component */
.card-header       /* Card header section */
.card-title        /* Card title styling */
.card-body         /* Card content area */
.card-footer       /* Card footer section */
```

### **Button Classes**
```css
.btn               /* Base button styles */
.btn-primary       /* Primary action button */
.btn-secondary     /* Secondary action button */
.btn-success       /* Success/confirm button */
.btn-warning       /* Warning button */
.btn-danger        /* Danger/destructive button */
.btn-sm            /* Small button variant */
```

### **Form Classes**
```css
.form-group        /* Form field container */
.form-label        /* Form field label */
.form-input        /* Text input styling */
.form-select       /* Select dropdown styling */
.form-textarea     /* Textarea styling */
.form-help         /* Help text styling */
.form-error        /* Error message styling */
```

### **Table Classes**
```css
.table-container   /* Table wrapper with overflow */
.table             /* Base table styling */
.table th          /* Table header cells */
.table td          /* Table data cells */
```

### **Utility Classes**
```css
.text-center       /* Center-align text */
.mt-1 to mt-5     /* Margin top utilities */
.mb-1 to mb-5     /* Margin bottom utilities */
.p-1 to p-5       /* Padding utilities */
.d-none            /* Hide element */
.d-block           /* Show element */
.d-flex            /* Flexbox display */
```

## 🔧 **Streamlit-Specific Implementation**

### **1. Custom Button Styling**
```python
def create_custom_button(label, key, button_type="primary"):
    """Create a custom styled button with accessibility"""
    button_class = f"btn btn-{button_type}"
    return st.markdown(
        f'<button class="{button_class}" data-key="{key}">{label}</button>',
        unsafe_allow_html=True
    )

# Usage
create_custom_button("Add Employee", "add_emp", "primary")
create_custom_button("Cancel", "cancel", "secondary")
```

### **2. Custom Card Components**
```python
def create_card(title, content, footer=None):
    """Create a QuickBooks-style card component"""
    card_html = f'''
    <div class="card">
        <div class="card-header">
            <h3 class="card-title">{title}</h3>
        </div>
        <div class="card-body">
            {content}
        </div>
    '''
    
    if footer:
        card_html += f'<div class="card-footer">{footer}</div>'
    
    card_html += '</div>'
    return st.markdown(card_html, unsafe_allow_html=True)

# Usage
create_card(
    title="Employee Summary",
    content="<p>Total employees: 24</p>",
    footer="<small>Last updated: Today</small>"
)
```

### **3. Custom Form Components**
```python
def create_form_field(label, field_type="text", required=False, help_text=None):
    """Create a styled form field with accessibility"""
    required_attr = "required" if required else ""
    aria_required = 'aria-required="true"' if required else ""
    
    field_html = f'''
    <div class="form-group">
        <label class="form-label">{label}</label>
        <input type="{field_type}" class="form-input" {required_attr} {aria_required}>
    '''
    
    if help_text:
        field_html += f'<div class="form-help">{help_text}</div>'
    
    field_html += '</div>'
    return st.markdown(field_html, unsafe_allow_html=True)

# Usage
create_form_field("Employee Name", "text", True, "Enter the full name")
create_form_field("Salary", "number", True, "Annual salary in dollars")
```

## 📱 **Responsive Design Implementation**

### **1. Mobile-First Approach**
```python
# Use Streamlit columns for responsive layouts
col1, col2, col3 = st.columns([1, 1, 1])

# On mobile, these will stack vertically
with col1:
    create_card("Budget", "$2.4M")
with col2:
    create_card("Employees", "24")
with col3:
    create_card("Status", "Active")
```

### **2. Responsive Tables**
```python
# Wrap tables in responsive containers
st.markdown('<div class="table-container">', unsafe_allow_html=True)
st.dataframe(df)  # Your Streamlit table
st.markdown('</div>', unsafe_allow_html=True)
```

## ♿ **Accessibility Implementation**

### **1. ARIA Labels and Roles**
```python
# Add ARIA attributes to Streamlit components
st.markdown('''
<div role="region" aria-labelledby="chart-heading">
    <h2 id="chart-heading">Financial Chart</h2>
    <!-- Your chart content -->
</div>
''', unsafe_allow_html=True)
```

### **2. Skip Links**
```python
# Add skip link at the top of your app
st.markdown('''
<a href="#main-content" class="skip-link">Skip to main content</a>
<div id="main-content">
    <!-- Your main app content -->
</div>
''', unsafe_allow_html=True)
```

### **3. Focus Management**
```python
# Ensure proper tab order in forms
st.markdown('''
<form class="employee-form" role="form">
    <div class="form-group">
        <label for="name">Name</label>
        <input type="text" id="name" class="form-input" tabindex="1">
    </div>
    <div class="form-group">
        <label for="salary">Salary</label>
        <input type="number" id="salary" class="form-input" tabindex="2">
    </div>
    <button type="submit" class="btn btn-primary" tabindex="3">Submit</button>
</form>
''', unsafe_allow_html=True)
```

## 🧪 **Testing and Validation**

### **1. Automated Testing**
```bash
# Install accessibility testing tools
npm install -g axe-core
npm install -g pa11y

# Test your application
axe http://localhost:8503
pa11y http://localhost:8503
```

### **2. Manual Testing Checklist**
- [ ] **Keyboard Navigation**: Tab through all interactive elements
- [ ] **Screen Reader**: Test with NVDA, VoiceOver, or JAWS
- [ ] **High Contrast**: Enable high contrast mode
- [ ] **Color Blindness**: Use NoCoffee Vision Simulator
- [ ] **Zoom**: Test text resizing up to 200%

### **3. Browser Testing**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers

## 🚨 **Common Issues and Solutions**

### **1. Streamlit CSS Conflicts**
```python
# Override Streamlit defaults with !important
st.markdown('''
<style>
.stButton > button {
    background-color: var(--qb-primary-blue) !important;
    color: var(--qb-white) !important;
}
</style>
''', unsafe_allow_html=True)
```

### **2. Responsive Issues**
```python
# Use CSS Grid for complex layouts
st.markdown('''
<style>
.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
}
</style>
''', unsafe_allow_html=True)
```

### **3. Accessibility Violations**
```python
# Always provide alt text for images
st.image(image, caption="Chart showing monthly budget", use_column_width=True)

# Use semantic HTML elements
st.markdown('<main role="main">', unsafe_allow_html=True)
# ... your content
st.markdown('</main>', unsafe_allow_html=True)
```

## 📚 **Additional Resources**

### **1. WCAG Guidelines**
- [WCAG 2.1 AA Checklist](https://www.w3.org/WAI/WCAG21/quickref/)
- [Understanding WCAG](https://www.w3.org/WAI/WCAG21/Understanding/)

### **2. QuickBooks Design**
- [Intuit Design System](https://design.intuit.com/)
- [QuickBooks Brand Guidelines](https://design.intuit.com/brand/)

### **3. Testing Tools**
- [WebAIM Color Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [WAVE Web Accessibility Evaluator](https://wave.webaim.org/)
- [axe DevTools](https://www.deque.com/axe/)

## 🎯 **Next Steps**

1. **Integrate CSS**: Add custom.css to your Streamlit app
2. **Update Components**: Replace existing styling with custom classes
3. **Add Accessibility**: Implement ARIA labels and semantic HTML
4. **Test Thoroughly**: Validate with accessibility tools
5. **User Testing**: Test with users who have accessibility needs
6. **Continuous Improvement**: Regular accessibility audits

---

*This implementation guide provides everything you need to make your SEAS Financial Tracker app Section 508 compliant while maintaining the QuickBooks design aesthetic.*
