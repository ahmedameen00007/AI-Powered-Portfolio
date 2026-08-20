"""
graph/relationship_manager.py

Relationship management for OVI Knowledge Graph.

Manages semantic relationships between entities with full
metadata and provenance tracking.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime


class Relationship:
    """Represents a semantic relationship between two entities."""

    def __init__(
        self,
        source_id: str,
        relationship_type: str,
        target_id: str,
        source_dataset: str | None = None,
        source_record_id: str | None = None,
        confidence: float = 1.0,
        start_date: str | None = None,
        end_date: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.source_id = source_id
        self.relationship_type = relationship_type
        self.target_id = target_id
        self.source_dataset = source_dataset
        self.source_record_id = source_record_id
        self.confidence = confidence
        self.start_date = start_date
        self.end_date = end_date
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return (
            f"Relationship({self.source_id} "
            f"--[{self.relationship_type}]--> "
            f"{self.target_id})"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert relationship to dictionary representation."""
        return {
            "source_id": self.source_id,
            "relationship_type": self.relationship_type,
            "target_id": self.target_id,
            "source_dataset": self.source_dataset,
            "source_record_id": self.source_record_id,
            "confidence": self.confidence,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "metadata": self.metadata,
        }


class RelationshipManager:
    """
    Manages relationships in the knowledge graph.

    Supports:
    - Creating semantic relationships
    - Querying relationships by entity
    - Filtering by relationship type
    - Metadata and provenance tracking
    """

    def __init__(self):
        self.relationships: list[Relationship] = []
        
        # Indexes for efficient lookup
        self.by_source: dict[str, list[Relationship]] = {}
        self.by_target: dict[str, list[Relationship]] = {}
        self.by_type: dict[str, list[Relationship]] = {}

    def add_relationship(
        self,
        source_id: str,
        relationship_type: str,
        target_id: str,
        source_dataset: str | None = None,
        source_record_id: str | None = None,
        confidence: float = 1.0,
        start_date: str | None = None,
        end_date: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Relationship:
        """
        Add a relationship to the graph.

        Args:
            source_id: Source entity ID
            relationship_type: Semantic relationship type
            target_id: Target entity ID
            source_dataset: Dataset this relationship came from
            source_record_id: Record ID in source dataset
            confidence: Confidence score (0-1)
            start_date: Start date for temporal relationships
            end_date: End date for temporal relationships
            metadata: Additional metadata

        Returns:
            Created Relationship instance
        """
        relationship = Relationship(
            source_id=source_id,
            relationship_type=relationship_type,
            target_id=target_id,
            source_dataset=source_dataset,
            source_record_id=source_record_id,
            confidence=confidence,
            start_date=start_date,
            end_date=end_date,
            metadata=metadata,
        )

        self.relationships.append(relationship)

        # Update indexes
        if source_id not in self.by_source:
            self.by_source[source_id] = []
        self.by_source[source_id].append(relationship)

        if target_id not in self.by_target:
            self.by_target[target_id] = []
        self.by_target[target_id].append(relationship)

        if relationship_type not in self.by_type:
            self.by_type[relationship_type] = []
        self.by_type[relationship_type].append(relationship)

        return relationship

    def get_relationships_from(
        self,
        entity_id: str,
        relationship_type: str | None = None,
    ) -> list[Relationship]:
        """
        Get all relationships where entity is the source.

        Args:
            entity_id: Source entity ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of matching relationships
        """
        relationships = self.by_source.get(entity_id, [])

        if relationship_type:
            relationships = [
                r for r in relationships
                if r.relationship_type == relationship_type
            ]

        return relationships

    def get_relationships_to(
        self,
        entity_id: str,
        relationship_type: str | None = None,
    ) -> list[Relationship]:
        """
        Get all relationships where entity is the target.

        Args:
            entity_id: Target entity ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of matching relationships
        """
        relationships = self.by_target.get(entity_id, [])

        if relationship_type:
            relationships = [
                r for r in relationships
                if r.relationship_type == relationship_type
            ]

        return relationships

    def get_all_relationships(
        self,
        entity_id: str,
        relationship_type: str | None = None,
    ) -> list[Relationship]:
        """
        Get all relationships involving an entity (as source or target).

        Args:
            entity_id: Entity ID
            relationship_type: Optional filter by relationship type

        Returns:
            List of matching relationships
        """
        from_rels = self.get_relationships_from(entity_id, relationship_type)
        to_rels = self.get_relationships_to(entity_id, relationship_type)

        return from_rels + to_rels

    def get_by_type(self, relationship_type: str) -> list[Relationship]:
        """
        Get all relationships of a specific type.

        Args:
            relationship_type: Relationship type

        Returns:
            List of matching relationships
        """
        return self.by_type.get(relationship_type, [])

    def get_neighbors(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        direction: str = "outgoing",
    ) -> list[str]:
        """
        Get neighboring entity IDs.

        Args:
            entity_id: Source entity ID
            relationship_type: Optional filter by relationship type
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of neighboring entity IDs
        """
        neighbors = []

        if direction in ("outgoing", "both"):
            outgoing = self.get_relationships_from(entity_id, relationship_type)
            neighbors.extend([r.target_id for r in outgoing])

        if direction in ("incoming", "both"):
            incoming = self.get_relationships_to(entity_id, relationship_type)
            neighbors.extend([r.source_id for r in incoming])

        return list(set(neighbors))  # Remove duplicates

    def relationship_count(self, relationship_type: str | None = None) -> int:
        """
        Count relationships, optionally by type.

        Args:
            relationship_type: Optional type filter

        Returns:
            Number of relationships
        """
        if relationship_type:
            return len(self.by_type.get(relationship_type, []))
        return len(self.relationships)

    def get_relationship_types(self) -> list[str]:
        """Get all relationship types in the graph."""
        return list(self.by_type.keys())
