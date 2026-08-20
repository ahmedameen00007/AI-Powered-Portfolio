"""
scripts/build_embeddings.py

Entry point for generating embeddings from OVI chunks.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.embeddings_builder import EmbeddingBackendUnavailable, EmbeddingsBuilder


def main() -> None:
    """Build embeddings for all OVI chunks."""

    print("=" * 60)
    print("OVI Embeddings Builder")
    print("=" * 60)
    print()

    builder = EmbeddingsBuilder()

    try:
        summary = builder.build_all()

    except EmbeddingBackendUnavailable as exc:
        print("✗ Embedding backend unavailable.")
        print()
        print(f"  {exc}")
        print()
        print("No embeddings were fabricated. Chunk generation is")
        print("unaffected and already complete in dataset/chunks/.")
        sys.exit(2)

    except FileNotFoundError as exc:
        print(f"✗ {exc}")
        sys.exit(1)

    except Exception as exc:
        print(f"✗ Error: {exc}")
        sys.exit(1)

    print(f"Embeddings generated: {summary['count']}")
    print(f"Embedding dimension:  {summary['dimension']}")
    print()
    print(f"Embeddings: {summary['embeddings_path']}")
    print(f"Manifest:   {summary['manifest_path']}")
    print(f"Config:     {summary['config_path']}")
    print()
    print("=" * 60)
    print("Embeddings build complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
