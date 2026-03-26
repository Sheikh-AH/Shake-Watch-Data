"""Process and transform data extracted from the API."""

from dotenv import load_dotenv
from os import environ as ENV

import pandas as pd
from extract import extract_data, get_connection

def filter_activities_data(activities_data:list[dict]) -> list[dict]:
    filter_list = ('id', 'name', 'calories','distance','moving_time','elapsed_time', 'total_elevation_gain', 'start_date_local', 'start_latlng', 'average_speed')
    filtered_data = []
    for run in activities_data:
        data = {}
        for field in filter_list:
            data[field] = run[field]
        data['effort'] = 0
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


def clean_data(data: tuple) -> tuple:
    """Main function to clean and transform data."""
    activities_detailed, streams = data[0], data[1]
    filtered_activities_data = filter_activities_data(activities_detailed)
    filtered_streams_data = filer_all_streams(streams)
    return filtered_activities_data, filtered_streams_data


if __name__ == '__main__':
    load_dotenv()
    connection = get_connection(ENV)
    data, streams = extract_data(connection, ENV)
    clean_activity_data, clean_streams = clean_data((data,streams))
    connection.close()
    print(clean_activity_data[0])