"""Load data into the database."""

from os import environ as ENV
from dotenv import load_dotenv

from extract import get_connection
from transform import clean_data


def upload_activities(conn, activities: list[dict]):
    print(2)
    """Load activities into the database."""
    cursor = conn.cursor()
    for activity in activities:
        cursor.execute(
            """
            INSERT INTO activities (
                activity_id,
                activity_name,
                calories,
                distance,
                moving_time,
                elapsed_time,
                total_elevation_gain,
                activity_type_id,
                start_datetime,
                start_loc
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                activity['id'],
                activity['name'],
                activity['calories'],
                activity['distance'],
                activity['moving_time'],
                activity['elapsed_time'],
                activity['total_elevation_gain'],
                activity['type_id'],
                activity['start_date_local'],
                activity['start_latlng']
            )
        )
    conn.commit()
    cursor.close()


def upload_streams(conn, streams: tuple):
    print(1)
    """Load activity streams into the database."""
    cursor = conn.cursor()
    for activity_id, stream_data in streams:
        cursor.execute(
            """
            INSERT INTO stream_sets (
                activity_id,
                time,
                distance,
                latlng,
                altitude,
                velocity_smooth,
                heartrate,
                cadence,
                watts,
                temp,
                moving,
                grade_smooth
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                activity_id,
                stream_data.get('time'),
                stream_data.get('distance'),
                stream_data.get('latlng'),
                stream_data.get('altitude'),
                stream_data.get('velocity_smooth'),
                stream_data.get('heartrate'),
                stream_data.get('cadence'),
                stream_data.get('watts'),
                stream_data.get('temp'),
                stream_data.get('moving'),
                stream_data.get('grade_smooth')
            )
        )
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    pass
