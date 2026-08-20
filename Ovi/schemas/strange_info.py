"""
schemas/strange_info.py

Pydantic schemas for OVI's personal and miscellaneous information.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseEntity, OVISchema


class FavoriteAnime(OVISchema):
    """Represents Ahmed's favorite anime."""

    title: str
    preference_strength: str
    description: str


class FavoriteFood(BaseEntity):
    """Represents a ranked favorite food."""

    rank: int
    name: str


class PreTechInterest(OVISchema):
    """Represents an interest Ahmed had before entering technology."""

    interest: str
    importance: str
    description: str


class PreviousOccupation(BaseEntity):
    """Represents a previous occupation or activity."""

    role: str
    sequence: int
    status: str


class TrainingCareerStatus(OVISchema):
    """Represents Ahmed's current status regarding training careers."""

    status: str
    description: str


class PhysicalInfo(OVISchema):
    """Represents physical information."""

    height_cm: float
    weight_kg: float


class StrangeInfo(OVISchema):
    """
    Canonical representation of miscellaneous personal information
    that does not belong to the standard professional or academic
    dataset categories.
    """

    favorite_anime: FavoriteAnime

    favorite_foods: list[FavoriteFood] = Field(
        default_factory=list
    )

    pre_tech_interests: list[PreTechInterest] = Field(
        default_factory=list
    )

    previous_occupations_and_activities: list[PreviousOccupation] = Field(
        default_factory=list
    )

    training_career_status: TrainingCareerStatus

    physical_info: PhysicalInfo | None = None
