"""
schemas/base.py

Base Pydantic models shared across OVI schemas.

This module contains only reusable structural components.
Domain-specific models belong in their respective schema modules.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class OVISchema(BaseModel):
    """
    Base schema for all OVI data models.

    Provides common Pydantic configuration for the entire
    schema layer.
    """

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
    )


class BaseEntity(OVISchema):
    """
    Base model for identifiable OVI entities.
    """

    id: str

