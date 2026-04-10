from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "SignalRank"
    app_env: str = "local"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    api_key: str = "change-me"

    postgres_url: str = "postgresql+psycopg2://postgres:postgres@postgres:5432/signalrank"
    mongo_url: str = "mongodb://mongo:27017"
    mongo_db_name: str = "signalrank"

    enrichment_api_url: str = "https://example.com/analyze"
    enrichment_api_key: str = "replace-me"
    request_timeout_seconds: int = 20

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
