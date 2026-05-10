"""OpenTelemetry tracing setup — graceful fallback when OTel not available."""
import logging

logger = logging.getLogger(__name__)


def setup_tracing():
    """Configure OpenTelemetry tracing with graceful fallback."""
    try:
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.resources import Resource
        from app.config import settings
    except ImportError:
        logger.debug("OpenTelemetry not installed — tracing disabled")
        return

    if not getattr(settings, 'otel_enabled', False):
        logger.info("OpenTelemetry tracing disabled via config")
        return

    try:
        resource = Resource.create({"service.name": getattr(settings, 'otel_service_name', 'auth-service')})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor()
        provider.add_span_processor(processor)
        # Install FastAPI instrumentation if available
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        except ImportError:
            pass
    except Exception as e:
        logger.warning(f"Failed to setup OpenTelemetry tracing: {e}")