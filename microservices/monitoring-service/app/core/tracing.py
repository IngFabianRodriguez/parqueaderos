"""OpenTelemetry tracing setup — graceful fallback if OTel not installed."""
from __future__ import annotations

import os


def setup_tracing(app):
    """Set up OpenTelemetry tracing with graceful fallback."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OLTPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        # OTel not installed — skip tracing silently
        return

    resource = Resource.create({"service.name": os.getenv("OTEL_SERVICE_NAME", "monitoring-service")})
    provider = TracerProvider(resource=resource)

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    try:
        exporter = OLTPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    except Exception:
        pass  # Silently skip if OTLP endpoint not available

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
