import json
import logging
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("resilientops.alert-webhook")

app = FastAPI(title="ResilientOps Alert Webhook", version="1.0.0")


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "alert-webhook"}


@app.post("/alerts")
async def alerts(request: Request) -> JSONResponse:
    payload = await request.json()
    timestamp = datetime.now(timezone.utc).isoformat()
    logger.info("alertmanager_payload=%s", json.dumps({"received_at": timestamp, "payload": payload}))
    return JSONResponse({"status": "received", "received_at": timestamp})
