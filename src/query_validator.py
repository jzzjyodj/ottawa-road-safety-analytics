"""Validate LLM-generated SQL before execution against DuckDB.

Checks performed in order:
1. UNSUPPORTED QUERY pass-through — returns valid immediately.
2. Strip trailing semicolon from the SQL string.
3. Multiple statement detection — blocks semicolon-separated batches.
4. Unsafe keyword check — blocks DROP, DELETE, INSERT, UPDATE, ALTER, CREATE, TRUNCATE.
5. Table reference validation — SQL must reference collisions_clean.
"""
import re
from typing import Tuple

UNSUPPORTED = "UNSUPPORTED QUERY"

UNSAFE_KEYWORDS = [
    "DROP", "DELETE", "INSERT", "UPDATE",
    "ALTER", "CREATE", "TRUNCATE",
]

ALLOWED_TABLE = "collisions_clean"


class ValidationError(Exception):
    """Raised when generated SQL fails a validation check."""


def validate_sql(sql: str) -> Tuple[bool, str, str]:
    """Validate a generated SQL string before execution against DuckDB.

    Returns a tuple of (is_valid, sql, reason). If valid, reason is an empty
    string. If invalid, is_valid is False and reason describes why.
    """
    # Check 1 — UNSUPPORTED QUERY pass-through
    if sql.strip() == UNSUPPORTED:
        return (True, sql, "")

    # Check 2 — Strip trailing semicolon
    sql = sql.strip().rstrip(";").strip()

    # Check 3 — Multiple statement detection
    statements = [s.strip() for s in sql.split(";") if s.strip()]
    if len(statements) > 1:
        return (False, sql, "Multiple SQL statements are not permitted")

    # Check 4 — Unsafe keyword check
    tokens = re.findall(r'\b\w+\b', sql.upper())
    for keyword in UNSAFE_KEYWORDS:
        if keyword in tokens:
            return (False, sql, f"Unsafe SQL detected: {keyword} operations are not permitted")

    # Check 5 — Table reference validation
    if ALLOWED_TABLE not in sql.lower():
        return (False, sql, f"SQL must query the {ALLOWED_TABLE} table only")

    return (True, sql, "")
