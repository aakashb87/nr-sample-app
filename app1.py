import os
import newrelic.agent
newrelic.agent.initialize("newrelic.ini")

from flask import Flask
import psycopg2
from psycopg2 import OperationalError

app = Flask(__name__)

PG_HOST = os.getenv("PGHOST", "nrpgdemo-aakashb.postgres.database.azure.com")
PG_DB = os.getenv("PGDATABASE", "postgres")
PG_USER = os.getenv("PGUSER", "demo")
PG_PASSWORD = os.getenv("PGPASSWORD", "b5yf.W9vhS9ebWC")
PG_SSLMODE = os.getenv("PGSSLMODE", "require")

def get_connection():
    return psycopg2.connect(
        host=PG_HOST,
        dbname=PG_DB,
        user=PG_USER,
        password=PG_PASSWORD,
        sslmode=PG_SSLMODE
    )

@app.route("/")
def home():
    return "Local NR DB demo app running against Azure PostgreSQL"

@app.route("/query")
def query():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT pg_sleep(0.3); SELECT NOW();")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"Query completed at {row[0]}"
    except OperationalError as e:
        return f"DB connection failed: {e}", 500
    except Exception as e:
        return f"Unexpected error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
