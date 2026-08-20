"""
schemas/chunk.py

Pydantic schema for OVI retrieval chunks.

A chunk is the retrieval unit produced from a single processed
entity (or, for entity-less files, a single processed record).
It preserves the canonical structured content alongside a
deterministic serialized text representation used only for
embedding generation.
"""

from __future__ import annotations

from typing import Any

from pydantic import Field

from schemas.base import OVISchema


class Chunk(OVISchema):
    """
    Canonical representation of a single retrieval chunk.
    """

    chunk_id: str
    entity_id: str
    entity_type: str

    source_file: str

    content: dict[str, Any]

    text: str = Field(
        description=(
            "Deterministic serialized text representation of "
            "'content', used only as embedding input."
        )
    )

    metadata: dict[str, Any] = Field(default_factory=dict)
