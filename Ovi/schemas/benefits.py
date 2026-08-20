"""
schemas/benefits.py

Pydantic schemas for OVI professional capabilities,
strengths, career direction, and value proposition.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import OVISchema


class CareerDirection(OVISchema):
    """Represents Ahmed's professional and career direction."""

    primary: str

    secondary: list[str] = Field(
        default_factory=list
    )

    long_term_goal: str


class Benefits(OVISchema):
    """
    Canonical representation of Ahmed's professional value,
    technical strengths, problem-solving capabilities,
    and career direction.
    """

    professional_value: list[str] = Field(
        default_factory=list
    )

    technical_strengths: list[str] = Field(
        default_factory=list
    )

    problem_solving_capabilities: list[str] = Field(
        default_factory=list
    )

    domain_exposure: list[str] = Field(
        default_factory=list
    )

    professional_advantages: list[str] = Field(
        default_factory=list
    )

    learning_and_growth: list[str] = Field(
        default_factory=list
    )

    collaboration_value: list[str] = Field(
        default_factory=list
    )

    career_direction: CareerDirection

    unique_value_proposition: str
