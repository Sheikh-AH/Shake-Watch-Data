"""Streamlit page to display all activities."""

from os import environ as ENV, _Environ
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

from tool import get_engine, get_activities_data, update_records
from ETL.pipeline import etl_pipeline
from ETL.extract import get_connection

def loading_and_prerequisites() -> tuple:
    load_dotenv()
    conn = get_engine(ENV)
    df = get_activities_data(conn)
    st.markdown('<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">', unsafe_allow_html=True)
    
    return conn, df

def update_activity_log(conn, config):
    """Callable for update button to update activities/records."""
    with st.spinner("Updating data ..."):
        etl_pipeline(config)
        print('activity updated')
        update_records(conn)
        print('records updated')


def gen_log_title_buttons(conn, config):
    """Create the title, filter and buttons above the activity log."""
    
    col_title, col_update = st.columns([0.7,0.3], vertical_alignment='bottom')

    col_title.title("Activity Log")

    tooltip = "Update the activity log with new activities."

    with col_update:
        cont = st.container(horizontal_alignment='right')
        cont.button("Update", help=tooltip, on_click=lambda: update_activity_log(conn, config))


def gen_activity_log_page(conn, config, df:pd.DataFrame):
    """Create the activity log."""
    gen_log_title_buttons(conn, config)
    
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

    if event.selection.rows: # type: ignore
        selected_row = df.iloc[event.selection.rows[0]] # type: ignore
        st.session_state['activity_id'] = selected_row['activity_id']
        st.switch_page("pages/run.py")


def get_last5_data(df):
    last5_data = df.sort_values(by='start_datetime', ascending = False).head(5)['activity_id']
    st.text(last5_data)


def gen_summary(df):
    st.space('small')
    l5tab, monthtab = st.tabs(['Last 5','Last Month'])

    with l5tab:
        st.header('Last 5 runs.')
        get_last5_data(df)
    
    with monthtab:
        st.header('Monthly')


def gen_athlete_records():
    with open('records_table.html') as f:
        html = f.read()

    values = {
        '{{run_count}}': 'value1 m/s',
        '{{max1kmPace}}': 'value1 m/s',
        '{{max5kmPace}}': 'value2 m/s',
        '{{maxPace}}': 'value3 m/s',
        '{{avgPace}}': 'value4 m/s',
        '{{maxHeartrate}}': 'value5 bpm',
        '{{avgHeartrate}}': 'value6 bpm',
        '{{maxDistance}}': 'value7 km',
        '{{maxAltitude}}': 'value8 m',
        '{{avgPower}}': 'value9 W',
        '{{avgCadence}}': 'value10 rpm',
    }
    
    for placeholder, value in values.items():
        html = html.replace(placeholder, str(value))
    
    st.html(html)


def gen_achievements():
    listOfAchievements = ['aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw',
                          'aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw',
                          'aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw','aaafgeasgeaw',]
    with st.container(border=True, gap='small', height=450):
            acheivements = st.container()
            for achievement in listOfAchievements:
                st.html(f'''
                    <div style="background-color: #52b399; border-radius: 10px; border: 2px solid #44ab46; padding: 10px;">
                        <p style="color: #000000; margin: 0;">{achievement}</p>
                    </div>
                ''')
    

if __name__ == "__main__":
    
    conn, df = loading_and_prerequisites()
    

    colLog, spacer, colSummary = st.columns([0.70,0.025,0.275])
    with colLog:
        gen_activity_log_page(conn, ENV, df)
    with colSummary:
        gen_summary(df)

    st.space('small')

    st.title('Athlete Records')
    colRecords, spacer, colAchievements = st.columns([0.5, 0.025,0.475])
    with colRecords:
        gen_athlete_records()
    with colAchievements:
        gen_achievements()
    


    
