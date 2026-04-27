FROM golang:1.24 AS builder
WORKDIR /app
COPY go.mod ./
RUN go mod download
COPY main.go ./
RUN CGO_ENABLED=0 GOOS=linux go build -o service-b main.go

FROM gcr.io/distroless/static-debian12
WORKDIR /app
COPY --from=builder /app/service-b ./service-b
EXPOSE 8002
ENTRYPOINT ["/app/service-b"]
