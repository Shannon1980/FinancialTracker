"""
Modern UI/UX Components for SEAS Financial Tracker
Implements accessibility best practices and modern design principles
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional, Any
import plotly.express as px
import plotly.graph_objects as go


class ModernUI:
    """Modern UI components with accessibility and design best practices"""
    
    def __init__(self):
        self.load_modern_css()
    
    def load_modern_css(self):
        """Load modern CSS with accessibility and design improvements"""
        css = """
        <style>
        /* Modern Design System */
        :root {
            --primary-color: #0073E6;
            --secondary-color: #1E1E1E;
            --success-color: #10B981;
            --warning-color: #F59E0B;
            --error-color: #EF4444;
            --background-color: #FFFFFF;
            --surface-color: #F8F9FA;
            --text-primary: #1E1E1E;
            --text-secondary: #6B7280;
            --border-color: #E5E7EB;
            --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
            --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --spacing-xs: 4px;
            --spacing-sm: 8px;
            --spacing-md: 16px;
            --spacing-lg: 24px;
            --spacing-xl: 32px;
            --spacing-xxl: 48px;
        }
        
        /* Base Typography */
        .stApp {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
        }
        
        /* Improved Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            line-height: 1.3;
            color: var(--text-primary);
            margin-bottom: var(--spacing-md);
        }
        
        h1 { font-size: 2.5rem; }
        h2 { font-size: 2rem; }
        h3 { font-size: 1.5rem; }
        h4 { font-size: 1.25rem; }
        h5 { font-size: 1.125rem; }
        h6 { font-size: 1rem; }
        
        /* Modern Card Components */
        .modern-card {
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
            border-radius: var(--radius-lg);
            padding: var(--spacing-xl);
            margin-bottom: var(--spacing-lg);
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .modern-card:hover {
            background: #F1F3F4;
            box-shadow: var(--shadow-md);
            transform: translateY(-1px);
        }
        
        .modern-card-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: var(--spacing-lg);
            padding-bottom: var(--spacing-md);
            border-bottom: 1px solid #D1D5DB;
            background: #F3F4F6;
            margin: calc(-1 * var(--spacing-xl)) calc(-1 * var(--spacing-xl)) var(--spacing-lg) calc(-1 * var(--spacing-xl));
            padding: var(--spacing-md) var(--spacing-xl);
            border-radius: var(--radius-lg) var(--radius-lg) 0 0;
        }
        
        .modern-card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }
        
        .modern-card-subtitle {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: 0;
        }
        
        /* Metric Cards */
        .metric-card {
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            text-align: center;
            box-shadow: var(--shadow-sm);
            transition: all 0.2s ease;
        }
        
        .metric-card:hover {
            background: #F1F3F4;
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
            line-height: 1;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin: var(--spacing-sm) 0 0 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-change {
            font-size: 0.75rem;
            margin-top: var(--spacing-xs);
        }
        
        .metric-change.positive {
            color: var(--success-color);
        }
        
        .metric-change.negative {
            color: var(--error-color);
        }
        
        /* Navigation */
        .modern-nav {
            background: #F8F9FA;
            border-bottom: 1px solid #E5E7EB;
            padding: var(--spacing-md) 0;
            margin-bottom: var(--spacing-xl);
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        }
        
        .nav-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--primary-color);
            margin: 0;
        }
        
        /* Form Improvements */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input,
        .stSelectbox > div > div > select,
        .stTextArea > div > div > textarea {
            border: 1px solid var(--border-color);
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-md);
            font-size: 1rem;
            transition: all 0.2s ease;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus,
        .stSelectbox > div > div > select:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(0, 115, 230, 0.1);
            outline: none;
        }
        
        /* Button Improvements */
        .stButton > button {
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: var(--radius-sm);
            padding: var(--spacing-sm) var(--spacing-lg);
            font-size: 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
            cursor: pointer;
        }
        
        .stButton > button:hover {
            background: #0056b3;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .stButton > button:active {
            transform: translateY(0);
        }
        
        /* Success Button */
        .stButton > button[data-testid="baseButton-secondary"] {
            background: var(--success-color);
        }
        
        .stButton > button[data-testid="baseButton-secondary"]:hover {
            background: #059669;
        }
        
        /* Alert Components */
        .alert {
            padding: var(--spacing-md);
            border-radius: var(--radius-md);
            margin-bottom: var(--spacing-md);
            border-left: 4px solid;
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
        }
        
        .alert-success {
            background: #F0FDF4;
            border-left-color: var(--success-color);
            border-color: #BBF7D0;
            color: #166534;
        }
        
        .alert-warning {
            background: #FFFBEB;
            border-left-color: var(--warning-color);
            border-color: #FED7AA;
            color: #92400E;
        }
        
        .alert-error {
            background: #FEF2F2;
            border-left-color: var(--error-color);
            border-color: #FECACA;
            color: #991B1B;
        }
        
        .alert-info {
            background: #EFF6FF;
            border-left-color: var(--primary-color);
            border-color: #BFDBFE;
            color: #1E40AF;
        }
        
        /* Loading States */
        .loading-spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(0, 115, 230, 0.3);
            border-radius: 50%;
            border-top-color: var(--primary-color);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Section Dividers */
        .section-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, #E5E7EB, transparent);
            margin: var(--spacing-xl) 0;
        }
        
        /* Content Areas */
        .content-section {
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
        }
        
        /* Form Containers */
        .form-container {
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
            border-radius: var(--radius-md);
            padding: var(--spacing-lg);
            margin-bottom: var(--spacing-md);
        }
        
        /* Data Tables */
        .data-table-container {
            background: #F8F9FA;
            border: 1px solid #E5E7EB;
            border-radius: var(--radius-md);
            padding: var(--spacing-md);
            margin-bottom: var(--spacing-md);
        }
        
        /* Responsive Design */
        @media (max-width: 768px) {
            .modern-card {
                padding: var(--spacing-lg);
                margin-bottom: var(--spacing-md);
            }
            
            .metric-value {
                font-size: 1.5rem;
            }
            
            h1 { font-size: 2rem; }
            h2 { font-size: 1.75rem; }
            h3 { font-size: 1.25rem; }
        }
        
        /* Accessibility Improvements */
        .sr-only {
            position: absolute;
            width: 1px;
            height: 1px;
            padding: 0;
            margin: -1px;
            overflow: hidden;
            clip: rect(0, 0, 0, 0);
            white-space: nowrap;
            border: 0;
        }
        
        /* Focus indicators */
        *:focus {
            outline: 2px solid var(--primary-color);
            outline-offset: 2px;
        }
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {
            :root {
                --border-color: #000000;
                --text-secondary: #000000;
            }
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def create_metric_card(self, title: str, value: str, change: Optional[str] = None, 
                          change_type: str = "neutral") -> str:
        """Create a modern metric card with accessibility features"""
        change_html = ""
        if change:
            change_class = "positive" if change_type == "positive" else "negative" if change_type == "negative" else ""
            change_html = f'<div class="metric-change {change_class}">{change}</div>'
        
        return f"""
        <div class="metric-card" role="region" aria-label="{title} metric">
            <div class="metric-value" aria-live="polite">{value}</div>
            <div class="metric-label">{title}</div>
            {change_html}
        </div>
        """
    
    def create_alert(self, message: str, alert_type: str = "info", 
                    title: Optional[str] = None) -> str:
        """Create accessible alert component"""
        title_html = f'<strong>{title}</strong><br>' if title else ""
        return f"""
        <div class="alert alert-{alert_type}" role="alert" aria-live="polite">
            {title_html}{message}
        </div>
        """
    
    def create_loading_state(self, message: str = "Loading...") -> str:
        """Create accessible loading state"""
        return f"""
        <div class="loading-spinner" aria-label="{message}" role="status">
            <span class="sr-only">{message}</span>
        </div>
        """
    
    def create_modern_card(self, title: str, content: str, subtitle: Optional[str] = None) -> str:
        """Create modern card component with accessibility features"""
        subtitle_html = f'<div class="modern-card-subtitle">{subtitle}</div>' if subtitle else ""
        
        return f"""
        <div class="modern-card" role="region" aria-labelledby="card-title">
            <div class="modern-card-header">
                <div>
                    <h3 class="modern-card-title" id="card-title">{title}</h3>
                    {subtitle_html}
                </div>
            </div>
            <div class="modern-card-content">
                {content}
            </div>
        </div>
        """
    
    def create_navigation_header(self, title: str, subtitle: Optional[str] = None) -> str:
        """Create modern navigation header"""
        subtitle_html = f'<p style="margin: 0; color: var(--text-secondary);">{subtitle}</p>' if subtitle else ""
        
        return f"""
        <div class="modern-nav">
            <div class="nav-title">{title}</div>
            {subtitle_html}
        </div>
        """
    
    def render_metric_grid(self, metrics: List[Dict[str, Any]], columns: int = 4):
        """Render a grid of metric cards"""
        cols = st.columns(columns)
        
        for i, metric in enumerate(metrics):
            with cols[i % columns]:
                card_html = self.create_metric_card(
                    title=metric.get('title', ''),
                    value=metric.get('value', ''),
                    change=metric.get('change'),
                    change_type=metric.get('change_type', 'neutral')
                )
                st.markdown(card_html, unsafe_allow_html=True)
    
    def render_alert(self, message: str, alert_type: str = "info", title: Optional[str] = None):
        """Render alert component"""
        alert_html = self.create_alert(message, alert_type, title)
        st.markdown(alert_html, unsafe_allow_html=True)
    
    def render_loading(self, message: str = "Loading..."):
        """Render loading state"""
        loading_html = self.create_loading_state(message)
        st.markdown(loading_html, unsafe_allow_html=True)
    
    def render_card(self, title: str, content: str, subtitle: Optional[str] = None):
        """Render modern card component"""
        card_html = self.create_modern_card(title, content, subtitle)
        st.markdown(card_html, unsafe_allow_html=True)
    
    def render_navigation(self, title: str, subtitle: Optional[str] = None):
        """Render navigation header"""
        nav_html = self.create_navigation_header(title, subtitle)
        st.markdown(nav_html, unsafe_allow_html=True)
    
    def create_accessible_chart(self, fig, title: str, description: str) -> go.Figure:
        """Create accessible chart with proper labels and descriptions"""
        # Add accessibility features to Plotly chart
        fig.update_layout(
            title={
                'text': title,
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 18, 'family': 'Inter'}
            },
            font={'family': 'Inter', 'size': 14},
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(t=60, l=60, r=60, b=60)
        )
        
        # Add description for screen readers
        fig.add_annotation(
            text=description,
            xref="paper", yref="paper",
            x=0, y=1.1,
            showarrow=False,
            font=dict(size=12, color="gray"),
            xanchor="left"
        )
        
        return fig
    
    def create_form_section(self, title: str, description: str) -> str:
        """Create accessible form section with light grey background"""
        return f"""
        <div class="modern-card" role="group" aria-labelledby="form-title" style="background: #F8F9FA; border: 1px solid #E5E7EB;">
            <div class="modern-card-header" style="background: #F3F4F6; border-bottom: 1px solid #D1D5DB;">
                <div>
                    <h3 class="modern-card-title" id="form-title">{title}</h3>
                    <div class="modern-card-subtitle">{description}</div>
                </div>
            </div>
            <div class="modern-card-content" style="background: #F8F9FA;">
        """
    
    def end_form_section(self) -> str:
        """End form section"""
        return "</div></div>"
    
    def create_content_section(self, content: str) -> str:
        """Create content section with light grey background"""
        return f"""
        <div class="content-section">
            {content}
        </div>
        """
    
    def create_form_container(self, content: str) -> str:
        """Create form container with light grey background"""
        return f"""
        <div class="form-container">
            {content}
        </div>
        """
    
    def create_data_table_container(self, content: str) -> str:
        """Create data table container with light grey background"""
        return f"""
        <div class="data-table-container">
            {content}
        </div>
        """
    
    def create_section_divider(self) -> str:
        """Create section divider"""
        return '<div class="section-divider"></div>'
    
    def render_content_section(self, content: str):
        """Render content section"""
        section_html = self.create_content_section(content)
        st.markdown(section_html, unsafe_allow_html=True)
    
    def render_form_container(self, content: str):
        """Render form container"""
        container_html = self.create_form_container(content)
        st.markdown(container_html, unsafe_allow_html=True)
    
    def render_data_table_container(self, content: str):
        """Render data table container"""
        container_html = self.create_data_table_container(content)
        st.markdown(container_html, unsafe_allow_html=True)
    
    def render_section_divider(self):
        """Render section divider"""
        divider_html = self.create_section_divider()
        st.markdown(divider_html, unsafe_allow_html=True)
