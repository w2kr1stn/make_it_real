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


class UserStory(BaseModel):
    """INVEST-compliant user story for product development."""

    title: str = Field(..., description="User story title in 'As a... I want... So that...' format")
    description: str = Field(..., description="Detailed user story description")
    acceptance_criteria: list[str] = Field(..., description="Testable acceptance criteria")
    definition_of_done: list[str] = Field(..., description="Definition of done checklist")
    priority: str = Field(..., description="Priority level: high, medium, low")
    estimate: str = Field(default="", description="Story point estimate or effort estimation")


class PRDSection(BaseModel):
    """Individual section of a Product Requirements Document."""

    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content")
    subsections: list["PRDSection"] = Field(default=[], description="Nested subsections")


class TechnicalSpec(BaseModel):
    """Complete technical specification generated from curated idea."""

    press_release: dict[str, str] = Field(..., description="Amazon Working Backwards press release")
    faq: dict[str, list[str]] = Field(..., description="Internal and customer FAQs")
    user_stories: list[UserStory] = Field(..., description="INVEST-compliant user stories")
    technical_requirements: list[str] = Field(..., description="Core technical requirements")
    success_metrics: list[str] = Field(..., description="Key success metrics and KPIs")
    timeline: str = Field(..., description="Estimated development timeline")
    sections: list[PRDSection] = Field(default=[], description="Additional PRD sections")


# Enable forward references for recursive PRDSection model
PRDSection.model_rebuild()
