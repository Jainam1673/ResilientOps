#!/usr/bin/env bash
set -euo pipefail

TARGET_DEPLOYMENT="${1:-service-a}"
NAMESPACE="${2:-resilientops}"

POD=$(kubectl -n "$NAMESPACE" get pods -l "app=${TARGET_DEPLOYMENT}" -o jsonpath='{.items[0].metadata.name}')

if [[ -z "$POD" ]]; then
  echo "No pod found for deployment ${TARGET_DEPLOYMENT} in ${NAMESPACE}"
  exit 1
fi

kubectl -n "$NAMESPACE" exec "$POD" -- sh -c "nohup python -c 'x=[]\nwhile True: x.append(\"x\"*1024*1024)' >/tmp/mem_stress.log 2>&1 &"

echo "Memory stress started in pod ${POD}."
