"""
graph/graph_builder.py

Main graph builder for OVI Knowledge Graph.

Orchestrates the construction of the complete knowledge graph
from processed datasets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from graph.entity_resolver import EntityResolver
from graph.relationship_manager import RelationshipManager
from graph.timeline_builder import TimelineBuilder
from graph.graph_search import GraphSearch


class GraphBuilder:
    """
    Builds the OVI Knowledge Graph from processed datasets.

    Pipeline:
        Processed Datasets
            ↓
        Create Entities
            ↓
        Resolve Entities
            ↓
        Create Relationships
            ↓
        Build Timeline
            ↓
        Knowledge Graph
    """

    def __init__(
        self,
        processed_dir: str | Path = "dataset/processed",
    ):
        self.processed_dir = Path(processed_dir)

        # Core components
        self.entity_resolver = EntityResolver()
        self.relationship_manager = RelationshipManager()
        self.timeline_builder = TimelineBuilder()
        self.graph_search = GraphSearch(
            self.entity_resolver,
            self.relationship_manager,
        )

        # Statistics
        self.stats = {
            "datasets_processed": 0,
            "entities_created": 0,
            "relationships_created": 0,
            "timeline_events": 0,
            "errors": [],
        }

    def load_dataset(self, filename: str) -> dict[str, Any] | None:
        """Load a processed dataset."""
        path = self.processed_dir / filename

        if not path.exists():
            self.stats["errors"].append(f"Dataset not found: {filename}")
            return None

        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            self.stats["errors"].append(f"Error loading {filename}: {e}")
            return None

    def build(self) -> None:
        """Build the complete knowledge graph from all datasets."""
        print("Building OVI Knowledge Graph...")
        print("=" * 60)

        # Create Ahmed as the central entity
        ahmed = self.entity_resolver.create_entity(
            entity_id="ahmed_ameen",
            entity_type="Person",
            name="Ahmed Ameen",
            aliases=["Ahmed", "Ahmed Khaled Mohamed Ameen"],
            attributes={},
        )
        self.stats["entities_created"] += 1

        # Process each dataset
        self._process_basic_info(ahmed)
        self._process_personal_info(ahmed)
        self._process_education(ahmed)
        self._process_courses(ahmed)
        self._process_experience(ahmed)
        self._process_projects(ahmed)
        self._process_achievements(ahmed)
        self._process_benefits(ahmed)

        # Build timeline
        self._build_timeline()

        # Update statistics
        self.stats["entities_created"] = self.entity_resolver.entity_count()
        self.stats["relationships_created"] = self.relationship_manager.relationship_count()
        self.stats["timeline_events"] = self.timeline_builder.event_count()

        print()
        print("=" * 60)
        print("Graph build complete!")
        self._print_statistics()

    def _process_basic_info(self, ahmed) -> None:
        """Process basic_info.json"""
        print("\nProcessing: basic_info.json")

        data = self.load_dataset("basic_info.json")
        if not data:
            return

        # Update Ahmed's attributes
        ahmed.attributes.update({
            "full_name": data.get("full_name"),
            "birth_date": data.get("birth_date"),
            "city": data.get("city"),
            "specialist": data.get("specialist"),
        })

        # Create location entity
        city = data.get("city")
        if city:
            location = self.entity_resolver.get_or_create_entity(
                name=city,
                entity_type="Location",
            )

            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="located_in",
                target_id=location.id,
                source_dataset="basic_info",
                confidence=1.0,
            )

        self.stats["datasets_processed"] += 1
        print("  ✓ Processed")

    def _process_personal_info(self, ahmed) -> None:
        """Process personal_info.json"""
        print("\nProcessing: personal_info.json")

        data = self.load_dataset("personal_info.json")
        if not data:
            return

        # Store bio
        ahmed.attributes["bio"] = data.get("bio")

        # Create interest entities
        for interest in data.get("interests", []):
            interest_entity = self.entity_resolver.get_or_create_entity(
                name=interest,
                entity_type="Topic",
            )

            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="interested_in",
                target_id=interest_entity.id,
                source_dataset="personal_info",
                confidence=1.0,
            )

        # Create skill entities from strengths
        for strength in data.get("strengths", []):
            skill_entity = self.entity_resolver.get_or_create_entity(
                name=strength,
                entity_type="Skill",
            )

            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="skilled_in",
                target_id=skill_entity.id,
                source_dataset="personal_info",
                confidence=1.0,
            )

        # Store other attributes
        ahmed.attributes["goals"] = data.get("goals", [])
        ahmed.attributes["personality"] = data.get("personality", [])
        ahmed.attributes["hobbies"] = data.get("hobbies", [])
        ahmed.attributes["languages"] = data.get("languages", [])

        self.stats["datasets_processed"] += 1
        print("  ✓ Processed")

    def _process_education(self, ahmed) -> None:
        """Process education.json"""
        print("\nProcessing: education.json")

        data = self.load_dataset("education.json")
        if not data:
            return

        # Create university entity
        university_name = data.get("university")
        if university_name:
            university = self.entity_resolver.get_or_create_entity(
                name=university_name,
                entity_type="University",
            )

            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="studied_at",
                target_id=university.id,
                source_dataset="education",
                confidence=1.0,
                metadata={
                    "degree": data.get("degree"),
                    "major": data.get("major"),
                    "graduation_date": data.get("graduation_date"),
                },
            )

            # Create faculty entity
            faculty_name = data.get("faculty")
            if faculty_name:
                faculty = self.entity_resolver.get_or_create_entity(
                    name=faculty_name,
                    entity_type="Faculty",
                )

                self.relationship_manager.add_relationship(
                    source_id=university.id,
                    relationship_type="has_faculty",
                    target_id=faculty.id,
                    source_dataset="education",
                    confidence=1.0,
                )

                self.relationship_manager.add_relationship(
                    source_id=ahmed.id,
                    relationship_type="enrolled_in",
                    target_id=faculty.id,
                    source_dataset="education",
                    confidence=1.0,
                )

        # Process academic projects
        for proj in data.get("academic_projects", []):
            proj_name = proj.get("name")
            if proj_name:
                project = self.entity_resolver.get_or_create_entity(
                    name=proj_name,
                    entity_type="Project",
                    attributes={
                        "description": proj.get("description"),
                        "category": "academic",
                    },
                )

                self.relationship_manager.add_relationship(
                    source_id=ahmed.id,
                    relationship_type="built",
                    target_id=project.id,
                    source_dataset="education",
                    confidence=1.0,
                )

                # Link technologies
                for tech_name in proj.get("technologies", []):
                    tech = self.entity_resolver.get_or_create_entity(
                        name=tech_name,
                        entity_type="Technology",
                    )

                    self.relationship_manager.add_relationship(
                        source_id=project.id,
                        relationship_type="uses_technology",
                        target_id=tech.id,
                        source_dataset="education",
                        confidence=1.0,
                    )

        self.stats["datasets_processed"] += 1
        print("  ✓ Processed")

    def _process_courses(self, ahmed) -> None:
        """Process courses.json"""
        print("\nProcessing: courses.json")

        data = self.load_dataset("courses.json")
        if not data or "certifications" not in data:
            return

        for cert in data["certifications"]:
            cert_id = cert.get("id")
            cert_name = cert.get("title")

            if not cert_name:
                continue

            # Create certification entity
            certification = self.entity_resolver.get_or_create_entity(
                name=cert_name,
                entity_type="Certification",
                entity_id_prefix=cert_id,
                attributes={
                    "type": cert.get("type"),
                    "completion_date": cert.get("completion_date"),
                    "platform": cert.get("platform"),
                },
            )

            # Ahmed completed this certification
            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="completed",
                target_id=certification.id,
                source_dataset="courses",
                source_record_id=cert_id,
                confidence=1.0,
                start_date=cert.get("start_date"),
                end_date=cert.get("completion_date"),
            )

            # Provider relationship
            provider_name = cert.get("provider")
            if provider_name:
                provider = self.entity_resolver.get_or_create_entity(
                    name=provider_name,
                    entity_type="Organization",
                )

                self.relationship_manager.add_relationship(
                    source_id=certification.id,
                    relationship_type="provided_by",
                    target_id=provider.id,
                    source_dataset="courses",
                    source_record_id=cert_id,
                    confidence=1.0,
                )

            # Platform relationship
            platform_name = cert.get("platform")
            if platform_name:
                platform = self.entity_resolver.get_or_create_entity(
                    name=platform_name,
                    entity_type="Platform",
                )

                self.relationship_manager.add_relationship(
                    source_id=certification.id,
                    relationship_type="hosted_on",
                    target_id=platform.id,
                    source_dataset="courses",
                    source_record_id=cert_id,
                    confidence=1.0,
                )

            # Topics
            for topic_name in cert.get("topics", []):
                topic = self.entity_resolver.get_or_create_entity(
                    name=topic_name,
                    entity_type="Topic",
                )

                self.relationship_manager.add_relationship(
                    source_id=certification.id,
                    relationship_type="covers",
                    target_id=topic.id,
                    source_dataset="courses",
                    source_record_id=cert_id,
                    confidence=1.0,
                )

                # Create reverse relationship for queries
                self.relationship_manager.add_relationship(
                    source_id=topic.id,
                    relationship_type="covered_in",
                    target_id=certification.id,
                    source_dataset="courses",
                    source_record_id=cert_id,
                    confidence=1.0,
                )

        self.stats["datasets_processed"] += 1
        print(f"  ✓ Processed {len(data['certifications'])} certifications")

    def _process_experience(self, ahmed) -> None:
        """Process experience.json"""
        print("\nProcessing: experience.json")

        data = self.load_dataset("experience.json")
        if not data or "experiences" not in data:
            return

        for exp in data["experiences"]:
            exp_id = exp.get("id")
            
            # Create organization entity
            org_data = exp.get("organization", {})
            org_name = org_data.get("name")

            if not org_name:
                continue

            organization = self.entity_resolver.get_or_create_entity(
                name=org_name,
                entity_type="Organization",
                attributes={"type": org_data.get("type")},
            )

            # Ahmed worked at this organization
            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="worked_at",
                target_id=organization.id,
                source_dataset="experience",
                source_record_id=exp_id,
                confidence=1.0,
                start_date=exp.get("start_date"),
                end_date=exp.get("end_date"),
                metadata={
                    "role": exp.get("role"),
                    "employment_type": exp.get("employment_type"),
                    "status": exp.get("status"),
                },
            )

            # Create role entity
            role_name = exp.get("role")
            if role_name:
                role = self.entity_resolver.get_or_create_entity(
                    name=role_name,
                    entity_type="Role",
                )

                self.relationship_manager.add_relationship(
                    source_id=ahmed.id,
                    relationship_type="worked_as",
                    target_id=role.id,
                    source_dataset="experience",
                    source_record_id=exp_id,
                    confidence=1.0,
                    start_date=exp.get("start_date"),
                    end_date=exp.get("end_date"),
                )

            # Technologies used
            for tech_name in exp.get("technologies", []):
                tech = self.entity_resolver.get_or_create_entity(
                    name=tech_name,
                    entity_type="Technology",
                )

                self.relationship_manager.add_relationship(
                    source_id=ahmed.id,
                    relationship_type="uses_technology",
                    target_id=tech.id,
                    source_dataset="experience",
                    source_record_id=exp_id,
                    confidence=1.0,
                )

        self.stats["datasets_processed"] += 1
        print(f"  ✓ Processed {len(data['experiences'])} experiences")

    def _process_projects(self, ahmed) -> None:
        """Process projects.json"""
        print("\nProcessing: projects.json")

        data = self.load_dataset("projects.json")
        if not data or "projects" not in data:
            return

        for proj in data["projects"]:
            proj_id = proj.get("id")
            proj_name = proj.get("name")

            if not proj_name:
                continue

            # Create project entity
            project = self.entity_resolver.get_or_create_entity(
                name=proj_name,
                entity_type="Project",
                entity_id_prefix=proj_id,
                attributes={
                    "title": proj.get("title"),
                    "description": proj.get("description"),
                    "category": "professional",
                },
            )

            # Ahmed built this project
            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="built",
                target_id=project.id,
                source_dataset="projects",
                source_record_id=proj_id,
                confidence=1.0,
            )

            # Technologies
            for tech_name in proj.get("technologies", []):
                tech = self.entity_resolver.get_or_create_entity(
                    name=tech_name,
                    entity_type="Technology",
                )

                self.relationship_manager.add_relationship(
                    source_id=project.id,
                    relationship_type="uses_technology",
                    target_id=tech.id,
                    source_dataset="projects",
                    source_record_id=proj_id,
                    confidence=1.0,
                )

            # Domains
            for domain_name in proj.get("domains", []):
                domain = self.entity_resolver.get_or_create_entity(
                    name=domain_name,
                    entity_type="Domain",
                )

                self.relationship_manager.add_relationship(
                    source_id=project.id,
                    relationship_type="belongs_to_domain",
                    target_id=domain.id,
                    source_dataset="projects",
                    source_record_id=proj_id,
                    confidence=1.0,
                )

        self.stats["datasets_processed"] += 1
        print(f"  ✓ Processed {len(data['projects'])} projects")

    def _process_achievements(self, ahmed) -> None:
        """Process achievements.json"""
        print("\nProcessing: achievements.json")

        data = self.load_dataset("achievements.json")
        if not data or "activities" not in data:
            return

        for activity in data["activities"]:
            activity_id = activity.get("id")
            activity_name = activity.get("name")

            if not activity_name:
                continue

            # Create achievement entity
            achievement = self.entity_resolver.get_or_create_entity(
                name=activity_name,
                entity_type="Achievement",
                entity_id_prefix=activity_id,
                attributes={
                    "type": activity.get("type"),
                    "participation": activity.get("participation"),
                    "date": activity.get("date"),
                    "year": activity.get("year"),
                },
            )

            # Ahmed achieved this
            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="achieved",
                target_id=achievement.id,
                source_dataset="achievements",
                source_record_id=activity_id,
                confidence=1.0,
                metadata={
                    "date": activity.get("date"),
                    "year": activity.get("year"),
                },
            )

            # Organizer relationship
            organizer_name = activity.get("organizer")
            if organizer_name:
                organizer = self.entity_resolver.get_or_create_entity(
                    name=organizer_name,
                    entity_type="Organization",
                )

                self.relationship_manager.add_relationship(
                    source_id=achievement.id,
                    relationship_type="organized_by",
                    target_id=organizer.id,
                    source_dataset="achievements",
                    source_record_id=activity_id,
                    confidence=1.0,
                )

        self.stats["datasets_processed"] += 1
        print(f"  ✓ Processed {len(data['activities'])} achievements")

    def _process_benefits(self, ahmed) -> None:
        """Process benefits.json"""
        print("\nProcessing: benefits.json")

        data = self.load_dataset("benefits.json")
        if not data:
            return

        # Technical strengths as skills
        for strength in data.get("technical_strengths", []):
            skill = self.entity_resolver.get_or_create_entity(
                name=strength,
                entity_type="Skill",
            )

            self.relationship_manager.add_relationship(
                source_id=ahmed.id,
                relationship_type="skilled_in",
                target_id=skill.id,
                source_dataset="benefits",
                confidence=1.0,
            )

        # Store other benefits as attributes
        ahmed.attributes["professional_value"] = data.get("professional_value", [])
        ahmed.attributes["problem_solving_capabilities"] = data.get("problem_solving_capabilities", [])

        self.stats["datasets_processed"] += 1
        print("  ✓ Processed")

    def _build_timeline(self) -> None:
        """Build timeline from all datasets."""
        print("\nBuilding timeline...")

        # Load datasets for timeline
        education = self.load_dataset("education.json")
        courses = self.load_dataset("courses.json")
        experience = self.load_dataset("experience.json")
        achievements = self.load_dataset("achievements.json")

        self.timeline_builder.build_from_datasets(
            education=education,
            courses=courses,
            experience=experience,
            achievements=achievements,
        )

        print(f"  ✓ Created {self.timeline_builder.event_count()} timeline events")

    def _print_statistics(self) -> None:
        """Print graph statistics."""
        print("\nGraph Statistics:")
        print(f"  Datasets processed: {self.stats['datasets_processed']}")
        print(f"  Entities created: {self.stats['entities_created']}")
        print(f"  Relationships created: {self.stats['relationships_created']}")
        print(f"  Timeline events: {self.stats['timeline_events']}")
        print(f"  Errors: {len(self.stats['errors'])}")

        if self.stats["errors"]:
            print("\nErrors:")
            for error in self.stats["errors"]:
                print(f"  - {error}")

        print("\nEntity breakdown:")
        for entity_type in ["Person", "Organization", "University", "Certification", 
                           "Project", "Technology", "Topic", "Skill", "Achievement"]:
            count = self.entity_resolver.entity_count(entity_type)
            if count > 0:
                print(f"  {entity_type}: {count}")

        print("\nRelationship types:")
        for rel_type in sorted(self.relationship_manager.get_relationship_types()):
            count = self.relationship_manager.relationship_count(rel_type)
            print(f"  {rel_type}: {count}")

    def export_to_json(self, output_path: str | Path) -> None:
        """Export the graph to JSON format."""
        output_path = Path(output_path)

        graph_data = {
            "entities": [
                entity.to_dict()
                for entity in self.entity_resolver.get_all_entities()
            ],
            "relationships": [
                rel.to_dict()
                for rel in self.relationship_manager.relationships
            ],
            "timeline": [
                event.to_dict()
                for event in self.timeline_builder.get_chronological_events()
            ],
            "statistics": self.stats,
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(graph_data, f, indent=2, ensure_ascii=False)

        print(f"\nGraph exported to: {output_path}")
