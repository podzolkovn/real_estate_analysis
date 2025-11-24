import time
import asyncio
from functools import wraps

from app.core import logger
from app.core.metrics import TRANSFORM_DURATION


def track_duration(sla_ms: int = 50, label: str = None):
    """
    Декоратор для измерения времени выполнения асинхронной функции и логирования,
    если время выполнения превышает заданное SLA (в миллисекундах).

    Также отправляет метрику времени выполнения в систему мониторинга Prometheus
    через `TRANSFORM_DURATION`.

    :param sla_ms: Пороговое значение (в миллисекундах), при превышении которого будет выведено предупреждение в лог. По умолчанию 50 мс.
    :param label: Произвольная метка для метода (используется в логах и метриках).
                  Если не указана, будет использовано полное имя функции (`__qualname__`).

    :raises TypeError: Если декоратор применён к неасинхронной функции.

    :return: Обёрнутая асинхронная функция с измерением и логированием времени выполнения.
    """

    def decorator(func):
        if not asyncio.iscoroutinefunction(func):
            raise TypeError(
                "track_duration decorator must be applied to async functions."
            )

        @wraps(func)
        async def wrapper(*args, **kwargs):
            method_name = label or func.__qualname__
            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                TRANSFORM_DURATION.labels(method=method_name).observe(duration_ms)
                if duration_ms > sla_ms:
                    logger.warning(
                        f"[SLA] {method_name} took {duration_ms:.2f}ms (exceeds {sla_ms}ms)"
                    )
                else:
                    logger.debug(f"[SLA] {method_name} took {duration_ms:.2f}ms")

        return wrapper

    return decorator
