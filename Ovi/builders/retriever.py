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


class BM25Retriever:
    """
    A self-contained BM25 keyword search fallback.

    Used when sentence-transformers is not available (e.g. Vercel serverless).
    Reads directly from the committed dataset/chunks/chunks.jsonl file —
    no network access, no ML models, no extra dependencies required.
    """

    def __init__(self, chunks_dir: Path) -> None:
        self._chunks: list[dict[str, Any]] = []
        chunks_path = chunks_dir / "chunks.jsonl"
        with chunks_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self._chunks.append(json.loads(line))

        self._N = len(self._chunks)
        self._tf: list[dict[str, float]] = []
        self._df: dict[str, int] = {}
        self._dl: list[int] = []
        self._build_index()

    # ── BM25 helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        import re
        return re.findall(r"[a-z0-9]+", text.lower())

    @staticmethod
    def _chunk_text(chunk: dict[str, Any]) -> str:
        content = chunk.get("content", {})
        if isinstance(content, dict):
            return " ".join(str(v) for v in content.values() if v)
        return str(content or "")

    def _build_index(self) -> None:
        import math
        for chunk in self._chunks:
            tokens = self._tokenize(self._chunk_text(chunk))
            self._dl.append(len(tokens))
            tf: dict[str, float] = {}
            for t in tokens:
                tf[t] = tf.get(t, 0) + 1
            self._tf.append(tf)
            for t in set(tokens):
                self._df[t] = self._df.get(t, 0) + 1
        self._avgdl = (sum(self._dl) / self._N) if self._N else 1

    def _bm25_score(self, query_tokens: list[str], doc_idx: int,
                    k1: float = 1.5, b: float = 0.75) -> float:
        import math
        score = 0.0
        tf = self._tf[doc_idx]
        dl = self._dl[doc_idx]
        for t in query_tokens:
            if t not in tf:
                continue
            n = self._df.get(t, 0)
            idf = math.log((self._N - n + 0.5) / (n + 0.5) + 1)
            tf_norm = (tf[t] * (k1 + 1)) / (tf[t] + k1 * (1 - b + b * dl / self._avgdl))
            score += idf * tf_norm
        return score

    # ── Public search ─────────────────────────────────────────────────────────

    def search(
        self,
        query: str,
        top_k: int = 5,
        entity_type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        query_tokens = self._tokenize(query)
        scores = [
            self._bm25_score(query_tokens, i) + _keyword_boost(query, self._chunks[i].get("entity_type", ""))
            for i in range(self._N)
        ]
        if entity_type_filter:
            for i, chunk in enumerate(self._chunks):
                if chunk.get("entity_type") != entity_type_filter:
                    scores[i] = 0.0

        top_indices = sorted(range(self._N), key=lambda i: scores[i], reverse=True)[:top_k]
        results = []
        for idx in top_indices:
            chunk = self._chunks[idx]
            results.append({
                "chunk_id": chunk.get("chunk_id", str(idx)),
                "entity_id": chunk.get("entity_id", ""),
                "entity_type": chunk.get("entity_type", ""),
                "source_file": chunk.get("source_file", ""),
                "score": scores[idx],
                "boosted_score": scores[idx],
                "content": chunk.get("content"),
            })
        return results

    def search_multi(
        self,
        queries: list[str],
        top_k: int = 15,
    ) -> list[dict[str, Any]]:
        best: dict[str, dict] = {}
        for q in queries:
            for result in self.search(q, top_k=top_k):
                cid = result["chunk_id"]
                if cid not in best or result["boosted_score"] > best[cid]["boosted_score"]:
                    best[cid] = result
        merged = sorted(best.values(), key=lambda r: r["boosted_score"], reverse=True)
        return merged[:top_k]

    def get_entity_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for chunk in self._chunks:
            etype = chunk.get("entity_type", "unknown")
            counts[etype] = counts.get(etype, 0) + 1
        return counts


class Retriever:
    """
    Loads the persisted embedding index and answers similarity
    queries against it.

    Falls back to BM25Retriever automatically when sentence-transformers
    is not available (e.g. Vercel serverless), with no network calls needed.
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
        self._bm25: BM25Retriever | None = None   # populated when ST unavailable
        self._use_bm25 = False

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_model(self):
        if self._model is not None or self._use_bm25:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        except ImportError:
            # sentence-transformers not available — switch to BM25 mode
            self._use_bm25 = True
            self._bm25 = BM25Retriever(self.chunks_dir)
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

        Falls back to BM25 automatically when sentence-transformers is
        unavailable (no embedding model or network required).

        Each result contains: chunk_id, entity_id, entity_type,
        source_file, score, and the chunk's structured content.
        """

        # Trigger model loading (sets _use_bm25 if ST is unavailable)
        self._load_model()

        # BM25 fallback: delegate fully to BM25Retriever
        if self._use_bm25 and self._bm25 is not None:
            return self._bm25.search(query, top_k=top_k)

        import numpy as np

        self._load_index()
        self._load_chunks()

        model = self._model

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
        Delegates to BM25Retriever.search_multi when in BM25 mode.
        """
        # BM25 fallback path
        self._load_model()
        if self._use_bm25 and self._bm25 is not None:
            return self._bm25.search_multi(queries, top_k=top_k)

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
        """
        # BM25 fallback path
        self._load_model()
        if self._use_bm25 and self._bm25 is not None:
            return self._bm25.get_entity_counts()

        self._load_index()

        counts: dict[str, int] = {}
        for entry in self._manifest:  # type: ignore[union-attr]
            etype = entry.get("entity_type", "unknown")
            counts[etype] = counts.get(etype, 0) + 1

        return counts

