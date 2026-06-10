from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "two_factor_auth"
    JWT_SECRET_KEY: str = "super-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60
    TOTP_ISSUER: str = "TwoFactorApp"
    RP_NAME: str = "TwoFactorApp"
    RP_ID: str = "localhost"
    RP_ORIGIN: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


settings = Settings()
