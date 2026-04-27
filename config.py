from pydantic_settings import BaseSettings, SettingsConfigDict


class WebAppSettings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        env_file_encoding="utf-8"
    )

    def get_db_url(self):
        return self.database_url


settings = WebAppSettings()
