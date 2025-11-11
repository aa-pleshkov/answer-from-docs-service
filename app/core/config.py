from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Хранение настроек приложения.
    """
    
    # Настройки FastAPI приложения
    APP_TITLE: str = "Answer from Docs Service"
    APP_VERSION: str = "1.0.0"
    
    # Настройки сервера
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Настройки подключения к LLM по API
    LLM_API_KEY: str
    LLM_MODEL: str = "qwen3-max"
    LLM_API_BASE: str = "https://bothub.chat/api/v2/openai/v1"
    
    # Пути
    PATH_TO_SYSTEM_PROMPT: str = "prompts/system.txt"
    PATH_TO_ANSWER_SCHEMA: str = "schemas/answer_schema.json"
    FILES_JSON_PATH: str = "storage/files.json"
    QUESTIONS_JSON_PATH: str = "storage/questions.json"

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


# Экземпляр настроек
settings = Settings()