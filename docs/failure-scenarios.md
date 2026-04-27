# Failure Scenarios and Expected Behavior

## 1) Service Crash

Trigger:
- ./scripts/failures/simulate_crash.sh service-a

Expected impact:
- In-flight requests may fail briefly.
- Deployment controller creates a replacement pod.
- Readiness probe prevents traffic to initializing pod.

Signals to inspect:
- kubectl -n resilientops get pods -w
- Gateway 5xx spike in Grafana.
- Kubernetes events for pod restart.

## 2) Injected Latency

Trigger:
- ./scripts/failures/simulate_latency.sh service-a 1200

Expected impact:
- Gateway response latency increases.
- Error rate may increase if timeout budget is exceeded.

Signals to inspect:
- Gateway p95 latency panel in Grafana.
- service-a logs in Kibana.

## 3) Injected Error Rate

Trigger:
- ./scripts/failures/simulate_error_rate.sh service-b 0.4

Expected impact:
- Gateway 502 responses increase.
- Upstream service error metrics rise.

Signals to inspect:
- gateway_errors_total and service_b_errors_total metrics.
- Kibana query: service: service-b AND chaos.

## 4) Resource Exhaustion (CPU)

Trigger:
- ./scripts/failures/simulate_cpu_stress.sh service-a

Expected impact:
- CPU usage rises for target pod.
- HPA may increase replicas when metrics server is present.

Signals to inspect:
- kubectl -n resilientops top pods
- Grafana CPU panel and HPA status.

## 5) Resource Exhaustion (Memory)

Trigger:
- ./scripts/failures/simulate_memory_stress.sh service-a

Expected impact:
- Memory usage rises and container may approach or hit limits.
- Pod restarts can occur if OOMKill is triggered.

Signals to inspect:
- kubectl -n resilientops describe pod <pod-name>
- Grafana memory trends and restart counts.

## 6) Dependency Failure (Redis Down)

Trigger:
- ./scripts/failures/simulate_redis_down.sh

Expected impact:
- service-a readiness fails and request errors increase.
- gateway returns 502 for aggregated endpoint.

Signals to inspect:
- service-a readiness probe failures.
- Redis deployment scaled to zero.
- Error spikes in Grafana and logs in Kibana.

## 7) Network Failure (Dropped Traffic)

Trigger:
- ./scripts/failures/simulate_network_drop.sh

Expected impact:
- Gateway cannot reach service-a due to NetworkPolicy block.
- Aggregated gateway endpoint returns higher 5xx rate.

Signals to inspect:
- kubectl -n resilientops get networkpolicy
- gateway_errors_total increase
- alert firing in Alertmanager for error/latency

Restore:
- ./scripts/failures/restore_network.sh

## Recovery

Run:
- ./scripts/recover.sh

Recovery actions:
- Reset chaos variables to normal.
- Restore Redis replicas.
- Restart app deployments.
- Wait for rollout success.
