import pandas as pd
import streamlit as st

from dashboard.components.chart_components import (
    render_correlation_heatmap,
    render_risk_distribution,
    render_scatter_plot,
    render_score_distribution,
)


def show_analytics_page():
    """Display the analytics and analysis page."""
    st.markdown('<h1 class="main-header">Analytics & Analysis</h1>', unsafe_allow_html=True)

    if 'analysis_results' not in st.session_state or not st.session_state.analysis_results:
        st.info("Run the full analysis from the sidebar to view analytics.")
        if st.session_state.get('current_data') is not None:
            data = st.session_state.current_data
            st.markdown("### Quick Data Snapshot")
            k1, k2, k3 = st.columns(3)
            with k1:
                st.metric("Students", len(data))
            with k2:
                st.metric("Mean Quiz", f"{data['quiz_score'].mean():.1f}")
            with k3:
                st.metric("Mean Attendance", f"{data['attendance_percentage'].mean():.1f}%")
        return

    analysis_results = st.session_state.analysis_results
    perf_results = analysis_results.get('performance', {})

    st.markdown('<h2 class="sub-header">Performance Metrics</h2>', unsafe_allow_html=True)
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    with metric_col1:
        st.metric("Mean Quiz Score", f"{perf_results.get('mean_quiz_score', 0):.1f}")
    with metric_col2:
        st.metric("Mean Assignment Score", f"{perf_results.get('mean_assignment_score', 0):.1f}")
    with metric_col3:
        st.metric("Mean Attendance", f"{perf_results.get('mean_attendance', 0):.1f}%")
    with metric_col4:
        st.metric("Mean Completion", f"{perf_results.get('mean_completion', 0):.1f}%")

    st.markdown('<h3 class="sub-header">Score Distributions</h3>', unsafe_allow_html=True)
    dist_col1, dist_col2 = st.columns(2)
    with dist_col1:
        if st.session_state.get('current_data') is not None:
            render_score_distribution(st.session_state.current_data, 'quiz_score', "Quiz Score Distribution")
    with dist_col2:
        if st.session_state.get('current_data') is not None:
            render_score_distribution(st.session_state.current_data, 'assignment_score', "Assignment Score Distribution")

    if analysis_results.get('risk_prediction'):
        st.markdown('<h3 class="sub-header">Risk Prediction</h3>', unsafe_allow_html=True)
        risk_results = analysis_results['risk_prediction']
        risk_col1, risk_col2, risk_col3 = st.columns(3)
        with risk_col1:
            st.metric("High Risk Students", f"{risk_results.get('high_risk_count', 0)}")
        with risk_col2:
            st.metric("Medium Risk Students", f"{risk_results.get('medium_risk_count', 0)}")
        with risk_col3:
            st.metric("Low Risk Students", f"{risk_results.get('low_risk_count', 0)}")

        if risk_results.get('risk_categories'):
            risk_counts = pd.Series(risk_results['risk_categories']).value_counts()
            render_risk_distribution(risk_counts, "Risk Level Distribution")

    if perf_results.get('correlations'):
        st.markdown('<h3 class="sub-header">Correlation Analysis</h3>', unsafe_allow_html=True)
        corr_matrix = pd.DataFrame(perf_results['correlations'])
        if not corr_matrix.empty:
            render_correlation_heatmap(corr_matrix, "Correlation Heatmap of Key Metrics")

    if perf_results.get('attendance_impact'):
        st.markdown('<h3 class="sub-header">Attendance Impact Analysis</h3>', unsafe_allow_html=True)
        attendance_data = perf_results['attendance_impact']
        att_col1, att_col2, att_col3 = st.columns(3)
        with att_col1:
            st.metric("High Attendance Avg Score", f"{attendance_data.get('high_attendance_avg_score', 0):.1f}")
        with att_col2:
            st.metric("Low Attendance Avg Score", f"{attendance_data.get('low_attendance_avg_score', 0):.1f}")
        with att_col3:
            st.metric("Score Difference", f"{attendance_data.get('difference', 0):.1f}")

        if st.session_state.get('current_data') is not None:
            render_scatter_plot(
                st.session_state.current_data,
                'attendance_percentage',
                'quiz_score',
                None,
                "Attendance Percentage vs Quiz Score",
            )
