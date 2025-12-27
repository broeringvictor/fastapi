from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ "
    Notes:
        - Criar banco via docker:
           docker run --name fastapi -e POSTGRES_PASSWORD=mysecretpassword -d postgres
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", E
    )

    # Database settings (defaults allow tests to run without .env)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    POSTGRES_HOST: str

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    AUTH_COOKIE_SECURE: bool
    AUTH_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
