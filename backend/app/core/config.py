from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Media Factory"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./media_factory.db"
    
    # OpenRouter LLM
    OPENROUTER_API_KEY: Optional[str] = None
    DEFAULT_LLM_MODEL: str = "anthropic/claude-3.5-sonnet"
    
    # Maya TTS Service Endpoint
    MAYA3_API_BASE: str = "http://localhost:8080/v1"
    MAYA3_ENABLED: bool = True
    
    # Storage
    STORAGE_LOCAL_DIR: str = "./storage"
    
    # Cost Guardrails (USD per finished minute)
    MAX_COST_PER_MINUTE_USD: float = 0.20
    DEFAULT_EPISODE_BUDGET_USD: float = 2.00

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
