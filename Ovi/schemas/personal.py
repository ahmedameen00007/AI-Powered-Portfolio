"""
schemas/personal.py

Pydantic schemas for OVI personal-profile information.

This module defines the canonical structure of Ahmed's
personal information after processing.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from schemas.base import OVISchema


class Language(OVISchema):
    """Represents a language and the user's proficiency level."""

    language: str
    proficiency: str


class BasicInfo(OVISchema):
    """
    Basic information about Ahmed.
    """

    name: str
    full_name: str
    birth_date: str
    city: str
    specialist: str


class PersonalInfo(OVISchema):
    """
    Personal information about Ahmed.
    """

    bio: str

    interests: list[str] = Field(default_factory=list)
    hobbies: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)

    personality: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)

    languages: list[Language] = Field(default_factory=list)

    areas_of_interest: list[str] = Field(default_factory=list)
    career_interests: list[str] = Field(default_factory=list)
    learning_interests: list[str] = Field(default_factory=list)

    personal_preferences: list[str] = Field(default_factory=list)
    fun_facts: list[str] = Field(default_factory=list)


class PersonalProfile(OVISchema):
    """
    Canonical personal profile for OVI.

    Combines the information currently stored across:
        - basic_info.json
        - personal_info.json
    """

    # Basic Information
    name: str
    full_name: str
    birth_date: str
    city: str
    specialist: str

    # Personal Information
    bio: str

    interests: list[str] = Field(default_factory=list)
    hobbies: list[str] = Field(default_factory=list)
    goals: list[str] = Field(default_factory=list)

    personality: list[str] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)

    languages: list[Language] = Field(default_factory=list)

    areas_of_interest: list[str] = Field(default_factory=list)
    career_interests: list[str] = Field(default_factory=list)
    learning_interests: list[str] = Field(default_factory=list)

    personal_preferences: list[str] = Field(default_factory=list)
    fun_facts: list[str] = Field(default_factory=list)
