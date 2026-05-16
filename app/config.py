from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WebAppSettings(BaseSettings):
    database_url: str = Field(alias="POSTGRES_CONNECTION_STRING")
    api_key: str = Field(default="secret", alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file="../.env",
        extra="ignore",
        env_file_encoding="utf-8",
        populate_by_name=True,
    )

    def get_db_url(self):
        return self.database_url

    def get_return_api_key(self):
        return self.api_key


settings = WebAppSettings()
