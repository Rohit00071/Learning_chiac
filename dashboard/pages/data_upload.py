import streamlit as st
import pandas as pd
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.data_agent import DataAgent
from utils.synthetic_data_generator import generate_synthetic_data
from utils.logger import get_logger

logger = get_logger(__name__)

def show_data_upload_page():
    """Display the data upload and management page."""
    st.markdown('<h1 class="main-header">📊 Data Management</h1>', unsafe_allow_html=True)

    # Initialize data agent if not exists
    if 'data_agent' not in st.session_state:
        from database.database import LearningDatabase
        from utils.config import DATABASE_PATH
        st.session_state.data_agent = DataAgent(DATABASE_PATH)

    # Auto-sync data_loaded state from data_agent to sidebar/app state
    if hasattr(st.session_state.data_agent, 'data') and st.session_state.data_agent.data is not None and not st.session_state.data_agent.data.empty:
        st.session_state.data_loaded = True
        st.session_state.current_data = st.session_state.data_agent.data

    st.markdown("### Current Data Status")
    if hasattr(st.session_state.data_agent, 'data') and st.session_state.data_agent.data is not None:
        data = st.session_state.data_agent.data
        st.success(f"Currently loaded: {len(data)} student records")
    else:
        st.info("No data currently loaded.")

    # Data upload section
    st.markdown("### Load New Data")
    data_source = st.radio(
        "Select Data Source:",
        ["Upload CSV", "Use Synthetic Data", "Load from Database"],
        horizontal=True,
        key="data_source_selector"
    )

    if data_source == "Upload CSV":
        st.markdown("#### Upload CSV File")
        uploaded_file = st.file_uploader("Choose a CSV file containing learner data", type="csv")
        if uploaded_file is not None:
            if st.button("Load Uploaded Data", type="primary"):
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

                        # Clean up temp file
                        temp_path.unlink(missing_ok=True)

                        st.success("Data loaded successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error loading data: {e}")
                        logger.error(f"Error loading uploaded CSV: {e}")

    elif data_source == "Use Synthetic Data":
        st.markdown("#### Generate Synthetic Data")
        col1, col2 = st.columns([3, 1])
        with col1:
            num_students = st.slider("Number of Synthetic Students:", 10, 1000, 100, help="Generate realistic learner data for testing")
        with col2:
            st.write("")  # Spacer
            if st.button("Generate Data", type="primary"):
                with st.spinner("Generating synthetic data..."):
                    try:
                        synthetic_data = generate_synthetic_data(num_students)
                        st.session_state.data_agent.data = synthetic_data
                        st.session_state.current_data = synthetic_data
                        st.session_state.data_loaded = True
                        st.success(f"Generated {num_students} synthetic student records!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error generating synthetic data: {e}")
                        logger.error(f"Error generating synthetic data: {e}")

    elif data_source == "Load from Database":
        st.markdown("#### Load from Database")
        if st.button("Load Data from Database", type="primary"):
            with st.spinner("Loading data from database..."):
                try:
                    st.session_state.data_agent.load_from_database()
                    st.session_state.current_data = st.session_state.data_agent.get_data()
                    if st.session_state.current_data is not None and not st.session_state.current_data.empty:
                        st.session_state.data_loaded = True
                        st.success("Data loaded from database!")
                        st.rerun()
                    else:
                        st.warning("No data found in database. Consider generating synthetic data first.")
                except Exception as e:
                    st.error(f"Error loading data from database: {e}")
                    logger.error(f"Error loading data from database: {e}")

    # Data preview and info
    if hasattr(st.session_state.data_agent, 'data') and st.session_state.data_agent.data is not None:
        data = st.session_state.data_agent.data
        st.markdown("### Data Preview")
        st.dataframe(data.head(10), use_container_width=True)

        # Data information
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown("#### Data Information")
            st.write(f"**Shape:** {data.shape}")
            st.write(f"**Columns:** {', '.join(data.columns.tolist())}")

        with info_col2:
            st.markdown("#### Data Types")
            st.write(data.dtypes)

        # Missing values analysis
        st.markdown("#### Missing Values Analysis")
        missing_data = data.isnull().sum()
        missing_count = missing_data.sum()
        if missing_count > 0:
            st.warning(f"Found {missing_count} missing values in the dataset")
            missing_df = pd.DataFrame({
                'Column': missing_data.index,
                'Missing Count': missing_data.values,
                'Missing Percentage': (missing_data.values / len(data) * 100).round(2)
            })
            st.dataframe(missing_df[missing_df['Missing Count'] > 0], use_container_width=True)
        else:
            st.success("✅ No missing values detected!")

        # Basic statistics
        st.markdown("#### Basic Statistics")
        st.write(data.describe())