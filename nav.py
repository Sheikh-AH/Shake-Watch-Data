"""Dashboard home page."""

import streamlit as st


def navigation():
    home = st.Page('home.py', title="Home Page", default=True)
    logpage = st.Page('activitylog.py', title='Activity Log')
    healthpage = st.Page('health.py', title='Health Overview')
    nav = st.navigation([home, logpage, healthpage])
    nav.run()


if __name__ == "__main__":
    navigation()
