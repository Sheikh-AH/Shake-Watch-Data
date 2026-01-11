DROP DATABASE IF EXISTS watch_data;
CREATE DATABASE watch_data;
\c watch_data;

CREATE TABLE activity_types (
    activity_type_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    activity_type_name VARCHAR(20) NOT NULL
);

CREATE TABLE activities (
    activity_id BIGINT PRIMARY KEY,
    activity_name VARCHAR(255), --name in api data
    calories INT,
    distance NUMERIC,
    moving_time INT,
    elapsed_time INT,
    total_elevation_gain INT,
    activity_type_id INT NOT NULL, --sport_type in api data
    start_datetime TIMESTAMP, --start_date_local in api data
    start_loc NUMERIC[], --start_latlng in api data
    FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id) ON DELETE NO ACTION
);

CREATE TABLE stream_sets (
    stream_sets_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    activity_id BIGINT,
    time NUMERIC[],
    distance NUMERIC[],
    latlng NUMERIC[],
    altitude NUMERIC[],
    velocity_smooth NUMERIC[],
    heartrate NUMERIC[],
    cadence NUMERIC[],
    watts NUMERIC[],
    temp NUMERIC[],
    moving BOOLEAN[],
    grade_smooth NUMERIC[],
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE
);

INSERT INTO activity_types (activity_type_name)
VALUES 
    ('Run'),
    ('Walk'),
    ('WeightTraining'),
    ('Workout')
;