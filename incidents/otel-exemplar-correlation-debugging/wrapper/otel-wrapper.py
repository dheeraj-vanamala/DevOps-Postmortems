import psutil
from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.propagate import extract, inject
import time
import logging
import os

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get service name dynamically
service_name = os.environ.get("OTEL_SERVICE_NAME", "unknown-service")

# Setup OTel
resource = Resource(attributes={
    "service.name": service_name,
    "host.name": os.uname().nodename,
})
metrics.set_meter_provider(MeterProvider(
    resource=resource,
    metric_readers=[PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint="localhost:4317", insecure=True),
        export_interval_millis=1000
    )]
))
trace.set_tracer_provider(TracerProvider(resource=resource))
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Memory gauge
def memory_usage_callback(_):
    process = psutil.Process()
    mem_usage = process.memory_info().rss
    yield metrics.Observation(mem_usage, {"pid": str(os.getpid())})

meter.create_observable_gauge(
    "process_memory_usage_bytes",
    callbacks=[memory_usage_callback],
    unit="bytes",
    description="Memory usage of the process",
)

# Singleton counters
started_counter = meter.create_counter("requests_started")
completed_counter = meter.create_counter("requests_completed")

# Middleware
class OtelMiddleware:
    def __init__(self, app):
        self.app = app
        self.service_name = service_name
        self.flask_app = None  # Will be set in instrument_app

    def __call__(self, environ, start_response):
        from flask import Request, g
        request = Request(environ)
        context = extract(request.headers) if "traceparent" in request.headers else None
        with self.flask_app.app_context():  # Add app context
            with tracer.start_as_current_span(
                f"{request.path}-handler",
                context=context
            ) as span:
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.route", request.path)
                span.set_attribute("http.user_agent", request.headers.get("User-Agent", "unknown"))
                span.set_attribute("http.query", request.query_string.decode() or "none")
                span.set_attribute("http.host", request.host)
                start_time = time.time()
                start_cpu = psutil.cpu_times()
                attrs = {
                    "route": request.path,
                    "method": request.method,
                    "service_name": self.service_name
                }
                started_counter.add(1, attrs)
                # Inject trace context for outgoing requests
                headers = {}
                inject(headers)
                g.trace_headers = headers  # Safe in app context
                def wrapped_start_response(status, headers, exc_info=None):
                    return start_response(status, headers, exc_info)
                try:
                    response_iter = self.app(environ, wrapped_start_response)
                    response_body = list(response_iter)
                    duration = (time.time() - start_time) * 1000
                    status_code = int(wrapped_start_response.status.split()[0]) if hasattr(wrapped_start_response, "status") else 200
                    size = sum(len(chunk) for chunk in response_body) if response_body else 0
                except Exception as e:
                    duration = (time.time() - start_time) * 1000
                    status_code = 500
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    attrs["status"] = str(status_code)
                    meter.create_counter("requests_failed_total").add(1, attrs)
                    completed_counter.add(1, attrs)
                    raise
                cpu_time = psutil.cpu_times()
                cpu_usage = (cpu_time.user - start_cpu.user + cpu_time.system - start_cpu.system) * 1000
                attrs["status"] = str(status_code)
                meter.create_histogram("request_duration_ms").record(duration, attrs)
                meter.create_counter("requests_total").add(1, attrs)
                meter.create_histogram("response_size_bytes").record(size, attrs)
                meter.create_histogram("request_cpu_time_ms").record(cpu_usage, attrs)
                meter.create_counter("request_status_code").add(1, attrs)
                meter.create_counter("request_method_count").add(1, {
                    "method": request.method,
                    "service_name": self.service_name
                })
                span.set_attribute("http.status_code", status_code)
                logger.debug(f"Handled {request.path}: {duration}ms, {size} bytes")
                completed_counter.add(1, attrs)
                return response_body

def instrument_app(app):
    middleware = OtelMiddleware(app.wsgi_app)
    middleware.flask_app = app  # Store Flask app reference
    app.wsgi_app = middleware