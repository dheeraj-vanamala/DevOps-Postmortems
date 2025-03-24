from flask import Flask, jsonify
import requests
import uuid
import time

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set up MeterProvider
resource = Resource(attributes={"service.name": "server-a"})
exporter = OTLPMetricExporter(endpoint="http://localhost:4317/v1/metrics")
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=1000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter("server-a")
tracer = trace.get_tracer("server-a")
request_duration = meter.create_histogram("custom_request_duration", unit="ms", description="Request duration")

app = Flask(__name__)


@app.route('/')
def home():
    try:
        print("📡 Incoming request received at Server A")
        
        # Fetch greeting from Server B
        greeting_response = requests.get("http://localhost:5001/greet")
        print(f"🔹 Server B Response: {greeting_response.status_code} - {greeting_response.text}")

        # Fetch name from Server C
        name_response = requests.get("http://localhost:5002/name")
        print(f"🔹 Server C Response: {name_response.status_code} - {name_response.text}")

        greeting = greeting_response.json()["greeting"]
        name = name_response.json()["name"]
        
        final_message = {"message": f"{greeting} {name}"}
        print(f"✅ Final Response: {final_message}")

        return jsonify(final_message)

    except Exception as e:
        print(f"❌ Error in Server A: {e}")
        return jsonify({"error": str(e)}), 500
    

@app.route('/test')
def test():
    request_id = str(uuid.uuid4())
    start_time = time.time()
    time.sleep(0.01)  # Fake some work
    duration = (time.time() - start_time) * 1000  # Milliseconds
    request_duration.record(duration, attributes={"http.method": "GET", "request_id": request_id, "route": "/test"})
    return f"Request ID: {request_id}, Duration: {duration:.2f}ms"

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=6000)