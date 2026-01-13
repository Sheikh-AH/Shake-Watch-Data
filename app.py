import streamlit as st

st.set_page_config(page_title="Watch Data Dashboard", layout="wide")

st.title("Watch Data Dashboard")
st.write("Select a page from the sidebar to view activity data.")

pages = [
    st.Page("pages/activitylog.py", title="Activity Log", icon="📋"),
    st.Page("pages/health.py", title="Health Log", icon="❤️"),
    st.Page("pages/run.py", title="Run Details", icon="🏃‍♂️")
]

pg = st.navigation(pages)
pg.run()
