from functools import lru_cache
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    jwt_secret: str
    jwt_algorithm: str
    jwt_lifetime_sec: int

    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str = "5432"
    postgres_db: str

    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str
    redis_user: str = "default"

    @computed_field  # type: ignore
    @property
    def postgres_url(self) -> str:
        return f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @computed_field  # type: ignore
    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_user}:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_env_settings() -> "EnvSettings":
    return EnvSettings()  # type: ignore
