"""Pydantic models for aiask CLI input validation."""

from pydantic import BaseModel, field_validator


class QuestionInput(BaseModel):
    """Input validation for user questions."""

    message: str

    @field_validator("message")
    @classmethod
    def validate_message_length(cls, v: str) -> str:
        """Validate message is between 1 and 1000 characters."""
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message must be 1-1000 characters")
        return v


class AIResponse(BaseModel):
    """Response model for AI answers."""

    content: str
    tokens_used: int = 0
    latency_ms: int = 0
