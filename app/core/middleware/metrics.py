import time
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware

from app.core import metrics


class RequestMetricsMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):
        endpoint = request.url.path
        if endpoint.startswith("api/"):
            method = request.method
            start_time = time.time()
            response = await call_next(request)
            duration = time.time() - start_time
            status = str(response.status_code)

            metrics.REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(
                duration
            )
            metrics.TOTAL_REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status=status
            ).inc()

            if 400 <= int(status) < 600:
                metrics.HTTP_ERROR_COUNT.labels(
                    method=method, endpoint=endpoint, status=status
                ).inc()

            if (
                hasattr(response, "body_iterator")
                and response.body_iterator is not None
            ):
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                metrics.RESPONSE_SIZE.labels(method=method, endpoint=endpoint).inc(
                    len(body)
                )
                response.body_iterator = iterate_in_threadpool(iter([body]))

            return response
        else:
            return await call_next(request)
