"""Contains helper functions for app and pipeline."""

from os import environ as ENV, _Environ

from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import numpy as np

from sqlalchemy import create_engine


def get_engine(_config: _Environ):
    """Get sqlalchemy engine."""
    connection_string = (
        f"postgresql://{_config['DB_USER']}:{_config['DB_PASSWORD']}"
        f"@{_config['DB_HOST']}:{_config['DB_PORT']}/watch_data"
    )
    return create_engine(connection_string)


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

def calculate_effort(df: pd.DataFrame):
    avg_hr = np.mean(df['heartrate'])
    dist = df['distance'][-1]
    time = df['time'][-1]
    var_hr = np.var(df['heartrate'])
    # effort = weighted formula of above variables and personal limits

def get_ss_field_data(conn, field):
    """Gets data for a single field from stream_sets table in db. Removes lowest 5%"""
    query = f"SELECT {field} FROM stream_sets"
    df = pd.read_sql(query, conn).dropna()
    vals = np.array([int(val) for row in df[field] for val in row])
    vals = vals[vals > np.quantile(vals,0.05)]
    return vals


if __name__ == '__main__':
    load_dotenv()

    conn = get_engine(ENV)
    
    print(min(get_ss_field_data(conn, 'heartrate')))