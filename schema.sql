CREATE TABLE IF NOT EXISTS activities (
    activity_id INTEGER PRIMARY KEY,
    activity_name VARCHAR(255), --name in api data
    calories INTEGER,
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain INTEGER,
    activity_type VARCHAR(20), --sport_type in api data
    start_at TIMESTAMP, --start_date_local in api data
    location_city VARCHAR(30)
);

CREATE TABLE IF NOT EXISTS stream_sets (
    stream_sets_id INTEGER PRIMARY KEY,
    activity_id INTEGER,
    streams BLOB NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE
)