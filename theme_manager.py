"""
Theme Manager for SEAS Financial Tracker
Handles light/dark mode switching and theme persistence
"""

import streamlit as st
from typing import Dict, Any


class ThemeManager:
    """Manages application themes and styling"""
    
    def __init__(self):
        self.initialize_theme_state()
    
    def initialize_theme_state(self):
        """Initialize theme state in session"""
        if 'theme' not in st.session_state:
            st.session_state.theme = 'light'
        if 'theme_initialized' not in st.session_state:
            st.session_state.theme_initialized = False
    
    def get_current_theme(self) -> str:
        """Get current theme"""
        return st.session_state.get('theme', 'light')
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        current_theme = self.get_current_theme()
        new_theme = 'dark' if current_theme == 'light' else 'light'
        st.session_state.theme = new_theme
        st.rerun()
    
    def get_theme_colors(self) -> Dict[str, str]:
        """Get color scheme for current theme"""
        if self.get_current_theme() == 'dark':
            return {
                'primary': '#0073E6',
                'secondary': '#1E1E1E',
                'background': '#0E1117',
                'surface': '#262730',
                'text': '#FFFFFF',
                'text_secondary': '#B0B0B0',
                'border': '#3A3A3A',
                'success': '#00C851',
                'warning': '#FF8800',
                'error': '#FF4444',
                'info': '#33B5E5',
                'card_background': '#1E1E1E',
                'sidebar_background': '#1E1E1E',
                'header_background': '#0073E6',
                'tab_background': '#262730',
                'tab_active': '#0073E6',
                'tab_hover': '#3A3A3A'
            }
        else:
            return {
                'primary': '#0073E6',
                'secondary': '#F8F9FA',
                'background': '#FFFFFF',
                'surface': '#F1F3F4',
                'text': '#1F2937',
                'text_secondary': '#6B7280',
                'border': '#E5E7EB',
                'success': '#10B981',
                'warning': '#F59E0B',
                'error': '#EF4444',
                'info': '#3B82F6',
                'card_background': '#FFFFFF',
                'sidebar_background': '#F8F9FA',
                'header_background': '#0073E6',
                'tab_background': '#F1F3F4',
                'tab_active': '#0073E6',
                'tab_hover': '#E6F2FF'
            }
    
    def apply_theme_css(self):
        """Apply theme-specific CSS"""
        colors = self.get_theme_colors()
        theme = self.get_current_theme()
        
        css = f"""
        <style>
        /* Theme Variables */
        :root {{
            --primary-color: {colors['primary']};
            --secondary-color: {colors['secondary']};
            --background-color: {colors['background']};
            --surface-color: {colors['surface']};
            --text-color: {colors['text']};
            --text-secondary: {colors['text_secondary']};
            --border-color: {colors['border']};
            --success-color: {colors['success']};
            --warning-color: {colors['warning']};
            --error-color: {colors['error']};
            --info-color: {colors['info']};
            --card-background: {colors['card_background']};
            --sidebar-background: {colors['sidebar_background']};
            --header-background: {colors['header_background']};
            --tab-background: {colors['tab_background']};
            --tab-active: {colors['tab_active']};
            --tab-hover: {colors['tab_hover']};
        }}
        
        /* Main App Styling */
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        
        /* Header Styling */
        .main-header {{
            background: linear-gradient(135deg, var(--header-background) 0%, #0056b3 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .main-header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        
        .subtitle {{
            margin-top: 0.5rem;
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: var(--surface-color);
            padding: 8px;
            border-radius: 12px;
            margin-bottom: 2rem;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: var(--tab-background);
            border-radius: 8px;
            padding: 12px 20px;
            font-weight: 500;
            transition: all 0.2s ease;
            color: var(--text-color);
            border: 1px solid var(--border-color);
        }}
        
        .stTabs [aria-selected="true"] {{
            background: var(--tab-active);
            color: white;
            border-color: var(--tab-active);
        }}
        
        .stTabs [data-baseweb="tab"]:hover {{
            background: var(--tab-hover);
            color: var(--text-color);
        }}
        
        /* Sidebar Styling */
        .css-1d391kg {{
            background-color: var(--sidebar-background);
        }}
        
        .css-1d391kg .stSelectbox label {{
            color: var(--text-color);
        }}
        
        /* Card Styling */
        .metric-card {{
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .metric-card h3 {{
            color: var(--text-color);
            margin: 0 0 0.5rem 0;
            font-size: 0.9rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-card .metric-value {{
            color: var(--primary-color);
            font-size: 2rem;
            font-weight: 700;
            margin: 0;
        }}
        
        .metric-card .metric-change {{
            color: var(--text-secondary);
            font-size: 0.8rem;
            margin-top: 0.25rem;
        }}
        
        /* Section Styling */
        .section-container {{
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        
        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }}
        
        .section-header h3 {{
            color: var(--text-color);
            margin: 0;
            font-size: 1.25rem;
            font-weight: 600;
        }}
        
        /* Button Styling */
        .stButton > button {{
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            background: #0056b3;
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }}
        
        /* Data Table Styling */
        .stDataFrame {{
            background: var(--card-background);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }}
        
        /* Plotly Chart Styling */
        .js-plotly-plot {{
            background: var(--card-background);
            border-radius: 8px;
        }}
        
        /* Status Badges */
        .status-badge {{
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .status-active {{
            background: var(--success-color);
            color: white;
        }}
        
        .status-pending {{
            background: var(--warning-color);
            color: white;
        }}
        
        .status-completed {{
            background: var(--info-color);
            color: white;
        }}
        
        /* Theme Toggle Button */
        .theme-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: var(--primary-color);
            color: white;
            border: none;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            font-size: 1.2rem;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            transition: all 0.2s ease;
        }}
        
        .theme-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
        }}
        
        /* Dark theme specific adjustments */
        {self._get_dark_theme_css() if theme == 'dark' else ''}
        
        /* Light theme specific adjustments */
        {self._get_light_theme_css() if theme == 'light' else ''}
        </style>
        """
        
        st.markdown(css, unsafe_allow_html=True)
    
    def _get_dark_theme_css(self) -> str:
        """Get dark theme specific CSS"""
        return """
        /* Dark theme specific styles */
        .stSelectbox > div > div {
            background-color: var(--surface-color);
            color: var(--text-color);
        }
        
        .stTextInput > div > div > input {
            background-color: var(--surface-color);
            color: var(--text-color);
            border-color: var(--border-color);
        }
        
        .stNumberInput > div > div > input {
            background-color: var(--surface-color);
            color: var(--text-color);
            border-color: var(--border-color);
        }
        
        .stTextArea > div > div > textarea {
            background-color: var(--surface-color);
            color: var(--text-color);
            border-color: var(--border-color);
        }
        
        /* Plotly dark theme */
        .plotly .modebar {
            background-color: var(--surface-color) !important;
        }
        
        .plotly .modebar-btn {
            color: var(--text-color) !important;
        }
        """
    
    def _get_light_theme_css(self) -> str:
        """Get light theme specific CSS"""
        return """
        /* Light theme specific styles */
        .stSelectbox > div > div {
            background-color: white;
            color: var(--text-color);
        }
        
        .stTextInput > div > div > input {
            background-color: white;
            color: var(--text-color);
            border-color: var(--border-color);
        }
        
        .stNumberInput > div > div > input {
            background-color: white;
            color: var(--text-color);
            border-color: var(--border-color);
        }
        
        .stTextArea > div > div > textarea {
            background-color: white;
            color: var(--text-color);
            border-color: var(--border-color);
        }
        """
    
    def render_theme_toggle(self):
        """Render theme toggle button"""
        theme_icon = "🌙" if self.get_current_theme() == 'light' else "☀️"
        
        if st.button(theme_icon, key="theme_toggle", help=f"Switch to {'dark' if self.get_current_theme() == 'light' else 'light'} mode"):
            self.toggle_theme()
    
    def get_plotly_theme(self) -> Dict[str, Any]:
        """Get Plotly theme configuration"""
        colors = self.get_theme_colors()
        
        if self.get_current_theme() == 'dark':
            return {
                'layout': {
                    'paper_bgcolor': colors['background'],
                    'plot_bgcolor': colors['surface'],
                    'font': {'color': colors['text']},
                    'xaxis': {
                        'gridcolor': colors['border'],
                        'color': colors['text']
                    },
                    'yaxis': {
                        'gridcolor': colors['border'],
                        'color': colors['text']
                    }
                }
            }
        else:
            return {
                'layout': {
                    'paper_bgcolor': 'white',
                    'plot_bgcolor': 'white',
                    'font': {'color': colors['text']},
                    'xaxis': {
                        'gridcolor': colors['border'],
                        'color': colors['text']
                    },
                    'yaxis': {
                        'gridcolor': colors['border'],
                        'color': colors['text']
                    }
                }
            }


def render_theme_toggle_sidebar():
    """Render theme toggle in sidebar"""
    theme_manager = ThemeManager()
    
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🎨 Theme")
        
        current_theme = theme_manager.get_current_theme()
        theme_display = "🌙 Dark Mode" if current_theme == 'dark' else "☀️ Light Mode"
        
        if st.button(f"Switch to {'Light' if current_theme == 'dark' else 'Dark'} Mode", 
                    use_container_width=True, key="sidebar_theme_toggle"):
            theme_manager.toggle_theme()
        
        st.markdown(f"**Current:** {theme_display}")
