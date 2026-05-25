import streamlit as st

def render_kpi_card(title, value, icon="📊", prefix="", suffix="", help_text=None):
    """
    Render a KPI card component.

    Args:
        title (str): Title of the KPI
        value (any): Value to display
        icon (str): Emoji icon
        prefix (str): Prefix for value (e.g., "$")
        suffix (str): Suffix for value (e.g., "%")
        help_text (str, optional): Help text to show on hover
    """
    formatted_value = f"{prefix}{value}{suffix}" if not isinstance(value, str) else value

    if help_text:
        st.metric(label=f"{icon} {title}", value=formatted_value, help=help_text)
    else:
        st.metric(label=f"{icon} {title}", value=formatted_value)

def render_metric_card(title, value, icon="📊", color="#1f77b4"):
    """
    Render a custom metric card with HTML styling.

    Args:
        title (str): Title of the metric
        value (any): Value to display
        icon (str): Emoji icon
        color (str): Color for the accent bar
    """
    st.markdown(f"""
    <div style="
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid {color};
        margin: 0.5rem 0;
    ">
        <div style="font-size: 2rem; font-weight: bold; color: {color};">{icon} {value}</div>
        <div style="font-size: 1rem; color: var(--text-color); opacity: 0.7;">{title}</div>
    </div>
    """, unsafe_allow_html=True)