from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = "dev-secret-change-in-production"
    email_address: str = ""
    email_password: str = ""
    database_url: str = "sqlite:///./jobs.db"
    gemini_api_key: str = ""

    class Config:
        env_file = ".env"

settings = Settings()