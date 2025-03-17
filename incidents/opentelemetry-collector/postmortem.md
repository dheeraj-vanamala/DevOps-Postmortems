# 🚨 OpenTelemetry Collector – Unknown Exporter `jaeger` Postmortem  

## 📌 Incident Summary  
**Date:** 2025-03-17  
**Affected System:** OpenTelemetry Collector → Jaeger  
**Impact:** OpenTelemetry Collector failed to start due to an invalid exporter configuration, preventing all traces from being sent to Jaeger.  
**Duration:** [Time from issue start to resolution]  

---

## ❌ What Failed?  
The OpenTelemetry Collector failed to start with an error stating that the `jaeger` exporter was unknown.  
As a result, traces were not being collected and sent to Jaeger, leading to a complete loss of observability data.

---

## 🔍 Why Did It Fail?  
- OpenTelemetry Collector no longer supports the `jaeger` exporter.  
- The configuration was still using `jaeger` as an exporter, which caused OpenTelemetry to fail during startup.  
- OpenTelemetry now requires traces to be sent via the OTLP exporter instead.  
- This mismatch caused the OpenTelemetry Collector to fail on startup.  

---

## 🕵️ How Did We Detect It?  
- Checked OpenTelemetry logs and observed an error mentioning `unknown type: "jaeger" for id: "jaeger"`.  
- Looked at OpenTelemetry’s documentation and found that `jaeger` exporter was deprecated.  
- Checked the valid exporters list in logs, which confirmed that `jaeger` was missing.  
- Verified that Jaeger now expects traces via OTLP instead.  

---

## 🛠 How Did We Fix It?  
### ✅ Solution Implemented  
1. Replaced the `jaeger` exporter with `otlp` in the OpenTelemetry Collector configuration.  
2. Restarted the OpenTelemetry Collector to apply the changes.  
3. Triggered a test request from a Python service and verified that traces appeared in Jaeger UI.  

---

## 🎯 Lessons Learned & Preventive Measures  
- Stay updated on OpenTelemetry breaking changes—exporters may be deprecated in newer versions.  
- Use OTLP as the standard tracing protocol instead of service-specific exporters.  
- Before upgrading OpenTelemetry versions, check the changelog to avoid unexpected failures.  
- Ensure observability pipelines are resilient to config changes by testing in a staging environment before applying in production.  

---

## 📂 Related Files & Logs  
📌 **Logs Before Fix:**  
- `logs/otel-collector-before-fix.log`  

📌 **Logs After Fix:**  
- `logs/otel-collector-after-fix.log`  

---

## ✅ Status: Resolved  
The issue was successfully fixed, and OpenTelemetry traces are now appearing in Jaeger as expected. 🎯🚀  