import streamlit as st


def show_recommendations_page():
    """Display the recommendations page."""
    st.markdown('<h1 class="main-header">Recommendations</h1>', unsafe_allow_html=True)

    if ('recommendations' not in st.session_state or not st.session_state.recommendations) and st.session_state.get('analysis_results'):
        if st.button("Generate Recommendations", type="primary"):
            data_with_analysis = st.session_state.analysis_agent.get_data_with_analysis()
            st.session_state.recommendations = st.session_state.recommendation_agent.generate_recommendations(
                data_with_analysis,
                st.session_state.analysis_results,
                st.session_state.get('insights', []),
            )
            st.session_state.recommendations_generated = True
            st.rerun()

    if 'recommendations' not in st.session_state or not st.session_state.recommendations:
        st.info("Run full analysis, then generate recommendations to view this page.")
        return

    recommendations = st.session_state.recommendations
    st.markdown('<h2 class="sub-header">Recommendations Overview</h2>', unsafe_allow_html=True)

    priority_counts = {}
    for rec in recommendations:
        priority = rec.get('priority', 'Unknown')
        priority_counts[priority] = priority_counts.get(priority, 0) + 1

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Recommendations", len(recommendations))
    with c2:
        st.metric("High Priority", priority_counts.get('High', 0))
    with c3:
        st.metric("Medium Priority", priority_counts.get('Medium', 0))
    with c4:
        st.metric("Low Priority", priority_counts.get('Low', 0))

    student_filter = st.text_input("Filter by Student ID", placeholder="e.g., STU1005")
    filtered = recommendations
    if student_filter:
        filtered = [r for r in filtered if student_filter.lower() in r.get('student_id', '').lower()]

    for rec in filtered:
        st.markdown(
            f"""
            <div style="padding: 0.75rem; margin: 0.4rem 0; background-color: var(--secondary-background-color); border-radius: 0.5rem; border-left: 4px solid #28a745;">
                <strong>{rec.get('category', 'General')}</strong> ({rec.get('priority', 'Unknown')})<br>
                {rec.get('text', '')}<br>
                <small>Student: {rec.get('student_name', 'N/A')} ({rec.get('student_id', 'N/A')}) | Course: {rec.get('course', 'N/A')}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )
