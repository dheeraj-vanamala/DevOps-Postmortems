# 🧵 Auto-Instrumentation Exemplars Missing – Postmortem Summary

This postmortem captures the debugging journey of enabling **trace-metric correlation** using **OpenTelemetry Exemplars** in a Python Flask service with **auto-instrumentation**.

Despite traces and metrics being emitted correctly, **exemplars were missing** from Prometheus metrics during auto-instrumentation. The report outlines the root cause, investigation steps, manual instrumentation validation, final fixes, and next steps toward building a plug-and-play observability wrapper.

📁 Dive into the full postmortem for technical deep-dive, learnings, and future work.

## 📌 Incident Summary  
**Date:** 2025-03-27
**Affected System:** OpenTelemetry Auto-Instrumentation → Exemplars in Prometheus  
**Impact:** Missing exemplars in Prometheus metrics despite auto-instrumentation being enabled.  
**Duration:** [Insert Time Taken for Debugging and Fix]  

---

## ❌ What Failed?
Exemplars were not showing up consistently for trace-metric correlation despite being emitted by the application code through OpenTelemetry auto-instrumentation.

---

## 🔍 Why Did It Fail?
- **Auto-instrumentation for exemplars was inconsistent**. While traces were working perfectly, exemplars were emitted randomly without any predictable pattern or correlation to the metrics. This was a **black box** issue, where auto-instrumentation could not be relied upon for consistent exemplar tracing.
- **OpenTelemetry's Python implementation** of auto-instrumentation still had **undocumented behavior** when it came to propagating exemplars across spans and metrics, which resulted in sporadic or missing exemplars.

---

## 🕵️ How Did We Detect It?
- We used **manual instrumentation** to verify if exemplars were working. When applied, they appeared as expected in the logs, confirming that the issue was related to auto-instrumentation.
- **Investigating auto-instrumentation configuration** revealed that it only sporadically emitted exemplars without a reliable pattern. After testing various configurations and reviewing the OpenTelemetry documentation, it was clear that auto-instrumentation was not functioning as expected for this use case.

---

## 🛠️ How Did We Fix It?
- **Switching to manual instrumentation** for trace-metric correlation via a custom wrapper to ensure **consistency** and **predictability** in exemplar emission.
- **Wrapper-based approach** allowed us to guarantee **trace context propagation** and **exemplar consistency** across multiple services without relying on unreliable auto-instrumentation.
  
> While manual instrumentation provided consistent exemplar output, OpenTelemetry’s Python auto-instrumentation remained inconsistent and unreliable—exemplars were emitted randomly without a clear pattern.  
>  
> As a result, we **deprecated reliance on auto-instrumentation for exemplar tracing** and moved forward with a **custom Python wrapper** to ensure consistent, reusable tracing and metrics across all services.

---

## 🎯 Lessons Learned & Preventive Measures  
- **Auto-instrumentation for exemplars** (Python) still behaves like a **black box**—unpredictable and hard to debug. It is **not yet production-ready** for our needs and should not be relied upon for critical trace-metric correlation.  
- **Wrapper-based manual instrumentation** gives us **full control** and **consistent results**, especially when trace-metric correlation is critical. We recommend this approach for more complex or high-visibility observability use cases.
- **Documenting issues** and sharing findings with the community helps identify gaps in tooling and improves understanding of limitations in observability systems like OpenTelemetry.

---

## 📂 Related Tools/Configurations
- **Wrapper Code:**  
  - [`wrapper/otel-wrapper.py`](wrapper/otel-wrapper.py)  

---

## ✅ Status: Resolved (Partially)  
The issue of missing exemplars has been resolved through **manual instrumentation** with a custom wrapper. However, the OpenTelemetry Python auto-instrumentation still **requires further stabilization** before it can be fully relied upon for exemplars and trace-metric correlation.  
The next steps involve **evaluating solutions** to ensure **long-term reliability** and **scalability** across services.

---

## 💡 Next Steps  
- **Assess the impact of using manual instrumentation** versus auto-instrumentation in production environments at scale.  
- Explore **integrating OpenTelemetry with Mimic** to ensure persistent exemplars and better metric retention over time.
- **Monitor further OpenTelemetry updates** to determine if the auto-instrumentation improvements solve the current issues with exemplars.