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


def get_activities_data(conn):
    """Join all data into a single dataframe."""
    query = """
    SELECT 
        a.start_datetime,
        a.calories,
        a.elapsed_time,
        a.activity_id,
        a.activity_name,
        at.activity_type_name
    FROM activities a
    JOIN activity_types at USING (activity_type_id);
    """
    activities_types_streams = pd.read_sql(query, conn)
    activities_types_streams = activities_types_streams.loc[:,
                                                            ~activities_types_streams.columns.duplicated()]
    return activities_types_streams


def activity_log_page(config: _Environ):
    st.title("Activity Log")
    conn = get_engine(config)
    activities_types_streams = get_activities_data(conn)
    df = activities_types_streams[['start_datetime', 'activity_name',
                                  'activity_type_name', 'calories', 'elapsed_time', 'activity_id']]
    event = st.dataframe(
        df,
        column_config={
            'start_datetime': st.column_config.DateColumn(
                "Started At",
                help="The date and time when the activity started.",
                format="YYYY-MM-DD HH:mm:ss",
            ),
            'activity_name': st.column_config.TextColumn(
                "Activity Label",
                help="The label given to the activity.",
            ),
            'activity_type_name': st.column_config.TextColumn(
                "Type",
                help="The type of activity performed.",
            ),
            'calories': st.column_config.NumberColumn(
                "Calories Burned",
                help="Total calories burned during the activity.",
                format="%d kcal",
            ),
            'elapsed_time': st.column_config.NumberColumn(
                "Elapsed Time",
                help="Total elapsed time of the activity in seconds.",
                format="%d sec",
            ),
            'activity_id': None,
        },
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True
    )

    if event.selection.rows:
        selected_row = df.iloc[event.selection.rows[0]]

        if selected_row['activity_type_name'] == 'Run':
            st.session_state['activity_id'] = selected_row['activity_id']
            st.switch_page("pages/run.py")
        else:
            st.warning("Details only available for runs")


if __name__ == "__main__":

    load_dotenv()
    activity_log_page(ENV)
