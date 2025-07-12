"""Pydantic models for structured data in MakeItReal."""

from pydantic import BaseModel, Field


class ProductIdea(BaseModel):
    """Structured representation of a product idea."""

    raw_idea: str = Field(..., description="Original user input for the idea")
    problem_statement: str = Field(..., description="Clear problem this product solves")
    target_users: list[str] = Field(..., description="Primary user segments")
    value_proposition: str = Field(..., description="Core value delivered to users")


class Competitor(BaseModel):
    """Information about a competitor."""

    name: str = Field(..., description="Competitor name")
    description: str = Field(..., description="Brief description of the competitor")


class MarketAnalysis(BaseModel):
    """Market research and competitive analysis."""

    market_size: str = Field(..., description="Assessment of total addressable market")
    competitors: list[Competitor] = Field(
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
    estimate: str = Field(default="TBD", description="Story point estimate or effort estimation")


class PressRelease(BaseModel):
    """Press release section of technical spec."""

    headline: str = Field(..., description="Press release headline")
    subtitle: str = Field(..., description="Press release subtitle")
    intro: str = Field(..., description="Introduction paragraph")
    problem: str = Field(..., description="Problem statement")
    solution: str = Field(..., description="Solution description")
    leader_quote: str = Field(..., description="Quote from company leader")
    how_it_works: str = Field(..., description="How the product works")
    customer_quote: str = Field(..., description="Quote from a customer")
    call_to_action: str = Field(..., description="Call to action")


class FAQ(BaseModel):
    """FAQ section of technical spec."""

    internal: list[str] = Field(..., description="Internal Q&A pairs")
    customer: list[str] = Field(..., description="Customer Q&A pairs")


class TechnicalSpec(BaseModel):
    """Complete technical specification generated from curated idea."""

    press_release: PressRelease = Field(..., description="Amazon Working Backwards press release")
    faq: FAQ = Field(..., description="Internal and customer FAQs")
    user_stories: list[UserStory] = Field(..., description="INVEST-compliant user stories")
    technical_requirements: list[str] = Field(..., description="Core technical requirements")
    success_metrics: list[str] = Field(..., description="Key success metrics and KPIs")
    timeline: str = Field(..., description="Estimated development timeline")


class EvaluationResult(BaseModel):
    """Complete evaluation output from the Evaluator agent."""

    feasibility_score: float = Field(
        ..., ge=0.0, le=1.0, description="Technical feasibility score (0.0-1.0)"
    )
    resource_score: float = Field(
        ..., ge=0.0, le=1.0, description="Resource availability score (0.0-1.0)"
    )
    timeline_score: float = Field(
        ..., ge=0.0, le=1.0, description="Timeline realism score (0.0-1.0)"
    )
    risk_assessment: str = Field(..., description="Overall risk assessment summary")
    recommendations: list[str] = Field(
        ..., description="Actionable recommendations for implementation"
    )
    go_no_go: str = Field(
        ..., pattern="^(GO|NO_GO)$", description="Final recommendation: GO or NO_GO"
    )
