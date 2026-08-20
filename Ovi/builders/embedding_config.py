"""
builders/embedding_config.py

Central configuration for the OVI embeddings stage.

Kept as a single source of truth so the model name/dimension
are never duplicated between the builder, the index reader,
and retrieval/query code.
"""

from __future__ import annotations

# sentence-transformers model id (local, no API key required).
# Small, fast, well-suited to short structured records like these.
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Output dimensionality of the model above. Used to validate
# generated embeddings without having to reload the model.
EMBEDDING_DIMENSION = 384

# Embeddings are L2-normalized at storage time so that a plain
# dot product is equivalent to cosine similarity at query time.
NORMALIZE_EMBEDDINGS = True
