"""
graph/entity_resolver.py

Entity resolution for OVI Knowledge Graph.

Determines whether different entity references represent the same
real-world entity using deterministic rules.
"""

from __future__ import annotations

from typing import Any
import re


class Entity:
    """Represents a canonical entity in the knowledge graph."""

    def __init__(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        aliases: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        self.id = entity_id
        self.type = entity_type
        self.name = name
        self.aliases = aliases or []
        self.attributes = attributes or {}

    def __repr__(self) -> str:
        return f"Entity(id={self.id}, type={self.type}, name={self.name})"

    def to_dict(self) -> dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            "id": self.id,
            "type": self.type,
            "name": self.name,
            "aliases": self.aliases,
            "attributes": self.attributes,
        }


class EntityResolver:
    """
    Resolves entity references to canonical entities.

    Uses deterministic rules:
    - Exact ID matching
    - Normalized name matching
    - Known aliases
    - Dataset context
    """

    def __init__(self):
        self.entities: dict[str, Entity] = {}
        self.name_index: dict[str, str] = {}  # normalized_name -> entity_id
        self.alias_index: dict[str, str] = {}  # normalized_alias -> entity_id
        
        # Known organization aliases
        self.known_aliases = {
            "deeplearning.ai": ["deeplearning.ai", "deeplearning ai"],
            "nvidia": ["nvidia", "nvidia deep learning institute", "nvidia dli"],
            "ibm": ["ibm"],
            "microsoft": ["microsoft"],
            "coursera": ["coursera"],
            "kafr el sheikh university": ["kafr el sheikh university", "kfs university"],
        }

    def normalize_name(self, name: str) -> str:
        """
        Normalize a name for comparison.

        Normalization:
        - Lowercase
        - Trim whitespace
        - Remove extra spaces
        - Remove special characters (except spaces and dashes)
        """
        if not name:
            return ""

        # Lowercase
        name = name.lower().strip()

        # Remove extra whitespace
        name = re.sub(r'\s+', ' ', name)

        # Remove trailing/leading punctuation
        name = name.strip('.,;:!?')

        return name

    def create_entity(
        self,
        entity_id: str,
        entity_type: str,
        name: str,
        aliases: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Entity:
        """
        Create a new canonical entity.

        Args:
            entity_id: Unique identifier
            entity_type: Type of entity (Person, Organization, etc.)
            name: Canonical name
            aliases: Alternative names
            attributes: Additional attributes

        Returns:
            Created Entity instance
        """
        entity = Entity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            aliases=aliases or [],
            attributes=attributes or {},
        )

        self.entities[entity_id] = entity

        # Index by normalized name
        normalized_name = self.normalize_name(name)
        self.name_index[normalized_name] = entity_id

        # Index by aliases
        for alias in entity.aliases:
            normalized_alias = self.normalize_name(alias)
            self.alias_index[normalized_alias] = entity_id

        return entity

    def resolve(
        self,
        name: str,
        entity_type: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> str | None:
        """
        Resolve an entity reference to its canonical ID.

        Args:
            name: Entity name to resolve
            entity_type: Optional type hint
            context: Optional context (dataset, record, etc.)

        Returns:
            Canonical entity ID or None if not found
        """
        if not name:
            return None

        normalized = self.normalize_name(name)

        # Check name index
        if normalized in self.name_index:
            entity_id = self.name_index[normalized]
            
            # Verify type if provided
            if entity_type:
                entity = self.entities.get(entity_id)
                if entity and entity.type == entity_type:
                    return entity_id
            else:
                return entity_id

        # Check alias index
        if normalized in self.alias_index:
            entity_id = self.alias_index[normalized]
            
            # Verify type if provided
            if entity_type:
                entity = self.entities.get(entity_id)
                if entity and entity.type == entity_type:
                    return entity_id
            else:
                return entity_id

        # Check known aliases
        for canonical_name, alias_list in self.known_aliases.items():
            normalized_aliases = [self.normalize_name(a) for a in alias_list]
            if normalized in normalized_aliases:
                # Return the canonical form if it exists
                if canonical_name in self.name_index:
                    return self.name_index[canonical_name]

        return None

    def get_or_create_entity(
        self,
        name: str,
        entity_type: str,
        entity_id_prefix: str | None = None,
        aliases: list[str] | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> Entity:
        """
        Get an existing entity or create a new one.

        Args:
            name: Entity name
            entity_type: Type of entity
            entity_id_prefix: Prefix for generated ID
            aliases: Alternative names
            attributes: Additional attributes

        Returns:
            Resolved or newly created Entity
        """
        # Try to resolve existing entity
        entity_id = self.resolve(name, entity_type=entity_type)

        if entity_id:
            return self.entities[entity_id]

        # Create new entity
        if not entity_id_prefix:
            entity_id_prefix = entity_type.lower()

        # Generate unique ID
        base_id = f"{entity_id_prefix}_{self.normalize_name(name).replace(' ', '_')}"
        entity_id = base_id
        counter = 1

        while entity_id in self.entities:
            entity_id = f"{base_id}_{counter}"
            counter += 1

        return self.create_entity(
            entity_id=entity_id,
            entity_type=entity_type,
            name=name,
            aliases=aliases,
            attributes=attributes,
        )

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def get_all_entities(self, entity_type: str | None = None) -> list[Entity]:
        """
        Get all entities, optionally filtered by type.

        Args:
            entity_type: Optional type filter

        Returns:
            List of entities
        """
        if entity_type:
            return [
                entity
                for entity in self.entities.values()
                if entity.type == entity_type
            ]
        return list(self.entities.values())

    def entity_count(self, entity_type: str | None = None) -> int:
        """
        Count entities, optionally by type.

        Args:
            entity_type: Optional type filter

        Returns:
            Number of entities
        """
        if entity_type:
            return len(self.get_all_entities(entity_type))
        return len(self.entities)
