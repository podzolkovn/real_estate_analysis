from redis import Redis

from app.core import settings


def redis():
    return Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )


r = redis()
