"""Configuration settings for AI Work OS.

Uses environment variables with sensible defaults and validation.
Industrial-grade: validates all inputs, supports multiple environments.
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, field_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8",
                              populate_by_name=True)

    # --- AI Model Configuration ---
    ai_provider: str = "openai"  # openai, anthropic, openrouter
    ai_model: str = "gpt-4"
    ai_api_key: Optional[str] = Field(None, alias="OPENROUTER_API_KEY")
    ai_temperature: float = Field(0.7, ge=0.0, le=2.0)
    ai_max_tokens: int = Field(4096, ge=1, le=8192)

    # --- OpenRouter (for model independence) ---
    openrouter_api_key: Optional[str] = Field(None, alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = "https://openrouter.ai/api/v1"

    # --- Work Graph ---
    work_graph_db_path: str = "data/work_graph.json"

    # --- Memory ---
    memory_db_path: str = "data/memory.json"
    max_memory_items: int = Field(1000, ge=100, le=10000)

    # --- Permissions ---
    default_permission_level: str = "safe"  # safe, approval, high_risk

    # --- Verification ---
    verification_enabled: bool = True
    auto_fix_threshold: float = Field(0.8, ge=0.0, le=1.0)

    # --- Logging ---
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # --- System ---
    version: str = "2.0.0"
    environment: str = "development"  # development, production, testing

    @field_validator('ai_provider')
    @classmethod
    def validate_provider(cls, v: str) -> str:
        allowed = ['openai', 'anthropic', 'openrouter']
        if v not in allowed:
            raise ValueError(f'ai_provider must be one of: {allowed}')
        return v

    @field_validator('ai_temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if v < 0.0 or v > 2.0:
            raise ValueError('ai_temperature must be between 0.0 and 2.0')
        return v

    @field_validator('ai_max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: int) -> int:
        if v < 1 or v > 8192:
            raise ValueError('ai_max_tokens must be between 1 and 8192')
        return v

    @field_validator('auto_fix_threshold')
    @classmethod
    def validate_auto_fix_threshold(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError('auto_fix_threshold must be between 0.0 and 1.0')
        return v

    @property
    def is_configured(self) -> bool:
        """Check whether an API key is available for AI calls."""
        return self.openrouter_api_key is not None

    @property
    def effective_api_key(self) -> Optional[str]:
        """Return the API key to use for the active provider."""
        return self.openrouter_api_key or self.ai_api_key


settings = Settings()