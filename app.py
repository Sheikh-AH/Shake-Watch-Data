"""Starting point for the Streamlit Watch Data Dashboard application."""

import streamlit as st

st.set_page_config(page_title="Watch Data Dashboard", layout="wide")

pages = [
    st.Page("pages/activitylog.py", title="Activity Log", icon="📋"),
    st.Page("pages/run.py", title="Run Details", icon="🏃‍♂️")
]

pg = st.navigation(pages)
pg.run()
