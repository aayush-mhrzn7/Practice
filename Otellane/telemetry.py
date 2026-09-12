from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from fastapi import FastAPI


def setup_telemetry(app: FastAPI):
    # service.name is how Jaeger groups traces in the service dropdown.
    resource = Resource.create({"service.name": "otellane"})
    provider = TracerProvider(resource=resource)

    # Console: print finished spans to the API / worker terminal (learning).
    provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    # Make this the process-wide provider before instrumenting.
    trace.set_tracer_provider(provider)

    # instrument_app wraps this FastAPI instance. Celery/httpx use .instrument() on an instance.
    FastAPIInstrumentor.instrument_app(app)
    CeleryInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()

    # Host processes talk to Jaeger via localhost (not the Docker hostname "jaeger").
    # insecure=True: local OTLP has no TLS.
    exporter = OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True)
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return provider
