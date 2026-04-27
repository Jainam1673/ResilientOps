#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-resilientops}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

kubectl -n "$NAMESPACE" set env deploy/service-a CHAOS_LATENCY_MS=0 CHAOS_ERROR_RATE=0
kubectl -n "$NAMESPACE" set env deploy/service-b CHAOS_LATENCY_MS=0 CHAOS_ERROR_RATE=0
kubectl -n "$NAMESPACE" scale deploy/redis --replicas=1
kubectl -n "$NAMESPACE" delete -f "$REPO_ROOT/k8s/chaos/network-deny-service-a.yaml" --ignore-not-found

kubectl -n "$NAMESPACE" rollout restart deploy/service-a
kubectl -n "$NAMESPACE" rollout restart deploy/service-b
kubectl -n "$NAMESPACE" rollout restart deploy/api-gateway
kubectl -n "$NAMESPACE" rollout restart deploy/alert-webhook

kubectl -n "$NAMESPACE" rollout status deploy/service-a --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/service-b --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/api-gateway --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/alert-webhook --timeout=180s
kubectl -n "$NAMESPACE" rollout status deploy/redis --timeout=180s

echo "Recovery actions completed." 
