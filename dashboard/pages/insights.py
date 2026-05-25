import streamlit as st


def show_insights_page():
    """Display the insights page."""
    st.markdown('<h1 class="main-header">Insights</h1>', unsafe_allow_html=True)

    if ('insights' not in st.session_state or not st.session_state.insights) and st.session_state.get('analysis_results'):
        if st.button("Generate Insights", type="primary"):
            st.session_state.insights = st.session_state.insight_agent.generate_insights(
                st.session_state.analysis_results
            )
            st.session_state.insights_generated = True
            st.rerun()

    if 'insights' not in st.session_state or not st.session_state.insights:
        st.info("Run full analysis, then generate insights to view this page.")
        return

    insights = st.session_state.insights
    st.markdown('<h2 class="sub-header">Insights Overview</h2>', unsafe_allow_html=True)

    priority_counts = {}
    for insight in insights:
        priority = insight.get('priority', 'Unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Insights", len(insights))
    with c2:
        st.metric("High Priority", priority_counts.get('High', 0))
    with c3:
        st.metric("Medium Priority", priority_counts.get('Medium', 0))
    with c4:
        st.metric("Low Priority", priority_counts.get('Low', 0))

    priority_filter = st.selectbox("Filter by Priority", ["All", "High", "Medium", "Low"], index=0)
    filtered_insights = insights if priority_filter == "All" else [i for i in insights if i.get('priority') == priority_filter]

    for insight in filtered_insights:
        priority = insight.get('priority', 'Unknown')
        card_style = f"insight-card insight-{priority.lower()}"
        st.markdown(
            f"""
            <div class="{card_style}">
                <strong>{insight.get('category', 'General')}</strong><br>
                {insight.get('text', 'No insight text available')}<br>
                <small>Priority: {priority}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
