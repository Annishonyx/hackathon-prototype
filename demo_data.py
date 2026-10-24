"""
AICTE Application Validation Assistant - Demo Data Fixtures
Predefined demo datasets strictly for evaluation and prototype testing.
Contains no real applicant, institutional, or government records.
"""

from datetime import date
from typing import Dict, Any

# Canonical Demo Case (from requirements)
# Triggers: Name mismatch, Expired document, Ref match -> Manual review required
CANONICAL_DEMO_CASE: Dict[str, Any] = {
    "key": "canonical",
    "label": "Canonical Demo Case (Mismatched Name & Expired)",
    "app": {
        "institution": "Demo Institute of Technology",
        "ref_number": "NOC/DEMO/0001",
        "review_date": date(2026, 10, 24)
    },
    "doc": {
        "institution": "Demo Institute of Tech. & Science",
        "ref_number": "NOC/DEMO/0001",
        "validity_date": date(2026, 3, 31),
        "doc_present": True
    },
    "expected": {
        "flags": ["Name mismatch", "Expired document"],
        "status": "Manual review required",
        "ref_match": True,
        "name_match": False,
        "is_expired": True
    }
}

# Clean Pass Demo Case
# Triggers: 0 flags -> All automated checks passed
CLEAN_PASS_DEMO_CASE: Dict[str, Any] = {
    "key": "clean_pass",
    "label": "Clean-Pass Demo Case (Exact Match & Valid)",
    "app": {
        "institution": "Apex Engineering College",
        "ref_number": "NOC/2026/999",
        "review_date": date(2026, 10, 24)
    },
    "doc": {
        "institution": "  apex engineering college! ",
        "ref_number": "noc/2026/999",
        "validity_date": date(2027, 6, 30),
        "doc_present": True
    },
    "expected": {
        "flags": [],
        "status": "All automated checks passed",
        "ref_match": True,
        "name_match": True,
        "is_expired": False
    }
}

# Reference Number Mismatch Demo Case
REFERENCE_MISMATCH_DEMO_CASE: Dict[str, Any] = {
    "key": "ref_mismatch",
    "label": "Reference Number Mismatch Case",
    "app": {
        "institution": "National Institute of Science",
        "ref_number": "NOC/NORTH/100",
        "review_date": date(2026, 10, 24)
    },
    "doc": {
        "institution": "National Institute of Science",
        "ref_number": "NOC/SOUTH/200",
        "validity_date": date(2027, 10, 24),
        "doc_present": True
    },
    "expected": {
        "flags": ["Reference number mismatch"],
        "status": "Manual review required",
        "ref_match": False,
        "name_match": True,
        "is_expired": False
    }
}

DEMO_PRESETS = {
    "Canonical Demo Case (Mismatched Name & Expired)": CANONICAL_DEMO_CASE,
    "Clean-Pass Demo Case (Exact Match & Valid)": CLEAN_PASS_DEMO_CASE,
    "Reference Number Mismatch Case": REFERENCE_MISMATCH_DEMO_CASE
}