"""LLM integration module for simple OpenAI calls."""

from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for OpenAI integration."""

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = "https://api.openai.com/v1"

    class Config:
        env_file = ".env"


def simple_llm_call(idea: str) -> str:
    """Execute basic LLM call without agents.

    Args:
        idea: Product idea to analyze

    Returns:
        Structured analysis from the LLM
    """
    settings = Settings()

    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
    )

    prompt = f"""Analyze this product idea and provide structured feedback:

Product Idea: {idea}

Please provide analysis in this format:

## Product Concept
- Brief summary of the idea
- Target audience
- Core value proposition

## Market Potential
- Market size assessment
- Key competitors
- Differentiation opportunities

## Technical Considerations
- Recommended technology stack
- Development complexity (1-10 scale)
- Estimated timeline

## Next Steps
- 3 immediate actions to validate the idea
- Key risks to investigate

Keep the analysis concise but actionable."""

    response = llm.invoke(prompt)
    return response.content
