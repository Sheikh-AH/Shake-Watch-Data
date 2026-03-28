"""Streamlit page to display all activities."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


def get_engine(_config: _Environ):
    """Get sqlalchemy engine."""
    connection_string = (
        f"postgresql://{_config['DB_USER']}:{_config['DB_PASSWORD']}"
        f"@{_config['DB_HOST']}:{_config['DB_PORT']}/watch_data"
    )
    return create_engine(connection_string)


def get_dataframes(conn):
    """Get dataframes for activities, activity types, and stream sets."""
    activities_df = pd.read_sql("SELECT * FROM activities", conn)
    activity_types_df = pd.read_sql("SELECT * FROM activity_types", conn)
    stream_sets_df = pd.read_sql("SELECT * FROM stream_sets", conn)
    return activities_df, activity_types_df, stream_sets_df


def get_activities_data(conn) -> pd.DataFrame:
    """Join data for activity log."""
    query = """
    SELECT 
        a.start_datetime,
        a.calories,
        a.moving_time,
        a.activity_id,
        a.activity_name,
        a.effort,
        a.pace
    FROM activities a
    """
    activities_data = pd.read_sql(query, conn)
    df = activities_data.sort_values(by='start_datetime', ascending=False)
    return df


def gen_activity_log_page(df:pd.DataFrame):
    st.title("Activity Log")
    
    event = st.dataframe(
        df,
        column_config={
            'start_datetime': st.column_config.DateColumn(
                label="Started At",
                help="The date and time when the activity started.",
                format="YYYY-MM-DD HH:mm:ss",
                width="medium"
            ),
            'activity_name': st.column_config.TextColumn(
                label="Activity Label",
                help="The label given to the activity.",
                width="medium"
            ),
            'effort': st.column_config.NumberColumn(
                label="Effort",
                help="Effort of run",
                format="%d",
                width="small"
            ),
            'calories': st.column_config.NumberColumn(
                label="Calories Burned",
                help="Total calories burned during the activity.",
                format="%d kcal",
                width="small"
            ),
            'moving_time': st.column_config.NumberColumn(
                label="Duration",
                help="Total running time of the activity in seconds.",
                format="%d sec",
                width="small"
            ),
            'pace': st.column_config.NumberColumn(
                label="Pace",
                help="Average pace for run in m/s",
                format="%.2f m/s",
                width="small"
            ),
            'activity_id': None,
        },
        column_order=('start_datetime','activity_name','effort','calories','moving_time','pace'),
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
    )

    if event.selection.rows: # type: ignore
        selected_row = df.iloc[event.selection.rows[0]] # type: ignore
        st.session_state['activity_id'] = selected_row['activity_id']
        st.switch_page("pages/run.py")


def get_last5_data(df):
    last5_data = df.sort_values(by='start_datetime', ascending = False).head(5)['activity_id']
    st.text(last5_data)


def gen_summary(df):
    l5tab, monthtab = st.tabs(['Last 5','Last Month'])

    with l5tab:
        st.header('Last 5 runs.')
        get_last5_data(df)
    
    with monthtab:
        st.header('Monthly')


def gen_athlete_records():
    st.title('Athlete Records')


if __name__ == "__main__":
    
    load_dotenv()
    conn = get_engine(ENV)
    df = get_activities_data(conn)

    col1, col3, col2 = st.columns([0.70,0.05,0.25])

    with col1:
        gen_activity_log_page(df)

    with col2:
        gen_summary(df)

    st.space('medium')

    gen_athlete_records()


    
