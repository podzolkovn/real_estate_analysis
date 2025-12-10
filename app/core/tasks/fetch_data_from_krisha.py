from app.infrastructure.db.repositories.building_analisation import (
    BuildingAnalisationModelRepository,
)
from app.infrastructure.db.sessions import async_session_maker
from app.infrastructure.krisha_analitic import fetch_krisha_data


async def fetch_krisha() -> None:
    result: list[dict] = await fetch_krisha_data()
    async with async_session_maker() as session:
        build_analise_repo: BuildingAnalisationModelRepository = (
            BuildingAnalisationModelRepository(session)
        )
        await build_analise_repo.upsert_many(result)
