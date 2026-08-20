"""
graph/timeline_builder.py

Timeline construction for OVI Knowledge Graph.

Extracts and organizes temporal events from the knowledge graph
with proper date precision preservation.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime
import re


class TimelineEvent:
    """Represents a temporal event in Ahmed's timeline."""

    def __init__(
        self,
        event_id: str,
        event_type: str,
        date: str | None,
        entity_id: str | None = None,
        description: str | None = None,
        source_dataset: str | None = None,
        source_record_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.event_id = event_id
        self.event_type = event_type
        self.date = date
        self.entity_id = entity_id
        self.description = description
        self.source_dataset = source_dataset
        self.source_record_id = source_record_id
        self.metadata = metadata or {}

        # Parse date precision
        self.date_precision = self._determine_precision(date)

    def _determine_precision(self, date: str | None) -> str:
        """
        Determine the precision of a date string.

        Returns: "year", "month", "day", or "unknown"
        """
        if not date:
            return "unknown"

        # Full date: YYYY-MM-DD
        if re.match(r'^\d{4}-\d{2}-\d{2}$', date):
            return "day"

        # Year-month: YYYY-MM
        if re.match(r'^\d{4}-\d{2}$', date):
            return "month"

        # Year only: YYYY
        if re.match(r'^\d{4}$', date):
            return "year"

        return "unknown"

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "date": self.date,
            "date_precision": self.date_precision,
            "entity_id": self.entity_id,
            "description": self.description,
            "source_dataset": self.source_dataset,
            "source_record_id": self.source_record_id,
            "metadata": self.metadata,
        }

    def __repr__(self) -> str:
        return f"TimelineEvent({self.event_type} on {self.date})"


class TimelineBuilder:
    """
    Builds chronological timeline from knowledge graph.

    Extracts temporal events from:
    - Education (started, graduated)
    - Courses (completed)
    - Experience (started, ended)
    - Projects (created)
    - Achievements (received)
    """

    def __init__(self):
        self.events: list[TimelineEvent] = []
        self.event_counter = 0

    def add_event(
        self,
        event_type: str,
        date: str | None,
        entity_id: str | None = None,
        description: str | None = None,
        source_dataset: str | None = None,
        source_record_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> TimelineEvent:
        """
        Add an event to the timeline.

        Args:
            event_type: Type of event
            date: Date string (preserves precision)
            entity_id: Related entity ID
            description: Event description
            source_dataset: Source dataset
            source_record_id: Source record ID
            metadata: Additional metadata

        Returns:
            Created TimelineEvent
        """
        self.event_counter += 1
        event_id = f"event_{self.event_counter:04d}"

        event = TimelineEvent(
            event_id=event_id,
            event_type=event_type,
            date=date,
            entity_id=entity_id,
            description=description,
            source_dataset=source_dataset,
            source_record_id=source_record_id,
            metadata=metadata,
        )

        self.events.append(event)
        return event

    def get_events(
        self,
        event_type: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[TimelineEvent]:
        """
        Get events, optionally filtered.

        Args:
            event_type: Optional type filter
            start_date: Optional start date filter
            end_date: Optional end date filter

        Returns:
            List of matching events
        """
        events = self.events

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        if start_date:
            events = [
                e for e in events
                if e.date and e.date >= start_date
            ]

        if end_date:
            events = [
                e for e in events
                if e.date and e.date <= end_date
            ]

        return events

    def get_chronological_events(self) -> list[TimelineEvent]:
        """
        Get all events in chronological order.

        Events without dates are placed at the end.

        Returns:
            Sorted list of events
        """
        # Separate events with and without dates
        dated_events = [e for e in self.events if e.date]
        undated_events = [e for e in self.events if not e.date]

        # Sort dated events
        dated_events.sort(key=lambda e: e.date)

        return dated_events + undated_events

    def event_count(self) -> int:
        """Get total number of events."""
        return len(self.events)

    def get_event_types(self) -> list[str]:
        """Get all event types in the timeline."""
        return list(set(e.event_type for e in self.events))

    def build_from_datasets(
        self,
        education: dict[str, Any] | None = None,
        courses: dict[str, Any] | None = None,
        experience: dict[str, Any] | None = None,
        projects: dict[str, Any] | None = None,
        achievements: dict[str, Any] | None = None,
    ) -> None:
        """
        Build timeline from processed datasets.

        Args:
            education: Education dataset
            courses: Courses dataset
            experience: Experience dataset
            projects: Projects dataset
            achievements: Achievements dataset
        """
        # Process education
        if education:
            graduation_date = education.get("graduation_date")
            if graduation_date:
                self.add_event(
                    event_type="education_graduation",
                    date=graduation_date,
                    description=f"Expected graduation: {education.get('degree')}",
                    source_dataset="education",
                    metadata={"university": education.get("university")},
                )

        # Process courses
        if courses and "certifications" in courses:
            for cert in courses["certifications"]:
                cert_id = cert.get("id")

                # Completion date
                completion_date = cert.get("completion_date")
                if completion_date:
                    self.add_event(
                        event_type="course_completed",
                        date=completion_date,
                        entity_id=cert_id,
                        description=f"Completed: {cert.get('title')}",
                        source_dataset="courses",
                        source_record_id=cert_id,
                        metadata={
                            "provider": cert.get("provider"),
                            "type": cert.get("type"),
                        },
                    )

                # Start/end dates
                start_date = cert.get("start_date")
                end_date = cert.get("end_date")

                if start_date:
                    self.add_event(
                        event_type="course_started",
                        date=start_date,
                        entity_id=cert_id,
                        description=f"Started: {cert.get('title')}",
                        source_dataset="courses",
                        source_record_id=cert_id,
                    )

                if end_date:
                    self.add_event(
                        event_type="course_ended",
                        date=end_date,
                        entity_id=cert_id,
                        description=f"Ended: {cert.get('title')}",
                        source_dataset="courses",
                        source_record_id=cert_id,
                    )

        # Process experience
        if experience and "experiences" in experience:
            for exp in experience["experiences"]:
                exp_id = exp.get("id")
                role = exp.get("role")
                org_name = exp.get("organization", {}).get("name")

                start_date = exp.get("start_date")
                if start_date:
                    self.add_event(
                        event_type="job_started",
                        date=start_date,
                        entity_id=exp_id,
                        description=f"Started as {role} at {org_name}",
                        source_dataset="experience",
                        source_record_id=exp_id,
                        metadata={"role": role, "organization": org_name},
                    )

                end_date = exp.get("end_date")
                if end_date:
                    self.add_event(
                        event_type="job_ended",
                        date=end_date,
                        entity_id=exp_id,
                        description=f"Ended role as {role} at {org_name}",
                        source_dataset="experience",
                        source_record_id=exp_id,
                        metadata={"role": role, "organization": org_name},
                    )

        # Process achievements
        if achievements and "activities" in achievements:
            for activity in achievements["activities"]:
                activity_id = activity.get("id")
                name = activity.get("name")

                date = activity.get("date")
                if date:
                    self.add_event(
                        event_type="achievement_received",
                        date=date,
                        entity_id=activity_id,
                        description=f"Achievement: {name}",
                        source_dataset="achievements",
                        source_record_id=activity_id,
                        metadata={"type": activity.get("type")},
                    )

                # Also check year field
                year = activity.get("year")
                if year and not date:
                    self.add_event(
                        event_type="achievement_received",
                        date=str(year),
                        entity_id=activity_id,
                        description=f"Achievement: {name}",
                        source_dataset="achievements",
                        source_record_id=activity_id,
                        metadata={"type": activity.get("type")},
                    )
