"""
builders/retriever.py

Query-time retrieval over the OVI vector index.

    query
      ↓
    query embedding
      ↓
    vector similarity search (cosine, via dot product on
    L2-normalized vectors)
      ↓
    retrieved chunks
      ↓
    metadata / entity information

This module only reads dataset/indexes/; it does not regenerate
or modify the index.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from builders.embedding_config import EMBEDDING_MODEL_NAME
from builders.embeddings_builder import EmbeddingBackendUnavailable

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Keyword -> entity_type boost map.
#
# Why this exists: this corpus is small (~40 chunks) and cleanly
# partitioned by entity_type, and most real questions about a
# portfolio name their target type explicitly ("certifications",
# "projects", "experience"...). A general-purpose embedding model
# on short, templated, structurally-repetitive text (every
# certification chunk shares the same field labels) often can't
# separate types reliably on semantics alone - see e.g. a
# "certifications" query ranking a fitness-trainer chunk above
# actual certifications purely because both mention "training".
#
# This boost is a light nudge, not a hard filter: it adds a fixed
# bonus to the cosine score for chunks whose entity_type matches a
# keyword found in the query, so embeddings still decide ranking
# *within* a type (e.g. which certification is most relevant).
# Base keyword boost applied when a query keyword matches the entity_type.
_KEYWORD_BOOST = 0.30

_TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "basic_info": ("who is ahmed", "biography", "bio", "specialist"),
    "personal_info": ("personal", "personality", "interest", "goal", "about ahmed"),
    "certification": ("certificat", "course", "specialization", "coursera", "training program", "cert"),
    "project": ("project", "proj", "built", "developed", "created", "system he made"),
    "experience": ("experience", "experi", "internship", "job", "work at", "worked at", "employment", "position", "career"),
    "education": ("university", "degree", "major", "gpa", "study", "studied", "faculty", "college", "collage", "school", "department"),
    "achievement": ("achievement", "competition", "activity", "activities", "award", "prize"),
    "benefits": ("strength", "value proposition", "career direction", "benefit", "advantage", "why hire", "candidate"),
}


def _keyword_boost(query: str, entity_type: str) -> float:
    """
    Return a similarity bonus if the query text contains a keyword
    associated with `entity_type`, otherwise 0.0.
    """

    query_lower = query.lower()
    keywords = _TYPE_KEYWORDS.get(entity_type, ())

    if any(keyword in query_lower for keyword in keywords):
        return _KEYWORD_BOOST

    return 0.0


class Retriever:
    """
    Loads the persisted embedding index and answers similarity
    queries against it.
    """

    def __init__(
        self,
        indexes_dir: str | Path | None = None,
        chunks_dir: str | Path | None = None,
        model_name: str = EMBEDDING_MODEL_NAME,
    ) -> None:

        self.indexes_dir = Path(indexes_dir) if indexes_dir else _PROJECT_ROOT / "dataset/indexes"
        self.chunks_dir = Path(chunks_dir) if chunks_dir else _PROJECT_ROOT / "dataset/chunks"
        self.model_name = model_name

        self._model = None
        self._vectors = None
        self._manifest: list[dict[str, Any]] | None = None
        self._chunks_by_id: dict[str, dict[str, Any]] | None = None

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_model(self):

        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer

        except ImportError as exc:
            raise EmbeddingBackendUnavailable(
                "sentence-transformers is not installed."
            ) from exc

        try:
            self._model = SentenceTransformer(self.model_name)

        except Exception as exc:
            raise EmbeddingBackendUnavailable(
                f"Could not load embedding model '{self.model_name}': {exc}"
            ) from exc

        return self._model

    def _load_index(self) -> None:

        import numpy as np

        if self._vectors is not None:
            return

        embeddings_path = self.indexes_dir / "embeddings.npy"
        manifest_path = self.indexes_dir / "manifest.jsonl"

        if not embeddings_path.exists() or not manifest_path.exists():
            raise FileNotFoundError(
                "Embedding index not found. Run "
                "scripts/build_embeddings.py first."
            )

        self._vectors = np.load(embeddings_path)

        manifest = []

        with manifest_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    manifest.append(json.loads(line))

        self._manifest = manifest

    def _load_chunks(self) -> None:

        if self._chunks_by_id is not None:
            return

        chunks_path = self.chunks_dir / "chunks.jsonl"

        chunks_by_id = {}

        with chunks_path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    chunk = json.loads(line)
                    chunks_by_id[chunk["chunk_id"]] = chunk

        self._chunks_by_id = chunks_by_id

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Embed `query` and return the top_k most similar chunks.

        Each result contains: chunk_id, entity_id, entity_type,
        source_file, score, and the chunk's structured content.
        """

        import numpy as np

        self._load_index()
        self._load_chunks()

        model = self._load_model()

        query_vector = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True,
        )[0].astype("float32")

        scores = self._vectors @ query_vector

        boosted_scores = scores.copy()

        for index, entry in enumerate(self._manifest):
            boosted_scores[index] += _keyword_boost(query, entry["entity_type"])

        top_indices = np.argsort(-boosted_scores)[:top_k]

        results = []

        for index in top_indices:
            entry = self._manifest[index]
            chunk = self._chunks_by_id.get(entry["chunk_id"], {})

            results.append(
                {
                    "chunk_id": entry["chunk_id"],
                    "entity_id": entry["entity_id"],
                    "entity_type": entry["entity_type"],
                    "source_file": entry["source_file"],
                    "score": float(scores[index]),
                    "boosted_score": float(boosted_scores[index]),
                    "content": chunk.get("content"),
                }
            )

        return results

    def search_multi(
        self,
        queries: list[str],
        top_k: int = 15,
    ) -> list[dict]:
        """
        Run search() on each query variant, merge results, and deduplicate.

        This is used by the Query Expansion pipeline: the QueryExpander returns
        2-3 English search variants, and this method unions their results so
        that a chunk found by *any* variant is included in the context.

        Deduplication strategy: keep the highest boosted_score a chunk achieves
        across all variants. Final list is sorted by that max score descending,
        capped at top_k.

        Args:
            queries: List of English search query strings (1-3 items typical).
            top_k:   Maximum number of unique chunks to return.

        Returns:
            Merged, deduplicated, re-ranked list of chunk result dicts.
        """
        best: dict[str, dict] = {}  # chunk_id -> best result dict

        for q in queries:
            # Retrieve top_k from each variant so that niche chunks surface
            for result in self.search(q, top_k=top_k):
                cid = result["chunk_id"]
                if cid not in best or result["boosted_score"] > best[cid]["boosted_score"]:
                    best[cid] = result

        merged = sorted(best.values(), key=lambda r: r["boosted_score"], reverse=True)
        return merged[:top_k]

    def get_entity_counts(self) -> dict[str, int]:
        """
        Return a dict mapping each entity_type to its total count in the full
        knowledge base (as persisted in the manifest).

        This is used by the answer generator to inform the user when only a
        partial list is shown in a response (e.g. "Ahmed has 13 certifications
        in total — here are the most relevant ones. Ask for more if needed.").
        """
        self._load_index()

        counts: dict[str, int] = {}
        for entry in self._manifest:  # type: ignore[union-attr]
            etype = entry.get("entity_type", "unknown")
            counts[etype] = counts.get(etype, 0) + 1

        return counts

