"""
scripts/build_pipeline.py

Runs the complete OVI data pipeline end to end:

    raw/  -> processed/  -> chunks/  -> indexes/

Reuses the existing per-stage entry points (build_dataset,
build_chunks, build_embeddings) rather than duplicating their
logic. Each stage is run in order; the pipeline stops at the
first stage that fails, except the embeddings stage, whose
absence (e.g. no network access to download model weights) is
reported as a clear blocker without failing the datasets/chunks
work that already succeeded.
"""

import sys
from pathlib import Path

# Configure terminal output encoding to prevent UnicodeEncodeError on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.chunk_builder import ChunkBuilder
from builders.dataset_builder import DatasetBuilder
from builders.embeddings_builder import EmbeddingBackendUnavailable, EmbeddingsBuilder
from schemas.achievement import Achievement
from schemas.benefits import Benefits
from schemas.certification import Certification
from schemas.education import Education
from schemas.experience import Experience
from schemas.personal import BasicInfo, PersonalInfo
from schemas.project import Project


DATASETS = [
    {
        "filename": "basic_info.json",
        "schema": BasicInfo,
        "collection_key": None,
        "description": "Basic information",
    },
    {
        "filename": "personal_info.json",
        "schema": PersonalInfo,
        "collection_key": None,
        "description": "Personal information",
    },
    {
        "filename": "education.json",
        "schema": Education,
        "collection_key": None,
        "description": "Education",
    },
    {
        "filename": "courses.json",
        "schema": Certification,
        "collection_key": "certifications",
        "description": "Courses and certifications",
    },
    {
        "filename": "experience.json",
        "schema": Experience,
        "collection_key": "experiences",
        "description": "Professional and training experience",
    },
    {
        "filename": "projects.json",
        "schema": Project,
        "collection_key": "projects",
        "description": "Projects",
    },
    {
        "filename": "achievements.json",
        "schema": Achievement,
        "collection_key": "activities",
        "description": "Achievements and activities",
    },
    {
        "filename": "benefits.json",
        "schema": Benefits,
        "collection_key": None,
        "description": "Professional benefits and value proposition",
    },
]


def run_dataset_stage() -> bool:

    print("-" * 60)
    print("Stage 1/3: Dataset normalization + validation")
    print("-" * 60)

    builder = DatasetBuilder()
    failed = []

    for config in DATASETS:
        try:
            builder.build(
                filename=config["filename"],
                schema=config["schema"],
                collection_key=config["collection_key"],
            )
            print(f"  ✓ {config['description']}")

        except Exception as exc:
            print(f"  ✗ {config['description']}: {exc}")
            failed.append(config["filename"])

    print()

    if failed:
        print(f"Dataset stage failed for: {', '.join(failed)}")
        return False

    print(f"Dataset stage complete: {len(DATASETS)}/{len(DATASETS)} datasets.")
    print()
    return True


def run_chunk_stage() -> list | None:

    print("-" * 60)
    print("Stage 2/3: Chunk building")
    print("-" * 60)

    builder = ChunkBuilder()

    try:
        chunks = builder.build_all()

    except Exception as exc:
        print(f"  ✗ Chunk stage failed: {exc}")
        print()
        return None

    print(f"  ✓ {len(chunks)} chunks written to {builder.chunks_dir / 'chunks.jsonl'}")
    print()
    return chunks


def run_embeddings_stage() -> dict | None:

    print("-" * 60)
    print("Stage 3/3: Embedding generation")
    print("-" * 60)

    builder = EmbeddingsBuilder()

    try:
        summary = builder.build_all()

    except EmbeddingBackendUnavailable as exc:
        print("  ✗ Embedding backend unavailable (BLOCKED, not failed):")
        print(f"    {exc}")
        print()
        return None

    except Exception as exc:
        print(f"  ✗ Embeddings stage failed: {exc}")
        print()
        return None

    print(
        f"  ✓ {summary['count']} embeddings "
        f"(dim={summary['dimension']}) written to "
        f"{summary['embeddings_path']}"
    )
    print()
    return summary


def main() -> None:

    print("=" * 60)
    print("OVI Full Pipeline: raw -> processed -> chunks -> indexes")
    print("=" * 60)
    print()

    if not run_dataset_stage():
        sys.exit(1)

    chunks = run_chunk_stage()

    if chunks is None:
        sys.exit(1)

    embeddings_summary = run_embeddings_stage()

    print("=" * 60)

    if embeddings_summary is None:
        print("Pipeline partially complete: datasets + chunks OK, "
              "embeddings BLOCKED (see message above).")
        print("=" * 60)
        sys.exit(2)

    print("Pipeline complete: datasets + chunks + embeddings OK.")
    print("=" * 60)


if __name__ == "__main__":
    main()
