import logging
import os
import random
import time

import redis
from fastapi import FastAPI, HTTPException
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
CHAOS_LATENCY_MS = int(os.getenv("CHAOS_LATENCY_MS", "0"))
CHAOS_ERROR_RATE = float(os.getenv("CHAOS_ERROR_RATE", "0.0"))

REQUEST_COUNT = Counter("service_a_requests_total", "Total requests handled by service-a", ["status"])
REQUEST_LATENCY = Histogram("service_a_request_latency_seconds", "Service-a request latency")
ERROR_COUNT = Counter("service_a_errors_total", "Service-a error count", ["type"])
UP = Gauge("service_a_up", "Service-a process health")
UP.set(1)

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("resilientops.service-a")

app = FastAPI(title="ResilientOps Service A", version="1.0.0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)


def _inject_chaos() -> None:
    if CHAOS_LATENCY_MS > 0:
        time.sleep(CHAOS_LATENCY_MS / 1000)
    if CHAOS_ERROR_RATE > 0 and random.random() < CHAOS_ERROR_RATE:
        raise RuntimeError("injected chaos error")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "service-a"}


@app.get("/readyz")
def readyz() -> dict[str, str]:
    try:
        redis_client.ping()
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=503, detail="redis unavailable") from exc
    return {"status": "ready"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/v1/data")
def get_data() -> dict[str, object]:
    start = time.perf_counter()
    try:
        _inject_chaos()
        counter = redis_client.incr("service_a_counter")
        payload = {
            "service": "service-a",
            "counter": counter,
            "timestamp": int(time.time()),
        }
        REQUEST_COUNT.labels(status="success").inc()
        return payload
    except RuntimeError as exc:
        ERROR_COUNT.labels(type="chaos").inc()
        REQUEST_COUNT.labels(status="error").inc()
        logger.warning("chaos failure: %s", exc)
        raise HTTPException(status_code=500, detail="chaos induced failure") from exc
    except Exception as exc:  # noqa: BLE001
        ERROR_COUNT.labels(type="dependency").inc()
        REQUEST_COUNT.labels(status="error").inc()
        logger.exception("service-a failure")
        raise HTTPException(status_code=500, detail="service-a unavailable") from exc
    finally:
        REQUEST_LATENCY.observe(time.perf_counter() - start)
