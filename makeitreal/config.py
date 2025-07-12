"""Modern centralized configuration for MakeItReal using Pydantic v2."""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class OpenAISettings(BaseSettings):
    """Modern OpenAI configuration using Pydantic v2."""

    model_config = ConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"


# Global settings instance
openai_settings = OpenAISettings()
