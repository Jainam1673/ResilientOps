#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

kubectl apply -k "$REPO_ROOT/k8s/base"

kubectl -n resilientops rollout status deploy/api-gateway --timeout=180s
kubectl -n resilientops rollout status deploy/service-a --timeout=180s
kubectl -n resilientops rollout status deploy/service-b --timeout=180s
kubectl -n resilientops rollout status deploy/redis --timeout=180s
kubectl -n resilientops rollout status deploy/alert-webhook --timeout=180s

echo "ResilientOps deployed." 
