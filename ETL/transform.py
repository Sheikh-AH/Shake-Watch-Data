"""Process and transform data extracted from the API."""

from dotenv import load_dotenv
from os import environ as ENV
import json

from .extract import extract_data, get_connection

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


def find_first_index(stream_field, threshold):
    for i, item in enumerate(stream_field):
        if item >= threshold:
            return i
    return -1


def enrich_with_speeds(streams_data:list, activities_data: list) -> list[tuple]:
    """Calculate speed data for each 1k and 5k."""

    for i, stream in enumerate(streams_data):
        time_data = stream[1]['time']
        distance_data = stream[1]['distance']
        max_dist = int(max(distance_data)/1000)

        if max_dist >= 1:
            k1_pace = []
            prev_time,prev_dist = 0,0
            for j in range(1,max_dist+1):
                ind = find_first_index(distance_data, j*1000)
                curr_time = time_data[ind]
                curr_dist = distance_data[ind]
                mins = (curr_time-prev_time)/60
                dist = (curr_dist-prev_dist)/1000
                k1_pace.append(mins/dist)
                prev_time,prev_dist = curr_time, curr_dist
            activities_data[i]['1k_pace'] = k1_pace

        if max_dist >= 5:
            k5_pace = []
            prev_time,prev_dist = 0,0
            for k in range(5,max_dist+1,5):
                ind = find_first_index(distance_data, k*1000)
                curr_time = time_data[ind]
                curr_dist = distance_data[ind]
                mins = (curr_time-prev_time)/60
                dist = (curr_dist-prev_dist)/1000
                k5_pace.append(mins/dist)
                prev_time,prev_dist = curr_time, curr_dist
            activities_data[i]['5k_pace'] = k5_pace

    return activities_data

def clean_data(data: tuple) -> tuple:
    """Main function to clean and transform data."""
    activities_detailed, streams = data[0], data[1]
    print('Filtering.')
    filtered_activities_data = filter_activities_data(activities_detailed)
    filtered_streams_data = filer_all_streams(streams)
    print('Enriching.')
    enriched_activities = enrich_with_speeds(filtered_streams_data, filtered_activities_data)
    return enriched_activities, filtered_streams_data


if __name__ == '__main__':
    load_dotenv()

    # connection = get_connection(ENV)
    # data, streams = extract_data(connection, ENV, update_check=False)
    # connection.close()

    # with open('example_stream.json', 'r') as f:
    #     data = json.load(f)

    # activities_data = {'0':{}}

    # distance_data = data[1]['distance']
    # time_data = data[1]['time']
    # max_dist = int(max(distance_data)/1000)