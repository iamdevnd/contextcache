from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache
import os
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    app_name: str = "ContextCache"
    app_version: str = "1.0.0"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    
    # Database Settings
    arango_host: str = "localhost"
    arango_port: int = 8529
    arango_username: str = "root"
    arango_root_password: str
    arango_database: str = "contextcache"
    
    # Security Settings
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    admin_username: str = "admin"
    admin_password_hash: str
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000
    
    # NLP Settings
    spacy_model: str = "en_core_web_sm"
    embedding_model: str = "all-MiniLM-L6-v2"
    max_memory_items: int = 10000
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
