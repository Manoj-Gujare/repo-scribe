from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # AWS Bedrock
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"

    # GitHub
    GITHUB_TOKEN: str = ""

    # Tavily
    TAVILY_API_KEY: str = ""

    # Blog config
    BLOG_STYLE: str = "medium"
    BLOG_TONE: str = "technical"
    MAX_BLOG_WORDS: int = 1500

    # App
    OUTPUT_DIR: str = "output"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
