import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class ProjectConfig(BaseSettings):
    # database
    DATABASE_URI_FORMAT: str = "{db_engine}://{user}:{password}@{host}:{port}/{database}"
    DB_HOST: str = os.getenv("DB_HOST")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_ENGINE: str = os.getenv("DB_ENGINE")
    DB_NAME: str = os.getenv("DB_NAME")

    @property
    def DATABASE_URI(self) -> str:
        return self.DATABASE_URI_FORMAT.format(
            db_engine=self.DB_ENGINE,
            user=self.DB_USER,
            password=self.DB_PASSWORD,
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    @staticmethod
    def PROJECT_NAME() -> str:
        return "Biblioteca"

    @staticmethod
    def API_PREFIX() -> str:
        return "/api"

    @staticmethod
    def BACKEND_CORS_ORIGINS() -> list[str]:
        return ["*"]