"""
scripts/build_dataset.py

Entry point for building OVI processed datasets.
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

from builders.dataset_builder import DatasetBuilder
from schemas.certification import Certification
from schemas.personal import BasicInfo, PersonalInfo
from schemas.education import Education
from schemas.experience import Experience
from schemas.project import Project
from schemas.achievement import Achievement
from schemas.benefits import Benefits


# Dataset configuration
DATASETS = [
    {
        "filename": "basic_info.json",
        "schema": BasicInfo,
        "collection_key": None,
        "data_type": "basic_info",
        "description": "Basic information",
    },
    {
        "filename": "personal_info.json",
        "schema": PersonalInfo,
        "collection_key": None,
        "data_type": "personal",
        "description": "Personal information",
    },
    {
        "filename": "education.json",
        "schema": Education,
        "collection_key": None,
        "data_type": "education",
        "description": "Education",
    },
    {
        "filename": "courses.json",
        "schema": Certification,
        "collection_key": "certifications",
        "data_type": "certifications",
        "description": "Courses and certifications",
    },
    {
        "filename": "experience.json",
        "schema": Experience,
        "collection_key": "experiences",
        "data_type": "experiences",
        "description": "Professional and training experience",
    },
    {
        "filename": "projects.json",
        "schema": Project,
        "collection_key": "projects",
        "data_type": "projects",
        "description": "Projects",
    },
    {
        "filename": "achievements.json",
        "schema": Achievement,
        "collection_key": "activities",
        "data_type": "achievements",
        "description": "Achievements and activities",
    },
    {
        "filename": "benefits.json",
        "schema": Benefits,
        "collection_key": None,
        "data_type": "benefits",
        "description": "Professional benefits and value proposition",
    },
]


def main() -> None:
    """Build all OVI datasets."""
    
    builder = DatasetBuilder()
    
    print("=" * 60)
    print("OVI Dataset Builder")
    print("=" * 60)
    print()
    
    success_count = 0
    failed_datasets = []
    
    for config in DATASETS:
        filename = config["filename"]
        description = config["description"]
        
        print(f"Processing: {description} ({filename})")
        print(f"  Schema: {config['schema'].__name__}")
        print(f"  Data type: {config['data_type']}")
        
        try:
            builder.build(
                filename=filename,
                schema=config["schema"],
                collection_key=config["collection_key"],
            )
            
            print(f"  ✓ Success")
            success_count += 1
            
        except FileNotFoundError as exc:
            print(f"  ✗ File not found: {exc}")
            failed_datasets.append((filename, str(exc)))
            
        except Exception as exc:
            print(f"  ✗ Error: {exc}")
            failed_datasets.append((filename, str(exc)))
        
        print()
    
    print("=" * 60)
    print(f"Summary: {success_count}/{len(DATASETS)} datasets processed successfully")
    print("=" * 60)
    
    if failed_datasets:
        print()
        print("Failed datasets:")
        for filename, error in failed_datasets:
            print(f"  - {filename}: {error}")
        
        sys.exit(1)
    
    print()
    print("All datasets processed successfully!")


if __name__ == "__main__":
    main()