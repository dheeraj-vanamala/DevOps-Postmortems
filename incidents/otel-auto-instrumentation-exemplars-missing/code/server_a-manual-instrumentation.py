from flask import Flask, jsonify
import requests
import uuid
import time

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader, ConsoleMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


metric_file_handler = logging.FileHandler("metrics.log")
metric_file_handler.setLevel(logging.INFO)
metric_formatter = logging.Formatter('%(message)s')  # Just the metric JSON
metric_file_handler.setFormatter(metric_formatter)

# Create a logger specifically for metrics
metric_logger = logging.getLogger("metrics")
metric_logger.setLevel(logging.INFO)
metric_logger.addHandler(metric_file_handler)
metric_logger.propagate = False  # Prevent metrics from going to root logger

# Custom ConsoleMetricExporter to use the metric logger
class FileMetricExporter(ConsoleMetricExporter):
    def export(self, metrics_data, **kwargs):
        from io import StringIO
        output = StringIO()
        super().export(metrics_data, file=output)
        metric_logger.info(output.getvalue())
        output.close()

resource = Resource(attributes={"service.name": "service-a"})
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)))
tracer = trace.get_tracer(__name__)

console_metric_exporter = FileMetricExporter()
console_reader = PeriodicExportingMetricReader(console_metric_exporter, export_interval_millis=1000)
otlp_metric_exporter = OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True)
otlp_reader = PeriodicExportingMetricReader(otlp_metric_exporter, export_interval_millis=1000)
meter_provider = MeterProvider(resource=resource, metric_readers=[console_reader, otlp_reader])
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter("custom_requests_total", description="Total custom requests")
request_duration = meter.create_histogram("custom_request_duration", unit="ms", description="Custom request duration")

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
    try:
        with tracer.start_as_current_span("custom-operation") as span:
            start_time = time.time()
            time.sleep(0.01)
            duration = (time.time() - start_time) * 1000
            request_id = str(uuid.uuid4())
            request_counter.add(1, attributes={"http.method": "GET", "request_id": request_id})
            request_duration.record(duration, attributes={"http.method": "GET", "request_id": request_id})
            span.set_attribute("http.method", "GET")
            return jsonify({"message": "Test"})
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)