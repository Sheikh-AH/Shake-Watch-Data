"""Tests for transform sectin of pipeline."""

from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from transform import *

class TestFilterFuncs:
    """Tests for filter functions."""
    
    def test_valid_acts_filter(self, activity_example):
        """Test that filter_activities_data keeps only required fields."""
        result = filter_activities_data([activity_example])
        
        expected_fields = {'id', 'name', 'calories',
                           'distance', 'moving_time','elapsed_time', 'total_elevation_gain', 'start_date_local','start_latlng', 'average_speed'}

        assert len(result) == 1
        assert set(result[0].keys()) == expected_fields
        
        assert 'effort' not in result[0]
        assert 'sport_type' not in result[0]
        assert 'description' not in result[0]
        assert 'workout_type' not in result[0]
        
        assert result[0]['id'] == activity_example['id']
        assert result[0]['name'] == activity_example['name']
        assert result[0]['calories'] == activity_example['calories']


    def test_valid_streams_filter(self, streams_example):
        """Test that filter_streams keeps only required stream fields."""
        result = filter_streams(streams_example)

        expected_fields = {
            'time', 'distance', 'latlng','altitude', 'velocity_smooth',
            'heartrate', 'cadence', 'watts', 'temp', 'moving', 'grade_smooth'
        }
        
        print(result)
        for field in result.keys():
            assert field in expected_fields
        
        assert 'extra_field' not in result
        assert 'calories' not in result
        assert 'metadata' not in result
        
        if streams_example.get('time'):
            assert result['time'] == streams_example['time']['data']
        if streams_example.get('distance'):
            assert result['distance'] == streams_example['distance']['data']
        
        if not streams_example.get('heartrate'):
            assert not result.get('heartrate')