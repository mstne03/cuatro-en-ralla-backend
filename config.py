from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Local dev: path to JSON file. Production: leave empty and set FIREBASE_SERVICE_ACCOUNT_JSON.
    firebase_service_account_path: str = "./firebase-service-account.json"
    # Full JSON string of the service account (takes precedence over path when set).
    firebase_service_account_json: str = ""
    allowed_origins: list[str] = ["http://localhost:4200"]


settings = Settings()
