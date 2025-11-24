import tomllib

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


def get_version_from_pyproject(path="pyproject.toml") -> str:
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return data["tool"]["poetry"]["version"]


class Settings(BaseSettings):
    """
    Configuration class for application settings, including database and JWT secrets, loaded from environment variables.
    """

    version: str = get_version_from_pyproject()

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    LOCALE_DIR: str = "locales"
    DEFAULT_LOCALE: str = "en"

    @property
    def DB_URL(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:"
            f"{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    class Config:
        env_file: str = ".env"
        extra: str = "ignore"


settings: Settings = Settings()
