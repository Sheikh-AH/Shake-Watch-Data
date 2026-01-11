import psycopg2
from dotenv import load_dotenv
from os import environ as ENV


def get_connection():
    connection = psycopg2.connect(
        user=ENV['DB_USER'],
        password=ENV['DB_PASSWORD'],
        host=ENV['DB_HOST'],
        port=ENV['DB_PORT'],
        dbname=ENV['DB_NAME']
    )
    return connection


if __name__ == '__main__':
    load_dotenv()
    conn = get_connection()
    print("Database connection established.")
    conn.close()
    print("Database connection closed.")
