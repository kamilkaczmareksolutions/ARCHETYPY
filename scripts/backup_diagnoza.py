#!/usr/bin/env python3
"""Backup JSON + pełna synchronizacja claude-mem."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "diagnoza_surowe_dane.json"
DST = ROOT / "diagnoza_surowe_dane.local.json"
SYNC_SCRIPT = ROOT / "scripts" / "sync_diagnoza_to_mem.py"


def main() -> int:
  if not SRC.exists():
    print("Brak diagnoza_surowe_dane.json — pomijam backup.")
    return 0

  try:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
  except json.JSONDecodeError as e:
    print(f"Błąd JSON w {SRC.name}: {e}", file=sys.stderr)
    return 1

  if not isinstance(rows, list) or not rows:
    print("Ankieta pusta — pomijam backup.")
    return 0

  shutil.copy2(SRC, DST)
  print(f"Backup OK: {len(rows)} wpisów → {DST.name}")

  if SYNC_SCRIPT.exists():
    rc = subprocess.run(
      [sys.executable, str(SYNC_SCRIPT), "--replace", "--quiet"],
      cwd=ROOT,
    ).returncode
    if rc == 0:
      print("claude-mem: pełna synchronizacja profilu OK.")
    else:
      print("claude-mem: sync pominięty (worker niedostępny).", file=sys.stderr)

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
