# 🚨 Flask Debug Mode – OpenTelemetry Auto-Instrumentation Failure

## 📌 Incident Summary
**Date:** 2025-03-17
**Affected System:** OpenTelemetry Auto-Instrumentation → Flask Application
**Impact:** OpenTelemetry auto-instrumentation failed to capture traces due to Flask’s debug mode interfering with instrumentation.
**Duration:** [Time from issue start to resolution]

---

## ❌ What Failed?
OpenTelemetry auto-instrumentation was enabled for a Flask application, but no traces were being captured.
As a result, requests to the Flask application were **not generating traces**, preventing observability in OpenTelemetry and Jaeger.

---

## 🔍 Why Did It Fail?
- Flask’s **debug mode (debug=True) enabled the auto-reloader**, which **broke OpenTelemetry’s ability to hook into Flask** properly.
- OpenTelemetry instrumentation **was being applied at startup**, but Flask’s auto-reloader caused the process to restart, undoing the instrumentation.
- This prevented OpenTelemetry from capturing traces even though manual instrumentation worked correctly.
- The issue was documented in OpenTelemetry’s official troubleshooting guide, but it was overlooked during debugging.

---

## 🕵️ How Did We Detect It?
- Checked OpenTelemetry logs but found **no traces being generated**.
- Verified that OpenTelemetry instrumentation **was modifying Flask middleware**, but **no traces were sent to OpenTelemetry Collector**.
- Compared the behavior with **manual instrumentation**, which worked correctly.
- Turned off debug=True to **prevent Flask from auto-reloading**, and auto-instrumentation started working immediately.
- Found documentation stating that **Flask’s auto-reloader can break OpenTelemetry instrumentation**.

---

## 🛠 How Did We Fix It?
## ✅ Solution Implemented
1. **Disabled Flask’s debug mode (debug=False)** to prevent unnecessary reloads.
2. **Alternatively, set use_reloader=False** to allow debug mode without breaking OpenTelemetry.
3. Restarted the application and verified that traces were now appearing in OpenTelemetry and Jaeger.
4. Confirmed that Flask auto-instrumentation was correctly applying after the fix.

---

## 🎯 Lessons Learned & Preventive Measures
- Flask’s debug=True enables an **auto-reloader**, which can interfere with OpenTelemetry’s auto-instrumentation.
- If **debug mode is needed**, use use_reloader=False to avoid breaking OpenTelemetry.
- Always check OpenTelemetry **official troubleshooting documentation** for known issues before deep debugging.
- **When debugging auto-instrumentation failures, compare behavior with manual instrumentation** to isolate the issue.

---

## ✅ Status: Resolved
The issue was successfully fixed, and OpenTelemetry traces are now being captured correctly from the Flask application. 🎯🚀