from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AviAI Backend"
    secret_key: str = "aviai-dev-secret"
    access_token_expire_minutes: int = 60 * 24 * 7
    use_mock_data: bool = True
    database_url: str = (
        "mysql+pymysql://root:123456@127.0.0.1:3306/aviai?charset=utf8mb4"
    )
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"
    deepseek_vision_model: str = "deepseek-chat"
    deepseek_timeout_seconds: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
