"""Process and transform data extracted from the API."""

from dotenv import load_dotenv
from os import environ as ENV

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


def find_first_index(stream_field, threshold):
    for i, item in enumerate(stream_field):
        if item >= threshold:
            return i
    return -1


def enrich_with_speeds(streams_data:list[tuple]) -> list[tuple]:
    """Calculate speed data for each 1k and 5k."""

    for stream in streams_data:
        time_data = stream[1]['time']
        distance_data = stream[1]['distance']
        max_dist = int(max(distance_data)/1000)

        if max_dist >= 1:
            k1_speed = []
            for i in range(1,max_dist+1):
                ind = find_first_index(distance_data, i*1000)
                k1_speed.append(distance_data[ind]/time_data[ind])
            stream[1]['1k_speed'] = k1_speed

        if max_dist >= 5:
            k5_speed = []
            for i in range(5,max_dist+1,5):
                ind = find_first_index(distance_data, i*1000)
                k5_speed.append(distance_data[ind]/time_data[ind])
            stream[1]['5k_speed'] = k5_speed

    return streams_data

def clean_data(data: tuple) -> tuple:
    """Main function to clean and transform data."""
    activities_detailed, streams = data[0], data[1]
    filtered_activities_data = filter_activities_data(activities_detailed)
    filtered_streams_data = filer_all_streams(streams)
    enriched_streams = enrich_with_speeds(filtered_streams_data)
    return filtered_activities_data, enriched_streams


if __name__ == '__main__':
    load_dotenv()

    connection = get_connection(ENV)
    data, streams = extract_data(connection, ENV, update_check=False)
    connection.close()

    clean_activity_data, clean_streams = clean_data((data,streams))

    print(clean_streams[0])