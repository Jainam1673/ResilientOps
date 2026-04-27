#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-resilientops}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

kubectl -n "$NAMESPACE" delete -f "$REPO_ROOT/k8s/chaos/network-deny-service-a.yaml" --ignore-not-found

echo "Removed network policy block for gateway -> service-a."
