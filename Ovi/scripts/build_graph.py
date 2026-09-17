"""
scripts/build_graph.py

Build the OVI Knowledge Graph from processed datasets.
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

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from graph.graph_builder import GraphBuilder


def main() -> None:
    """Build the OVI Knowledge Graph."""
    
    # Create builder
    builder = GraphBuilder(
        processed_dir=project_root / "dataset" / "processed"
    )
    
    # Build the graph
    builder.build()
    
    # Export to JSON
    output_path = project_root / "dataset" / "graph" / "knowledge_graph.json"
    builder.export_to_json(output_path)
    
    print()
    print("=" * 60)
    print("Knowledge Graph build complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
