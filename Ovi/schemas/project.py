"""
schemas/project.py

Pydantic schemas for OVI projects.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import BaseEntity


class Project(BaseEntity):
    """
    Canonical representation of a personal, professional,
    or academic project.
    """

    name: str
    title: str
    description: str

    technologies: list[str] = Field(
        default_factory=list
    )

    domains: list[str] = Field(
        default_factory=list
    )
