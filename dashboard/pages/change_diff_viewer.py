import streamlit as st
import pandas as pd
from dashboard.components.kpi_card import render_metric_card

def show_change_diff_viewer_page():
    """Display the change diff viewer page."""
    st.markdown('<h1 class="main-header">🔄 Change Diff Viewer</h1>', unsafe_allow_html=True)

    st.markdown("### Tracking Insight Evolution Over Time")
    st.markdown("""
    This page shows how insights and recommendations change as more data is added to the system.
    Run analysis multiple times with different datasets to see the evolution of insights.
    """)

    # Check if we have at least one analysis
    if 'insights' not in st.session_state or not st.session_state.insights:
        st.info("👈 Please run analysis at least once to enable change detection.")
        return

    # Initialize diff viewer agent if not exists
    if 'diff_viewer_agent' not in st.session_state:
        from agents.diff_viewer_agent import ChangeDiffViewerAgent
        from database.database import LearningDatabase
        from utils.config import DATABASE_PATH
        st.session_state.diff_viewer_agent = ChangeDiffViewerAgent(DATABASE_PATH)

    # Load current and previous insights
    st.session_state.diff_viewer_agent.load_current_insights(st.session_state.insights)
    st.session_state.diff_viewer_agent.load_previous_insights()

    # Compute differences
    diff_results = st.session_state.diff_viewer_agent.compute_insight_differences()

    # Display summary statistics
    st.markdown("#### Comparison Summary")
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    with summary_col1:
        render_metric_card("Current Insights", diff_results['total_current'], "📊")
    with summary_col2:
        render_metric_card("Previous Insights", diff_results['total_previous'], "📊")
    with summary_col3:
        render_metric_card("New Insights", len(diff_results['added']), "✅")
    with summary_col4:
        render_metric_card("Removed Insights", len(diff_results['removed']), "❌")

    # Display detailed differences
    diff_text = st.session_state.diff_viewer_agent.format_diff_for_display()
    st.text(diff_text)

    # Trend analysis
    st.markdown("#### Trend Analysis")
    trends = st.session_state.diff_viewer_agent.get_insight_trends()

    trend_col1, trend_col2 = st.columns([2, 1])
    with trend_col1:
        trend_description = {
            'no_data': 'No data available for trend analysis',
            'increasing_concern': '📈 Increasing number of high-priority insights (potential emerging issues)',
            'improving_situation': '📉 Decreasing number of high-priority insights (situation improving)',
            'moderate_changes': '🔄 Moderate changes in insight priorities',
            'stable': '✅ Insight priorities remain stable'
        }.get(trends['trend'], trends['trend'])

        st.info(f"**Overall Trend:** {trend_description}")

    with trend_col2:
        if st.session_state.diff_viewer_agent.get_latest_analysis_snapshot():
            st.success("📁 Baseline snapshot available")
        else:
            st.warning("📁 No baseline snapshot found")

    # Option to save current snapshot
    st.markdown("#### Actions")
    action_col1, action_col2 = st.columns([3, 1])
    with action_col1:
        st.caption("Save the current analysis as a baseline for future comparisons")
    with action_col2:
        if st.button("💾 Save as Baseline", type="secondary"):
            if 'analysis_results' in st.session_state:
                st.session_state.diff_viewer_agent.save_current_snapshot(st.session_state.analysis_results)
                st.success("Current analysis saved as baseline!")
            else:
                st.error("No analysis results available to save")

    # Information about the diff viewer
    st.markdown('<h2 class="sub-header">How the Change Diff Viewer Works</h2>', unsafe_allow_html=True)
    st.markdown("""
    The Change Diff Viewer helps you understand how your learning analytics insights evolve over time:

    **How it works:**
    1. After each analysis run, the current insights are saved as a snapshot in the database
    2. When you run analysis again, the system compares the new insights with the previous snapshot
    3. Differences are highlighted in three categories:
       - **Added**: New insights that appeared in the current analysis
       - **Removed**: Insights that were present before but are no longer detected
       - **Modified**: Insights that changed in priority or significance

    **What you can learn:**
    - Are new issues emerging as more data is collected?
    - Are previous concerns being resolved with additional data?
    - How stable are your insights as the dataset grows?
    - Are you seeing consistent patterns or fluctuating conclusions?

    **Best practices:**
    - Run analysis with your initial dataset to establish a baseline
    - Add new data and run analysis again to see how insights change
    - Use the "Save as Baseline" button to establish a new reference point
    - Look for trends in the types of insights that are added or removed over time
    """)