import streamlit as st
import os
from pathlib import Path

root = Path(__file__).parent
os.chdir(str(root))

st.set_page_config(
    page_title="AI Learning Analytics Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

from dashboard.main import run

run()
