"""Process and transform data extracted from the API."""

from dotenv import load_dotenv
from os import environ as ENV, path
from json import load
import numpy as np

import pandas as pd
from extract import extract_data, get_connection


def filter_activities_data(activities_data:list[dict]) -> list[dict]:
    filter_list = ('id', 'name', 'calories','distance','moving_time','elapsed_time', 'total_elevation_gain', 'start_date_local', 'start_latlng', 'average_speed')
    filtered_data = []
    for run in activities_data:
        data = {}
        for field in filter_list:
            data[field] = run[field]
        filtered_data.append(data)
    return filtered_data


def filter_streams(streams: dict) -> dict:
    """Process streams data."""
    list_of_streams = [
        "time",
        "distance",
        "latlng",
        "altitude",
        "velocity_smooth",
        "heartrate",
        "cadence",
        "watts",
        "temp",
        "moving",
        "grade_smooth"
    ]

    filtered_streams = {}
    for key in streams.keys():
        if key in list_of_streams:
            filtered_streams[key] = streams[key]['data']

    return filtered_streams


def filer_all_streams(streams: list[dict]) -> list[tuple]:
    """Filter all streams data."""
    return [(stream[0], filter_streams(stream[1])) for stream in streams]


def find_first_index(stream_field, threshold):
    for i, item in enumerate(stream_field):
        if item >= threshold:
            return i
    return -1


def calculate_paces(max_dist:float, interval:int, time_stream:list, dist_stream:list):
    """Get the paces for a run for different distance intervals."""

    pace = []
    prev_time,prev_dist = 0,0
    for i in range(interval,max_dist+1, interval):
        ind = find_first_index(dist_stream, i*1000)
        curr_time = time_stream[ind]
        curr_dist = dist_stream[ind]
        mins = (curr_time-prev_time)/60
        dist = (curr_dist-prev_dist)/1000
        print(mins, dist, mins, curr_dist, curr_time, prev_dist, prev_time, ind)
        pace.append(mins/dist)
        prev_time,prev_dist = curr_time, curr_dist
    
    return pace


def get_paces(time_stream:list, dist_stream:list) -> list[tuple]:
    """Calculate speed data for each 1k and 5k."""

    max_dist = int(max(dist_stream)/1000)

    if max_dist >= 1:
        k1_pace = calculate_paces(max_dist, 1, time_stream, dist_stream)
    else:
        k1_pace = None

    if max_dist >= 5:
        k5_pace = calculate_paces(max_dist, 5, time_stream, dist_stream)
    else:
        k5_pace = None

    return k1_pace, k5_pace


def calculate_effort(limits:dict, run_time:int, run_dist: float, run_hr: list):
    """Calculate effort for a run"""

    max_hr = limits['max_hr']
    max_time = limits['max_time']
    max_dist = limits['max_dist']

    avg_hr = np.mean(run_hr)

    t_weight = run_time/max_time
    dist_weight = run_dist/max_dist
    hr_weight = avg_hr/(max_hr*0.75)


    effort = 100*(2*t_weight+3*dist_weight+8*hr_weight)/13
    if effort == 0 or effort > 100:
        print(t_weight, dist_weight, hr_weight)
    return effort


def enrich_data(config, activities_data: list, streams_data:list):
    """Enrich data with effort values"""

    ath_data_path = config['ATH_DATA_PATH']
    if path.exists(ath_data_path):
        with open(ath_data_path,'r') as f:
            limits = load(f)
        print('Athlete Data Found')
    else:
        limits = {}
        limits['max_hr'] = 180
        limits['max_time'] = 30*60
        limits['max_dist'] = 5000

    for ind,val in enumerate(streams_data):
        run_time = activities_data[ind]['moving_time']
        run_dist = activities_data[ind]['distance']
        k1_paces, k5_paces = get_paces(val[1]['time'], val[1]['distance'])
        if val[1]['heartrate']:
            effort = int(calculate_effort(limits, run_time, run_dist, val[1])['heartrate'])
        else:
            effort = None
        activities_data[ind]['1k_pace'] = k1_paces
        activities_data[ind]['5k_pace'] = k5_paces
        activities_data[ind]['effort'] = effort
        print('Data enriched')
    
    return activities_data


def transform_data(config, data: tuple) -> tuple:
    """Main function to clean and transform data."""
    activities_detailed, streams = data[0], data[1]
    print('Filtering.')
    filtered_acts_data = filter_activities_data(activities_detailed)
    filtered_streams_data = filer_all_streams(streams)
    print('Enriching.')
    enriched_activities = enrich_data(config, filtered_acts_data, filtered_streams_data)
    return enriched_activities, filtered_streams_data
