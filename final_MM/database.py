import psycopg2

DB_CONFIG = {
    "dbname": "mind matrix",
    "user": "postgres",
    "password": "ash228637",
    "host": "localhost",
    "port": "5433"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)
