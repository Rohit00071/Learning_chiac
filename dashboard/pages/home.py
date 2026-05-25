import pandas as pd
import streamlit as st

from dashboard.components.chart_components import render_risk_distribution, render_score_distribution
from dashboard.components.kpi_card import render_metric_card


def show_home_page():
    """Display the home dashboard page."""
    st.markdown('<h1 class="main-header">AI Learning Analytics Dashboard</h1>', unsafe_allow_html=True)

    st.markdown("### Pipeline Status")
    status_cols = st.columns(4)
    with status_cols[0]:
        st.metric("Data Loaded", "Yes" if st.session_state.get('data_loaded', False) else "No")
    with status_cols[1]:
        st.metric("Analysis Ready", "Yes" if st.session_state.get('analysis_completed', False) else "No")
    with status_cols[2]:
        st.metric("Insights Ready", "Yes" if st.session_state.get('insights_generated', False) else "No")
    with status_cols[3]:
        st.metric("Recommendations Ready", "Yes" if st.session_state.get('recommendations_generated', False) else "No")

    if 'current_data' not in st.session_state or st.session_state.current_data is None:
        st.info("Please load data using the sidebar to begin analysis.")
        return

    data = st.session_state.current_data

    st.markdown('<h2 class="sub-header">Dashboard Overview</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_metric_card("Total Students", len(data) if data is not None else 0, "Users")

    with col2:
        if st.session_state.get('analysis_results'):
            perf = st.session_state.analysis_results.get('performance', {})
            render_metric_card("Avg Quiz Score", f"{perf.get('mean_quiz_score', 0):.1f}", "Quiz")
        else:
            render_metric_card("Avg Quiz Score", "-", "Quiz")

    with col3:
        if st.session_state.get('analysis_results'):
            risk = st.session_state.analysis_results.get('risk_prediction', {})
            render_metric_card("High Risk Students", f"{risk.get('high_risk_percentage', 0):.1f}%", "Risk")
        else:
            render_metric_card("High Risk Students", "-", "Risk")

    with col4:
        render_metric_card("Insights Generated", len(st.session_state.get('insights', [])) or "-", "Insights")

    if st.session_state.get('analysis_results'):
        st.markdown('<h3 class="sub-header">Performance Overview</h3>', unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            if data is not None and not data.empty:
                render_score_distribution(data, 'quiz_score', "Quiz Score Distribution")

        with chart_col2:
            risk_data = st.session_state.analysis_results.get('risk_prediction', {})
            if 'risk_categories' in risk_data:
                risk_counts = pd.Series(risk_data['risk_categories']).value_counts()
                render_risk_distribution(risk_counts, "Student Risk Distribution")

    if st.session_state.get('insights'):
        st.markdown('<h3 class="sub-header">Recent Insights</h3>', unsafe_allow_html=True)
        for insight in st.session_state.insights[:3]:
            priority_class = f"insight-{insight['priority'].lower()}"
            st.markdown(
                f"""
                <div class="insight-card {priority_class}">
                    <strong>{insight['category']}</strong><br>
                    {insight['text']}
                    <br><small>Priority: {insight['priority']}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
