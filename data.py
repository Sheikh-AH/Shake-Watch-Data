"""Extract and process watch data."""

from requests import get, post
from os import environ as ENV, _Environ
from dotenv import load_dotenv, set_key
from datetime import datetime


def check_access_token(config: _Environ) -> None:
    """Check if the existing access token is valid."""
    if datetime.now().timestamp() >= float(config['EXPIRES_AT']):
        post_data = {
            'client_id': ENV['CLIENT_ID'],
            'client_secret': ENV['CLIENT_SECRET'],
            'refresh_token': ENV['REFRESH_TOKEN'],
            'grant_type': 'refresh_token'}
        result = post(
            'https://www.strava.com/api/v3/oauth/token',
            data=post_data
        ).json()

        set_key('.env', "ACCESS_TOKEN", result['access_token'])
        set_key('.env', "EXPIRES_AT", str(result['expires_at']))
        set_key('.env', "REFRESH_TOKEN", result['refresh_token'])


if __name__ == '__main__':

    load_dotenv()
    check_access_token(ENV)
