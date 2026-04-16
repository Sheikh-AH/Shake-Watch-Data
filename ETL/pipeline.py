"""Gather all ETL pipeline components."""
from os import environ as ENV, _Environ
from dotenv import load_dotenv
from pathlib import Path
import sys
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from extract import extract_data, get_connection
from transform import transform_data
from load import upload_activities, upload_streams


def etl_pipeline(config: _Environ):
    """Run the ETL pipeline."""
    
    conn = get_connection(config)
    activities_detailed, streams = extract_data(conn, config, update_check=True)
    if activities_detailed:
        transformed_acts, transformed_strms = transform_data(config, (activities_detailed, streams))
        upload_activities(conn, transformed_acts)
        upload_streams(conn, transformed_strms)
        st.info(f'{len(activities_detailed)} new activities added.')
    else:
        print('No new activities.')
        st.info('No new activities.')

    conn.close()


if __name__ == '__main__':

    load_dotenv()
    etl_pipeline(ENV)

