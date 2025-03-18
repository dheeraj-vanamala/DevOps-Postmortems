# 🚨 Prometheus Not Collecting Metrics from OpenTelemetry Collector – Postmortem  

## 📌 Incident Summary  
**Date:** 2025-03-18  
**Affected System:** OpenTelemetry Collector → Prometheus  
**Impact:** Prometheus failed to scrape metrics from OpenTelemetry Collector, leading to missing observability data.  
**Duration:** [Time from issue start to resolution]  

---

## ❌ What Failed?  
Prometheus **was not collecting any metrics** from the OpenTelemetry Collector, preventing visibility into application and system performance.

---

## 🔍 Why Did It Fail?  
- **Debugging was disabled in OpenTelemetry Collector**, making it appear as though metrics were not being collected.  
- **Port 9464 was not exposed in the Docker Compose file**, meaning Prometheus could not scrape metrics from the OpenTelemetry Collector.  
- **We initially searched for OpenTelemetry-related PromQL queries instead of checking what metrics were even available.**  
- **The OpenTelemetry Collector was collecting metrics correctly, but Prometheus could not access them due to missing port binding.**  

---

## 🕵️ How Did We Detect It?  
- **Checked OpenTelemetry Collector logs** and saw no indication of metrics being collected.  
- **Ran Python applications with `OTEL_METRICS_EXPORTER=console`**, confirming that metrics were being generated but not exported.  
- **Enabled `debug` in OpenTelemetry Collector configuration**, which revealed that it was indeed collecting metrics.  
- **Used `curl -s http://localhost:9464/metrics` but got no response**, indicating that the port was not exposed.  
- **Checked `docker port otel-collector 9464` and found that no public port was bound.**  
- **Reviewed the `docker-compose.yml` file and found that port 9464 was missing from the OpenTelemetry Collector service.**  
- **After fixing the port binding, verified the available metrics via `/metrics` API.**  
- **Ran PromQL queries and confirmed that Prometheus was now successfully collecting and storing metrics.**  

---

## 🛠 How Did We Fix It?  
### ✅ Solution Implemented  
1. **Enabled `debug` in OpenTelemetry Collector configuration** to verify if metrics were being collected.  
2. **Added port binding (`9464:9464`) to the OpenTelemetry Collector service in `docker-compose.yml`.**  
3. **Restarted OpenTelemetry Collector and Prometheus** to apply the changes.  
4. **Verified that `curl -s http://localhost:9464/metrics` returned valid metric data.**  
5. **Ran PromQL queries** (`http_client_duration_milliseconds_count`, `http_server_active_requests`, `system_memory_usage_bytes`, etc.) and confirmed successful metric collection.  
6. **Set up Grafana dashboards** to visualize Prometheus metrics.  

---

## 🎯 Lessons Learned & Preventive Measures  
- **Always enable debugging when troubleshooting OpenTelemetry Collector issues** to avoid false assumptions.  
- **Verify available metrics first (`curl /metrics`) before assuming Prometheus is at fault.**  
- **Ensure proper port bindings are configured in Docker Compose** to allow Prometheus to scrape OpenTelemetry metrics.  
- **Validate Prometheus targets (`Status -> Targets` in the Prometheus UI) to check if scrapes are happening correctly.**  
- **Use PromQL queries that match the actual exposed metrics, rather than assuming certain metric names exist.**  
- **Set up Grafana early to visualize metrics and detect collection failures faster.**  

---

## 📂 Related Configurations  
📌 **Before Fix:**  
- [`configs/otel-config-before-fix.yml`](configs/otel-config-before-fix.yml)  
- [`configs/docker-compose-before-fix.yml`](configs/docker-compose-before-fix.yml)  

📌 **After Fix:**  
- [`configs/otel-config-after-fix.yml`](configs/otel-config-after-fix.yml)  
- [`configs/docker-compose-after-fix.yml`](configs/docker-compose-after-fix.yml)  

---

## 📂 Related Files & Logs  
📌 **Logs After Fix:**  
- `logs/otel-collector-before-fix.log`  
- `logs/otel-collector-after-fix.log`  

---

## ✅ Status: Resolved  
The issue was successfully fixed, and Prometheus is now collecting metrics from OpenTelemetry Collector. 🚀