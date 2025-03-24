# 🧵 Auto-Instrumentation Exemplars Missing – Postmortem Summary

This postmortem captures the debugging journey of enabling **trace-metric correlation** using **OpenTelemetry Exemplars** in a Python Flask service with **auto-instrumentation**.

Despite traces and metrics being emitted correctly, **exemplars were missing** from Prometheus metrics during auto-instrumentation. The report outlines the root cause, investigation steps, manual instrumentation validation, final fixes, and next steps toward building a plug-and-play observability wrapper.

📁 Dive into the full postmortem for technical deep-dive, learnings, and future work.