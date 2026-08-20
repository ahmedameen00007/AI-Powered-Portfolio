"""
tests/test_normalizer.py

Tests for the DataNormalizer functionality.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from builders.normalizer import DataNormalizer


def test_normalize_url():
    """Test URL normalization extracts URLs from Markdown links."""
    
    # Test markdown URL extraction
    markdown_url = "[https://coursera.org/verify/UJC3QS4IZECD](https://coursera.org/verify/UJC3QS4IZECD)"
    result = DataNormalizer.normalize_url(markdown_url)
    assert result == "https://coursera.org/verify/UJC3QS4IZECD", f"Expected clean URL, got: {result}"
    
    # Test plain URL
    plain_url = "https://coursera.org/verify/UJC3QS4IZECD"
    result = DataNormalizer.normalize_url(plain_url)
    assert result == "https://coursera.org/verify/UJC3QS4IZECD", f"Expected same URL, got: {result}"
    
    # Test None
    result = DataNormalizer.normalize_url(None)
    assert result is None, f"Expected None, got: {result}"
    
    print("✓ URL normalization tests passed")


def test_parse_duration_to_hours():
    """Test duration string parsing to hours."""
    
    test_cases = [
        ("6 hours 26 minutes", 6.433333333333334),
        ("6 hours", 6.0),
        ("45 minutes", 0.75),
        ("2h 30m", 2.5),
        ("90 minutes", 1.5),
        ("1h", 1.0),
        (None, None),
        ("", None),
    ]
    
    for duration_str, expected_hours in test_cases:
        result = DataNormalizer.parse_duration_to_hours(duration_str)
        
        if expected_hours is None:
            assert result is None, f"Expected None for '{duration_str}', got: {result}"
        else:
            assert result is not None, f"Expected {expected_hours} for '{duration_str}', got None"
            assert abs(result - expected_hours) < 0.001, f"Expected {expected_hours} for '{duration_str}', got: {result}"
    
    print("✓ Duration parsing tests passed")


def test_normalize_string():
    """Test string normalization."""
    
    # Test whitespace trimming
    assert DataNormalizer.normalize_string("  hello  ") == "hello"
    
    # Test empty string to None
    assert DataNormalizer.normalize_string("") is None
    assert DataNormalizer.normalize_string("   ") is None
    
    # Test None
    assert DataNormalizer.normalize_string(None) is None
    
    print("✓ String normalization tests passed")


def test_normalize_string_list():
    """Test string list normalization."""
    
    # Test list normalization
    result = DataNormalizer.normalize_string_list(["  Python  ", "RAG", "  ", None, "AI"])
    assert result == ["Python", "RAG", "AI"], f"Expected cleaned list, got: {result}"
    
    # Test single string to list
    result = DataNormalizer.normalize_string_list("Python")
    assert result == ["Python"], f"Expected single-item list, got: {result}"
    
    # Test None
    result = DataNormalizer.normalize_string_list(None)
    assert result == [], f"Expected empty list, got: {result}"
    
    print("✓ String list normalization tests passed")


def test_normalize_certification():
    """Test certification record normalization."""
    
    raw_cert = {
        "id": "cert_001",
        "title": "  Neural Networks  ",
        "type": "Course",
        "provider": "DeepLearning.AI",
        "platform": "Coursera",
        "completion_date": "2025-07-18",
        "duration": "6 hours 26 minutes",
        "verification": {
            "id": "ABC123",
            "url": "[https://example.com](https://example.com)"
        },
        "included_courses": ["Course 1", "Course 2"],
        "topics": ["AI", "ML"]
    }
    
    normalized = DataNormalizer.normalize_certification(raw_cert)
    
    # Check title is trimmed
    assert normalized["title"] == "Neural Networks", f"Expected trimmed title, got: {normalized['title']}"
    
    # Check duration parsing
    assert normalized["duration_hours"] is not None, "Expected duration_hours to be calculated"
    assert abs(normalized["duration_hours"] - 6.433333333333334) < 0.001
    
    # Check URL extraction
    assert normalized["verification"]["url"] == "https://example.com", f"Expected clean URL, got: {normalized['verification']['url']}"
    
    # Check included courses
    assert len(normalized["included_courses"]) == 2
    assert normalized["included_courses"][0]["title"] == "Course 1"
    
    print("✓ Certification normalization tests passed")


if __name__ == "__main__":
    print("Running DataNormalizer tests...")
    print()
    
    test_normalize_url()
    test_parse_duration_to_hours()
    test_normalize_string()
    test_normalize_string_list()
    test_normalize_certification()
    
    print()
    print("=" * 60)
    print("All tests passed!")
    print("=" * 60)
