import argparse
import json
import time
from datetime import datetime

import requests


def main() -> None:
    parser = argparse.ArgumentParser(description="Watch gateway health and request behavior")
    parser.add_argument("--url", default="http://localhost:8080/api/process")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--count", type=int, default=50)
    args = parser.parse_args()

    for i in range(args.count):
        ts = datetime.utcnow().isoformat()
        try:
            start = time.perf_counter()
            response = requests.get(args.url, timeout=3)
            latency_ms = (time.perf_counter() - start) * 1000
            status = response.status_code
            body = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            print(json.dumps({"time": ts, "idx": i + 1, "status": status, "latency_ms": round(latency_ms, 2), "body": body}))
        except Exception as exc:  # noqa: BLE001
            print(json.dumps({"time": ts, "idx": i + 1, "status": "error", "error": str(exc)}))
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
