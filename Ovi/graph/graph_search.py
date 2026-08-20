"""
graph/graph_search.py

Graph search and traversal for OVI Knowledge Graph.

Supports multi-hop queries and relationship-based reasoning.
"""

from __future__ import annotations

from typing import Any
from graph.entity_resolver import Entity, EntityResolver
from graph.relationship_manager import Relationship, RelationshipManager


class GraphSearch:
    """
    Search and traversal operations on the knowledge graph.

    Supports:
    - Single-hop queries
    - Multi-hop traversal
    - Path finding
    - Relationship-based reasoning
    """

    def __init__(
        self,
        entity_resolver: EntityResolver,
        relationship_manager: RelationshipManager,
    ):
        self.entity_resolver = entity_resolver
        self.relationship_manager = relationship_manager

    def find_entity(
        self,
        name: str,
        entity_type: str | None = None,
    ) -> Entity | None:
        """
        Find an entity by name.

        Args:
            name: Entity name
            entity_type: Optional type filter

        Returns:
            Entity or None
        """
        entity_id = self.entity_resolver.resolve(name, entity_type)
        if entity_id:
            return self.entity_resolver.get_entity(entity_id)
        return None

    def get_related_entities(
        self,
        entity_id: str,
        relationship_type: str | None = None,
        direction: str = "outgoing",
    ) -> list[Entity]:
        """
        Get entities related to the given entity.

        Args:
            entity_id: Source entity ID
            relationship_type: Optional relationship filter
            direction: "outgoing", "incoming", or "both"

        Returns:
            List of related entities
        """
        neighbor_ids = self.relationship_manager.get_neighbors(
            entity_id,
            relationship_type,
            direction,
        )

        entities = []
        for neighbor_id in neighbor_ids:
            entity = self.entity_resolver.get_entity(neighbor_id)
            if entity:
                entities.append(entity)

        return entities

    def traverse(
        self,
        start_entity_id: str,
        relationship_types: list[str],
        max_depth: int = 3,
    ) -> list[list[str]]:
        """
        Multi-hop traversal from a starting entity.

        Args:
            start_entity_id: Starting entity ID
            relationship_types: List of relationship types to follow
            max_depth: Maximum traversal depth

        Returns:
            List of paths (each path is a list of entity IDs)
        """
        paths = [[start_entity_id]]
        completed_paths = []

        for depth in range(max_depth):
            new_paths = []

            for path in paths:
                current_entity = path[-1]

                # Get neighbors for this entity
                for rel_type in relationship_types:
                    neighbors = self.relationship_manager.get_neighbors(
                        current_entity,
                        relationship_type=rel_type,
                        direction="outgoing",
                    )

                    for neighbor in neighbors:
                        # Avoid cycles
                        if neighbor not in path:
                            new_path = path + [neighbor]
                            new_paths.append(new_path)

            if not new_paths:
                break

            completed_paths.extend(new_paths)
            paths = new_paths

        return completed_paths

    def find_path(
        self,
        start_entity_id: str,
        end_entity_id: str,
        max_depth: int = 5,
    ) -> list[str] | None:
        """
        Find a path between two entities (BFS).

        Args:
            start_entity_id: Starting entity ID
            end_entity_id: Target entity ID
            max_depth: Maximum search depth

        Returns:
            Path as list of entity IDs, or None if no path found
        """
        if start_entity_id == end_entity_id:
            return [start_entity_id]

        visited = set()
        queue = [(start_entity_id, [start_entity_id])]

        while queue:
            current_id, path = queue.pop(0)

            if len(path) > max_depth:
                continue

            if current_id in visited:
                continue

            visited.add(current_id)

            # Get all neighbors
            neighbors = self.relationship_manager.get_neighbors(
                current_id,
                direction="both",
            )

            for neighbor_id in neighbors:
                if neighbor_id == end_entity_id:
                    return path + [neighbor_id]

                if neighbor_id not in visited:
                    queue.append((neighbor_id, path + [neighbor_id]))

        return None

    def query_courses_completed(self, person_id: str) -> list[Entity]:
        """Query: What courses has this person completed?"""
        return self.get_related_entities(
            person_id,
            relationship_type="completed",
            direction="outgoing",
        )

    def query_studied_at(self, person_id: str) -> list[Entity]:
        """Query: Where did this person study?"""
        return self.get_related_entities(
            person_id,
            relationship_type="studied_at",
            direction="outgoing",
        )

    def query_worked_at(self, person_id: str) -> list[Entity]:
        """Query: Where did this person work?"""
        return self.get_related_entities(
            person_id,
            relationship_type="worked_at",
            direction="outgoing",
        )

    def query_technologies_used(self, person_id: str) -> list[Entity]:
        """Query: What technologies has this person used?"""
        # Direct technology usage
        direct_tech = self.get_related_entities(
            person_id,
            relationship_type="uses_technology",
            direction="outgoing",
        )

        # Technologies from projects
        projects = self.get_related_entities(
            person_id,
            relationship_type="built",
            direction="outgoing",
        )

        project_tech = []
        for project in projects:
            tech_entities = self.get_related_entities(
                project.id,
                relationship_type="uses_technology",
                direction="outgoing",
            )
            project_tech.extend(tech_entities)

        # Combine and deduplicate
        all_tech = direct_tech + project_tech
        seen_ids = set()
        unique_tech = []

        for tech in all_tech:
            if tech.id not in seen_ids:
                seen_ids.add(tech.id)
                unique_tech.append(tech)

        return unique_tech

    def query_projects_with_skill(
        self,
        person_id: str,
        skill_name: str,
    ) -> list[Entity]:
        """Query: Which projects demonstrate a specific skill?"""
        # Find the skill entity
        skill_entity = self.find_entity(skill_name, entity_type="Technology")
        if not skill_entity:
            return []

        # Find all projects by this person
        projects = self.get_related_entities(
            person_id,
            relationship_type="built",
            direction="outgoing",
        )

        # Filter projects that use this skill
        matching_projects = []
        for project in projects:
            project_tech = self.get_related_entities(
                project.id,
                relationship_type="uses_technology",
                direction="outgoing",
            )

            if skill_entity in project_tech:
                matching_projects.append(project)

        return matching_projects

    def query_knowledge_source(
        self,
        person_id: str,
        topic_name: str,
    ) -> list[Entity]:
        """Query: Where did this person learn about a topic?"""
        # Find topic entity
        topic_entity = self.find_entity(topic_name, entity_type="Topic")
        if not topic_entity:
            return []

        # Find courses covering this topic
        courses_about_topic = self.get_related_entities(
            topic_entity.id,
            relationship_type="covered_in",
            direction="incoming",
        )

        # Filter to courses completed by this person
        completed_courses = self.query_courses_completed(person_id)
        completed_ids = {c.id for c in completed_courses}

        relevant_courses = [
            c for c in courses_about_topic
            if c.id in completed_ids
        ]

        return relevant_courses
