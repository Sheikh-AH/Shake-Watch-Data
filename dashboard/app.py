"""Entry point for the Streamlit Watch Data Dashboard application."""

import sys
from pathlib import Path
import streamlit as st

BASE_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.append(BASE_DIR)

st.set_page_config(page_title="Watch Data Dashboard", layout="wide")

pages = [
    st.Page("pages/activitylog.py", title="Activity Log", icon="📋"),
    st.Page("pages/run.py", title="Run Details", icon="🏃‍♂️")
]

pg = st.navigation(pages)
pg.run()
