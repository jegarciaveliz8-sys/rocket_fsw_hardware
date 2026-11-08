from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_title: str = "ODYSSEY-1 Modular Mission Control Center"
    version: str = "1.3.0"
    database_url: str = "sqlite:///odyssey_telemetry.db"
    mqtt_broker_host: str = "localhost"
    ollama_host: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()
