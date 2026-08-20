"""
scripts/query.py

Retrieval smoke test / manual query CLI for the OVI vector index.

Usage:

    python scripts/query.py "What certifications does Ahmed have?"

    python scripts/query.py --smoke-test

Requires dataset/indexes/ to already exist (run
scripts/build_embeddings.py first).
"""

import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.embeddings_builder import EmbeddingBackendUnavailable
from builders.retriever import Retriever


SMOKE_TEST_TOP_K = 5

SMOKE_TEST_QUERIES = [
    "What certifications does Ahmed have?",
    "Which certifications did he complete on Coursera?",
    "What did he study related to Generative AI?",
    "What projects has he worked on?",
    "What experience does he have with Python?",
    "What did he study at university?",
]


def print_results(query: str, results: list[dict]) -> None:

    print(f"Query: {query}")

    for result in results:
        title = (
            result["content"].get("title")
            or result["content"].get("name")
            or result["content"].get("role")
            or result["content"].get("degree")
            or result["entity_id"]
        )

        print(
            f"  [{result['boosted_score']:.3f} raw={result['score']:.3f}] "
            f"{result['chunk_id']} ({result['entity_type']}): {title}"
        )

    print()


def run_smoke_test(retriever: Retriever) -> None:

    for query in SMOKE_TEST_QUERIES:
        results = retriever.search(query, top_k=SMOKE_TEST_TOP_K)
        print_results(query, results)


def main() -> None:

    retriever = Retriever()

    try:
        if len(sys.argv) > 1 and sys.argv[1] != "--smoke-test":
            query = " ".join(sys.argv[1:])
            results = retriever.search(query, top_k=5)
            print_results(query, results)
        else:
            run_smoke_test(retriever)

    except EmbeddingBackendUnavailable as exc:
        print(f"✗ Embedding backend unavailable: {exc}")
        sys.exit(2)

    except FileNotFoundError as exc:
        print(f"✗ {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
