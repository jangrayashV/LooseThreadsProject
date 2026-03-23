from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SQLALCHEMY_DB_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRATION_TIME: int
    ALGORITHM: str

    model_config = {"env_file": ".env"}

settings = Settings()