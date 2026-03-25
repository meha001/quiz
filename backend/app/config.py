from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Основные настройки приложения
    app_name: str = "College Project API"
    app_env: str = "development"
    debug: bool = True

    # CORS origin'ы задаются одной строкой через запятую в .env
    cors_origins: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    def parsed_cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
