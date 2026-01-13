from os import environ as ENV, _Environ
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine


def get_engine(_config: _Environ):
    connection_string = (
        f"postgresql://{_config['DB_USER']}:{_config['DB_PASSWORD']}"
        f"@{_config['DB_HOST']}:{_config['DB_PORT']}/watch_data"
    )
    return create_engine(connection_string)


def get_dataframes(conn):
    activities_df = pd.read_sql("SELECT * FROM activities", conn)
    activity_types_df = pd.read_sql("SELECT * FROM activity_types", conn)
    stream_sets_df = pd.read_sql("SELECT * FROM stream_sets", conn)
    return activities_df, activity_types_df, stream_sets_df


def join_data(conn):
    query = """
    SELECT 
        a.activity_id,
        a.activity_name,
        a.calories,
        a.distance,
        a.moving_time,
        a.elapsed_time,
        a.total_elevation_gain,
        a.activity_type_id,
        a.start_datetime,
        a.start_loc,
        at.activity_type_name,
        ss.stream_sets_id,
        ss.time,
        ss.distance as stream_distance,
        ss.latlng,
        ss.altitude,
        ss.velocity_smooth,
        ss.heartrate,
        ss.cadence,
        ss.watts,
        ss.temp,
        ss.moving,
        ss.grade_smooth
    FROM activities a
    JOIN activity_types at ON a.activity_type_id = at.activity_type_id
    JOIN stream_sets ss ON a.activity_id = ss.activity_id
    """
    activities_types_streams = pd.read_sql(query, conn)
    return activities_types_streams


def activity_log_page(config: _Environ):
    st.title("Activity Log")
    conn = get_engine(config)
    activities_types_streams = join_data(conn)
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
        st.session_state['activity_id'] = selected_row['activity_id']
        st.switch_page("pages/run.py")


if __name__ == "__main__":

    load_dotenv()
    activity_log_page(ENV)
