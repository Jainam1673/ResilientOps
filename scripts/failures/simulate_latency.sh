#!/usr/bin/env bash
set -euo pipefail

TARGET_DEPLOYMENT="${1:-service-a}"
LATENCY_MS="${2:-800}"
NAMESPACE="${3:-resilientops}"

kubectl -n "$NAMESPACE" set env deploy/"$TARGET_DEPLOYMENT" CHAOS_LATENCY_MS="$LATENCY_MS"
kubectl -n "$NAMESPACE" rollout status deploy/"$TARGET_DEPLOYMENT" --timeout=180s

echo "Injected ${LATENCY_MS}ms latency into ${TARGET_DEPLOYMENT}."
