"""
AICTE Application Validation Assistant - Local SQLite Persistence (database.py)
Stores reviewer decisions locally in 'aicte_records.db' using standard library sqlite3.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = "aicte_records.db"


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Creates a connection to the SQLite database with dictionary-like row access."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initializes the SQLite review_decisions table if it does not exist."""
    conn = get_db_connection(db_path)
    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS review_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                app_institution TEXT NOT NULL,
                app_ref_number TEXT NOT NULL,
                app_review_date TEXT NOT NULL,
                doc_source_type TEXT NOT NULL,
                doc_institution TEXT,
                doc_ref_number TEXT,
                doc_validity_date TEXT,
                flags TEXT NOT NULL,              -- JSON encoded list of triggered flag strings
                status TEXT NOT NULL,             -- Overall review status
                reviewer_decision TEXT NOT NULL,  -- 'Accept for review', 'Request correction', 'Escalate'
                reviewer_comments TEXT
            );
        """)
    conn.close()


def insert_review_decision(
    app_institution: str,
    app_ref_number: str,
    app_review_date: str,
    doc_source_type: str,
    doc_institution: Optional[str],
    doc_ref_number: Optional[str],
    doc_validity_date: Optional[str],
    flags: List[str],
    status: str,
    reviewer_decision: str,
    reviewer_comments: Optional[str] = "",
    db_path: str = DEFAULT_DB_PATH
) -> int:
    """
    Inserts a completed application validation decision into the local SQLite database.
    Returns the newly inserted row ID.
    """
    init_db(db_path)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    flags_json = json.dumps(flags)

    conn = get_db_connection(db_path)
    with conn:
        cursor = conn.execute("""
            INSERT INTO review_decisions (
                created_at,
                app_institution,
                app_ref_number,
                app_review_date,
                doc_source_type,
                doc_institution,
                doc_ref_number,
                doc_validity_date,
                flags,
                status,
                reviewer_decision,
                reviewer_comments
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            created_at,
            (app_institution or "").strip(),
            (app_ref_number or "").strip(),
            str(app_review_date),
            doc_source_type,
            (doc_institution or "").strip(),
            (doc_ref_number or "").strip(),
            str(doc_validity_date or ""),
            flags_json,
            status,
            reviewer_decision,
            (reviewer_comments or "").strip()
        ))
        inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id


def get_record_by_id(record_id: int, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieves a single validation decision record by primary key."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.execute("SELECT * FROM review_decisions WHERE id = ?", (record_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return None
    data = dict(row)
    data["flags"] = json.loads(data["flags"])
    return data


def get_recent_decisions(limit: int = 5, db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Retrieves the most recent saved review records."""
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.execute("SELECT * FROM review_decisions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    records = []
    for r in rows:
        d = dict(r)
        d["flags"] = json.loads(d["flags"])
        records.append(d)
    return records