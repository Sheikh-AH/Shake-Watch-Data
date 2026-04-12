"""Contains helper functions for app and pipeline."""

from os import environ as ENV, _Environ, path
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from json import dump, load
from streamlit import success as st_success
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
        a.avg_pace
    FROM activities a
    """
    activities_data = pd.read_sql(query, conn)
    df = activities_data.sort_values(by='start_datetime', ascending=False)
    return df

def get_stream_field_data(conn, field:str, max_only:bool = False, update:bool = True):
    """Gets data for a single field from stream_sets table in db. Removes lowest 5%"""

    if not update:
        query = f"SELECT {field} FROM stream_sets"
    else:
        with open('athlete_data.json','r') as f:
            data = load(f)
            last_updated = data['last_updated']
        query = f"SELECT ss.{field} FROM stream_sets AS ss JOIN activities USING (activity_id) WHERE start_datetime > '{last_updated}'"
    
    df = pd.read_sql(query, conn).dropna()
    if df.empty:
        return None

    if not max_only:
        vals = np.array([int(val) for row in df[field] for val in row])
        vals = vals[vals > np.quantile(vals,0.05)]
    else:
        vals = np.array([max(row) for row in df[field]])
        vals = vals.max()

    return vals

def get_total_records(conn, update = True) -> tuple:
    """Get the total distance, time and count of runs."""
    query = "SELECT moving_time, distance, calories, pace_1k, pace_5k FROM activities"
    if update:
        with open('athlete_data.json','r') as f:
            data = load(f)
            last_updated = data['last_updated']
        query += f"WHERE start_datetime > '{last_updated}'"

    df = pd.read_sql(query, conn)
    if df.empty:
        raise Exception('No new data found.')
    
    total_time = np.array(df['moving_time']).sum()
    total_dist = np.array(df['distance']).sum()
    total_calories = np.array(df['calories']).sum()

    k1 = np.array([min(row) for row in df['pace_1k'] if row != [9999]])
    k5 = np.array([min(row) for row in df['pace_5k'] if row != [9999]])
    if len(k1) != 0:
        min_1k = k1.min()
    else:
        min_1k = 9999
    if len(k5) != 0:
        min_5k = k5.min()
    else:
        min_5k = 9999

    run_count = df.shape[0]

    return run_count, total_time, total_dist, total_calories, min_1k, min_5k

def get_records_values(conn, update_check = True) -> dict:
    """Get values for the athlete record stats"""
    records = {}
    heartrate = get_stream_field_data(conn, 'heartrate', update = update_check)
    if not heartrate:
        return None
    velocity = get_stream_field_data(conn, 'velocity_smooth', update = update_check)
    cadence = get_stream_field_data(conn, 'cadence', update = update_check)
    power = get_stream_field_data(conn, 'watts', update = update_check)
    run_count, total_time, total_distance, total_calories, min_1k, min_5k = get_total_records(conn, update = update_check)
    records['max_hr'] = int(heartrate.max())
    records['avg_hr'] = int(heartrate.mean())
    records['max_vel'] = round(float(velocity.max()), 2)
    records['avg_vel'] = round(float(velocity.mean()), 2)
    records['avg_cadence'] = int(cadence.mean()*2)
    records['avg_power'] = int(power.mean())
    records['max_time'] = int(get_stream_field_data(conn, 'time', max_only=True, update=update_check))
    records['max_dist'] = int(get_stream_field_data(conn, 'distance', max_only=True, update=update_check))
    records['max_altitude'] = int(get_stream_field_data(conn, 'altitude', max_only=True, update=update_check))
    records['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    records['run_count'] = int(run_count)
    records['total_time'] = int(total_time)
    records['total_distance'] = int(total_distance)
    records['total_calories'] = int(total_calories)
    records['min_1k'] = round(float(min_1k),2)
    records['min_5k'] = round(float(min_5k),2)
    return records

def compare_data(current:dict, new:dict) -> dict:
    """Compare new and old record data."""
    updated = current.copy()
    max_keys = ('max_hr', 'max_vel', 'max_time', 'max_dist', 'max_altitude')
    min_keys = ('min_1k', 'min_5k')
    avg_keys = ('avg_hr','avg_vel','avg_cadence','avg_power')
    total_keys = ('run_count', 'total_time', 'total_distance', 'total_calories')

    for key in max_keys:
        if key in new and new[key] is not None:
            if new[key] > current[key]:
                updated[key] = new[key]
    
    for key in min_keys:
        if key in new and new[key] is not None:
            if new[key] < current[key]:
                updated[key] = new[key]
    
    for key in avg_keys:
        if key in new and new[key] is not None:
            updated[key] = (current[key] + new[key])/2

    for key in total_keys:
        if key in new and new[key] is not None:
            updated[key] += key

    updated['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return updated

def write_records_to_file(vals:dict):
    """Update the athlete record stats json file with new values"""
    with open('athlete_data.json', 'w') as f:
        dump(vals, f)
    print('Records have been updated.')
    st_success('Records have been updated.')

def update_records(conn):
    """Update/Create athlete data file."""
    if path.exists('athlete_data.json'):
        with open('athlete_data.json','r') as f:
            current_data = load(f)
        new_data = get_records_values(conn, update_check=True)
        if not new_data:
            print('No new data')
            data = False
        else:
            data = compare_data(current_data, new_data)
    else:
        data = get_records_values(conn, update_check=False)
    if data:
        write_records_to_file(data)

def calculate_effort(df: pd.DataFrame):
    """Calculate effort for a run"""
    avg_hr = np.mean(df['heartrate'])
    dist = df['distance'][-1]
    time = df['time'][-1]
    var_hr = np.var(df['heartrate'])
    # effort = weighted formula of above variables and personal limits

if __name__ == '__main__':
    load_dotenv()
    conn = get_engine(ENV)

    # update_records(conn)
    data = get_records_values(conn, update_check=False)
    write_records_to_file(data)
