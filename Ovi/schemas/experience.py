"""
schemas/experience.py

Pydantic schemas for OVI professional and training experience.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseEntity, OVISchema


class Organization(OVISchema):
    """Represents an organization associated with an experience."""

    name: str
    type: str


class Experience(BaseEntity):
    """
    Canonical representation of a professional or training experience.
    """

    organization: Organization

    role: str
    employment_type: str

    start_date: str
    end_date: str | None = None

    status: str

    duration_hours: float | None = None
    overall_score: float | None = None

    responsibilities: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
