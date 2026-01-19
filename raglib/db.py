import psycopg
from pgvector.psycopg import register_vector

def connect():
    # psycopg reads PG* env vars automatically
    conn = psycopg.connect("")
    register_vector(conn)
    return conn