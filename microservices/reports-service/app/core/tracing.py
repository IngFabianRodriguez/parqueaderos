"""OpenTelemetry tracing setup."""

import logging
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

from app.config import settings

logger = logging.getLogger(__name__)


def setup_tracing():
    """Configure OpenTelemetry tracing."""
    if not settings.otel_enabled:
        logger.info("OpenTelemetry tracing disabled")
        return

    resource = Resource.create({SERVICE_NAME: settings.otel_service_name})
    provider = TracerProvider(resource=resource)

    try:
        exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
        processor = BatchSpanProcessor(exporter)
        provider.add_span_processor(processor)
    except Exception as e:
        logger.warning(f"Failed to setup OTLP exporter: {e}")

    provider.add_span_processor(BatchSpanProcessor())