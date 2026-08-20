"""
scripts/build_chunks.py

Entry point for building OVI retrieval chunks from the
processed datasets.
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.chunk_builder import ChunkBuilder


def main() -> None:
    """Build chunks for all OVI processed datasets."""

    print("=" * 60)
    print("OVI Chunk Builder")
    print("=" * 60)
    print()

    builder = ChunkBuilder()

    try:
        chunks = builder.build_all()

    except Exception as exc:
        print(f"✗ Error: {exc}")
        sys.exit(1)

    entity_types: dict[str, int] = {}

    for chunk in chunks:
        entity_types[chunk["entity_type"]] = (
            entity_types.get(chunk["entity_type"], 0) + 1
        )

    print(f"Total chunks generated: {len(chunks)}")
    print()
    print("By entity type:")

    for entity_type, count in sorted(entity_types.items()):
        print(f"  - {entity_type}: {count}")

    print()
    print(f"Output: {builder.chunks_dir / 'chunks.jsonl'}")
    print()
    print("=" * 60)
    print("Chunk build complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
