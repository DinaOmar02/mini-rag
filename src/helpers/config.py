from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_CHUNLK_SIZE: int

    MONGODB_URL: str
    MONGODB_DATABASE:str

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    GENERATION_MODEL_ID: str
    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_SIZE: int

    DEFAULT_INPUT_MAX_CHARACTERS: int
    DEFAULT_GENERATION_MAX_OUTPUT: int
    DEFAULT_GENERATION_TEMPERATURE: float

    COHERE_API_KEY: str

    OPENAI_URL: str
    OPENAI_API_KEY: str

    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str

    PRIMARY_LANG: str = "en"
    DEFAULT_LANG: str = "en"

    class Config:
        env_file = ".env"


def get_settings():
    return Settings()

