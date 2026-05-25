import streamlit as st
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

st.set_page_config(
    page_title="AI Learning Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dashboard.main import run

run()
