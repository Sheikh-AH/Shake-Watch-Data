"""Gather all ETL pipeline components."""
from os import environ as ENV, _Environ
from dotenv import load_dotenv
from extract import extract_data, get_connection, check_access_token
from transform import clean_data
from load import upload_activities, upload_streams


def etl_pipeline(conn, config: _Environ):
    """Run the ETL pipeline."""
    check_access_token(config)
    activities_detailed, streams = extract_data(conn, ENV)
    clean_activities_data, clean_streams_data = clean_data(
        conn, ENV, (activities_detailed, streams))
    upload_activities(conn, clean_activities_data)
    upload_streams(conn, clean_streams_data)


if __name__ == '__main__':

    load_dotenv()
    conn = get_connection()
    etl_pipeline(conn, ENV)
    conn.close()
