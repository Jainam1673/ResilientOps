#!/usr/bin/env bash
set -euo pipefail

TARGET_DEPLOYMENT="${1:-service-a}"
ERROR_RATE="${2:-0.35}"
NAMESPACE="${3:-resilientops}"

kubectl -n "$NAMESPACE" set env deploy/"$TARGET_DEPLOYMENT" CHAOS_ERROR_RATE="$ERROR_RATE"
kubectl -n "$NAMESPACE" rollout status deploy/"$TARGET_DEPLOYMENT" --timeout=180s

echo "Injected ${ERROR_RATE} error rate into ${TARGET_DEPLOYMENT}."
