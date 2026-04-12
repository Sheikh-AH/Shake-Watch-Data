"""Gather all ETL pipeline components."""
from os import environ as ENV, _Environ
from dotenv import load_dotenv

import streamlit as st

from .extract import extract_data, get_connection
from .transform import clean_data
from .load import upload_activities, upload_streams


def etl_pipeline(config: _Environ):
    """Run the ETL pipeline."""
    
    conn = get_connection(config)
    activities_detailed, streams = extract_data(conn, config, update_check=True)

    if activities_detailed:
        clean_activities, clean_streams = clean_data((activities_detailed, streams))
        upload_activities(conn, clean_activities)
        upload_streams(conn, clean_streams)
        st.info(f'{len(activities_detailed)} new activities added.')
    else:
        print('No new activities.')
        st.info('No new activities.')

    conn.close()


if __name__ == '__main__':

    load_dotenv()
    etl_pipeline(ENV)

