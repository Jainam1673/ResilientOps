import argparse
import subprocess
import time
from collections import deque

import requests


def run_recovery(namespace: str) -> None:
    subprocess.run(["./scripts/recover.sh", namespace], check=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple auto-heal loop for ResilientOps")
    parser.add_argument("--url", default="http://localhost:8080/api/process")
    parser.add_argument("--interval", type=float, default=5.0)
    parser.add_argument("--window", type=int, default=12)
    parser.add_argument("--failure-threshold", type=float, default=0.5)
    parser.add_argument("--namespace", default="resilientops")
    args = parser.parse_args()

    recent = deque(maxlen=args.window)

    while True:
        ok = 0
        try:
            response = requests.get(args.url, timeout=2.5)
            ok = 1 if response.status_code < 500 else 0
        except Exception:
            ok = 0

        recent.append(ok)

        if len(recent) == args.window:
            success_ratio = sum(recent) / len(recent)
            if success_ratio < (1.0 - args.failure_threshold):
                print(f"Failure threshold breached (success_ratio={success_ratio:.2f}), running recovery...")
                run_recovery(args.namespace)
                recent.clear()

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
