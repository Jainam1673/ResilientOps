# ResilientOps Runbook

## Prerequisites

- Docker
- kind or Kubernetes cluster
- kubectl
- metrics-server installed in cluster (for HPA behavior)

## Build and Deploy

1. ./scripts/setup-kind.sh
2. ./scripts/build-images.sh
3. kind load docker-image resilientops/api-gateway:latest --name resilientops
4. kind load docker-image resilientops/service-a:latest --name resilientops
5. kind load docker-image resilientops/service-b:latest --name resilientops
6. ./scripts/deploy.sh

## Access Services

1. kubectl -n resilientops port-forward svc/api-gateway 8080:80
2. kubectl -n resilientops port-forward svc/grafana 3000:3000
3. kubectl -n resilientops port-forward svc/kibana 5601:5601
4. kubectl -n resilientops port-forward svc/prometheus 9090:9090
5. kubectl -n resilientops port-forward svc/alertmanager 9093:9093

## Smoke Test

- curl http://localhost:8080/healthz
- curl http://localhost:8080/api/process
- python scripts/monitor/health_watch.py --url http://localhost:8080/api/process --count 20

## Linux Debugging Commands

- kubectl -n resilientops get svc,pods
- kubectl -n resilientops exec deploy/api-gateway -- ss -tulpen
- kubectl -n resilientops exec deploy/api-gateway -- sh -c 'getent hosts service-a service-b redis'
- kubectl -n resilientops logs deploy/service-a --tail=100
- kubectl -n resilientops logs daemonset/filebeat --tail=100
- kubectl -n resilientops logs deploy/alert-webhook --tail=100

## Auto-Heal Loop

- python scripts/automation/auto_heal.py --url http://localhost:8080/api/process
- This script triggers scripts/recover.sh when sustained failures are detected.

## Incident Workflow

1. Identify symptom in Grafana (latency, errors, saturation).
2. Correlate with Kibana logs by service and timestamp.
3. Validate Kubernetes health (probes, restarts, events).
4. Execute targeted recovery (scripts/recover.sh).
5. Confirm post-recovery SLO trend and pod readiness.
