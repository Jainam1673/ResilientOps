#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-resilientops}"

kubectl -n "$NAMESPACE" scale deploy/redis --replicas=0

echo "Redis scaled to 0 replicas (dependency failure simulated)."
