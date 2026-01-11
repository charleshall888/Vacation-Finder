from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite+aiosqlite:///./vacation_finder.db"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Default Search Configuration
    default_origin_city: str = "Athens"
    default_origin_state: str = "GA"
    default_max_distance_miles: int = 400
    default_min_bedrooms: int = 7
    default_max_bedrooms: int = 9
    default_max_price_per_week: float = 15000.0
    default_max_beach_walk_minutes: int = 10

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
