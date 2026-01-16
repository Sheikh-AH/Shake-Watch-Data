"""Extract and process watch data."""

from datetime import datetime
from os import environ as ENV, _Environ

from requests import get, post
from dotenv import set_key, load_dotenv
from psycopg2 import connect


BASE_URL = 'https://www.strava.com/api/v3'


def get_connection(config: _Environ):
    """Get conneciton to PSTGRESQL database."""
    connection = connect(
        user=config['DB_USER'],
        password=config['DB_PASSWORD'],
        host=config['DB_HOST'],
        port=config['DB_PORT'],
        dbname=config['DB_NAME']
    )
    return connection


def get_access_token(config: _Environ) -> None:
    """Get initial access token and refresh token."""

    post_data = {
        'client_id': config['CLIENT_ID'],
        'client_secret': config['CLIENT_SECRET'],
        'code': config['AUTH_CODE'],
        'grant_type': 'authorization_code'}
    response = post('https://www.strava.com/api/v3/oauth/token',
                    data=post_data, timeout=10).json()

    set_key('.env', "ACCESS_TOKEN", response['access_token'])
    set_key('.env', "EXPIRES_AT", str(response['expires_at']))
    set_key('.env', "REFRESH_TOKEN", response['refresh_token'])


def check_access_token(config: _Environ) -> None:
    """Check if the existing access token is valid."""

    if datetime.now().timestamp() >= float(config['EXPIRES_AT']):
        post_data = {
            'client_id': config['CLIENT_ID'],
            'client_secret': config['CLIENT_SECRET'],
            'refresh_token': config['REFRESH_TOKEN'],
            'grant_type': 'refresh_token'}
        response = post(
            'https://www.strava.com/api/v3/oauth/token',
            data=post_data, timeout=10
        ).json()
        set_key('.env', "ACCESS_TOKEN", response['access_token'])
        set_key('.env', "EXPIRES_AT", str(response['expires_at']))
        set_key('.env', "REFRESH_TOKEN", response['refresh_token'])
        print('Token Updated')
    print('Token Valid')


def get_stats(config: _Environ) -> dict:
    """Get overall summary stats."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    response = get(
        f'{BASE_URL}/athletes/{config["ATHLETE_ID"]}/stats',
        headers=auth_info, timeout=10).json()

    return response


def get_activities(config: _Environ) -> list[dict]:
    """Get a list of activities."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    end_point = '/athlete/activities'
    response = get(
        f'{BASE_URL}{end_point}',
        headers=auth_info, timeout=10
    ).json()

    return response


def get_activity_ids(activities: list[dict]) -> list[int]:
    """Get the id's for all activities."""
    return [activity['id'] for activity in activities]


def filter_for_stored_data(conn, activity_ids: list[int]) -> list[int]:
    """Check stored data for activiy ids."""

    with conn.cursor() as cur:
        cur.execute("SELECT activity_id FROM activities;")
        stored_ids = cur.fetchall()
        if stored_ids:
            s_ids = [i[0] for i in stored_ids]
            missing_ids = [i for i in activity_ids if i not in s_ids]
            return missing_ids
    return activity_ids


def get_activity_info(config: _Environ, activity_id: int) -> list[dict]:
    """Get a info of activities."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    end_point = f'/activities/{activity_id}'
    response = get(
        f'{BASE_URL}{end_point}',
        headers=auth_info, timeout=10
    ).json()

    return response


def get_detailed_activities(config: _Environ, activity_ids: list[dict]):
    """Get detailed activity information from id."""
    return [get_activity_info(config, activity_id) for activity_id in activity_ids]


def get_activity_streams(config: _Environ, activity_id: int) -> list[dict]:
    """Get a list of activities."""

    streams = ",".join([
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
    ])

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    end_point = f'/activities/{activity_id}/streams'
    params = {
        "keys": streams,
        "key_by_type": "true"
    }

    response = get(
        f'{BASE_URL}{end_point}',
        headers=auth_info,
        params=params,
        timeout=10
    ).json()

    return (activity_id, response)


def get_all_activity_streams(config: _Environ, activity_ids: list[int]) -> list[dict]:
    """Get all activity streams from a list of activity ids."""
    return [get_activity_streams(config, activity_id) for activity_id in activity_ids]


def extract_data(conn, config: _Environ):
    """Main function to extract data."""
    check_access_token(config)
    activities_basic = get_activities(config)
    activity_ids = get_activity_ids(activities_basic)
    # activity_ids = filter_for_stored_data(conn, activity_ids)
    activities_detailed = get_detailed_activities(config, activity_ids)
    streams = get_all_activity_streams(config, activity_ids)
    return activities_detailed, streams


if __name__ == '__main__':
    load_dotenv()

    connection = get_connection(ENV)
    data, streams = extract_data(connection, ENV)
    connection.close()
    with open('extracted.txt', 'w') as f:
        f.write(str(streams[20][1]['time']))
