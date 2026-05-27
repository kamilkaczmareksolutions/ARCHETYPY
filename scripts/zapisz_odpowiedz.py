#!/usr/bin/env python3
"""Dopisz jedną odpowiedź diagnostyczną do diagnoza_surowe_dane.json + sync claude-mem."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "diagnoza_surowe_dane.json"
SYNC_SCRIPT = ROOT / "scripts" / "sync_diagnoza_to_mem.py"


def _sync_mem(qid: int) -> None:
    if not SYNC_SCRIPT.exists():
        return
    subprocess.run(
        [sys.executable, str(SYNC_SCRIPT), "--question-id", str(qid), "--quiet"],
        cwd=ROOT,
        check=False,
    )


def main() -> None:
    if len(sys.argv) != 4:
        print('Użycie: python scripts/zapisz_odpowiedz.py <id> "<pytanie>" "<odpowiedz>"')
        sys.exit(1)

    qid = int(sys.argv[1])
    pytanie = sys.argv[2]
    odpowiedz = sys.argv[3]

    if DATA_FILE.exists():
        rows = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    else:
        rows = []

    rows = [r for r in rows if r.get("id") != qid]
    rows.append({"id": qid, "pytanie": pytanie, "odpowiedz": odpowiedz})
    rows.sort(key=lambda r: r["id"])

    DATA_FILE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Zapisano id={qid}. Łącznie wpisów: {len(rows)}/100")

    _sync_mem(qid)


if __name__ == "__main__":
  main()
