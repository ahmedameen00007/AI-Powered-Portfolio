"""
schemas/education.py

Pydantic schemas for OVI educational information.
"""

from __future__ import annotations

from pydantic import Field

from schemas.base import OVISchema


class GPA(OVISchema):
    """Represents Ahmed's academic GPA across university years."""

    scale: str

    year_1: float | None = None
    year_2: float | None = None
    year_3: float | None = None
    year_4: float | None = None


class Thesis(OVISchema):
    """Represents the current thesis status."""

    status: str


class AcademicProject(OVISchema):
    """Represents a project completed as part of academic study."""

    name: str
    description: str
    technologies: list[str] = Field(default_factory=list)


class Education(OVISchema):
    """
    Canonical representation of Ahmed's academic education.
    """

    degree: str
    university: str
    faculty: str
    department: str

    major: str
    minor: str | None = None

    academic_level: str
    graduation_date: str

    gpa: GPA

    academic_achievements: list[str] = Field(default_factory=list)

    thesis: Thesis | None = None

    academic_projects: list[AcademicProject] = Field(
        default_factory=list
    )

    academic_interests: list[str] = Field(default_factory=list)
