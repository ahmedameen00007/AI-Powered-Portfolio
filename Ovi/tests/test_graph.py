"""
tests/test_graph.py

Tests for OVI Knowledge Graph components.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graph.entity_resolver import EntityResolver
from graph.relationship_manager import RelationshipManager
from graph.timeline_builder import TimelineBuilder


def test_entity_resolution():
    """Test entity resolution."""
    print("Testing entity resolution...")
    
    resolver = EntityResolver()
    
    # Create Ahmed entity
    ahmed = resolver.create_entity(
        entity_id="ahmed_ameen",
        entity_type="Person",
        name="Ahmed Ameen",
        aliases=["Ahmed", "Ahmed Khaled Mohamed Ameen"],
    )
    
    # Test exact name resolution
    assert resolver.resolve("Ahmed Ameen") == "ahmed_ameen"
    
    # Test alias resolution
    assert resolver.resolve("Ahmed") == "ahmed_ameen"
    assert resolver.resolve("Ahmed Khaled Mohamed Ameen") == "ahmed_ameen"
    
    # Test case-insensitive resolution
    assert resolver.resolve("ahmed ameen") == "ahmed_ameen"
    assert resolver.resolve("AHMED AMEEN") == "ahmed_ameen"
    
    # Test whitespace normalization
    assert resolver.resolve("  Ahmed  Ameen  ") == "ahmed_ameen"
    
    print("  ✓ Entity resolution tests passed")


def test_duplicate_organization_resolution():
    """Test that same organization in multiple datasets resolves correctly."""
    print("Testing organization resolution...")
    
    resolver = EntityResolver()
    
    # Create organization from first dataset
    org1 = resolver.get_or_create_entity(
        name="DeepLearning.AI",
        entity_type="Organization",
    )
    
    # Try to create same organization from second dataset
    org2 = resolver.get_or_create_entity(
        name="DeepLearning.AI",
        entity_type="Organization",
    )
    
    # Should resolve to same entity
    assert org1.id == org2.id
    
    # Case-insensitive
    org3 = resolver.get_or_create_entity(
        name="deeplearning.ai",
        entity_type="Organization",
    )
    assert org1.id == org3.id
    
    print("  ✓ Organization resolution tests passed")


def test_relationship_creation():
    """Test relationship creation and querying."""
    print("Testing relationships...")
    
    resolver = EntityResolver()
    rel_manager = RelationshipManager()
    
    # Create entities
    ahmed = resolver.create_entity(
        entity_id="ahmed_ameen",
        entity_type="Person",
        name="Ahmed Ameen",
    )
    
    cert = resolver.create_entity(
        entity_id="cert_001",
        entity_type="Certification",
        name="Neural Networks and Deep Learning",
    )
    
    org = resolver.create_entity(
        entity_id="org_deeplearning",
        entity_type="Organization",
        name="DeepLearning.AI",
    )
    
    # Create relationships
    rel1 = rel_manager.add_relationship(
        source_id=ahmed.id,
        relationship_type="completed",
        target_id=cert.id,
        source_dataset="courses",
        source_record_id="cert_001",
        confidence=1.0,
    )
    
    rel2 = rel_manager.add_relationship(
        source_id=cert.id,
        relationship_type="provided_by",
        target_id=org.id,
        source_dataset="courses",
        confidence=1.0,
    )
    
    # Test querying
    rels_from_ahmed = rel_manager.get_relationships_from(ahmed.id)
    assert len(rels_from_ahmed) == 1
    assert rels_from_ahmed[0].target_id == cert.id
    
    rels_to_cert = rel_manager.get_relationships_to(cert.id)
    assert len(rels_to_cert) == 1
    assert rels_to_cert[0].source_id == ahmed.id
    
    # Test relationship type filtering
    completed_rels = rel_manager.get_relationships_from(
        ahmed.id,
        relationship_type="completed",
    )
    assert len(completed_rels) == 1
    
    print("  ✓ Relationship tests passed")


def test_provenance():
    """Test that relationships preserve provenance."""
    print("Testing provenance...")
    
    resolver = EntityResolver()
    rel_manager = RelationshipManager()
    
    ahmed = resolver.create_entity("ahmed", "Person", "Ahmed Ameen")
    project = resolver.create_entity("proj_001", "Project", "OVI")
    
    rel = rel_manager.add_relationship(
        source_id=ahmed.id,
        relationship_type="built",
        target_id=project.id,
        source_dataset="projects",
        source_record_id="project_001",
        confidence=1.0,
    )
    
    # Verify provenance
    assert rel.source_dataset == "projects"
    assert rel.source_record_id == "project_001"
    assert rel.confidence == 1.0
    
    print("  ✓ Provenance tests passed")


def test_timeline():
    """Test timeline construction."""
    print("Testing timeline...")
    
    timeline = TimelineBuilder()
    
    # Add events
    event1 = timeline.add_event(
        event_type="course_completed",
        date="2025-07-18",
        description="Completed: Neural Networks",
        source_dataset="courses",
    )
    
    event2 = timeline.add_event(
        event_type="job_started",
        date="2026-02",
        description="Started internship",
        source_dataset="experience",
    )
    
    event3 = timeline.add_event(
        event_type="achievement_received",
        date="2025",
        description="Achievement received",
        source_dataset="achievements",
    )
    
    # Test date precision
    assert event1.date_precision == "day"
    assert event2.date_precision == "month"
    assert event3.date_precision == "year"
    
    # Test chronological ordering
    chronological = timeline.get_chronological_events()
    assert chronological[0] == event3  # 2025
    assert chronological[1] == event1  # 2025-07-18
    assert chronological[2] == event2  # 2026-02
    
    print("  ✓ Timeline tests passed")


def test_entity_types():
    """Test different entity types."""
    print("Testing entity types...")
    
    resolver = EntityResolver()
    
    # Create various entity types
    person = resolver.create_entity("p1", "Person", "Ahmed")
    org = resolver.create_entity("o1", "Organization", "Microsoft")
    tech = resolver.create_entity("t1", "Technology", "Python")
    skill = resolver.create_entity("s1", "Skill", "Problem Solving")
    
    # Test filtering by type
    assert resolver.entity_count("Person") == 1
    assert resolver.entity_count("Organization") == 1
    assert resolver.entity_count("Technology") == 1
    assert resolver.entity_count("Skill") == 1
    assert resolver.entity_count() == 4
    
    print("  ✓ Entity type tests passed")


if __name__ == "__main__":
    print("Running Knowledge Graph tests...")
    print("=" * 60)
    print()
    
    test_entity_resolution()
    test_duplicate_organization_resolution()
    test_relationship_creation()
    test_provenance()
    test_timeline()
    test_entity_types()
    
    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
