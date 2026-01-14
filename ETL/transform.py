"""Process and transform data extracted from the API."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from datetime import datetime

from sqlite3 import Connection

from extract import get_connection, extract_data


def get_type_mapping(conn: Connection) -> dict:
    """Retrieve activity type mapping from the database."""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT activity_type_id, activity_type_name FROM activity_types")
    rows = cursor.fetchall()
    cursor.close()
    return {row[1]: row[0] for row in rows}


def convert_types_to_ids(mapping: dict, activities: list[dict]) -> list[dict]:
    """Convert activity type names to their corresponding IDs."""
    for activity in activities:
        activity['type_id'] = mapping.get(activity['sport_type'])
    return activities


def clean_activities(conn: Connection, activities_detailed: list[dict]) -> list[dict]:
    """Process activities data."""
    type_mapping = get_type_mapping(conn)
    activities = convert_types_to_ids(type_mapping, activities_detailed)
    return activities


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


def filer_all_streams(streams: list[dict]) -> list[dict]:
    """Filter all streams data."""
    return [(stream[0], filter_streams(stream[1])) for stream in streams]


def clean_data(conn, ENV: _Environ, extract_data: tuple) -> tuple:
    """Main function to clean and transform data."""
    activities_detailed, streams = extract_data[0], extract_data[1]
    clean_activities_data = clean_activities(conn, activities_detailed)
    clean_streams_data = filer_all_streams(streams)
    return clean_activities_data, clean_streams_data


if __name__ == '__main__':
    pass
