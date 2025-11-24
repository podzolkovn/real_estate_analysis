from prometheus_client import Counter, Histogram, Gauge


HTTP_ERROR_COUNT = Counter(
    "http_errors_total",
    "Total number of HTTP error responses",
    ["method", "endpoint", "status"],
)

TOTAL_REQUEST_COUNT = Counter(
    "http_requests_total", "Total number of requests", ["method", "endpoint", "status"]
)

REQUEST_LATENCY = Histogram(
    "http_server_requests_seconds",
    "Histogram of HTTP request durations in seconds",
    ["method", "endpoint"],
)

RESPONSE_SIZE = Counter(
    "http_response_throughput_bytes",
    "Total size of HTTP responses in bytes",
    ["method", "endpoint"],
)
CIRCUIT_BREAKER_STATE_GAUGE = Gauge(
    "circuit_breaker_state_gauge",
    "Current state of circuit breaker: 0=CLOSED, 1=HALF_OPEN, 2=OPEN",
    ["service"],
)
CIRCUIT_BREAKER_STATE = Counter(
    "circuit_breaker_state_total",
    "Total circuit breaker state transitions",
    ["service", "state"],
)

CIRCUIT_CALL_DURATION = Histogram(
    "circuit_breaker_call_duration_seconds",
    "Duration of circuit breaker protected calls (including retries)",
    ["service"],
    buckets=(0.25, 0.5, 1, 2, 5, 7.5, 10, 15, 20, 25, 30, 35, 40, 45),
)

TRANSFORM_DURATION = Histogram(
    name="data_transform_duration_ms",
    documentation="Duration of data transformation methods in milliseconds",
    labelnames=["method"],
    buckets=(5, 10, 25, 50, 75, 100, 200, 500, 1000),
)
