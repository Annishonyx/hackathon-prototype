"""
AICTE Application Validation Assistant - Validation Engine (validator.py)
Implements strict deterministic string normalization and exact rule evaluations
for 1-Day MVP document comparison. No fuzzy matching or external APIs.
"""

import re
import string
from datetime import date, datetime
from typing import Dict, List, Optional, Any
from dateutil import parser as date_parser


def normalize_text(val: Optional[str]) -> str:
    """
    Applies strict deterministic normalization:
    1. Null/Empty check: returns empty string if None or whitespace.
    2. Lowercase conversion.
    3. Punctuation removal: strips ASCII punctuation and symbols.
    4. Whitespace collapse: converts internal consecutive whitespace/tabs/newlines
       to a single space, and strips leading/trailing whitespace.
    """
    if not val:
        return ""
    # Convert to lowercase string
    text = str(val).lower()
    # Replace punctuation characters with spaces to avoid unintentionally joining words
    # e.g., "Tech. & Science" -> "tech    science" -> "tech science"
    text = re.sub(r'[' + re.escape(string.punctuation) + r']', ' ', text)
    # Collapse multiple whitespace characters into a single space and strip
    return " ".join(text.split())


def parse_date_to_object(val: Any) -> Optional[date]:
    """
    Converts various date representations (str, date, datetime) into a standard datetime.date object.
    Returns None if parsing fails.
    """
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, str):
        val_str = val.strip()
        if not val_str:
            return None
        try:
            dt = date_parser.parse(val_str, fuzzy=False)
            return dt.date()
        except Exception:
            try:
                dt = date_parser.parse(val_str, fuzzy=True)
                return dt.date()
            except Exception:
                return None
    return None


def validate_application(
    app_institution: str,
    app_ref: str,
    app_review_date: Any,
    doc_institution: Optional[str],
    doc_ref: Optional[str],
    doc_validity_date: Any,
    doc_present: bool = True
) -> Dict[str, Any]:
    """
    Evaluates application metadata against document metadata deterministically.

    Flags:
    - Missing document: Document missing, missing key manual fallback fields, or date unparseable.
    - Name mismatch: Normalized institution names do not match.
    - Reference number mismatch: Normalized NOC reference numbers do not match.
    - Expired document: Document validity date is strictly earlier than application review date.

    Returns:
        dict containing:
        - 'flags': list of triggered flag strings
        - 'status': "Manual review required" (if >=1 flag) or "All automated checks passed" (if 0 flags)
        - 'normalized_app_institution': normalized string
        - 'normalized_doc_institution': normalized string
        - 'normalized_app_ref': normalized string
        - 'normalized_doc_ref': normalized string
        - 'parsed_app_date': datetime.date object
        - 'parsed_doc_date': datetime.date object
        - 'details': per-field status breakdown dictionary
    """
    flags: List[str] = []

    parsed_app_date = parse_date_to_object(app_review_date)
    parsed_doc_date = parse_date_to_object(doc_validity_date)

    norm_app_inst = normalize_text(app_institution)
    norm_doc_inst = normalize_text(doc_institution)

    norm_app_ref = normalize_text(app_ref)
    norm_doc_ref = normalize_text(doc_ref)

    # 1. Missing Document Evaluation
    is_missing = False
    if not doc_present:
        is_missing = True
    elif not norm_doc_inst or not norm_doc_ref or parsed_doc_date is None:
        is_missing = True

    if is_missing:
        flags.append("Missing document")

    # 2. Detailed Checks
    name_matched = False
    ref_matched = False
    is_expired = False

    if doc_present and norm_doc_inst:
        if norm_app_inst != norm_doc_inst:
            flags.append("Name mismatch")
        else:
            name_matched = True
    elif not is_missing:
        flags.append("Name mismatch")

    if doc_present and norm_doc_ref:
        if norm_app_ref != norm_doc_ref:
            flags.append("Reference number mismatch")
        else:
            ref_matched = True
    elif not is_missing:
        flags.append("Reference number mismatch")

    if doc_present and parsed_doc_date and parsed_app_date:
        if parsed_doc_date < parsed_app_date:
            flags.append("Expired document")
            is_expired = True

    # Deduplicate flags preserving order
    unique_flags = list(dict.fromkeys(flags))

    # Overall Status determination
    if len(unique_flags) > 0:
        overall_status = "Manual review required"
    else:
        overall_status = "All automated checks passed"

    return {
        "flags": unique_flags,
        "status": overall_status,
        "normalized_app_institution": norm_app_inst,
        "normalized_doc_institution": norm_doc_inst,
        "normalized_app_ref": norm_app_ref,
        "normalized_doc_ref": norm_doc_ref,
        "parsed_app_date": parsed_app_date,
        "parsed_doc_date": parsed_doc_date,
        "details": {
            "name_match": name_matched,
            "ref_match": ref_matched,
            "is_expired": is_expired,
            "is_missing": is_missing
        }
    }