CREATE TABLE IF NOT EXISTS activity_types (
    activity_type_id INTEGER PRIMARY KEY,
    activity_type_name VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY,
    city_name VARCHAR(30) NOT NULL
);


CREATE TABLE IF NOT EXISTS activities (
    activity_id INTEGER PRIMARY KEY,
    activity_name VARCHAR(255), --name in api data
    calories INTEGER,
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain INTEGER,
    activity_type_id VARCHAR(20) NOT NULL, --sport_type in api data
    start_at TIMESTAMP, --start_date_local in api data
    city_id VARCHAR(30),
    FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id) ON DELETE NO ACTION,
    FOREIGN KEY (city_id) REFERENCES cities(city_id) ON DELETE NO ACTION
);

CREATE TABLE IF NOT EXISTS stream_sets (
    stream_sets_id INTEGER PRIMARY KEY,
    activity_id INTEGER,
    streams BLOB NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE
)