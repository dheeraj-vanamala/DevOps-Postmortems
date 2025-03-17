# OpenTelemetry Collector – Unknown Exporter `jaeger`  

This folder contains the postmortem report for the OpenTelemetry Collector startup failure due to an invalid `jaeger` exporter configuration.  

## 📌 Issue Summary  
- OpenTelemetry Collector failed to start because the `jaeger` exporter was removed in newer versions.  
- The configuration needed to be updated to use the `otlp` exporter instead.  
- This issue prevented traces from being collected and sent to Jaeger.  

📂 **Refer to the postmortem report for full details.**  