"""Pydantic models for structured data in MakeItReal."""

from pydantic import BaseModel, Field


class ProductIdea(BaseModel):
    """Structured representation of a product idea."""

    raw_idea: str = Field(..., description="Original user input for the idea")
    problem_statement: str = Field(..., description="Clear problem this product solves")
    target_users: list[str] = Field(..., description="Primary user segments")
    value_proposition: str = Field(..., description="Core value delivered to users")


class MarketAnalysis(BaseModel):
    """Market research and competitive analysis."""

    market_size: str = Field(..., description="Assessment of total addressable market")
    competitors: list[dict[str, str]] = Field(
        ..., description="Key competitors with name and description"
    )
    opportunities: list[str] = Field(..., description="Market opportunities identified")
    risks: list[str] = Field(..., description="Market and competitive risks")


class CurationResult(BaseModel):
    """Complete output from the Idea Curator agent."""

    product_idea: ProductIdea = Field(..., description="Structured product concept")
    market_analysis: MarketAnalysis = Field(..., description="Market and competitive insights")
    recommended_features: list[str] = Field(
        ..., description="Priority features for initial implementation"
    )
    next_steps: list[str] = Field(..., description="Actionable next steps for validation")
