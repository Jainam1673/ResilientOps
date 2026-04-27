# ResilientOps Architecture

ResilientOps is a production-inspired SRE playground with three application services and two observability planes.

## Control Plane

- Kubernetes Deployments ensure desired state and auto-restart failed pods.
- Readiness and liveness probes gate traffic and trigger recovery.
- HorizontalPodAutoscaler scales gateway and service-a based on CPU utilization.

## Data Plane

- api-gateway (Python/FastAPI) receives external requests and aggregates responses from service-a and service-b.
- service-a (Python/FastAPI) serves stateful data and depends on Redis.
- service-b (Go) performs transformation and returns lightweight JSON payloads.
- Redis is the primary in-memory datastore used by service-a.

## Observability Plane

- Prometheus scrapes /metrics from all services.
- Grafana provides dashboards for latency, error rates, and resource behavior.
- Prometheus alert rules evaluate SRE thresholds for latency, errors, and saturation.
- Alertmanager routes alerts to an internal webhook receiver.
- Filebeat ships container logs to Logstash.
- Logstash enriches and forwards logs to Elasticsearch.
- Kibana enables incident investigation via indexed logs.

## Automation Plane

- scripts/automation/auto_heal.py monitors user-facing success rate.
- When failures breach threshold, it executes scripted recovery actions.
- scripts/recover.sh resets chaos settings, restores dependencies, and restarts key workloads.

## Request Lifecycle

1. Client sends request to api-gateway /api/process.
2. Gateway concurrently calls service-a /v1/data and service-b /v1/transform.
3. service-a increments Redis counter and returns timestamped payload.
4. service-b returns transformed payload.
5. Gateway returns aggregate response and emits latency/error metrics.

## Networking Model

- Services use ClusterIP networking and DNS names:
  - api-gateway.resilientops.svc.cluster.local
  - service-a.resilientops.svc.cluster.local
  - service-b.resilientops.svc.cluster.local
  - redis.resilientops.svc.cluster.local
- kube-proxy performs load balancing across pod replicas.
