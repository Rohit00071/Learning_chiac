import streamlit as st
import pandas as pd
from dashboard.components.kpi_card import render_metric_card

def show_validation_report_page():
    """Display the validation report page."""
    st.markdown('<h1 class="main-header">✅ Validation Report</h1>', unsafe_allow_html=True)

    st.markdown("### Pipeline Quality Validation")
    st.markdown("""
    This page validates the quality and completeness of each stage in the AI learning analytics pipeline.
    Run the validation to check that all components are functioning correctly.
    """)

    # Run validation button
    if st.button("🔍 Run Full Validation", type="primary"):
        with st.spinner("Running validation checks..."):
            try:
                # Import validation agent
                from agents.validation_agent import ValidationChecklistAgent
                import pandas as pd

                # Initialize validation agent if not exists
                if 'validation_agent' not in st.session_state:
                    st.session_state.validation_agent = ValidationChecklistAgent()

                # Prepare validation data from session state
                validation_data = {
                    'original_data': getattr(st.session_state.get('data_agent', None), 'data', None),
                    'processed_data': getattr(st.session_state.get('data_agent', None), 'processed_data', None),
                    'normalized_data': st.session_state.get('data_agent', None).normalize_data() if st.session_state.get('data_agent') and st.session_state.data_loaded else None,
                    'analysis_results': st.session_state.get('analysis_results', {}),
                    'insights': st.session_state.get('insights', []),
                    'recommendations': st.session_state.get('recommendations', []),
                    'visualizations_count': 3 if st.session_state.get('analysis_completed', False) else 0,
                    'risk_predictions': st.session_state.get('analysis_results', {}).get('risk_prediction', {})
                }

                # Run validation
                validation_results = st.session_state.validation_agent.run_full_validation(validation_data)
                st.session_state.last_validation = validation_results

                st.success("Validation completed!")

            except Exception as e:
                st.error(f"Error during validation: {e}")

    # Display validation results
    if hasattr(st.session_state, 'last_validation'):
        validation_results = st.session_state.last_validation

        # Overall status
        overall_passed = validation_results.get('overall_passed', False)
        passed_stages = validation_results.get('passed_stages', 0)
        total_stages = validation_results.get('total_stages', 0)
        success_rate = validation_results.get('success_rate', 0)

        # Status indicator
        if overall_passed:
            st.success(f"🎉 Pipeline Validation PASSED ({passed_stages}/{total_stages} stages)")
        else:
            st.error(f"❌ Pipeline Validation FAILED ({passed_stages}/{total_stages} stages)")

        # Metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Stages Passed", f"{passed_stages}/{total_stages}")
        with metric_col2:
            st.metric("Success Rate", f"{success_rate:.1f}%")
        with metric_col3:
            st.metric("Overall Status", "PASS" if overall_passed else "FAIL")

        # Detailed results
        st.markdown("### Detailed Validation Results")
        validation_text = st.session_state.validation_agent.format_validation_for_display()
        st.text(validation_text)

        # Expandable JSON view
        with st.expander("View Raw Validation Data (JSON)"):
            st.json(validation_results['validation_results'])

    else:
        st.info("Click 'Run Full Validation' to check the quality of the analysis pipeline.")

    # Information about validation stages
    st.markdown('<h2 class="sub-header">Validation Stages Explained</h2>', unsafe_allow_html=True)
    st.markdown("""
    The validation process checks the following stages of the AI learning analytics pipeline:

    1. **Data loaded successfully** - Verifies that learner data has been loaded from CSV, synthetic generation, or database
    2. **Missing values handled** - Checks that all missing values in the data have been properly addressed
    3. **Data normalized** - Confirms that numeric features have been normalized to 0-1 scale for analysis
    4. **Analysis completed** - Ensures that performance analysis, clustering, and risk prediction have been executed
    5. **Insights generated** - Validates that human-readable insights have been produced from the analysis
    6. **Recommendations generated** - Checks that personalized and actionable recommendations have been created
    7. **Visualizations rendered** - Confirms that charts and graphs have been generated for data visualization
    8. **Risk predictions completed** - Verifies that risk assessment models have been run and scored

    Each stage is marked as PASS or FAIL with detailed explanations for any failures.
    """)