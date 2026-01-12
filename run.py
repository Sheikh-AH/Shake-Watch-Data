import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from os import environ as ENV, _Environ
from plotly import graph_objects as go

load_dotenv()


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


def normalize_values(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()
    normalized_series = (series - min_val) / (max_val - min_val)
    if 100 < series.max() <= 1000:
        normalized_series *= 0.75
    elif 100 > series.max() >= 25:
        normalized_series *= 0.5
    elif 25 > series.max():
        normalized_series *= 0.25
    return normalized_series


def gen_disttime_plot(df: pd.DataFrame, activity_id: int):
    df_filtered = df[df['activity_id'] == activity_id].copy()

    # Explode all array columns
    df_filtered = df_filtered.explode(
        ['time', 'stream_distance', 'heartrate', 'altitude', 'velocity_smooth', 'cadence', 'watts'])

    # Convert to numeric
    df_filtered['time'] = pd.to_numeric(df_filtered['time'], errors='coerce')
    df_filtered['stream_distance'] = pd.to_numeric(
        df_filtered['stream_distance'], errors='coerce')
    df_filtered['heartrate'] = pd.to_numeric(
        df_filtered['heartrate'], errors='coerce')
    df_filtered['altitude'] = pd.to_numeric(
        df_filtered['altitude'], errors='coerce')
    df_filtered['velocity_smooth'] = pd.to_numeric(
        df_filtered['velocity_smooth'], errors='coerce')
    df_filtered['cadence'] = pd.to_numeric(
        df_filtered['cadence'], errors='coerce')
    df_filtered['watts'] = pd.to_numeric(df_filtered['watts'], errors='coerce')

    # Normalize values for better comparison
    for col in ['stream_distance', 'heartrate', 'altitude', 'velocity_smooth', 'cadence', 'watts']:
        df_filtered[col] = normalize_values(df_filtered[col])

    # Map metric names to columns
    metric_map = {
        "Distance": ("stream_distance", "Distance (m)"),
        "Heart Rate": ("heartrate", "Heart Rate (bpm)"),
        "Altitude": ("altitude", "Altitude (m)"),
        "Velocity": ("velocity_smooth", "Velocity (m/s)"),
        "Cadence": ("cadence", "Cadence (rpm)"),
        "Power": ("watts", "Power (W)")
    }

    fig = go.Figure()

    # Add all metrics
    for metric, (col, metric_label) in metric_map.items():
        fig.add_trace(go.Scatter(
            x=df_filtered['time'],
            y=df_filtered[col],
            name=metric_label,
            visible=True
        ))

    fig.update_layout(
        title='Activity Metrics vs Time',
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(title='Normalized Values'),
        hovermode='x unified'
    )

    return fig


def gen_run_list(df: pd.DataFrame) -> None:
    run_activities = df[df['activity_type_name'] == 'Run']
    run_list = run_activities[[
        'activity_id', 'activity_name']].drop_duplicates().to_dict('records')
    st.write(run_activities)


if __name__ == '__main__':
    conn = get_engine(ENV)
    activities_df, activity_types_df, stream_sets_df = get_dataframes(conn)
    activities_types_streams = join_data(conn)
    gen_run_list(activities_types_streams)
    # activity_id = activities_df.iloc[activity_idx]['activity_id']
    # st.title(f"Activity: {activities_df.iloc[activity_idx]['activity_name']}")

    # filtered_data = activities_types_streams[activities_types_streams['activity_id'] == activity_id]
    # st.write(f"Data points: {filtered_data.shape[0]}")

    # fig = gen_disttime_plot(activities_types_streams, activity_id)
    # st.plotly_chart(fig, use_container_width=True)
