"""
Configuration settings for AI Work OS.

Uses environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # AI Model Configuration
    ai_provider: str = "openai"  # openai, anthropic, openrouter
    ai_model: str = "gpt-4"
    ai_api_key: Optional[str] = None
    ai_temperature: float = 0.7
    ai_max_tokens: int = 4096

    # OpenRouter (for model independence)
    openrouter_api_key: Optional[str] = None
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # Work Graph
    work_graph_db_path: str = "data/work_graph.json"

    # Memory
    memory_db_path: str = "data/memory.json"
    max_memory_items: int = 1000

    # Permissions
    default_permission_level: str = "safe"  # safe, approval, high_risk

    # Verification
    verification_enabled: bool = True
    auto_fix_threshold: float = 0.8

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()