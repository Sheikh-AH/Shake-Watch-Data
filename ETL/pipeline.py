"""Gather all ETL pipeline components."""
from os import environ as ENV, _Environ
from dotenv import load_dotenv, dotenv_values
from pathlib import Path
import sys
import streamlit as st

BASE_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.append(BASE_DIR)
ENV_FILE = BASE_DIR + '/ETL/.env'
ATH_FILE = BASE_DIR + '/dashboard/app_utils/athlete_data.json'

from ETL.extract import extract_data, get_connection
from ETL.transform import transform_data
from ETL.load import upload_activities, upload_streams


def etl_pipeline(config = None, ath_file_path = ATH_FILE):
    """Run the ETL pipeline."""
    if not config:
        config = dotenv_values(ENV_FILE)
    conn = get_connection(config)
    activities_detailed, streams = extract_data(conn, config, update_check=True)
    if activities_detailed:
        transformed_acts, transformed_strms = transform_data(ath_file_path, (activities_detailed, streams))
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

