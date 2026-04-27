.PHONY: build deploy recover chaos-crash chaos-latency chaos-error chaos-redis-down chaos-network-drop chaos-network-restore chaos-mem watch auto-heal

build:
	./scripts/build-images.sh

deploy:
	./scripts/deploy.sh

recover:
	./scripts/recover.sh

chaos-crash:
	./scripts/failures/simulate_crash.sh service-a

chaos-latency:
	./scripts/failures/simulate_latency.sh service-a 1200

chaos-error:
	./scripts/failures/simulate_error_rate.sh service-b 0.4

chaos-redis-down:
	./scripts/failures/simulate_redis_down.sh

chaos-network-drop:
	./scripts/failures/simulate_network_drop.sh

chaos-network-restore:
	./scripts/failures/restore_network.sh

chaos-mem:
	./scripts/failures/simulate_memory_stress.sh service-a

watch:
	python scripts/monitor/health_watch.py --url http://localhost:8080/api/process --count 50

auto-heal:
	python scripts/automation/auto_heal.py --url http://localhost:8080/api/process
