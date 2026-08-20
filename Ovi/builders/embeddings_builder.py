"""
builders/embeddings_builder.py

Embeddings builder for the OVI retrieval pipeline.

Pipeline stage:

    dataset/chunks/chunks.jsonl
        ↓
    Embeddings Builder
        ↓
    dataset/indexes/embeddings.npy      (float32, N x dim)
    dataset/indexes/manifest.jsonl      (chunk_id, entity_id, entity_type,
                                          source_file, metadata; row i of
                                          the manifest corresponds to row i
                                          of the embedding matrix)
    dataset/indexes/index_config.json   (model name, dimension, count)

Uses a local sentence-transformers model (no API key required).
The model name/dimension live in builders/embedding_config.py so
they are never duplicated across the builder and the retriever.

If the embedding model cannot be loaded (e.g. no network access
to download model weights, or the dependency is not installed),
this builder raises EmbeddingBackendUnavailable rather than
fabricating embeddings.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from builders.embedding_config import (
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL_NAME,
    NORMALIZE_EMBEDDINGS,
)


class EmbeddingBackendUnavailable(Exception):
    """
    Raised when the embedding model/backend cannot be loaded.

    This is a hard stop, not a fallback trigger: the pipeline must
    never fabricate embeddings when the real backend is unavailable.
    """


class EmbeddingsBuilder:
    """
    Generates one embedding per chunk using a local sentence-transformers
    model and writes the result to dataset/indexes/.
    """

    def __init__(
        self,
        chunks_dir: str | Path = "dataset/chunks",
        indexes_dir: str | Path = "dataset/indexes",
        model_name: str = EMBEDDING_MODEL_NAME,
    ) -> None:

        self.chunks_dir = Path(chunks_dir)
        self.indexes_dir = Path(indexes_dir)
        self.model_name = model_name

        self.indexes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._model = None

    # ------------------------------------------------------------------
    # Model loading
    # ------------------------------------------------------------------

    def _load_model(self):

        if self._model is not None:
            return self._model

        try:
            from sentence_transformers import SentenceTransformer

        except ImportError as exc:
            raise EmbeddingBackendUnavailable(
                "sentence-transformers is not installed. "
                "Install it with: pip install sentence-transformers"
            ) from exc

        try:
            self._model = SentenceTransformer(self.model_name)

        except Exception as exc:
            raise EmbeddingBackendUnavailable(
                f"Could not load embedding model '{self.model_name}'. "
                f"This usually means there is no network access to "
                f"download the model weights (first run requires "
                f"downloading from huggingface.co), or the model id "
                f"is invalid. Original error: {exc}"
            ) from exc

        return self._model

    # ------------------------------------------------------------------
    # Load chunks
    # ------------------------------------------------------------------

    def load_chunks(
        self,
        filename: str = "chunks.jsonl",
    ) -> list[dict[str, Any]]:

        path = self.chunks_dir / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Chunks file not found: {path}. "
                f"Run scripts/build_chunks.py first."
            )

        chunks = []

        with path.open("r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if line:
                    chunks.append(json.loads(line))

        return chunks

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------

    def build_all(
        self,
        chunks_filename: str = "chunks.jsonl",
    ) -> dict[str, Any]:
        """
        Generate embeddings for every chunk and persist them.

        Returns a summary dict with counts and output paths.
        """

        import numpy as np

        chunks = self.load_chunks(chunks_filename)

        if not chunks:
            raise ValueError("No chunks found; nothing to embed.")

        model = self._load_model()

        texts = [chunk["text"] for chunk in chunks]

        vectors = model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=NORMALIZE_EMBEDDINGS,
            convert_to_numpy=True,
        )

        vectors = np.asarray(vectors, dtype="float32")

        if vectors.shape[0] != len(chunks):
            raise RuntimeError(
                "Embedding count does not match chunk count "
                f"({vectors.shape[0]} != {len(chunks)})."
            )

        if vectors.shape[1] != EMBEDDING_DIMENSION:
            raise RuntimeError(
                f"Unexpected embedding dimension {vectors.shape[1]}; "
                f"expected {EMBEDDING_DIMENSION}. Update "
                f"builders/embedding_config.py if the model changed."
            )

        embeddings_path = self.indexes_dir / "embeddings.npy"
        manifest_path = self.indexes_dir / "manifest.jsonl"
        config_path = self.indexes_dir / "index_config.json"

        np.save(embeddings_path, vectors)

        with manifest_path.open("w", encoding="utf-8") as file:
            for row_index, chunk in enumerate(chunks):
                manifest_entry = {
                    "row": row_index,
                    "chunk_id": chunk["chunk_id"],
                    "entity_id": chunk["entity_id"],
                    "entity_type": chunk["entity_type"],
                    "source_file": chunk["source_file"],
                    "metadata": chunk["metadata"],
                }

                file.write(json.dumps(manifest_entry, ensure_ascii=False))
                file.write("\n")

        config = {
            "model_name": self.model_name,
            "dimension": int(vectors.shape[1]),
            "count": int(vectors.shape[0]),
            "normalized": NORMALIZE_EMBEDDINGS,
        }

        with config_path.open("w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False, indent=2)

        return {
            "count": int(vectors.shape[0]),
            "dimension": int(vectors.shape[1]),
            "embeddings_path": str(embeddings_path),
            "manifest_path": str(manifest_path),
            "config_path": str(config_path),
        }
