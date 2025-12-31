"""Extract and process watch data."""

from requests import get, post
from os import environ as ENV, _Environ
from dotenv import load_dotenv, set_key
from datetime import datetime

BASE_URL = 'https://www.strava.com/api/v3'


def get_access_token(config: _Environ) -> None:
    """Get initial access token and refresh token."""

    post_data = {
        'client_id': ENV['CLIENT_ID'],
        'client_secret': ENV['CLIENT_SECRET'],
        'code': ENV['AUTH_CODE'],
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
            'client_id': ENV['CLIENT_ID'],
            'client_secret': ENV['CLIENT_SECRET'],
            'refresh_token': ENV['REFRESH_TOKEN'],
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


def get_stats(config: _Environ):
    """Get overall summary stats."""

    auth_info = {"Authorization": f'Bearer {config["ACCESS_TOKEN"]}'}
    response = get(
        f'{BASE_URL}/athletes/{config["CLIENT_ID"]}/stats',
        headers=auth_info)

    return response.json()


if __name__ == '__main__':

    load_dotenv()
    check_access_token(ENV)
    recent_runs = get_stats(ENV)['recent_run_totals']
    all_runs = get_stats(ENV)['all_run_totals']
    print(recent_runs)
