"""Streamlit page to display all activities."""

import sys
from os import environ as ENV
from dotenv import load_dotenv
import json

from pathlib import Path
import pandas as pd
import streamlit as st

BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(BASE_DIR)

from dashboard.app_utils.data_tools import get_engine, get_activities_data, update_records
from ETL.pipeline import etl_pipeline

ATH_FILE = BASE_DIR + '/dashboard/app_utils/athlete_data.json'
RECORDS_FILE = BASE_DIR + '/dashboard/app_utils/records_table.html'


def loading_and_prerequisites(ath_data_file_path:str) -> tuple:
    """Load prerequisite values, config and data."""
    load_dotenv()
    conn = get_engine(ENV)
    df = get_activities_data(conn)
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">', unsafe_allow_html=True)
    with open(ath_data_file_path) as ath_data:
        data = json.load(ath_data)

    return conn, df, data


def update_activity_log(conn):
    """Callable for update button to update activities/records."""
    with st.spinner("Updating data ..."):
        etl_pipeline()
        update_records(conn)



def gen_log_title_buttons(conn):
    """Create the title, filter and buttons above the activity log."""
    col_title, col_update = st.columns([0.7,0.3], vertical_alignment='bottom')

    col_title.title("Activity Log")
    tooltip = "Update the activity log with new activities."
    with col_update:
        cont = st.container(horizontal_alignment='right')
        cont.button("Update", help=tooltip, on_click=lambda: update_activity_log(conn))


def gen_activity_log_page(conn, df:pd.DataFrame):
    """Create the activity log."""
    gen_log_title_buttons(conn)
    
    event = st.dataframe(
        df,
        column_config={
            'start_datetime': st.column_config.DateColumn(
                label="Started At",
                help="The date and time when the activity started.",
                format="YYYY-MM-DD HH:mm:ss",
                width="medium"
            ),
            'activity_name': st.column_config.TextColumn(
                label="Activity Label",
                help="The label given to the activity.",
                width="medium"
            ),
            'effort': st.column_config.NumberColumn(
                label="Effort",
                help="Effort of run",
                format="%d",
                width="small"
            ),
            'calories': st.column_config.NumberColumn(
                label="Calories Burned",
                help="Total calories burned during the activity.",
                format="%d kcal",
                width="small"
            ),
            'moving_time': st.column_config.NumberColumn(
                label="Duration",
                help="Total running time of the activity in seconds.",
                format="%d sec",
                width="small"
            ),
            'pace': st.column_config.NumberColumn(
                label="Pace",
                help="Average pace for run in m/s",
                format="%.2f m/s",
                width="small"
            ),
            'activity_id': None,
        },
        column_order=('start_datetime','activity_name','effort','calories','moving_time','pace'),
        on_select="rerun",
        selection_mode="single-row",
        hide_index=True,
    )

    if event.selection.rows:
        selected_row = df.iloc[event.selection.rows[0]]
        st.session_state['activity_id'] = selected_row['activity_id']
        st.switch_page("pages/run.py")


def render_metric_row(current_value, previous_value, label):
    """Render a metric row with progress bar and trend indicator."""
    col1, col2 = st.columns([0.97,0.03], gap='small', vertical_alignment='bottom')
    with col1:
        st.progress(current_value, text=label)
    with col2:
        if current_value - previous_value >= 0:
            icon = 'app_tools/images/green_triangle.png'
        else:
            icon = 'app_tools/images/red_triangle.png'
        st.image(icon, width='content')


def gen_last5_data(df, ath_data):
    """Generate gauges and metrics for last 5 runs sections."""
    last10 = df.sort_values(by='start_datetime', ascending = False).head(10)
    max_pace = 1000/(60*(ath_data['min_1k']))

    avg_effort = last10[:5]['effort'].mean()
    avg_pace = last10[:5]['avg_pace'].mean()
    avg_distance = last10[:5]['distance'].mean()

    delta_eff = avg_effort - last10[5:]['effort'].mean()
    delta_pace = avg_pace - last10[5:]['avg_pace'].mean()
    delta_dist = avg_distance - last10[5:]['distance'].mean()

    st.progress(avg_effort/100, text='Avg. Effort')
    st.progress(avg_pace/max_pace, text='Avg. Pace')
    st.progress(avg_distance/ath_data['max_dist'], text='Avg. Distance')

    st.space('xxsmall')
    col1,col2,col3 = st.columns(3)

    with col1:
        st.metric(label='Effort', value=avg_effort, chart_type='Area', chart_data=last10['effort'][::-1], border=True, delta=delta_eff)
    with col2:
        st.metric(label='Pace', value=round(avg_pace,2), chart_type='Area', chart_data=last10['avg_pace'][::-1], border=True, delta=delta_pace)
    with col3:
        st.metric(label='Distance', value=round(avg_distance,2), chart_type='Area', chart_data=last10['distance'][::-1], border=True, delta=delta_dist)
        
        
def gen_summary(df, ath_data):
    """Generate dashboard elements for last 5 runs and monthly summary section."""
    st.space('small')
    l5tab, monthtab = st.tabs(['Last 5','Last Month'])

    with l5tab:
        gen_last5_data(df, ath_data)
    
    with monthtab:
        st.header('Monthly')


def gen_athlete_records(data):
    """Generate records table for dashboard."""
    with open(RECORDS_FILE) as f:
        html = f.read()
    
    values = {}
    exclude = ('max_altitude', 'last_updated')

    for key in data.keys():
        if key not in exclude:
            values[f'{{{key}}}'] = data[key]
    
    for placeholder, value in values.items():
        html = html.replace(placeholder, str(value))
    
    st.html(html)


def gen_achievements():
    """Generate achievements section for dashboard."""
    listOfAchievements = []
    with st.container(border=True, gap='small', height=450):
        for achievement in listOfAchievements:
            st.html(f'''
                <div style="background-color: #52b399; border-radius: 10px; border: 2px solid #44ab46; padding: 10px;">
                    <p style="color: #000000; margin: 0;">{achievement}</p>
                </div>
            ''')


def gen_badges():
    """Create badge icons."""
    pass


if __name__ == "__main__":
    
    conn, all_runs_df, ath_data = loading_and_prerequisites(ATH_FILE)
    

    colLog, colSummary = st.columns([0.7,0.3], gap="large")
    with colLog:
        gen_activity_log_page(conn, all_runs_df)
    with colSummary:
        gen_summary(all_runs_df, ath_data)

    st.space('small')

    st.title('Records & Milestones')
    colRecords, spacer, colAchievements = st.columns([0.5, 0.025,0.475])
    with colRecords:
        gen_athlete_records(ath_data)
    with colAchievements:
        gen_achievements()

