import streamlit as st
from pathlib import Path
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import page functions
from dashboard.pages.home import show_home_page
from dashboard.pages.data_upload import show_data_upload_page
from dashboard.pages.analytics import show_analytics_page
from dashboard.pages.insights import show_insights_page
from dashboard.pages.recommendations import show_recommendations_page
from dashboard.pages.validation_report import show_validation_report_page
from dashboard.pages.change_diff_viewer import show_change_diff_viewer_page

# Import utilities for session state initialization
from utils.logger import get_logger
from agents.data_agent import DataAgent
from agents.analysis_agent import AnalysisAgent
from agents.insight_agent import InsightAgent
from agents.recommendation_agent import RecommendationAgent
from agents.validation_agent import ValidationChecklistAgent
from agents.diff_viewer_agent import ChangeDiffViewerAgent
from database.database import LearningDatabase
from utils.config import DATABASE_PATH
from utils.synthetic_data_generator import generate_synthetic_data

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Learning Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
def load_css():
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--text-color);
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color);
        margin: 0.5rem 0;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: var(--primary-color);
    }
    .metric-label {
        font-size: 1rem;
        color: var(--text-color);
        opacity: 0.7;
    }
    .insight-card {
        background-color: var(--background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    .insight-high { border-left-color: #dc3545; }
    .insight-medium { border-left-color: #ffc107; }
    .insight-low { border-left-color: #28a745; }
    .recommendation-card {
        background-color: var(--secondary-background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    .stTab { font-size: 1.1rem; }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state agents and data
def initialize_session_state():
    """Initialize all agents and session state variables."""
    # Initialize agents only once
    if 'data_agent' not in st.session_state:
        st.session_state.data_agent = DataAgent(DATABASE_PATH)
    if 'analysis_agent' not in st.session_state:
        st.session_state.analysis_agent = AnalysisAgent()
    if 'insight_agent' not in st.session_state:
        st.session_state.insight_agent = InsightAgent()
    if 'recommendation_agent' not in st.session_state:
        st.session_state.recommendation_agent = RecommendationAgent()
    if 'validation_agent' not in st.session_state:
        st.session_state.validation_agent = ValidationChecklistAgent()
    if 'diff_viewer_agent' not in st.session_state:
        st.session_state.diff_viewer_agent = ChangeDiffViewerAgent(DATABASE_PATH)

    # Initialize data and analysis flags
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'analysis_completed' not in st.session_state:
        st.session_state.analysis_completed = False
    if 'insights_generated' not in st.session_state:
        st.session_state.insights_generated = False
    if 'recommendations_generated' not in st.session_state:
        st.session_state.recommendations_generated = False
    if 'current_data' not in st.session_state:
        st.session_state.current_data = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = {}
    if 'insights' not in st.session_state:
        st.session_state.insights = []
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = []

    logger.info("Session state initialized")

# Load CSS
load_css()
initialize_session_state()

# Sidebar navigation
st.sidebar.title("🎓 AI Learning Analytics")
st.sidebar.image(str(project_root / "dashboard" / "banner.png"), width="stretch")

# Navigation menu
page = st.sidebar.selectbox(
    "Navigate to:",
    [
        "🏠 Home Dashboard",
        "📊 Data Upload",
        "📈 Analytics",
        "💡 Insights",
        "🎯 Recommendations",
        "✅ Validation Report",
        "🔄 Change Diff Viewer"
    ]
)

# Data management section in sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Management")

data_source = st.sidebar.radio(
    "Data Source:",
    ["Upload CSV", "Use Synthetic Data", "Load from Database"],
    key="sidebar_data_source"
)

if data_source == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload CSV", type="csv", label_visibility="collapsed")
    if uploaded_file is not None:
        if st.sidebar.button("Load Data", key="sidebar_load_csv"):
            with st.spinner("Loading data..."):
                try:
                    # Save uploaded file temporarily
                    temp_path = project_root / "data" / "temp_upload.csv"
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())

                    # Load data using data agent
                    st.session_state.data_agent.load_csv(str(temp_path))
                    st.session_state.current_data = st.session_state.data_agent.get_data()
                    st.session_state.data_loaded = True
                    st.sidebar.success("Data loaded!")
                    # Clean up temp file
                    temp_path.unlink(missing_ok=True)
                except Exception as e:
                    st.sidebar.error(f"Error: {e}")
                    logger.error(f"Error loading uploaded CSV: {e}")

elif data_source == "Use Synthetic Data":
    num_students = st.sidebar.slider("Students:", 20, 500, 100, key="sidebar_synth_slider")
    if st.sidebar.button("Generate Data", key="sidebar_gen_synth"):
        with st.spinner("Generating data..."):
            try:
                synthetic_data = generate_synthetic_data(num_students)
                st.session_state.data_agent.data = synthetic_data
                st.session_state.current_data = synthetic_data
                st.session_state.data_loaded = True
                st.sidebar.success(f"Generated {num_students} records!")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
                logger.error(f"Error generating synthetic data: {e}")

elif data_source == "Load from Database":
    if st.sidebar.button("Load from DB", key="sidebar_load_db"):
        with st.spinner("Loading from database..."):
            try:
                st.session_state.data_agent.load_from_database()
                st.session_state.current_data = st.session_state.data_agent.get_data()
                if st.session_state.current_data is not None and not st.session_state.current_data.empty:
                    st.session_state.data_loaded = True
                    st.sidebar.success("Data loaded from DB!")
                else:
                    st.sidebar.warning("No data in database")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
                logger.error(f"Error loading data from database: {e}")

# Analysis button in sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Run Full Analysis", type="primary", use_container_width=True, disabled=not st.session_state.get('data_loaded', False)):
    with st.spinner("Running analysis pipeline..."):
        try:
            # Step 1: Clean and normalize data
            cleaned_data = st.session_state.data_agent.clean_data()
            normalized_data = st.session_state.data_agent.normalize_data()

            # Step 2: Run analysis
            st.session_state.analysis_agent.load_data(normalized_data)
            st.session_state.analysis_results = {
                'performance': st.session_state.analysis_agent.analyze_performance(),
                'clustering': st.session_state.analysis_agent.perform_clustering(),
                'risk_prediction': st.session_state.analysis_agent.predict_performance_risk()
            }
            st.session_state.analysis_completed = True

            # Step 3: Generate insights
            st.session_state.insights = st.session_state.insight_agent.generate_insights(
                st.session_state.analysis_results
            )
            st.session_state.insights_generated = True

            # Step 4: Generate recommendations
            data_with_analysis = st.session_state.analysis_agent.get_data_with_analysis()
            st.session_state.recommendations = st.session_state.recommendation_agent.generate_recommendations(
                data_with_analysis,
                st.session_state.analysis_results,
                st.session_state.insights
            )
            st.session_state.recommendations_generated = True

            # Step 5: Save snapshot for diff viewer
            st.session_state.diff_viewer_agent.load_current_insights(st.session_state.insights)
            st.session_state.diff_viewer_agent.save_current_snapshot(st.session_state.analysis_results)

            st.sidebar.success("Analysis completed!")
            logger.info("Full analysis pipeline completed")

        except Exception as e:
            st.sidebar.error(f"Analysis error: {e}")
            logger.error(f"Error during analysis pipeline: {e}")

# Reset button in sidebar
if st.sidebar.button("🔄 Reset All Data", use_container_width=True):
    # Clear session state
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Page routing
if page == "🏠 Home Dashboard":
    show_home_page()
elif page == "📊 Data Upload":
    show_data_upload_page()
elif page == "📈 Analytics":
    show_analytics_page()
elif page == "💡 Insights":
    show_insights_page()
elif page == "🎯 Recommendations":
    show_recommendations_page()
elif page == "✅ Validation Report":
    show_validation_report_page()
elif page == "🔄 Change Diff Viewer":
    show_change_diff_viewer_page()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: var(--text-color); opacity: 0.7; font-size: 0.9rem;">
        AI Learning Analytics Dashboard | Built with Streamlit & Multi-Agent AI Architecture<br>
        © 2026 Educational Analytics Inc. | <a href="https://github.com/yourusername/ai-learning-analytics" target="_blank">GitHub</a>
    </div>
    """,
    unsafe_allow_html=True
)

# Cleanup function (called implicitly)
def cleanup():
    try:
        st.session_state.data_agent.close()
        st.session_state.diff_viewer_agent.close()
    except:
        pass