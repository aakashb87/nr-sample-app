import os
import json
import time

from flask import Flask, jsonify
import psycopg2
from psycopg2 import OperationalError

import newrelic.agent

from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Gauge

# --- New Relic setup ---------------------------------------------------------

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "newrelic.ini")
if os.path.exists(CONFIG_PATH):
    newrelic.agent.initialize(CONFIG_PATH)
else:
    print("WARNING: newrelic.ini not found; New Relic APM will not be active")

# --- OpenTelemetry setup (OSS traces to New Relic) ---------------------------

NR_OTEL_API_KEY = os.getenv("NR_OTEL_API_KEY", "573fbf9fb0f300660a50b267d52a839bFFFFNRAL")

otlp_exporter = OTLPSpanExporter(
    endpoint="https://otlp.nr-data.net:4318/v1/traces",
    headers={"api-key": NR_OTEL_API_KEY},
)

otel_provider = TracerProvider()
otel_processor = BatchSpanProcessor(otlp_exporter)
otel_provider.add_span_processor(otel_processor)
trace.set_tracer_provider(otel_provider)

# --- Flask app + instrumentation --------------------------------------------

app = Flask(__name__)

# Wrap Flask app with New Relic WSGI middleware
app = newrelic.agent.wsgi_application()(app)

# Attach OpenTelemetry instrumentation
FlaskInstrumentor().instrument_app(app)
Psycopg2Instrumentor().instrument()

# Prometheus metrics for Flask app (this will add /metrics)
metrics = PrometheusMetrics(app, path="/metrics")
metrics.info("app_info", "Application info", version="1.0.0")

# Custom Prometheus metrics for DB health
db_up_gauge = Gauge("db_up", "Is the DB reachable? 1 = yes, 0 = no")
db_latency_gauge = Gauge(
    "db_sample_query_duration_seconds",
    "Latency of a simple DB health-check query in seconds",
)

# --- Database Configuration ---
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
def update_db_health_metrics():
    """Run a lightweight DB check and update Prometheus gauges."""
    start = time.perf_counter()
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()

        duration = time.perf_counter() - start
        db_up_gauge.set(1)
        db_latency_gauge.set(duration)
        return True, duration
    except Exception:
        db_up_gauge.set(0)
        # leave latency as last known or set to 0 if you prefer
        return False, None

@app.route("/")
def hello():
    return "Hello, World!"
@app.route("/about")
def about():
    return "This is the upgraded Azure + New Relic demo app."
@app.route("/status")
def status():
    return jsonify({
        "app": "NR demo",
        "status": "ok",
        "message": "App is running and responding",
    })
@app.route("/products")
def list_products():
    """Return all products from the database as JSON."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, category, price, created_at
            FROM products
            ORDER BY created_at DESC;
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        products = [
            {
                "id": r[0],
                "name": r[1],
                "category": r[2],
                "price": float(r[3]),
                "created_at": r[4].isoformat()
            }
            for r in rows
        ]

        return jsonify(products)

    except OperationalError as e:
        return jsonify({"error": f"DB connection failed: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
@app.route("/products/slow")
def products_slow():
    """
    Intentionally slow DB query to simulate a performance problem.
    Useful for seeing slow DB spans in monitoring tools.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        # Force a ~400ms delay in the database, then run a query
        cur.execute("""
            SELECT pg_sleep(0.4);
            SELECT id, name, category, price
            FROM products
            WHERE price > 10.0;
        """)
        rows = cur.fetchall()

        cur.close()
        conn.close()

        return f"Slow products query returned {len(rows)} rows"

    except OperationalError as e:
        return jsonify({"error": f"DB connection failed (slow): {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Unexpected error in /products/slow: {str(e)}"}), 500
@app.route("/cpu-heavy")
def cpu_heavy():
    """
    CPU-bound endpoint: sorts a large list to spike CPU usage.
    This helps differentiate CPU bottlenecks from DB bottlenecks.
    """
    data = list(range(500000, 0, -1))  # 500k integers in reverse order
    data.sort()                        # CPU-intensive sort
    return "CPU-heavy operation completed"
@app.route("/file-large")
def file_large():
    """
    Large-response endpoint.
    Generates a big JSON payload to simulate heavy response size / bandwidth.
    """
    big_payload = [
        {"id": i, "name": f"Product-{i}", "price": float(i) / 10.0}
        for i in range(0, 50000)
    ]
    return app.response_class(
        response=json.dumps(big_payload),
        status=200,
        mimetype="application/json",
    )
@app.route("/db-health")
def db_health():
    """
    DB health endpoint:
    - Returns JSON for humans / dashboards
    - Updates Prometheus metrics for /metrics scrape
    """
    ok, duration = update_db_health_metrics()
    if ok:
        return jsonify({
            "db_up": True,
            "latency_seconds": duration,
        })
    else:
        return jsonify({
            "db_up": False,
            "error": "DB check failed (see application logs / Prometheus metric db_up).",
        }), 500
@app.route("/routes")
def routes():
    """Debug endpoint: list all registered routes."""
    return jsonify(sorted([str(r) for r in app.url_map.iter_rules()]))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
