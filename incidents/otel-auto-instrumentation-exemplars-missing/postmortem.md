# 🚨 Auto-Instrumentation with Missing Exemplars – Postmortem  

## 📌 Incident Summary  
**Date:** 2025-03-24 
**Affected System:** Python Flask Service A → OpenTelemetry → Prometheus  
**Impact:** Trace IDs were not appearing in metrics during auto-instrumentation, causing loss of trace-metric correlation via exemplars.  
**Duration:** ~4-5 days of investigation, debugging, and validation  

---

## ❌ What Failed?  
Auto-instrumentation of the Python service failed to attach trace context to the emitted metrics.  
This led to exemplars not being present in the `/metrics` endpoint, breaking correlation between traces and metrics in real-time observability pipelines.

---

## 🔍 Why Did It Fail?  

1. Auto-instrumentation was successful in generating traces, but metrics had no attached trace context, resulting in no exemplars.  
2. OpenTelemetry hooks for auto-instrumentation were not able to bind the trace and metric context automatically in Python.  
3. Exemplars were only available in real-time and not persisted, further complicating visibility.  
4. Lack of proper code instrumentation meant the correlation wasn't established automatically, as assumed.

---

## 🧪 Step-by-Step Timeline & Investigation  

1. **Correlation Goal Identified**:  
   Observed that traces and metrics were both being generated successfully → Next objective was enabling correlation between them.

2. **Initial Auto-Instrumentation Attempt**:  
   Auto-instrumentation showed traces with trace_ids → But the metrics had no trace_id or exemplars.

3. **Tried Manual Trace ID Injection**:  
   Added custom code (generated earlier) to inject trace context manually into metrics — partial workaround.

4. **Discovered Exemplars Feature**:  
   Realized via research that OpenTelemetry supports Exemplars — designed for trace-metric correlation.

5. **Started Debugging with Exemplars**:  
   Switched focus to enabling exemplars via environment variables — but still not working in auto-instrumentation.

6. **Switched to Manual Instrumentation for Debugging**:  
   Updated Python server code with explicit trace context, span context, and request ID manually during metric export.

7. **Exemplars Working in Manual Mode**:  
   Successfully emitted exemplars in Prometheus when using manual instrumentation → Proved that the stack supports it.

8. **Back to Auto-Instrumentation with Same Setup**:  
   Switched back to auto-instrumentation using same collector, Prometheus config, and environment variables → Still no exemplars.

9. **Root Cause Narrowed to Python Auto-Instrumentation**:  
   Confirmed that Python OpenTelemetry auto-instrumentation doesn’t automatically link trace context to metrics.

10. **Patched Python App Code**:  
   Added minimal tracing code: explicitly generated spans, trace context, and metric recording block → Exemplars showed up in logs.

11. **Real-Time Detection of Exemplars**:  
   Realized that `/metrics` endpoint only shows exemplars while traffic is in-flight → Confirmed by curling the API during request bursts.

12. **Confirmed Lack of Persistence**:  
   Concluded that exemplars aren’t persisted by default in our current Prometheus + Grafana + OTEL setup.  
   Tools like Grafana Mimir are required for exemplar persistence and historical correlation.

---

## 🛠 How Did We Fix It?  

- Switched to manual trace and metric recording in Flask app with opentelemetry.instrumentation setup.  
- Added logic to link active span context with metric histograms.  
- Validated the presence of exemplars in `/metrics` endpoint during active requests.  
- Created clean workflow to reproduce and verify trace-metric correlation.  
- Identified limitations of current setup and planned next steps for persistence using Mimir.

---

## 🧪 Environment Variables & Application Run Command

### 🔧 Environment Variables Used:
OTEL_SERVICE_NAME="server-a"  
OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"  
OTEL_METRICS_EXPORTER="otlp"  
OTEL_TRACES_EXPORTER="otlp"  
OTEL_RESOURCE_ATTRIBUTES="service.name=server-a"  
OTEL_EXEMPLARS_SAMPLING_PROBABILITY=1.0  
OTEL_EXEMPLAR_FILTER="always_on"  
OTEL_PROPAGATORS="tracecontext"  
OTEL_LOG_LEVEL="debug"  
FLASK_APP="server_a"  

### 🚀 Command to Run the Python Application:
opentelemetry-instrument flask run --port=6000

📌 **Note:** Using `flask run` (instead of `python server_a.py`) ensures OpenTelemetry hooks into the Flask app correctly during auto-instrumentation. This was a key learning in the debugging phase.

---

## 🎯 Lessons Learned & Preventive Measures  

- Auto-instrumentation ≠ full correlation — especially in Python, trace and metric context often needs manual linking.  
- Real-time metrics ≠ persistent metrics — exemplars disappear post-request unless Mimir or another long-term store is configured.  
- Never assume metrics contain trace_id unless explicitly instrumented or verified via exemplars.  
- Investigate through both code and traffic — exemplars won’t show up until a request is actively being handled.  
- Be open to writing minimal code to test root causes instead of staying rigid in setup assumptions.

---

## 📂 Related Files & Logs  

- `code/server_a-manual-instrumentation.py` – Custom trace context creation and metric recording logic during manual instrumentation 
- `code/server_a-auto-instrumentation.py` -  Custom trace context creation and metric recording logic during auto instrumentation
- `configs/otel-collector-config.yml` – Changed the debug verbosity to detailed  
- `configs/prometheus.yml` – No change needed  
- `logs/otel-collector-after-fix.log` – Verified exemplar emission  
- `logs/metrics-after-fix.log` – Verified real-time exemplars during request bursts  

---

## ✅ Status: Resolved (Partially)  

- Auto-instrumentation fixed with minimal code support.  
- Exemplars emitting and visible in `/metrics` during active traffic.  
- Exemplar persistence is not yet implemented — to be solved with Grafana Mimir.  
- Wrapper work and full plug-and-play observability still in progress.

---

## 🧭 Next Steps: Observability Wrapper for Scale  

- Current implementation works with minimal code instrumentation but is not scalable across services.  
- We're planning to build a **generic observability wrapper** that can:  
  - Automatically inject trace context into metrics  
  - Emit exemplars correctly  
  - Support plug-and-play integration for any Python microservice  
  - Be compatible with internal services to maintain distributed tracing  
- This wrapper will ensure consistent correlation without modifying every individual application’s codebase.

This is a work-in-progress and will be documented as a separate milestone once implemented.