#!/usr/bin/env bash
set -euo pipefail

TARGET_DEPLOYMENT="${1:-service-a}"
NAMESPACE="${2:-resilientops}"

POD=$(kubectl -n "$NAMESPACE" get pods -l "app=${TARGET_DEPLOYMENT}" -o jsonpath='{.items[0].metadata.name}')

if [[ -z "$POD" ]]; then
  echo "No pod found for deployment ${TARGET_DEPLOYMENT} in ${NAMESPACE}"
  exit 1
fi

kubectl -n "$NAMESPACE" delete pod "$POD"
echo "Deleted pod ${POD}. Kubernetes will recreate it via Deployment controller."
