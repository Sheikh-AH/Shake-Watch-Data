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
    return {row[0]: row[1] for row in rows}


if __name__ == '__main__':

    load_dotenv()
    conn = get_connection('watch_data')

    # activities_detailed, activity_ids, streams = extract_data(conn, ENV)
    type_mapping = get_type_mapping(conn)
    print(type_mapping)

    conn.close()
