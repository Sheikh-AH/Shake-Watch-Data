DROP TABLE IF EXISTS activities;
DROP TABLE IF EXISTS activity_types;
DROP TABLE IF EXISTS stream_sets;


CREATE TABLE activity_types (
    activity_type_id INTEGER PRIMARY KEY,
    activity_type_name VARCHAR(20) NOT NULL
);

CREATE TABLE activities (
    activity_id INTEGER PRIMARY KEY,
    activity_name VARCHAR(255), --name in api data
    calories INTEGER,
    distance FLOAT,
    moving_time INTEGER,
    elapsed_time INTEGER,
    total_elevation_gain INTEGER,
    activity_type_id VARCHAR(20) NOT NULL, --sport_type in api data
    start_time TIMESTAMP, --start_date_local in api data
    start_loc VARCHAR(30) DEFAULT 1, --start_latlng in api data
    FOREIGN KEY (activity_type_id) REFERENCES activity_types(activity_type_id) ON DELETE NO ACTION
);

CREATE TABLE stream_sets (
    stream_sets_id INTEGER PRIMARY KEY,
    activity_id INTEGER,
    streams BLOB NOT NULL,
    FOREIGN KEY (activity_id) REFERENCES activities(activity_id) ON DELETE CASCADE
);

INSERT INTO activity_types (activity_type_name)
VALUES 
    ('Run'),
    ('Walk'),
    ('WeightTraining')
;