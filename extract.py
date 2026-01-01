"""Extract and process watch data."""

from requests import get, post
from os import environ as ENV, _Environ
from dotenv import load_dotenv, set_key
from datetime import datetime

BASE_URL = 'https://www.strava.com/api/v3'


def get_access_token(config: _Environ, call_time: int) -> None:
    """Get initial access token and refresh token."""

    post_data = {
        'client_id': config['CLIENT_ID'],
        'client_secret': config['CLIENT_SECRET'],
        'code': config['AUTH_CODE'],
        'grant_type': 'authorization_code'}
    response = post('https://www.strava.com/api/v3/oauth/token',
                    data=post_data).json()

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
            data=post_data
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
        headers=auth_info).json()
    return response


def get_activities(config: _Environ) -> list[dict]:
    """Get a list of activities."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    end_point = '/athlete/activities'
    response = get(
        f'{BASE_URL}{end_point}',
        headers=auth_info
    ).json()
    return response


def get_activity_ids(activities: list[dict]) -> list[int]:
    """Get the id's for all activities."""
    activity_ids = []
    for activity in activities:
        activity_ids.append(activity['id'])
    return activity_ids


def get_activity_info(config: _Environ, activity_id: int) -> list[dict]:
    """Get a list of activities."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    end_point = f'/activities/{activity_id}'
    response = get(
        f'{BASE_URL}{end_point}',
        headers=auth_info
    ).json()
    return response


def check_cache_for_activity_id():
    """Check stored data for activiy ids."""
    pass


def get_detailed_activities(config: _Environ, activity_ids: list[int]):
    activities_detailed_info = []
    for activity_id in activity_ids:
        activities_detailed_info.append(get_activity_info(config, activity_id))
    return (activities_detailed_info)


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
        params=params
    ).json()

    return response


if __name__ == '__main__':

    load_dotenv()

    check_access_token(ENV)

    recent_runs = get_stats(ENV)['recent_run_totals']
    all_runs = get_stats(ENV)['all_run_totals']
    activities_basic = get_activities(ENV)
    activity_ids = get_activity_ids(activities_basic)
    activities_detailed = get_detailed_activities(ENV, activity_ids)
    streams = get_activity_streams(ENV, activity_ids[1])

    print(streams)
