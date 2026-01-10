"""Process and transform data extracted from the API."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
from datetime import datetime

from sqlite3 import Connection

from extract import get_connection, main as extract_data


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


if __name__ == '__main__':

    load_dotenv()
    conn = get_connection('watch_data')

    activities_detailed, activity_ids, streams = extract_data(conn, ENV)
    type_mapping = get_type_mapping(conn)
    activities = convert_types_to_ids(type_mapping, activities_detailed)
    for activity in activities:
        print(activity['type_id'], activity['sport_type'])
    conn.close()
