# 🚨 OpenTelemetry – Jaeger Setup Postmortem  

## 📌 Incident Summary  
**Date:** 2025-03-17  
**Affected System:** OpenTelemetry Collector → Jaeger  
**Impact:** OpenTelemetry failed to send traces to Jaeger, causing loss of observability data.  
**Duration:** [Time from issue start to resolution]  

---

## ❌ What Failed?  
The OpenTelemetry Collector was **unable to communicate with Jaeger on port 14250**.  
As a result, traces were **not being collected and sent to Jaeger for visualization**.

---

## 🔍 Why Did It Fail?  
- **Jaeger was not exposing port 14250** for OpenTelemetry to send traces.  
- The **latest Jaeger image exposed port 4317 instead of 14250**, causing OpenTelemetry to send traces to a non-existent port.  
- **Configuration mismatch**: OpenTelemetry expected Jaeger to listen on `14250`, but it wasn’t configured correctly.  
- **Incorrect networking assumption**: Initially, we tried using `localhost:14250` inside Docker Compose, but inside a container, `localhost` only refers to itself, not the Jaeger container.  
- OpenTelemetry kept **retrying the connection in a loop**, leading to unnecessary CPU utilization and delays in debugging.

---

## 🕵️ How Did We Detect It?  
- **Checked OpenTelemetry logs** and observed repeated `connection refused` errors.  
- **Inspected Jaeger logs** and found that **14250 was not being exposed**.  
- **Ran a network check** and confirmed that Jaeger was only listening on `4317` instead of `14250`.  
- **Verified that `localhost:14250` was incorrect** inside Docker Compose, as `localhost` refers to the OpenTelemetry container itself, not the Jaeger container.  
- **Cross-checked online reports** on GitHub and Stack Overflow, where similar issues were reported for the latest Jaeger image.

---

## 🛠 How Did We Fix It?  
### ✅ **Solution Implemented**  
1. **Changed the Jaeger image from `latest` to `1.42.0`**, ensuring it properly exposes `14250`.  
2. **Updated OpenTelemetry config to use `jaeger:14250`** instead of `localhost:14250`.  
   - Initially, `jaeger:14250` **wasn’t resolving**, so we temporarily switched to `localhost:14250`.  
   - After adding `depends_on: jaeger` in `docker-compose.yml`, OpenTelemetry now starts **after Jaeger is ready**, making `jaeger:14250` work.  
   - Docker's internal DNS now correctly resolves `jaeger:14250`, making it the preferred approach inside Docker Compose.  
3. **Restarted Jaeger and OpenTelemetry Collector** after applying both fixes.  
4. **Verified exposed ports** in the container to confirm that `14250` was now active.  
5. **Monitored OpenTelemetry logs** to ensure traces were successfully being sent to Jaeger.  
6. **Checked Jaeger UI** to confirm that traces were appearing correctly.  

---

## 🎯 Lessons Learned & Preventive Measures  
- **Avoid using `latest` tags** in production—always pin a stable version (`1.42.0`) to avoid breaking changes.  
- **Always verify exposed ports before debugging application-level issues.**  
- **Inside Docker Compose, use service names (`jaeger:14250`) instead of `localhost:14250`** to ensure proper container-to-container communication.  
- **Use health checks and `depends_on` in Docker Compose** to prevent race conditions between dependent services.  
- **Maintain a documented troubleshooting guide** for similar issues in the future.  

---

## 📂 Related Files & Logs  
📌 **Logs Before Fix:**  
- [`logs/otel-collector-before-fix.log`](logs/otel-collector-before-fix.log)  
- [`logs/jaeger-before-fix.log`](logs/jaeger-before-fix.log)  

📌 **Logs After Fix:**  
- [`logs/otel-collector-after-fix.log`](logs/otel-collector-after-fix.log)  
- [`logs/jaeger-after-fix.log`](logs/jaeger-after-fix.log)  

---

## ✅ Status: **Resolved**  
The issue was successfully fixed, and OpenTelemetry traces are now appearing in Jaeger as expected. 🎯🚀  