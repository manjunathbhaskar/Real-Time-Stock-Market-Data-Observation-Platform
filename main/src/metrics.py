from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from functools import wraps

# Core metrics to monitor the FastAPI application and external API calls (yfinance)

# Counter for tracking the total number of requests by endpoint
REQUEST_COUNT = Counter(
    'market_data_requests_total',
    'Total number of requests to the API, broken down by endpoint',
    ['endpoint']
)

# Histogram for tracking the latency (response time) of requests by endpoint
REQUEST_LATENCY = Histogram(
    'request_latency_seconds',
    'Latency of API requests in seconds, broken down by endpoint',
    ['endpoint']
)

# Histogram for tracking the duration of yfinance API calls by operation type
YFINANCE_CALLS = Histogram(
    'yfinance_api_duration_seconds',
    'Duration of yfinance API calls in seconds, broken down by operation type',
    ['operation']
)

# Counter for tracking the total number of requests for specific stock symbols
SYMBOL_REQUESTS = Counter(
    'stock_symbol_requests_total',
    'Total number of requests for stock symbols, broken down by symbol',
    ['symbol']
)

# Counter for tracking errors, grouped by error type (exception names)
ERROR_COUNT = Counter(
    'market_data_errors_total',
    'Total number of errors, grouped by error type (exception names)',
    ['error_type']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to collect request metrics, including counting requests,
    measuring latency, and tracking errors."""
    
    async def dispatch(self, request: Request, call_next):
        """Intercepts incoming requests to measure performance and collect metrics."""
        start_time = time.time()
        endpoint = request.url.path

        # Increment request count for the current endpoint
        REQUEST_COUNT.labels(endpoint=endpoint).inc()

        try:
            # Process the request and calculate duration
            response = await call_next(request)
            duration = time.time() - start_time

            # Record request latency
            REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
            return response
        except Exception as e:
            # Track the error occurrence
            ERROR_COUNT.labels(error_type=type(e).__name__).inc()
            raise


def track_symbol_request(symbol: str):
    """Track requests made for specific stock symbols."""
    SYMBOL_REQUESTS.labels(symbol=symbol).inc()


def track_yfinance_operation(operation_name: str):
    """Decorator to time yfinance API operations, and record their duration."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Record the duration of the operation using the yfinance operation histogram
            with YFINANCE_CALLS.labels(operation=operation_name).time():
                return await func(*args, **kwargs)
        return wrapper
    return decorator


async def metrics_endpoint():
    """Endpoint exposed to Prometheus for scraping metrics."""
    return Response(
        generate_latest(),  # Prometheus client generates the latest metrics in a format Prometheus can scrape
        media_type=CONTENT_TYPE_LATEST
    )
