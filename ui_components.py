"""
Reusable UI Components for SEAS Financial Tracker
"""
import streamlit as st
from typing import List, Dict, Any, Callable
import pandas as pd

class MetricCard:
    """Reusable metric card component"""
    
    @staticmethod
    def render(icon: str, value: str, label: str, color: str = "#2E5BBA") -> None:
        """Render a metric card"""
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div class="metric-icon">{icon}</div>
            <div class="metric-value" style="color: {color};">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

class FinancialCard:
    """Reusable financial information card"""
    
    @staticmethod
    def render(title: str, items: List[Dict[str, Any]], is_total: bool = False) -> None:
        """Render a financial card"""
        items_html = ""
        for item in items:
            if is_total and item == items[-1]:
                items_html += f"""
                <div class="financial-item">
                    <span>{item['label']}</span>
                    <strong style="color: {item.get('color', '#2E5BBA')};">{item['value']}</strong>
                </div>
                """
            else:
                items_html += f"""
                <div class="financial-item">
                    <span>{item['label']}</span>
                    <strong>{item['value']}</strong>
                </div>
                """
        
        st.markdown(f"""
        <div class="financial-card">
            <h3>{title}</h3>
            {items_html}
        </div>
        """, unsafe_allow_html=True)

class RemovalInterface:
    """Reusable removal interface component"""
    
    @staticmethod
    def render(
        title: str,
        items: List[Any],
        item_display_func: Callable[[Any], str],
        item_details_func: Callable[[Any], Dict[str, str]],
        on_remove: Callable[[Any], None],
        item_count: int,
        bulk_operations: List[Dict[str, Any]] = None
    ) -> None:
        """Render a removal interface"""
        st.markdown(f'<div class="subheader">🗑️ {title}</div>', unsafe_allow_html=True)
        
        if not items:
            st.warning("⚠️ No items to remove.")
            return
        
        st.write("Select items to remove from the project:")
        
        # Individual removal
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            selected_item = st.selectbox(
                f"Choose item to remove:",
                options=[item_display_func(item) for item in items],
                key=f"{title.lower().replace(' ', '_')}_removal_select"
            )
        
        with col2:
            if selected_item:
                # Find the actual item object
                selected_obj = next((item for item in items if item_display_func(item) == selected_item), None)
                if selected_obj:
                    details = item_details_func(selected_obj)
                    for key, value in details.items():
                        st.write(f"**{key}:** {value}")
        
        with col3:
            if selected_item:
                if st.button("🗑️ Remove", type="secondary", key=f"remove_{title.lower().replace(' ', '_')}_btn"):
                    selected_obj = next((item for item in items if item_display_func(item) == selected_item), None)
                    if selected_obj:
                        on_remove(selected_obj)
                        st.success(f"✅ Item has been removed successfully.")
                        st.rerun()
        
        # Show current count
        st.info(f"📊 **Current {title} Count:** {item_count}")
        
        # Bulk operations
        if bulk_operations:
            st.markdown("---")
            st.markdown("**Bulk Operations:**")
            
            for operation in bulk_operations:
                col1, col2 = st.columns([2, 1])
                with col1:
                    if operation['type'] == 'select':
                        selected_bulk = st.selectbox(
                            operation['label'],
                            options=operation['options'],
                            key=f"bulk_{operation['key']}_select"
                        )
                    else:
                        selected_bulk = None
                
                with col2:
                    if st.button(operation['button_text'], type="secondary", key=f"bulk_{operation['key']}_btn"):
                        operation['action'](selected_bulk)
                        st.rerun()

class DataTable:
    """Reusable data table component"""
    
    @staticmethod
    def render(
        data: pd.DataFrame,
        columns: List[str],
        column_configs: Dict[str, Any] = None,
        key: str = "data_table",
        width: str = 'stretch'
    ) -> pd.DataFrame:
        """Render a data table with editing capabilities"""
        return st.data_editor(
            data[columns],
            column_config=column_configs or {},
            width=width,
            key=key
        )

class ChartContainer:
    """Reusable chart container component"""
    
    @staticmethod
    def render(chart_func: Callable, *args, **kwargs) -> None:
        """Render a chart in a styled container"""
        st.markdown("""
        <div class="stPlotlyChart">
        """, unsafe_allow_html=True)
        
        chart_func(*args, **kwargs)
        
        st.markdown("</div>", unsafe_allow_html=True)

class FormSection:
    """Reusable form section component"""
    
    @staticmethod
    def render(title: str, columns: int = 3):
        """Render a form section with expandable interface"""
        with st.expander(f"➕ {title}", expanded=False):
            return st.columns(columns)
    
    @staticmethod
    def create_expandable(title: str, columns: int = 3):
        """Create an expandable section and return columns"""
        expander = st.expander(f"➕ {title}", expanded=False)
        with expander:
            return st.columns(columns)

class SuccessMessage:
    """Reusable success message component"""
    
    @staticmethod
    def render(message: str) -> None:
        """Render a success message"""
        st.success(f"✅ {message}")

class ErrorMessage:
    """Reusable error message component"""
    
    @staticmethod
    def render(message: str) -> None:
        """Render an error message"""
        st.error(f"❌ {message}")

class WarningMessage:
    """Reusable warning message component"""
    
    @staticmethod
    def render(message: str) -> None:
        """Render a warning message"""
        st.warning(f"⚠️ {message}")

class InfoMessage:
    """Reusable info message component"""
    
    @staticmethod
    def render(message: str) -> None:
        """Render an info message"""
        st.info(f"📊 {message}")
