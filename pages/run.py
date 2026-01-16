import streamlit as st
from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import create_engine
from os import environ as ENV, _Environ
from plotly import graph_objects as go, express as px
from datetime import datetime

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


def get_id() -> int:
    try:
        activity_id = st.session_state.get('activity_id')
        st.query_params["activity_id"] = st.session_state['activity_id']
    except KeyError:
        if st.query_params.get("activity_id") is None:
            st.error(
                "No activity selected. Please go back to the Activity Log and select an activity.")
            st.stop()
        st.session_state['activity_id'] = st.query_params.get("activity_id")
        activity_id = st.session_state['activity_id']
    return activity_id


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


def gen_disttime_plot(org_df: pd.DataFrame) -> None:

    df = org_df.copy()
    for col in ['stream_distance', 'heartrate', 'altitude', 'velocity_smooth', 'cadence', 'watts']:
        df[col] = normalize_values(df[col])

    metric_map = {
        "stream_distance": "Distance (m)",
        "heartrate": "Heart Rate (bpm)",
        "altitude": "Altitude (m)",
        "velocity_smooth": "Velocity (m/s)",
        "cadence": "Cadence (rpm)",
        "watts": "Power (W)"
    }

    fig = go.Figure()

    for col, metric_label in metric_map.items():
        fig.add_trace(go.Line(
            x=df['time'],
            y=df[col],
            name=metric_label,
        ))

    fig.update_layout(
        title='Normalised Activity Metrics vs Time',
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(title='Normalised Values'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, width='stretch')


def summary_metrics(df: pd.DataFrame) -> None:
    total_distance = df['distance'].iloc[0] / 1000
    total_time = df['elapsed_time'].iloc[0] / 60
    avg_speed = total_distance / (total_time / 60)
    total_calories = df['calories'].iloc[0]

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(f"Total Distance", f"{total_distance:.2f} km")
    with col2:
        st.metric(f"Total Time", f"{total_time:.2f} mins")
    with col3:
        st.metric(f"Average Speed", f"{avg_speed:.2f} km/h")
    with col4:
        st.metric(f"Total Calories Burned", f"{total_calories} kcal")


def heart_rate_zones(df: pd.DataFrame) -> dict:
    max_hr = 220 - datetime.now().year + 2001  # assuming birth year 1990
    zones = {
        "Zone 1": (0.5 * max_hr, 0.6 * max_hr),
        "Zone 2": (0.6 * max_hr, 0.7 * max_hr),
        "Zone 3": (0.7 * max_hr, 0.8 * max_hr),
        "Zone 4": (0.8 * max_hr, 0.9 * max_hr),
        "Zone 5": (0.9 * max_hr, max_hr),
    }
    time_in_zones = {}
    for zone, (lower, upper) in zones.items():
        time_in_zone = df[(df['heartrate'] >= lower) &
                          (df['heartrate'] < upper)].shape[0]
        time_in_zones[zone] = time_in_zone
    return time_in_zones


def gen_heart_rate_plot(df: pd.DataFrame) -> None:

    col1, col2, col3 = st.columns(
        [4, 1, 1], gap='medium', vertical_alignment='center')
    data = go.Scatter(
        x=df['time'],
        y=df['heartrate'],
        mode='lines',
        name='Heart Rate (bpm)',
        fill='tozeroy',
        line=dict(color='rgba(0,120,255,0.6)'),
        fillcolor='rgba(0,120,255,0.1)',
        marker={'colorscale': 'RdYlGn'}
    )

    layout = go.Layout(
        title='Heart Rate vs Time',
        xaxis=dict(title='Time (seconds)'),
        yaxis=dict(title='Heart Rate (bpm)'),
    )

    fig = go.Figure(data, layout)

    for key, val in {"yellow": 120, "orange": 140, "red": 160}.items():
        fig.add_hline(
            y=val,
            line_dash="dash",
            line_color=key,
            annotation_text=f"{val} bpm"
        )

    time_in_zones = heart_rate_zones(df)
    total_time = sum(time_in_zones.values())

    with col1:
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.metric("Max Heart Rate", f"{df['heartrate'].max():.0f} bpm")
        st.metric("Avg Heart Rate", f"{df['heartrate'].mean():.0f} bpm")
        st.metric("Var Heart Rate", f"{df['heartrate'].std():.0f} bpm")
    with col3:
        for zone in time_in_zones:
            zone_proportion = time_in_zones[zone] / total_time
            st.progress(zone_proportion,
                        text=f"{zone} - {round(zone_proportion*100)}%")


def gen_velocity_plot(df: pd.DataFrame) -> None:
    fig = px.line(
        df,
        x='time',
        y='velocity_smooth',
        title='Velocity vs Time',
        labels={'time': 'Time (seconds)', 'velocity_smooth': 'Velocity (m/s)'}
    )
    st.plotly_chart(fig, width='stretch')


if __name__ == '__main__':
    conn = get_engine(ENV)

    activity_id = get_id()

    df = join_data(conn, activity_id)
    df = explode_data(df)

    st.title(
        f"Activity: {df['activity_name'].iloc[0]}     ({df['start_datetime'].iloc[0].strftime('%Y-%m-%d')})")
    st.space('small')
    summary_metrics(df)
    gen_disttime_plot(df)
    gen_heart_rate_plot(df)
    gen_velocity_plot(df[['time', 'velocity_smooth']])
