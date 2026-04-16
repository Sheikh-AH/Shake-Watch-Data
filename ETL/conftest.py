"""Fixtures for tests."""
import pytest

@pytest.fixture(params=[
    {
        "id": 17979035287,
        "name": "Evening Run",
        "calories": 197.0,
        "distance": 2510.2,
        "moving_time": 1066,
        "elapsed_time": 1066,
        "total_elevation_gain": 17.0,
        "start_date_local": "2026-04-04T19:23:13Z",
        "start_latlng": [58.536482, 0.087805],
        "average_speed": 2.355,
        "effort": 0,
        "sport_type": "Run",
    },
    {
        "id": 12345678901,
        "name": "Morning Run",
        "calories": 350.5,
        "distance": 5000.0,
        "moving_time": 1800,
        "elapsed_time": 1900,
        "total_elevation_gain": 45.5,
        "start_date_local": "2026-04-03T08:15:00Z",
        "start_latlng": [40.7128, -74.0060],
        "average_speed": 2.778,
        "description": "Nice run",
        "workout_type": "easy",
    },
    {
        "id": 99999999999,
        "name": "Quick Run",
        "calories": 100.0,
        "distance": 1000.0,
        "moving_time": 360,
        "elapsed_time": 420,
        "total_elevation_gain": 5.0,
        "start_date_local": "2026-04-02T18:30:00Z",
        "start_latlng": [51.5074, -0.6278],
        "average_speed": 2.778,
    },
])
def activity_example(request):
    """Parametrized fixture providing 3 example activity records."""
    return request.param


@pytest.fixture(params=[
    {
        "time": {"data": [0, 1, 2, 3, 4, 5]},
        "distance": {"data": [0, 100, 200, 300, 400, 500]},
        "latlng": {"data": [[51.536, 0.087], [51.537, 0.088]]},
        "altitude": {"data": [7.6, 7.8, 8.0, 8.2, 8.4, 8.6]},
        "velocity_smooth": {"data": [0, 2.5, 2.6, 2.7, 2.8, 2.9]},
        "heartrate": {"data": [100, 110, 120, 125, 130, 135]},
        "cadence": {"data": [0, 90, 92, 94, 96, 98]},
        "watts": {"data": [0, 150, 200, 250, 300, 350]},
        "temp": {"data": [15, 15, 16, 16, 17, 17]},
        "moving": {"data": [False, True, True, True, True, True]},
        "grade_smooth": {"data": [0, 0.5, 1.0, 1.5, 2.0, 2.5]},
        "extra_field": {"data": [1, 2, 3, 4, 5, 6]},
        "calories": {"data": [0, 10, 20, 30, 40, 50]},
    },
    {
        "time": {"data": [0, 2, 4, 6, 8]},
        "distance": {"data": [0, 200, 400, 600, 800]},
        "latlng": {"data": [[40.712, -74.006], [40.713, -74.007]]},
        "altitude": {"data": [10, 20, 30, 40, 50]},
        "velocity_smooth": {"data": [0, 2.0, 2.5, 3.0, 3.5]},
        "cadence": {"data": [0, 85, 90, 95, 100]},
        "temp": {"data": [12, 13, 14, 15, 16]},
        "moving": {"data": [False, True, True, True, True]},
        "grade_smooth": {"data": [0, 0.2, 0.4, 0.6, 0.8]},
        "metadata": {"data": [1, 2, 3, 4, 5]},
    },
    {
        "time": {"data": [0, 10, 20, 30]},
        "distance": {"data": [0, 50, 100, 150]},
        "latlng": {"data": [[51.5, -0.1], [51.51, -0.11]]},
        "altitude": {"data": [5, 6, 7, 8]},
        "velocity_smooth": {"data": [0, 5, 5, 5]},
        "heartrate": {"data": [90, 100, 110, 120]},
        "cadence": {"data": [0, 80, 85, 90]},
        "watts": {"data": [0, 100, 150, 200]},
        "temp": {"data": [20, 20, 21, 21]},
        "moving": {"data": [False, True, True, True]},
        "grade_smooth": {"data": [0, 0, 0, 1]},
    },
])
def streams_example(request):
    """Parametrized fixture providing 3 example stream objects."""
    return request.param

@pytest.fixture(params=[
    {
        'max_dist': 10,
        'interval': 5,
        'time': [60,120,180,240,390],
        'dist': [2000,4000,5000,7000,10000],
        'expected_paces': [3/5,3.5/5]
    },
    {
        'max_dist': 7,
        'interval': 1,
        'time': [60,100,120,180,240,390,450],
        'dist': [1010,2020,3000,4001,5000,6100,7000],
        'expected_paces': [1/1.01, (4/6)/1.01, (2/6)/0.98, 1/1.001, 1/0.999, 2.5/1.1, 1/0.9]
    }
])
def pace_data_example(request):
    return request.param


@pytest.fixture(params=[
    {
        'limits': {'max_hr': 180, 'max_time': 1800, 'max_dist': 5000},
        'run_time': 900,
        'run_dist': 2500,
        'run_hr': [120, 125, 130, 135, 140],
        'expected_effort': 78.49,
    },
    {
        'limits': {'max_hr': 180, 'max_time': 1800, 'max_dist': 5000},
        'run_time': 1500,
        'run_dist': 4500,
        'run_hr': [150, 155, 160, 165, 170],
        'expected_effort': 106.5,
    },
    {
        'limits': {'max_hr': 180, 'max_time': 1800, 'max_dist': 5000},
        'run_time': 600,
        'run_dist': 1500,
        'run_hr': [100, 110, 115, 120, 110],
        'expected_effort': 63.55,
    },
])
def effort_data_example(request):
    """Parametrized fixture providing 3 example effort calculation scenarios."""
    return request.param