from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_env: str = "dev"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    telegram_api_id: int
    telegram_api_hash: str
    telegram_bot_token: str

    encryption_key_base64: str
    api_token: str

    llm_provider: str = "openai"
    openai_api_key: str | None = None

    default_digest_hour: int = 8
    default_max_items: int = 15
    min_score: float = 0.4

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
