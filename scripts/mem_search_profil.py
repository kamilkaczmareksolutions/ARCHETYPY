#!/usr/bin/env python3
"""Fallback: szukaj w obserwacjach profilu ARCHETYPY (SQLite), gdy MCP search nie trafia."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

MEM_DB = Path.home() / ".claude-mem" / "claude-mem.db"
SESSION = "archetypy-diagnoza-ingest"
PROJECT = "ARCHETYPY"


def main() -> int:
    parser = argparse.ArgumentParser(description="Szukaj w zsynchronizowanym profilu claude-mem")
    parser.add_argument("query", help="np. ADHD, waga, partnerka")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    if not MEM_DB.exists():
        print("[]")
        return 1

    terms = [t for t in args.query.lower().split() if len(t) > 2]
    if not terms:
        terms = [args.query.lower()]

    conn = sqlite3.connect(MEM_DB)
    try:
        rows = conn.execute(
            """
            SELECT id, title, facts, text
            FROM observations
            WHERE project = ? AND memory_session_id = ?
            ORDER BY
              CASE WHEN title LIKE 'ARCHETYPY: profil%' THEN 0 ELSE 1 END,
              id DESC
            """,
            (PROJECT, SESSION),
        ).fetchall()
    finally:
        conn.close()

    hits: list[dict] = []
    for oid, title, facts, text in rows:
        blob = f"{title} {facts or ''} {text or ''}".lower()
        if any(t in blob for t in terms):
            hits.append({"id": oid, "title": title})
            if len(hits) >= args.limit:
                break

    print(json.dumps(hits, ensure_ascii=False))
    return 0 if hits else 1


if __name__ == "__main__":
    sys.exit(main())
