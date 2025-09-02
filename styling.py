"""
Styling and CSS management for SEAS Financial Tracker
Handles Section 508 compliant QuickBooks design system
"""

import streamlit as st
from typing import Optional


def load_css() -> None:
    """Load the comprehensive CSS for Section 508 compliance and QuickBooks design"""
    try:
        with open('static/custom.css', 'r') as f:
            css_content = f.read()
        st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        st.success("✅ Section 508 compliant QuickBooks design loaded successfully!")
    except FileNotFoundError:
        st.warning("⚠️ CSS file not found. Using default Streamlit styling.")
        load_fallback_css()
    except Exception as e:
        st.error(f"❌ Error loading CSS: {e}")
        load_fallback_css()


def load_fallback_css() -> None:
    """Load fallback QuickBooks-inspired styling when main CSS is not available"""
    st.markdown("""
    <style>
        .stApp { 
            background: #f7fafc; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
        }
        .stButton > button { 
            background: #2C7BE5; 
            color: white; 
            border-radius: 8px; 
            padding: 0.75rem 1.5rem; 
        }
        .stButton > button:hover { 
            background: #2D3748; 
            transform: translateY(-1px); 
        }
    </style>
    """, unsafe_allow_html=True)


def create_section(title: str, content: str, section_type: str = "info", 
                  status: Optional[str] = None, footer_content: Optional[str] = None, 
                  actions: Optional[list] = None) -> None:
    """Create a modular section with consistent styling"""
    
    # Section type classes
    type_classes = {
        "info": "info-section",
        "success": "success-section", 
        "warning": "warning-section",
        "danger": "danger-section"
    }
    
    # Status badges
    status_badges = {
        "active": "active",
        "pending": "pending",
        "completed": "completed",
        "ready": "completed",
        "needs_review": "pending"
    }
    
    # Build section HTML
    section_class = f"section-container {type_classes.get(section_type, 'info-section')}"
    status_html = f'<span class="section-status {status_badges.get(status, "active")}">{status or "Active"}</span>' if status else ""
    
    section_html = f'''
    <div class="{section_class}">
        <div class="section-header">
            <h3>{title}</h3>
            {status_html}
        </div>
        <div class="section-content">
            {content}
        </div>
    '''
    
    # Add footer if provided
    if footer_content or actions:
        section_html += '<div class="section-footer">'
        if footer_content:
            section_html += f'<span>{footer_content}</span>'
        if actions:
            section_html += '<div class="section-actions">'
            for action in actions:
                section_html += f'<button class="btn btn-{action["type"]}">{action["label"]}</button>'
            section_html += '</div>'
        section_html += '</div>'
    
    section_html += '</div>'
    
    return st.markdown(section_html, unsafe_allow_html=True)


def create_section_divider() -> None:
    """Create a visual separator between sections"""
    st.markdown("---")


def create_section_grid(sections: list, columns: int = 2) -> None:
    """Create a grid layout for multiple sections"""
    cols = st.columns(columns)
    for i, section in enumerate(sections):
        with cols[i % columns]:
            st.markdown(section)


def create_metric_card(title: str, value: str, change: Optional[str] = None, 
                      change_type: str = "positive") -> str:
    """Create a metric card with optional change indicator"""
    change_html = ""
    if change:
        change_class = "positive" if change_type == "positive" else "negative"
        change_html = f'<p class="metric-change {change_class}">{change}</p>'
    
    return f'''
    <div class="metric-card">
        <div class="metric-content">
            <h4 class="metric-title">{title}</h4>
            <p class="metric-value">{value}</p>
            {change_html}
        </div>
    </div>
    '''
