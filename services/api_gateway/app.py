import asyncio
import logging
import os
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.responses import Response

SERVICE_A_URL = os.getenv("SERVICE_A_URL", "http://service-a:8001")
SERVICE_B_URL = os.getenv("SERVICE_B_URL", "http://service-b:8002")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "2.0"))

REQUEST_COUNT = Counter(
    "gateway_requests_total",
    "Total requests handled by API Gateway",
    ["endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "gateway_request_latency_seconds",
    "API Gateway request latency",
    ["endpoint"],
)
ERROR_COUNT = Counter(
    "gateway_errors_total",
    "Gateway upstream failures",
    ["dependency"],
)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("resilientops.gateway")

app = FastAPI(title="ResilientOps API Gateway", version="1.0.0")


async def _call_service(client: httpx.AsyncClient, url: str) -> dict[str, Any]:
    response = await client.get(url, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "api-gateway"}


@app.get("/readyz")
async def readyz() -> dict[str, str]:
    async with httpx.AsyncClient() as client:
        try:
            await _call_service(client, f"{SERVICE_A_URL}/healthz")
            await _call_service(client, f"{SERVICE_B_URL}/healthz")
        except Exception as exc:  # noqa: BLE001
            logger.warning("readiness failed: %s", exc)
            raise HTTPException(status_code=503, detail="dependencies unavailable") from exc
    return {"status": "ready"}


@app.get("/metrics")
async def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/process")
async def process() -> dict[str, Any]:
    start = time.perf_counter()
    endpoint = "/api/process"
    async with httpx.AsyncClient() as client:
        try:
            service_a_task = _call_service(client, f"{SERVICE_A_URL}/v1/data")
            service_b_task = _call_service(client, f"{SERVICE_B_URL}/v1/transform")
            service_a_data, service_b_data = await asyncio.gather(service_a_task, service_b_task)
        except Exception as exc:  # noqa: BLE001
            ERROR_COUNT.labels(dependency="service-upstream").inc()
            REQUEST_COUNT.labels(endpoint=endpoint, status="error").inc()
            logger.exception("upstream call failed")
            raise HTTPException(status_code=502, detail="upstream service failed") from exc

    duration = time.perf_counter() - start
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(endpoint=endpoint, status="success").inc()

    return {
        "status": "ok",
        "gateway_latency_ms": round(duration * 1000, 2),
        "service_a": service_a_data,
        "service_b": service_b_data,
    }
