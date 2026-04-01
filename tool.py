"""Contains helper functions for app and pipeline."""

from os import environ as ENV, _Environ, path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from json import dump, load

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
    """Calculate effort for a run"""
    avg_hr = np.mean(df['heartrate'])
    dist = df['distance'][-1]
    time = df['time'][-1]
    var_hr = np.var(df['heartrate'])
    # effort = weighted formula of above variables and personal limits

def get_stream_field_data(conn, field:str, max_only:bool = False, update:bool = True):
    """Gets data for a single field from stream_sets table in db. Removes lowest 5%"""

    if not update:
        query = f"SELECT {field} FROM stream_sets"
    else:
        with open('athlete_data.json','r') as f:
            data = load(f)
            last_updated = data['last_updated']
        query = f"SELECT {field} FROM stream_sets JOIN activities USING (activity_id) WHERE start_datetime > '{last_updated}'"
    
    df = pd.read_sql(query, conn).dropna()
    if df.empty:
        raise Exception('No new data found.')

    if not max_only:
        vals = np.array([int(val) for row in df[field] for val in row])
        vals = vals[vals > np.quantile(vals,0.05)]
    else:
        vals = np.array([max(row) for row in df[field]])
        vals = vals.max()

    return vals

def get_records_values(conn, update_check = True) -> dict:
    """Get values for the athlete record stats"""
    records = {}
    heartrate = get_stream_field_data(conn, 'heartrate', update = update_check)
    velocity = get_stream_field_data(conn, 'velocity_smooth', update = update_check)
    cadence = get_stream_field_data(conn, 'cadence', update = update_check)
    power = get_stream_field_data(conn, 'watts', update = update_check)
    records['max_hr'] = int(heartrate.max())
    records['avg_hr'] = int(heartrate.mean())
    records['max_vel'] = round(float(velocity.max()), 2)
    records['avg_vel'] = round(float(velocity.mean()), 2)
    records['avg_cadence'] = int(cadence.mean())
    records['avg_power'] = int(power.mean())
    records['max_time'] = int(get_stream_field_data(conn, 'time', max_only=True))
    records['max_dist'] = int(get_stream_field_data(conn, 'distance', max_only=True))
    records['max_altitude'] = int(get_stream_field_data(conn, 'altitude', max_only=True))
    records['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return records

def write_records_to_file(vals:dict):
    """Update the athlete record stats json file with new values"""
    with open('athlete_data.json', 'w') as f:
        dump(vals, f)

def compare_data(current:dict, new:dict) -> dict:
    """Compare new and old record data."""
    updated = current.copy()
    max_keys = ('max_hr', 'max_vel', 'max_time', 'max_dist', 'max_altitude')
    avg_keys = ('avg_hr','avg_vel','avg_cadence','avg_power')

    for key in max_keys:
        if key in new and new[key] is not None:
            if new[key] > current[key]:
                updated[key] = new[key]
    
    for key in avg_keys:
        if key in new and new[key] is not None:
            updated[key] = (current[key] + new[key])/2

    updated['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return updated
        
def update_records(conn):
    """Update/Create athlete data file."""
    if path.isfile('./athlete_data.json'):
        with open('athlete_data.json','r') as f:
            current_data = load(f)
        new_data = get_records_values(conn, update_check=True)
        data = compare_data(current_data, new_data)
    else:
        data = get_records_values(conn, update_check=False)
    write_records_to_file(data)

if __name__ == '__main__':
    load_dotenv()
    conn = get_engine(ENV)

    # update_records(conn)
