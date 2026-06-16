import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    firebase_service_account_path: str = "./firebase-service-account.json"
    firebase_service_account_json: str = ""
    # Stored as a plain comma-separated string; parsed into a list via allowed_origins property.
    # In Render set ALLOWED_ORIGINS=https://your-frontend.onrender.com
    allowed_origins_raw: str = "http://localhost:4200"

    @property
    def allowed_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins_raw.split(",") if o.strip()]


settings = Settings(_env_file=".env")
