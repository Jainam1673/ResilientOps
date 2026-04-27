#!/usr/bin/env bash
set -euo pipefail

REGISTRY_PREFIX="${1:-resilientops}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

build() {
  local name="$1"
  local path="$2"
  docker build -t "${REGISTRY_PREFIX}/${name}:latest" "$path"
}

build api-gateway "$REPO_ROOT/services/api_gateway"
build service-a "$REPO_ROOT/services/service_a"
build service-b "$REPO_ROOT/services/service_b"
build alert-webhook "$REPO_ROOT/services/alert_webhook"

echo "Built images with prefix ${REGISTRY_PREFIX}" 
