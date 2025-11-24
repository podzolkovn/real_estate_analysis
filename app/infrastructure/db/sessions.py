from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)

from app.core.settings import settings

engine: AsyncEngine = create_async_engine(
    url=settings.DB_URL,
    pool_pre_ping=True,
    isolation_level="READ COMMITTED",
    future=True,
    connect_args={"timeout": 60},
    echo=False,
)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide an asynchronous SQLAlchemy session.
    Ensures proper management of session lifecycle.
    """
    async with async_session_maker() as session:
        yield session
