"""
builders/normalizer.py

Responsible for converting heterogeneous raw OVI data into
a consistent canonical representation.

The normalizer does NOT perform final validation.
Validation is handled separately by validators and Pydantic schemas.
"""

from __future__ import annotations

from typing import Any


class DataNormalizer:
    """
    Normalizes raw OVI data into canonical structures.

    Responsibilities:
    - Normalize common values
    - Normalize dates
    - Normalize lists
    - Normalize nested structures
    - Convert heterogeneous representations into one format
    - Preserve information without inventing new facts

    Non-responsibilities:
    - Schema validation
    - Data persistence
    - Embedding generation
    - Chunk creation
    - Graph construction
    """

    # ------------------------------------------------------------------
    # Generic normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_string(value: Any) -> str | None:
        """
        Normalize a value expected to represent a string.

        Returns None for empty or missing values.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        return value if value else None

    @staticmethod
    def normalize_url(value: Any) -> str | None:
        """
        Normalize a URL value.

        Extracts clean URLs from Markdown-style links:
            [https://example.com](https://example.com) -> https://example.com

        Returns None for empty or missing values.
        """

        if value is None:
            return None

        if not isinstance(value, str):
            value = str(value)

        value = value.strip()

        if not value:
            return None

        # Extract URL from Markdown link format: [url](url) or [text](url)
        import re
        markdown_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        match = re.match(markdown_pattern, value)

        if match:
            # Use the URL from the parentheses
            return match.group(2).strip()

        return value

    @staticmethod
    def normalize_list(value: Any) -> list[Any]:
        """
        Normalize a value into a list.

        Examples:
            None                  -> []
            "Python"              -> ["Python"]
            ["Python", "RAG"]     -> ["Python", "RAG"]
        """

        if value is None:
            return []

        if isinstance(value, list):
            return value

        return [value]

    @staticmethod
    def normalize_string_list(value: Any) -> list[str]:
        """
        Normalize a value into a clean list of strings.
        """

        items = DataNormalizer.normalize_list(value)

        normalized: list[str] = []

        for item in items:
            value = DataNormalizer.normalize_string(item)

            if value is not None:
                normalized.append(value)

        return normalized

    @staticmethod
    def parse_duration_to_hours(duration: str | None) -> float | None:
        """
        Parse a duration string into hours.

        Supported formats:
            - "6 hours"
            - "6 hours 26 minutes"
            - "45 minutes"
            - "2h 30m"
            - "90 minutes"
            - "1h"

        Returns:
            Numeric hours value or None if parsing fails.
        """

        if not duration:
            return None

        if not isinstance(duration, str):
            return None

        duration = duration.strip().lower()

        if not duration:
            return None

        import re

        total_hours = 0.0

        # Pattern: "6 hours", "2h"
        hours_pattern = r'(\d+(?:\.\d+)?)\s*(?:hours?|h)'
        hours_matches = re.findall(hours_pattern, duration)

        for match in hours_matches:
            total_hours += float(match)

        # Pattern: "26 minutes", "30m"
        minutes_pattern = r'(\d+(?:\.\d+)?)\s*(?:minutes?|mins?|m)'
        minutes_matches = re.findall(minutes_pattern, duration)

        for match in minutes_matches:
            total_hours += float(match) / 60.0

        return total_hours if total_hours > 0 else None

    # ------------------------------------------------------------------
    # Date normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_date(value: Any) -> str | None:
        """
        Normalize date-like values while preserving their precision.

        Examples:
            2025           -> "2025"
            "2025"         -> "2025"
            "2025-11"      -> "2025-11"
            "2025-11-16"   -> "2025-11-16"

        The normalizer does not convert partial dates into full dates.
        """

        value = DataNormalizer.normalize_string(value)

        if value is None:
            return None

        return value

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_verification(
        verification: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize certification verification information.
        """

        if verification is None:
            return None

        if not isinstance(verification, dict):
            return None

        return {
            "id": DataNormalizer.normalize_string(
                verification.get("id")
            ),
            "url": DataNormalizer.normalize_url(
                verification.get("url")
            ),
        }

    # ------------------------------------------------------------------
    # Certification normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_included_course(
        course: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize an included course.

        Raw data may represent a course as either:

            "Python Fundamentals"

        or:

            {
                "title": "Python Fundamentals",
                "hours": 3
            }
        """

        if isinstance(course, str):
            title = DataNormalizer.normalize_string(course)

            if title is None:
                return None

            return {
                "title": title,
                "hours": None,
            }

        if isinstance(course, dict):
            title = DataNormalizer.normalize_string(
                course.get("title")
            )

            if title is None:
                return None

            return {
                "title": title,
                "hours": course.get("hours"),
            }

        return None

    @staticmethod
    def normalize_certification(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a raw certification/course record.
        """

        normalized = {}

        # Core fields
        normalized["id"] = DataNormalizer.normalize_string(
            data.get("id")
        )

        normalized["title"] = DataNormalizer.normalize_string(
            data.get("title")
        )

        normalized["type"] = DataNormalizer.normalize_string(
            data.get("type")
        )

        normalized["provider"] = DataNormalizer.normalize_string(
            data.get("provider")
        )

        normalized["platform"] = DataNormalizer.normalize_string(
            data.get("platform")
        )

        # Dates
        normalized["completion_date"] = (
            DataNormalizer.normalize_date(
                data.get("completion_date")
            )
        )

        normalized["start_date"] = (
            DataNormalizer.normalize_date(
                data.get("start_date")
            )
        )

        normalized["end_date"] = (
            DataNormalizer.normalize_date(
                data.get("end_date")
            )
        )

        # Duration handling
        duration_str = DataNormalizer.normalize_string(
            data.get("duration")
        )
        normalized["duration"] = duration_str

        # Parse duration_hours from duration string if not provided
        duration_hours = data.get("duration_hours")

        if duration_hours is None and duration_str:
            duration_hours = DataNormalizer.parse_duration_to_hours(
                duration_str
            )

        normalized["duration_hours"] = duration_hours

        # Certificate identification
        normalized["certificate_id"] = (
            DataNormalizer.normalize_string(
                data.get("certificate_id")
            )
        )

        normalized["verification"] = (
            DataNormalizer.normalize_verification(
                data.get("verification")
            )
        )

        # Included courses
        normalized["included_courses"] = []

        for course in DataNormalizer.normalize_list(
            data.get("included_courses")
        ):
            normalized_course = (
                DataNormalizer.normalize_included_course(course)
            )

            if normalized_course is not None:
                normalized["included_courses"].append(
                    normalized_course
                )

        # Topics
        normalized["topics"] = (
            DataNormalizer.normalize_string_list(
                data.get("topics")
            )
        )

        return normalized

    @staticmethod
    def normalize_certifications(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the complete courses/certifications dataset.
        """

        certifications = []

        for item in data.get("certifications", []):
            if not isinstance(item, dict):
                continue

            certifications.append(
                DataNormalizer.normalize_certification(item)
            )

        return {
            "certifications": certifications
        }

    # ------------------------------------------------------------------
    # Education normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_gpa(
        gpa: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize GPA information.
        """

        if not isinstance(gpa, dict):
            return None

        return {
            "scale": DataNormalizer.normalize_string(
                gpa.get("scale")
            ),
            "year_1": gpa.get("year_1"),
            "year_2": gpa.get("year_2"),
            "year_3": gpa.get("year_3"),
            "year_4": gpa.get("year_4"),
        }

    @staticmethod
    def normalize_academic_project(
        project: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize an academic project.
        """

        if not isinstance(project, dict):
            return None

        return {
            "name": DataNormalizer.normalize_string(
                project.get("name")
            ),
            "description": DataNormalizer.normalize_string(
                project.get("description")
            ),
            "technologies": (
                DataNormalizer.normalize_string_list(
                    project.get("technologies")
                )
            ),
        }

    @staticmethod
    def normalize_education(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize educational information.
        """

        normalized = {}

        string_fields = [
            "degree",
            "university",
            "faculty",
            "department",
            "major",
            "minor",
            "academic_level",
            "graduation_date",
        ]

        for field in string_fields:
            normalized[field] = (
                DataNormalizer.normalize_string(
                    data.get(field)
                )
            )

        normalized["gpa"] = DataNormalizer.normalize_gpa(
            data.get("gpa")
        )

        normalized["academic_achievements"] = (
            DataNormalizer.normalize_string_list(
                data.get("academic_achievements")
            )
        )

        thesis = data.get("thesis")

        if isinstance(thesis, dict):
            normalized["thesis"] = {
                "status": DataNormalizer.normalize_string(
                    thesis.get("status")
                )
            }
        else:
            normalized["thesis"] = None

        normalized["academic_projects"] = []

        for project in DataNormalizer.normalize_list(
            data.get("academic_projects")
        ):
            normalized_project = (
                DataNormalizer.normalize_academic_project(
                    project
                )
            )

            if normalized_project is not None:
                normalized["academic_projects"].append(
                    normalized_project
                )

        normalized["academic_interests"] = (
            DataNormalizer.normalize_string_list(
                data.get("academic_interests")
            )
        )

        return normalized

    # ------------------------------------------------------------------
    # Experience normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_organization(
        organization: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize an organization object.
        """

        if not isinstance(organization, dict):
            return None

        return {
            "name": DataNormalizer.normalize_string(
                organization.get("name")
            ),
            "type": DataNormalizer.normalize_string(
                organization.get("type")
            ),
        }

    @staticmethod
    def normalize_experience(
        experience: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a single experience record.
        """

        normalized = {}

        normalized["id"] = DataNormalizer.normalize_string(
            experience.get("id")
        )

        normalized["organization"] = (
            DataNormalizer.normalize_organization(
                experience.get("organization")
            )
        )

        for field in [
            "role",
            "employment_type",
            "status",
        ]:
            normalized[field] = (
                DataNormalizer.normalize_string(
                    experience.get(field)
                )
            )

        normalized["start_date"] = (
            DataNormalizer.normalize_date(
                experience.get("start_date")
            )
        )

        normalized["end_date"] = (
            DataNormalizer.normalize_date(
                experience.get("end_date")
            )
        )

        # Preserve numeric fields
        normalized["duration_hours"] = experience.get("duration_hours")
        normalized["overall_score"] = experience.get("overall_score")

        normalized["responsibilities"] = (
            DataNormalizer.normalize_string_list(
                experience.get("responsibilities")
            )
        )

        normalized["technologies"] = (
            DataNormalizer.normalize_string_list(
                experience.get("technologies")
            )
        )

        return normalized

    @staticmethod
    def normalize_experiences(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the complete experience dataset.
        """

        experiences = []

        for experience in data.get("experiences", []):
            if not isinstance(experience, dict):
                continue

            experiences.append(
                DataNormalizer.normalize_experience(
                    experience
                )
            )

        return {
            "experiences": experiences
        }

    # ------------------------------------------------------------------
    # Project normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_project(
        project: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a single project.
        """

        return {
            "id": DataNormalizer.normalize_string(
                project.get("id")
            ),
            "name": DataNormalizer.normalize_string(
                project.get("name")
            ),
            "title": DataNormalizer.normalize_string(
                project.get("title")
            ),
            "description": DataNormalizer.normalize_string(
                project.get("description")
            ),
            "technologies": (
                DataNormalizer.normalize_string_list(
                    project.get("technologies")
                )
            ),
            "domains": DataNormalizer.normalize_string_list(
                project.get("domains")
            ),
        }

    @staticmethod
    def normalize_projects(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the complete project dataset.
        """

        projects = []

        for project in data.get("projects", []):
            if not isinstance(project, dict):
                continue

            projects.append(
                DataNormalizer.normalize_project(project)
            )

        return {
            "projects": projects
        }

    # ------------------------------------------------------------------
    # Achievement normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_achievement_certificate(
        certificate: Any,
    ) -> dict[str, Any] | None:
        """
        Normalize an achievement certificate.
        """

        if not isinstance(certificate, dict):
            return None

        return {
            "type": DataNormalizer.normalize_string(
                certificate.get("type")
            ),
            "issuer": DataNormalizer.normalize_string(
                certificate.get("issuer")
            ),
            "reference": DataNormalizer.normalize_string(
                certificate.get("reference")
            ),
            "signatories": (
                DataNormalizer.normalize_string_list(
                    certificate.get("signatories")
                )
            ),
        }

    @staticmethod
    def normalize_achievement(
        achievement: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize a single achievement/activity.
        """

        normalized = {}

        for field in [
            "id",
            "name",
            "type",
            "organizer",
            "event_series",
            "edition",
            "field",
            "participation",
            "achievement",
            "recognition",
            "description",
        ]:
            normalized[field] = (
                DataNormalizer.normalize_string(
                    achievement.get(field)
                )
            )

        normalized["date"] = (
            DataNormalizer.normalize_date(
                achievement.get("date")
            )
        )

        # Preserve year field
        normalized["year"] = achievement.get("year")

        normalized["certificate"] = (
            DataNormalizer.normalize_achievement_certificate(
                achievement.get("certificate")
            )
        )

        return normalized

    @staticmethod
    def normalize_achievements(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize the complete achievements dataset.
        """

        activities = []

        for activity in data.get("activities", []):
            if not isinstance(activity, dict):
                continue

            activities.append(
                DataNormalizer.normalize_achievement(
                    activity
                )
            )

        return {
            "activities": activities
        }

    # ------------------------------------------------------------------
    # Public dispatcher
    # ------------------------------------------------------------------

    def normalize(
        self,
        data: dict[str, Any],
        data_type: str,
    ) -> dict[str, Any]:
        """
        Normalize a dataset according to its type.

        Supported types:
            personal
            education
            certifications (or courses)
            experiences
            projects
            achievements
        """

        if not isinstance(data, dict):
            raise TypeError(
                "Raw dataset must be a dictionary."
            )

        normalizers = {
            "personal": self._normalize_personal,
            "personal_info": self._normalize_personal,  # Alias
            "basic_info": self.normalize_basic_info,
            "education": self.normalize_education,
            "certifications": self.normalize_certifications,
            "courses": self.normalize_certifications,  # Alias for certifications
            "experiences": self.normalize_experiences,
            "experience": self.normalize_experiences,  # Alias
            "projects": self.normalize_projects,
            "achievements": self.normalize_achievements,
            "benefits": self.normalize_benefits,
            "strange_info": self.normalize_strange_info,
        }

        normalizer = normalizers.get(data_type)

        if normalizer is None:
            raise ValueError(
                f"Unsupported dataset type: {data_type}"
            )

        return normalizer(data)

    # ------------------------------------------------------------------
    # Personal information
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_personal(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize personal information.
        """

        normalized = {}

        normalized["bio"] = (
            DataNormalizer.normalize_string(
                data.get("bio")
            )
        )

        for field in [
            "interests",
            "hobbies",
            "goals",
            "personality",
            "strengths",
            "weaknesses",
            "areas_of_interest",
            "career_interests",
            "learning_interests",
            "personal_preferences",
            "fun_facts",
        ]:
            normalized[field] = (
                DataNormalizer.normalize_string_list(
                    data.get(field)
                )
            )

        languages = []

        for language in DataNormalizer.normalize_list(
            data.get("languages")
        ):
            if not isinstance(language, dict):
                continue

            languages.append(
                {
                    "language": (
                        DataNormalizer.normalize_string(
                            language.get("language")
                        )
                    ),
                    "proficiency": (
                        DataNormalizer.normalize_string(
                            language.get("proficiency")
                        )
                    ),
                }
            )

        normalized["languages"] = languages

        return normalized

    @staticmethod
    def normalize_basic_info(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize basic information.
        """

        normalized = {}

        string_fields = [
            "name",
            "full_name",
            "birth_date",
            "city",
            "specialist",
        ]

        for field in string_fields:
            normalized[field] = (
                DataNormalizer.normalize_string(
                    data.get(field)
                )
            )

        return normalized

    # ------------------------------------------------------------------
    # Benefits normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_benefits(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize benefits/value proposition information.
        """

        # The raw data has benefits nested under a "benefits" key
        if "benefits" in data:
            data = data["benefits"]

        normalized = {}

        for field in [
            "professional_value",
            "technical_strengths",
            "problem_solving_capabilities",
            "domain_exposure",
            "professional_advantages",
            "learning_and_growth",
            "collaboration_value",
        ]:
            normalized[field] = (
                DataNormalizer.normalize_string_list(
                    data.get(field)
                )
            )

        # Normalize career direction
        career = data.get("career_direction")
        if isinstance(career, dict):
            normalized["career_direction"] = {
                "primary": DataNormalizer.normalize_string(
                    career.get("primary")
                ),
                "secondary": DataNormalizer.normalize_string_list(
                    career.get("secondary")
                ),
                "long_term_goal": DataNormalizer.normalize_string(
                    career.get("long_term_goal")
                ),
            }
        else:
            normalized["career_direction"] = None

        normalized["unique_value_proposition"] = (
            DataNormalizer.normalize_string(
                data.get("unique_value_proposition")
            )
        )

        return normalized

    # ------------------------------------------------------------------
    # Strange info normalization
    # ------------------------------------------------------------------

    @staticmethod
    def normalize_strange_info(
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize miscellaneous personal information.
        """

        # The raw data has strange_info nested under a "strange_info" key
        if "strange_info" in data:
            data = data["strange_info"]

        normalized = {}

        # Favorite anime
        anime = data.get("favorite_anime")
        if isinstance(anime, dict):
            normalized["favorite_anime"] = {
                "title": DataNormalizer.normalize_string(
                    anime.get("title")
                ),
                "preference_strength": DataNormalizer.normalize_string(
                    anime.get("preference_strength")
                ),
                "description": DataNormalizer.normalize_string(
                    anime.get("description")
                ),
            }
        else:
            normalized["favorite_anime"] = None

        # Favorite foods
        foods = []
        for food in DataNormalizer.normalize_list(
            data.get("favorite_foods")
        ):
            if not isinstance(food, dict):
                continue

            foods.append({
                "id": DataNormalizer.normalize_string(
                    food.get("id", f"food_{food.get('rank', 0)}")
                ),
                "rank": food.get("rank"),
                "name": DataNormalizer.normalize_string(
                    food.get("name")
                ),
            })

        normalized["favorite_foods"] = foods

        # Pre-tech interests
        interests = []
        for interest in DataNormalizer.normalize_list(
            data.get("pre_tech_interests")
        ):
            if not isinstance(interest, dict):
                continue

            interests.append({
                "interest": DataNormalizer.normalize_string(
                    interest.get("interest")
                ),
                "importance": DataNormalizer.normalize_string(
                    interest.get("importance")
                ),
                "description": DataNormalizer.normalize_string(
                    interest.get("description")
                ),
            })

        normalized["pre_tech_interests"] = interests

        # Previous occupations
        occupations = []
        for occupation in DataNormalizer.normalize_list(
            data.get("previous_occupations_and_activities")
        ):
            if not isinstance(occupation, dict):
                continue

            occupations.append({
                "id": DataNormalizer.normalize_string(
                    occupation.get("id", f"occupation_{occupation.get('sequence', 0)}")
                ),
                "role": DataNormalizer.normalize_string(
                    occupation.get("role")
                ),
                "sequence": occupation.get("sequence"),
                "status": DataNormalizer.normalize_string(
                    occupation.get("status")
                ),
            })

        normalized["previous_occupations_and_activities"] = occupations

        # Training career status
        status = data.get("training_career_status")
        if isinstance(status, dict):
            normalized["training_career_status"] = {
                "status": DataNormalizer.normalize_string(
                    status.get("status")
                ),
                "description": DataNormalizer.normalize_string(
                    status.get("description")
                ),
            }
        else:
            normalized["training_career_status"] = None

        # Physical info
        physical = data.get("physical_info")
        if isinstance(physical, dict):
            normalized["physical_info"] = {
                "height_cm": physical.get("height_cm"),
                "weight_kg": physical.get("weight_kg"),
            }
        else:
            normalized["physical_info"] = None

        return normalized
