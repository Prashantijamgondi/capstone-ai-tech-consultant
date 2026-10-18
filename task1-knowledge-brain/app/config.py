"""Configuration settings for Task 1: Knowledge Brain."""
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Knowledge Brain API"
    app_version: str = "1.0.0"
    host: str = "127.0.0.1"
    port: int = 8001
    
    # Sitemap & Crawler settings
    sitemap_url: str = "https://support.brilliantdirectories.com/support/sitemap.xml"
    request_delay_seconds: float = 0.5
    max_retries: int = 3
    retry_backoff_factor: float = 1.5
    user_agent: str = "AITechConsultant-Bot/1.0 (+http://localhost/bot)"
    
    # Model settings
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    default_model: str = "claude-3-5-sonnet-20241022"
    fast_model: str = "claude-3-5-haiku-20241022"
    
    # Storage settings
    data_dir: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
    manifest_path: str = os.path.join(data_dir, "manifests", "manifest.json")
    articles_dir: str = os.path.join(data_dir, "articles")
    images_dir: str = os.path.join(data_dir, "images")
    database_path: str = os.path.join(data_dir, "knowledge_brain.db")

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()
