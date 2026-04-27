#!/usr/bin/env bash
set -euo pipefail

CLUSTER_NAME="${1:-resilientops}"

kind create cluster --name "$CLUSTER_NAME"

cat <<EOF
Kind cluster created: $CLUSTER_NAME
Next steps:
1. Build images: ./scripts/build-images.sh
2. Load images into kind:
   kind load docker-image resilientops/api-gateway:latest --name $CLUSTER_NAME
   kind load docker-image resilientops/service-a:latest --name $CLUSTER_NAME
   kind load docker-image resilientops/service-b:latest --name $CLUSTER_NAME
   kind load docker-image resilientops/alert-webhook:latest --name $CLUSTER_NAME
3. Deploy stack: ./scripts/deploy.sh
EOF
