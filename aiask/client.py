"""OpenAI client wrapper for aiask CLI."""

import time

from openai import APIError, AuthenticationError, OpenAI, RateLimitError

from .config import Settings
from .models import AIResponse


class AIClient:
    """OpenAI client wrapper with retry logic."""

    def __init__(self, settings: Settings, use_local: bool = False):
        """Initialize client with settings."""
        self.settings = settings
        base_url = "http://localhost:8080/v1" if use_local else settings.openai_base_url
        api_key = "local-key" if use_local else settings.openai_api_key

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def ask_question(self, question: str) -> AIResponse:
        """Send question to AI and get response."""
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[{"role": "user", "content": question}],
                max_tokens=500,
            )

            end_time = time.time()
            latency_ms = int((end_time - start_time) * 1000)

            content = response.choices[0].message.content or ""
            tokens_used = response.usage.total_tokens if response.usage else 0

            return AIResponse(content=content, tokens_used=tokens_used, latency_ms=latency_ms)

        except (AuthenticationError, RateLimitError, APIError) as e:
            raise e
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}") from e

    def ask_question_with_retry(self, question: str, max_retries: int = 3) -> AIResponse:
        """Ask question with exponential backoff retry for rate limits."""
        for attempt in range(max_retries):
            try:
                return self.ask_question(question)
            except RateLimitError:
                if attempt == max_retries - 1:
                    raise RuntimeError("Service busy, try later") from None
                wait_time = 2**attempt  # Exponential backoff: 1s, 2s, 4s
                time.sleep(wait_time)
            except Exception as e:
                raise e
