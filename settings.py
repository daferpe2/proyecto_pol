from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str 
    AES_KEY_BASE64: str

    class Config:
        env_file = ".env"

settings = Settings()



