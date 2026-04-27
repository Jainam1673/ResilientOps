package main

import (
	"encoding/json"
	"log"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
	requestCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{Name: "service_b_requests_total", Help: "Total requests handled by service-b"},
		[]string{"status"},
	)
	requestLatency = prometheus.NewHistogram(
		prometheus.HistogramOpts{Name: "service_b_request_latency_seconds", Help: "Service-b request latency"},
	)
	errorCount = prometheus.NewCounterVec(
		prometheus.CounterOpts{Name: "service_b_errors_total", Help: "Service-b error count"},
		[]string{"type"},
	)
)

type transformResponse struct {
	Service   string `json:"service"`
	Message   string `json:"message"`
	Timestamp int64  `json:"timestamp"`
}

func envInt(name string, fallback int) int {
	raw := os.Getenv(name)
	if raw == "" {
		return fallback
	}
	value, err := strconv.Atoi(raw)
	if err != nil {
		return fallback
	}
	return value
}

func envFloat(name string, fallback float64) float64 {
	raw := os.Getenv(name)
	if raw == "" {
		return fallback
	}
	value, err := strconv.ParseFloat(raw, 64)
	if err != nil {
		return fallback
	}
	return value
}

func maybeInjectChaos() error {
	latencyMS := envInt("CHAOS_LATENCY_MS", 0)
	errorRate := envFloat("CHAOS_ERROR_RATE", 0.0)

	if latencyMS > 0 {
		time.Sleep(time.Duration(latencyMS) * time.Millisecond)
	}

	if errorRate > 0 && rand.Float64() < errorRate {
		return http.ErrAbortHandler
	}

	return nil
}

func healthz(w http.ResponseWriter, _ *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	_, _ = w.Write([]byte(`{"status":"ok","service":"service-b"}`))
}

func transform(w http.ResponseWriter, _ *http.Request) {
	start := time.Now()
	defer func() {
		requestLatency.Observe(time.Since(start).Seconds())
	}()

	if err := maybeInjectChaos(); err != nil {
		errorCount.WithLabelValues("chaos").Inc()
		requestCount.WithLabelValues("error").Inc()
		http.Error(w, "chaos induced failure", http.StatusInternalServerError)
		return
	}

	response := transformResponse{
		Service:   "service-b",
		Message:   "payload transformed",
		Timestamp: time.Now().Unix(),
	}

	payload, err := json.Marshal(response)
	if err != nil {
		errorCount.WithLabelValues("serialization").Inc()
		requestCount.WithLabelValues("error").Inc()
		http.Error(w, "serialization failed", http.StatusInternalServerError)
		return
	}

	requestCount.WithLabelValues("success").Inc()
	w.Header().Set("Content-Type", "application/json")
	_, _ = w.Write(payload)
}

func main() {
	rand.Seed(time.Now().UnixNano())
	prometheus.MustRegister(requestCount, requestLatency, errorCount)

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", healthz)
	mux.HandleFunc("/readyz", healthz)
	mux.HandleFunc("/v1/transform", transform)
	mux.Handle("/metrics", promhttp.Handler())

	addr := ":8002"
	log.Printf("service-b listening on %s", addr)
	if err := http.ListenAndServe(addr, mux); err != nil {
		log.Fatal(err)
	}
}
