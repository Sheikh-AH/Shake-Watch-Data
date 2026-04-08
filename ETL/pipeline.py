"""Gather all ETL pipeline components."""
from os import environ as ENV, _Environ
from dotenv import load_dotenv
from extract import extract_data, get_connection
from transform import clean_data
from load import upload_activities, upload_streams


def etl_pipeline(conn, config: _Environ):
    """Run the ETL pipeline."""
    activities_detailed, streams = extract_data(conn, config, update_check=True)
    clean_activities, clean_streams = clean_data((activities_detailed, streams))
    upload_activities(conn, clean_activities)
    upload_streams(conn, clean_streams)


if __name__ == '__main__':

    load_dotenv()
    connection = get_connection(ENV)
    etl_pipeline(connection, ENV)
    connection.close()
