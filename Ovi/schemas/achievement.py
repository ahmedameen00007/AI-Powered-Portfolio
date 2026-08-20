"""
schemas/achievement.py

Pydantic schemas for OVI achievements, activities,
competitions, and recognitions.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseEntity, OVISchema


class AchievementCertificate(OVISchema):
    """Represents a certificate associated with an achievement."""

    type: str
    issuer: str
    reference: str | None = None
    signatories: list[str] = Field(default_factory=list)


class Achievement(BaseEntity):
    """
    Canonical representation of an achievement,
    activity, competition, or participation.
    """

    name: str
    type: str

    organizer: str

    event_series: str | None = None
    edition: str | None = None

    date: str | None = None
    year: int | None = None

    field: str | None = None

    participation: str

    achievement: str | None = None
    recognition: str | None = None

    description: str

    certificate: AchievementCertificate | None = None
