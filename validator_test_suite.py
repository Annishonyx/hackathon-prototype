"""
AICTE Application Validation Assistant - Test Suite (tests/test_validator.py)
Executes the five mandatory test cases against validator.py and database.py.
"""

import os
from datetime import date
import pytest

from validator import normalize_text, validate_application
from database import init_db, insert_review_decision, get_record_by_id


def test_case_1_canonical_demo_case():
    """
    Test Case 1: Canonical Demo Case Verification
    Inputs:
      - Application: 'Demo Institute of Technology', 'NOC/DEMO/0001', '2026-10-24'
      - NOC Document: 'Demo Institute of Tech. & Science', 'NOC/DEMO/0001', '2026-03-31'
    Expected Output:
      - Triggered flags: 'Name mismatch' and 'Expired document'
      - 'Reference number mismatch' must NOT be flagged (exact normalized match)
      - Overall Status: 'Manual review required'
    """
    app_inst = "Demo Institute of Technology"
    app_ref = "NOC/DEMO/0001"
    app_review_date = date(2026, 10, 24)

    doc_inst = "Demo Institute of Tech. & Science"
    doc_ref = "NOC/DEMO/0001"
    doc_validity = date(2026, 3, 31)

    result = validate_application(
        app_institution=app_inst,
        app_ref=app_ref,
        app_review_date=app_review_date,
        doc_institution=doc_inst,
        doc_ref=doc_ref,
        doc_validity_date=doc_validity,
        doc_present=True
    )

    flags = result["flags"]
    assert "Name mismatch" in flags, "Expected 'Name mismatch' due to Tech. & Science vs Technology"
    assert "Expired document" in flags, "Expected 'Expired document' because 31 Mar 2026 < 24 Oct 2026"
    assert "Reference number mismatch" not in flags, "Reference number NOC/DEMO/0001 must match"
    assert "Missing document" not in flags
    assert result["status"] == "Manual review required"
    assert result["details"]["ref_match"] is True
    assert result["details"]["name_match"] is False
    assert result["details"]["is_expired"] is True


def test_case_2_exact_match_clean_pass():
    """
    Test Case 2: Exact Match Verification (Clean Pass)
    Inputs:
      - Application: 'Apex Engineering College', 'NOC/2026/999', '2026-10-24'
      - Document: '  apex engineering college! ', 'noc/2026/999', '2027-06-30'
    Expected Output:
      - Normalization eliminates spaces, punctuation, case differences
      - Document validity > review date
      - Flags: [] (empty)
      - Overall Status: 'All automated checks passed'
    """
    result = validate_application(
        app_institution="Apex Engineering College",
        app_ref="NOC/2026/999",
        app_review_date=date(2026, 10, 24),
        doc_institution="  apex engineering college! ",
        doc_ref="noc/2026/999",
        doc_validity_date="30 June 2027",
        doc_present=True
    )

    assert result["flags"] == []
    assert result["status"] == "All automated checks passed"
    assert result["details"]["name_match"] is True
    assert result["details"]["ref_match"] is True
    assert result["details"]["is_expired"] is False


def test_case_3_reference_number_mismatch():
    """
    Test Case 3: Reference Number Mismatch Detection
    Inputs:
      - Application: 'National Institute of Science', 'NOC/NORTH/100', '2026-10-24'
      - Document: 'National Institute of Science', 'NOC/SOUTH/200', '2027-10-24'
    Expected Output:
      - Triggered flag: 'Reference number mismatch' only
      - Name and date pass
      - Overall Status: 'Manual review required'
    """
    result = validate_application(
        app_institution="National Institute of Science",
        app_ref="NOC/NORTH/100",
        app_review_date=date(2026, 10, 24),
        doc_institution="National Institute of Science",
        doc_ref="NOC/SOUTH/200",
        doc_validity_date=date(2027, 10, 24),
        doc_present=True
    )

    assert "Reference number mismatch" in result["flags"]
    assert "Name mismatch" not in result["flags"]
    assert "Expired document" not in result["flags"]
    assert result["status"] == "Manual review required"
    assert result["details"]["ref_match"] is False
    assert result["details"]["name_match"] is True


def test_case_4_missing_document_handling():
    """
    Test Case 4: Missing Document Flag Handling
    Inputs:
      - Application: 'Vanguard Institute', 'NOC/VNG/01', '2026-10-24'
      - Document: None / Empty strings, doc_present=False or blank fallbacks
    Expected Output:
      - Triggered flag: 'Missing document'
      - Overall Status: 'Manual review required'
    """
    result_absent = validate_application(
        app_institution="Vanguard Institute",
        app_ref="NOC/VNG/01",
        app_review_date=date(2026, 10, 24),
        doc_institution="",
        doc_ref="",
        doc_validity_date=None,
        doc_present=False
    )
    assert "Missing document" in result_absent["flags"]
    assert result_absent["status"] == "Manual review required"

    result_no_date = validate_application(
        app_institution="Vanguard Institute",
        app_ref="NOC/VNG/01",
        app_review_date=date(2026, 10, 24),
        doc_institution="Vanguard Institute",
        doc_ref="NOC/VNG/01",
        doc_validity_date="",
        doc_present=True
    )
    assert "Missing document" in result_no_date["flags"]
    assert result_no_date["status"] == "Manual review required"


def test_case_5_database_persistence(tmp_path):
    """
    Test Case 5: SQLite Database Persistence Integration
    Action:
      - Initialize DB in temporary directory
      - Insert a complete review decision ('Request correction')
      - Query record back by row ID
    Expected Output:
      - Record retrieved with identical metadata, JSON flags deserialized, and correct reviewer decision
    """
    test_db = os.path.join(tmp_path, "test_aicte.db")
    init_db(test_db)

    inserted_id = insert_review_decision(
        app_institution="Demo Institute of Technology",
        app_ref_number="NOC/DEMO/0001",
        app_review_date="2026-10-24",
        doc_source_type="Canonical Demo Case",
        doc_institution="Demo Institute of Tech. & Science",
        doc_ref_number="NOC/DEMO/0001",
        doc_validity_date="2026-03-31",
        flags=["Name mismatch", "Expired document"],
        status="Manual review required",
        reviewer_decision="Request correction",
        reviewer_comments="Institution name on NOC differs from application; certificate expired on 31 Mar 2026.",
        db_path=test_db
    )

    assert inserted_id > 0

    record = get_record_by_id(inserted_id, db_path=test_db)
    assert record is not None
    assert record["id"] == inserted_id
    assert record["app_institution"] == "Demo Institute of Technology"
    assert record["app_ref_number"] == "NOC/DEMO/0001"
    assert record["reviewer_decision"] == "Request correction"
    assert record["status"] == "Manual review required"
    assert "Name mismatch" in record["flags"]
    assert "Expired document" in record["flags"]
    assert "NOC differs from application" in record["reviewer_comments"]