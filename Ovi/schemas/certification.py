"""
schemas/certification.py

Pydantic schemas for OVI courses, certifications,
specializations, and training programs.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseEntity, OVISchema


class Verification(OVISchema):
    """Represents online verification information for a credential."""

    id: str
    url: str


class IncludedCourse(OVISchema):
    """
    Represents a course included inside a certification or
    training program.

    Some raw records only provide the course title, while
    others also provide the number of hours.
    """

    title: str
    hours: float | None = None


class Certification(BaseEntity):
    """
    Canonical representation of a course, certification,
    specialization, or training program.
    """

    title: str
    type: str

    provider: str
    platform: str | None = None

    completion_date: str | None = None
    start_date: str | None = None
    end_date: str | None = None

    duration: str | None = None
    duration_hours: float | None = None

    certificate_id: str | None = None

    verification: Verification | None = None

    included_courses: list[IncludedCourse] = Field(
        default_factory=list
    )

    topics: list[str] = Field(default_factory=list)
