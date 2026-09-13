import os
import secrets
import logging
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List, Union

logger = logging.getLogger("kalvettu.config")

class Settings(BaseSettings):
    ENVIRONMENT: str = "production"
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    SUPABASE_DB_URL: Optional[str] = None
    KALVETTU_DB_URL: Optional[str] = "sqlite:///./kalvettu.db"
    
    # AI API Keys
    KALVETTU_AI_GEMINI_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    CEREBRAS_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    
    # Security: No hardcoded fallback secret in repository
    ADMIN_API_KEY: Optional[str] = None
    ALLOWED_HOSTS: Union[str, List[str]] = ["*"]
    CORS_ORIGINS: Union[str, List[str]] = [
        "https://silaimozhi.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173"
    ]
    MAX_UPLOAD_SIZE_MB: int = 10

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",") if host.strip()]
        return v

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Secure fallback: if ADMIN_API_KEY is not defined in environment, generate an ephemeral cryptographic token
if not settings.ADMIN_API_KEY:
    settings.ADMIN_API_KEY = secrets.token_urlsafe(32)
    logger.info("ADMIN_API_KEY not found in environment; generated ephemeral cryptographic key for session.")

