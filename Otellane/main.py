from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from celery import Celery
from celery.result import AsyncResult
from telemetry import setup_telemetry
import httpx

# /0 = broker (job queue). /1 = result backend (status + return value).
celery = Celery(
    "otellane",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)
app = FastAPI(title="Otellane", description="Otellane Otel API")
# Provider + instrumentors must be set up after the FastAPI app exists.
setup_telemetry(app)


class PingJob(BaseModel):
    url: str


@celery.task
def ping_job(url: str):
    # Runs in the worker process, not in FastAPI. This HTTP GET is what we trace.
    response = httpx.get(url, timeout=10)
    return response.status_code


@app.post("/jobs/ping")
def ping_job_endpoint(job: PingJob):
    """Enqueue one ping. Returns immediately with a job_id — the GET happens later."""
    # .delay() serializes the task onto Redis /0. It does not wait for httpx.
    job_info = ping_job.delay(job.url)
    return {"status": "Job created", "job_id": job_info.id, "job_status": job_info.status}


@app.post("/jobs/ping-batch")
def ping_job_batch_endpoint(jobs: List[PingJob]):
    """Fan-out: one API request publishes many tasks. Same trace, several GET children."""
    job_infos = [ping_job.delay(job.url) for job in jobs]
    return {
        "status": "Jobs created",
        "job_ids": [job_info.id for job_info in job_infos],
        "job_statuses": [job_info.status for job_info in job_infos],
    }


@app.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    # Look up Redis /1. app=celery is required or you get DisabledBackend.
    job_info = AsyncResult(job_id, app=celery)
    return {"status": job_info.status, "result": job_info.result}


@app.get("/health")
def get_health():
    return {"status": "ok"}
