"""
builders/serializer.py

Deterministic structured-content -> text serializer.

Responsibilities:
- Convert a chunk's structured `content` dict into a clean,
  human-readable key/value text representation.
- This text is used ONLY as embedding input. The structured
  `content` remains the canonical data.
- Never invent, reorder unpredictably, or drop information;
  the serialization must be deterministic and reproducible.

The serializer does NOT:
- Modify the structured content.
- Perform normalization or validation.
- Call any embedding model.
"""

from __future__ import annotations

from typing import Any

# Fields excluded from the serialized text body.
#
# 'id' is intentionally excluded: it carries no retrieval-relevant
# meaning and is already available as `chunk_id` / `entity_id`.
_EXCLUDED_KEYS = {"id"}


# A short natural-language lead sentence per entity_type, prepended
# to the serialized text right after the heading.
#
# Why this exists: short, label-heavy chunks (e.g. just "Certification"
# as a heading) can collide semantically with unrelated chunks that
# happen to share vocabulary (e.g. "training_career_status" mentions
# "training", which embeds close to "training programs" inside
# certifications). An explicit disambiguating sentence gives the
# embedding model a clearer, less ambiguous signal to anchor on.
_LEAD_SENTENCES: dict[str, str] = {
    "certification": (
        "This is one of Ahmed's certifications, courses, "
        "specializations, or training programs he completed."
    ),
    "experience": (
        "This is one of Ahmed's professional or training work "
        "experiences."
    ),
    "project": (
        "This is one of Ahmed's personal, professional, or "
        "academic projects."
    ),
    "achievement": (
        "This is one of Ahmed's achievements, activities, "
        "or competitions."
    ),
    "education": "This is Ahmed's university education record.",
    "benefits": (
        "This describes Ahmed's professional strengths and "
        "value as a candidate."
    ),
    "basic_info": "This is Ahmed's basic biographical information.",
    "personal_info": (
        "This is Ahmed's personal profile: interests, hobbies, "
        "and goals."
    ),
    "favorite_anime": (
        "This is Ahmed's favorite anime, a personal preference "
        "unrelated to his career."
    ),
    "favorite_food": (
        "This is one of Ahmed's favorite foods, a personal "
        "preference unrelated to his career."
    ),
    "pre_tech_interests": (
        "These are interests Ahmed had before entering the "
        "technology field."
    ),
    "previous_occupation": (
        "This is a past occupation or activity Ahmed did before "
        "his current AI career, not a certification or current job."
    ),
    "training_career_status": (
        "This describes Ahmed's past status as a fitness trainer "
        "(gym, boxing, calisthenics) - unrelated to his AI "
        "certifications or training courses."
    ),
    "physical_info": (
        "This is Ahmed's physical information such as height "
        "and weight."
    ),
}


# ----------------------------------------------------------------------
# Key humanization
# ----------------------------------------------------------------------

def humanize_key(key: str) -> str:
    """
    Convert a snake_case field name into a readable label.

    Example:
        "duration_hours" -> "Duration Hours"
    """

    return " ".join(
        part.capitalize() if not part.isupper() else part
        for part in key.split("_")
    )


def humanize_type(entity_type: str) -> str:
    """
    Convert an entity_type identifier into a readable heading.

    Example:
        "previous_occupation" -> "Previous Occupation"
    """

    return humanize_key(entity_type)


# ----------------------------------------------------------------------
# Value rendering
# ----------------------------------------------------------------------

def _render_scalar(value: Any) -> str:
    return str(value)


def _render_dict_lines(
    data: dict[str, Any],
    indent: int = 0,
) -> list[str]:
    """
    Render a dict as indented "Key: value" lines, recursing into
    nested dicts and lists. Skips None values and empty containers.
    """

    lines: list[str] = []
    pad = "  " * indent

    for key, value in data.items():

        if key in _EXCLUDED_KEYS and indent == 0:
            continue

        if value is None:
            continue

        if isinstance(value, dict):
            if not value:
                continue

            lines.append(f"{pad}{humanize_key(key)}:")
            lines.extend(_render_dict_lines(value, indent=indent + 1))

        elif isinstance(value, list):
            if not value:
                continue

            lines.append(f"{pad}{humanize_key(key)}:")
            lines.extend(_render_list_lines(value, indent=indent + 1))

        else:
            lines.append(
                f"{pad}{humanize_key(key)}: {_render_scalar(value)}"
            )

    return lines


def _render_list_lines(
    items: list[Any],
    indent: int = 0,
) -> list[str]:
    """
    Render a list as "- " bullet lines. Dict items are rendered as
    a compact single-line summary when they contain a natural label
    field (title/name/role/interest), otherwise as nested lines.
    """

    lines: list[str] = []
    pad = "  " * indent

    for item in items:

        if isinstance(item, dict):
            label_key = next(
                (
                    key
                    for key in ("title", "name", "role", "interest", "language")
                    if key in item and item[key]
                ),
                None,
            )

            if label_key is not None:
                extra_bits = []

                if "hours" in item and item["hours"] is not None:
                    extra_bits.append(f"{item['hours']} hours")

                if "proficiency" in item and item["proficiency"]:
                    extra_bits.append(str(item["proficiency"]))

                suffix = f" ({', '.join(extra_bits)})" if extra_bits else ""

                lines.append(f"{pad}- {item[label_key]}{suffix}")

            else:
                nested = _render_dict_lines(item, indent=indent + 1)

                if nested:
                    lines.append(f"{pad}-")
                    lines.extend(nested)

        elif isinstance(item, list):
            lines.extend(_render_list_lines(item, indent=indent))

        else:
            lines.append(f"{pad}- {_render_scalar(item)}")

    return lines


# ----------------------------------------------------------------------
# Public entry point
# ----------------------------------------------------------------------

def serialize_content(
    entity_type: str,
    content: dict[str, Any],
) -> str:
    """
    Deterministically serialize a chunk's structured content into
    clean text suitable as embedding input.

    The output always starts with a humanized entity-type heading,
    followed by "Field: value" lines (with simple nested indentation
    for dicts/lists), in the original field order.
    """

    lines = [humanize_type(entity_type)]

    lead_sentence = _LEAD_SENTENCES.get(entity_type)

    if lead_sentence:
        lines.append(lead_sentence)

    lines.extend(_render_dict_lines(content, indent=0))

    return "\n".join(lines)
