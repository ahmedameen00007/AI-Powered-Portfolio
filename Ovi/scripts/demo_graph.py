"""
scripts/demo_graph.py

Demonstrate OVI Knowledge Graph capabilities.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graph.graph_builder import GraphBuilder


def main() -> None:
    """Demonstrate graph queries."""
    
    print("=" * 60)
    print("OVI Knowledge Graph - Query Demonstration")
    print("=" * 60)
    print()
    
    # Build the graph
    builder = GraphBuilder(
        processed_dir=project_root / "dataset" / "processed"
    )
    builder.build()
    
    # Get components
    search = builder.graph_search
    ahmed_id = "ahmed_ameen"
    
    print("\n" + "=" * 60)
    print("Query 1: What courses has Ahmed completed?")
    print("=" * 60)
    
    courses = search.query_courses_completed(ahmed_id)
    print(f"\nFound {len(courses)} completed courses/certifications:")
    for course in courses[:5]:  # Show first 5
        attrs = course.attributes
        print(f"  • {course.name}")
        if attrs.get("type"):
            print(f"    Type: {attrs['type']}")
        if attrs.get("completion_date"):
            print(f"    Completed: {attrs['completion_date']}")
    
    if len(courses) > 5:
        print(f"  ... and {len(courses) - 5} more")
    
    print("\n" + "=" * 60)
    print("Query 2: Where did Ahmed study?")
    print("=" * 60)
    
    universities = search.query_studied_at(ahmed_id)
    print(f"\nFound {len(universities)} universities:")
    for uni in universities:
        print(f"  • {uni.name}")
    
    print("\n" + "=" * 60)
    print("Query 3: Where has Ahmed worked?")
    print("=" * 60)
    
    organizations = search.query_worked_at(ahmed_id)
    print(f"\nFound {len(organizations)} organizations:")
    for org in organizations:
        print(f"  • {org.name}")
        # Get the experience details
        rels = builder.relationship_manager.get_relationships_from(
            ahmed_id,
            relationship_type="worked_at"
        )
        for rel in rels:
            if rel.target_id == org.id:
                metadata = rel.metadata
                print(f"    Role: {metadata.get('role')}")
                print(f"    Period: {rel.start_date} to {rel.end_date or 'Present'}")
    
    print("\n" + "=" * 60)
    print("Query 4: What technologies has Ahmed used?")
    print("=" * 60)
    
    technologies = search.query_technologies_used(ahmed_id)
    print(f"\nFound {len(technologies)} technologies:")
    tech_names = sorted([tech.name for tech in technologies])
    
    # Group by category (AI, Data, Web, etc.)
    ai_related = [t for t in tech_names if any(keyword in t.lower() for keyword in ['ai', 'learning', 'neural', 'vision', 'llm'])]
    data_related = [t for t in tech_names if any(keyword in t.lower() for keyword in ['data', 'analytics', 'bi'])]
    other = [t for t in tech_names if t not in ai_related and t not in data_related]
    
    if ai_related:
        print("\n  AI/ML Technologies:")
        for tech in ai_related[:10]:
            print(f"    • {tech}")
    
    if data_related:
        print("\n  Data Technologies:")
        for tech in data_related[:10]:
            print(f"    • {tech}")
    
    if other and len(other) <= 10:
        print("\n  Other Technologies:")
        for tech in other:
            print(f"    • {tech}")
    
    print("\n" + "=" * 60)
    print("Query 5: Which projects demonstrate AI skills?")
    print("=" * 60)
    
    ai_projects = search.query_projects_with_skill(ahmed_id, "Artificial Intelligence")
    print(f"\nFound {len(ai_projects)} projects using Artificial Intelligence:")
    for proj in ai_projects:
        print(f"  • {proj.name}")
        attrs = proj.attributes
        if attrs.get("title"):
            print(f"    {attrs['title']}")
    
    print("\n" + "=" * 60)
    print("Query 6: Timeline - Recent events")
    print("=" * 60)
    
    timeline = builder.timeline_builder
    chronological = timeline.get_chronological_events()
    
    print(f"\nShowing last 10 events (out of {len(chronological)} total):")
    for event in chronological[-10:]:
        print(f"  [{event.date or 'Unknown'}] {event.event_type}")
        if event.description:
            print(f"    {event.description}")
    
    print("\n" + "=" * 60)
    print("Query 7: Multi-hop reasoning - RAG knowledge source")
    print("=" * 60)
    
    # Find where Ahmed learned about RAG
    rag_courses = search.query_knowledge_source(ahmed_id, "RAG")
    
    if rag_courses:
        print(f"\nAhmed learned about RAG from {len(rag_courses)} course(s):")
        for course in rag_courses:
            print(f"  • {course.name}")
    else:
        print("\nNo specific courses found covering RAG topic.")
        print("Checking for courses mentioning RAG in their name...")
        
        all_courses = search.query_courses_completed(ahmed_id)
        rag_mentions = [c for c in all_courses if 'rag' in c.name.lower()]
        
        if rag_mentions:
            print(f"\nFound {len(rag_mentions)} courses mentioning RAG:")
            for course in rag_mentions:
                print(f"  • {course.name}")
    
    print("\n" + "=" * 60)
    print("Graph Statistics Summary")
    print("=" * 60)
    
    stats = builder.stats
    print(f"\n  Datasets processed: {stats['datasets_processed']}")
    print(f"  Entities: {stats['entities_created']}")
    print(f"  Relationships: {stats['relationships_created']}")
    print(f"  Timeline events: {stats['timeline_events']}")
    
    print("\n" + "=" * 60)
    print("Demonstration Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
