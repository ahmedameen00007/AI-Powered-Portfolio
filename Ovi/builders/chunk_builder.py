"""
builders/chunk_builder.py

Entity-level chunk builder for the OVI retrieval pipeline.

Pipeline stage:

    dataset/processed/
        ↓
    Chunk Builder
        ↓
    dataset/chunks/chunks.jsonl

Chunking strategy:

    1 meaningful entity = 1 chunk

For collection files (certifications, experiences, projects,
achievements) each record already carries a stable `id` and
becomes its own chunk.

For single-record files with no internal id (basic_info,
personal_info, education, benefits) the whole file is one
coherent entity and becomes a single chunk, keyed by a stable
synthetic id derived from the data type.

`strange_info.json` is a container of several unrelated
sub-entities (favorite anime, favorite foods, pre-tech interests,
previous occupations, training status, physical info). Each
sub-entity is chunked individually so that unrelated questions
("what's your favorite food?" vs "what did you do before tech?")
retrieve focused, relevant chunks instead of one large blob.

The builder does NOT:
- Normalize or validate source data (already done upstream).
- Generate embeddings.
- Invent or drop information.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from builders.serializer import serialize_content
from schemas.chunk import Chunk

# Top-level value types kept as chunk metadata (used for filtering,
# not embedded as text). Nested dicts/lists are intentionally
# excluded from metadata to avoid duplicating the full content.
_METADATA_SCALAR_TYPES = (str, int, float, bool)


class ChunkBuilder:
    """
    Builds entity-level retrieval chunks from processed OVI datasets.
    """

    def __init__(
        self,
        processed_dir: str | Path = "dataset/processed",
        chunks_dir: str | Path = "dataset/chunks",
    ) -> None:

        self.processed_dir = Path(processed_dir)
        self.chunks_dir = Path(chunks_dir)

        self.chunks_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ------------------------------------------------------------------
    # Load
    # ------------------------------------------------------------------

    def load_processed(
        self,
        filename: str,
    ) -> dict[str, Any]:

        path = self.processed_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Processed dataset not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    # ------------------------------------------------------------------
    # Metadata extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_metadata(
        entity_type: str,
        source_file: str,
        content: dict[str, Any],
    ) -> dict[str, Any]:

        metadata: dict[str, Any] = {
            "entity_type": entity_type,
            "source_file": source_file,
        }

        for key, value in content.items():
            if key == "id":
                continue

            if isinstance(value, _METADATA_SCALAR_TYPES) or value is None:
                metadata[key] = value

        return metadata

    # ------------------------------------------------------------------
    # Single chunk construction
    # ------------------------------------------------------------------

    def _make_chunk(
        self,
        chunk_id: str,
        entity_id: str,
        entity_type: str,
        source_file: str,
        content: dict[str, Any],
    ) -> dict[str, Any]:

        text = serialize_content(
            entity_type=entity_type,
            content=content,
        )

        metadata = self._extract_metadata(
            entity_type=entity_type,
            source_file=source_file,
            content=content,
        )

        chunk = Chunk(
            chunk_id=chunk_id,
            entity_id=entity_id,
            entity_type=entity_type,
            source_file=source_file,
            content=content,
            text=text,
            metadata=metadata,
        )

        return chunk.model_dump(mode="json")

    # ------------------------------------------------------------------
    # Collection files (1 record = 1 chunk, record already has an id)
    # ------------------------------------------------------------------

    def build_collection_chunks(
        self,
        source_file: str,
        records: list[dict[str, Any]],
        entity_type: str,
    ) -> list[dict[str, Any]]:

        chunks = []

        for record in records:
            entity_id = record["id"]

            chunks.append(
                self._make_chunk(
                    chunk_id=entity_id,
                    entity_id=entity_id,
                    entity_type=entity_type,
                    source_file=source_file,
                    content=record,
                )
            )

        return chunks

    # ------------------------------------------------------------------
    # Single-record files (whole file = 1 chunk, synthetic id)
    # ------------------------------------------------------------------

    def build_single_chunk(
        self,
        source_file: str,
        data: dict[str, Any],
        entity_type: str,
        entity_id: str,
    ) -> dict[str, Any]:

        return self._make_chunk(
            chunk_id=entity_id,
            entity_id=entity_id,
            entity_type=entity_type,
            source_file=source_file,
            content=data,
        )

    # ------------------------------------------------------------------
    # strange_info.json (mixed sub-entities)
    # ------------------------------------------------------------------

    def build_strange_info_chunks(
        self,
        source_file: str,
        data: dict[str, Any],
    ) -> list[dict[str, Any]]:

        chunks: list[dict[str, Any]] = []

        if data.get("favorite_anime"):
            chunks.append(
                self._make_chunk(
                    chunk_id="favorite_anime",
                    entity_id="favorite_anime",
                    entity_type="favorite_anime",
                    source_file=source_file,
                    content=data["favorite_anime"],
                )
            )

        for food in data.get("favorite_foods", []):
            chunks.append(
                self._make_chunk(
                    chunk_id=food["id"],
                    entity_id=food["id"],
                    entity_type="favorite_food",
                    source_file=source_file,
                    content=food,
                )
            )

        if data.get("pre_tech_interests"):
            chunks.append(
                self._make_chunk(
                    chunk_id="pre_tech_interests",
                    entity_id="pre_tech_interests",
                    entity_type="pre_tech_interests",
                    source_file=source_file,
                    content={"interests": data["pre_tech_interests"]},
                )
            )

        for occupation in data.get("previous_occupations_and_activities", []):
            chunks.append(
                self._make_chunk(
                    chunk_id=occupation["id"],
                    entity_id=occupation["id"],
                    entity_type="previous_occupation",
                    source_file=source_file,
                    content=occupation,
                )
            )

        if data.get("training_career_status"):
            chunks.append(
                self._make_chunk(
                    chunk_id="training_career_status",
                    entity_id="training_career_status",
                    entity_type="training_career_status",
                    source_file=source_file,
                    content=data["training_career_status"],
                )
            )

        if data.get("physical_info"):
            chunks.append(
                self._make_chunk(
                    chunk_id="physical_info",
                    entity_id="physical_info",
                    entity_type="physical_info",
                    source_file=source_file,
                    content=data["physical_info"],
                )
            )

        return chunks

    # ------------------------------------------------------------------
    # Save
    # ------------------------------------------------------------------

    def save_chunks(
        self,
        chunks: list[dict[str, Any]],
        filename: str = "chunks.jsonl",
    ) -> Path:

        path = self.chunks_dir / filename

        with path.open("w", encoding="utf-8") as file:
            for chunk in chunks:
                file.write(json.dumps(chunk, ensure_ascii=False))
                file.write("\n")

        return path

    # ------------------------------------------------------------------
    # Build all
    # ------------------------------------------------------------------

    def build_all(self) -> list[dict[str, Any]]:
        """
        Build chunks for every processed OVI dataset and write the
        result to dataset/chunks/chunks.jsonl.
        """

        all_chunks: list[dict[str, Any]] = []

        # Single-record files with no internal id.
        single_files = [
            ("basic_info.json", "basic_info", "basic_info"),
            ("personal_info.json", "personal_info", "personal_info"),
            ("education.json", "education", "education"),
            ("benefits.json", "benefits", "benefits"),
        ]

        for filename, entity_type, entity_id in single_files:
            data = self.load_processed(filename)

            all_chunks.append(
                self.build_single_chunk(
                    source_file=filename,
                    data=data,
                    entity_type=entity_type,
                    entity_id=entity_id,
                )
            )

        # Collection files (record already has a stable id).
        collection_files = [
            ("courses.json", "certifications", "certification"),
            ("experience.json", "experiences", "experience"),
            ("projects.json", "projects", "project"),
            ("achievements.json", "activities", "achievement"),
        ]

        for filename, collection_key, entity_type in collection_files:
            data = self.load_processed(filename)
            records = data[collection_key]

            all_chunks.extend(
                self.build_collection_chunks(
                    source_file=filename,
                    records=records,
                    entity_type=entity_type,
                )
            )

        self.save_chunks(all_chunks)

        return all_chunks
