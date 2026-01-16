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


def join_data(conn, activity_id: int) -> pd.DataFrame:
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
    WHERE a.activity_id = %s
    """
    activities_types_streams = pd.read_sql(
        query, conn, params=(int(activity_id),))

    return activities_types_streams


def explode_data(df: pd.DataFrame) -> pd.DataFrame:
    cols = ['time', 'stream_distance', 'heartrate',
            'altitude', 'velocity_smooth', 'cadence', 'watts']

    df = df.explode(cols)

    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df



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


def gen_disttime_plot(df: pd.DataFrame) -> None:
    df = explode_data(df)

    for col in ['stream_distance', 'heartrate', 'altitude', 'velocity_smooth', 'cadence', 'watts']:
        df[col] = normalize_values(df[col])

    metric_map = {
        "Distance": ("stream_distance", "Distance (m)"),
        "Heart Rate": ("heartrate", "Heart Rate (bpm)"),
        "Altitude": ("altitude", "Altitude (m)"),
        "Velocity": ("velocity_smooth", "Velocity (m/s)"),
        "Cadence": ("cadence", "Cadence (rpm)"),
        "Power": ("watts", "Power (W)")
    }

    fig = go.Figure()

    for metric, (col, metric_label) in metric_map.items():
        fig.add_trace(go.Scatter(
            x=df['time'],
            y=df[col],
            name=metric_label,
            visible=True
        ))

    fig.update_layout(
        title='Normalised Activity Metrics vs Time',
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(title='Normalised Values'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, width='stretch')


if __name__ == '__main__':
    conn = get_engine(ENV)
    activity_id = st.session_state.get('activity_id')
    activities_types_streams = join_data(conn, activity_id)

    st.title(f"Activity: {activities_types_streams['activity_name'].iloc[0]}")

    fig = gen_disttime_plot(activities_types_streams)
    
