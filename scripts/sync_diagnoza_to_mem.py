#!/usr/bin/env python3
"""
Synchronizuje diagnoza_surowe_dane.json → claude-mem (lokalnie ~/.claude-mem, nie Git).

Wywoływany automatycznie przez zapisz_odpowiedz.py i backup_diagnoza.py.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "diagnoza_surowe_dane.json"
PROJECT = "ARCHETYPY"
MEMORY_SESSION_ID = "archetypy-diagnoza-ingest"
PROFILE_TITLE = "ARCHETYPY: profil użytkownika z diagnostyki"
QUESTION_TITLE_PREFIX = "ARCHETYPY diagnoza — pytanie "
BASE_EPOCH = 1_770_000_000_000  # stabilne id epoki per pytanie (unikanie duplikatów przy --replace)
WORKER_HOST = os.environ.get("CLAUDE_MEM_WORKER_HOST", "127.0.0.1")
WORKER_PORT = os.environ.get("CLAUDE_MEM_WORKER_PORT", "37777")
MEM_DB = Path.home() / ".claude-mem" / "claude-mem.db"


def _now() -> tuple[str, int]:
    dt = datetime.now(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z"), int(dt.timestamp() * 1000)


def _load_settings_port() -> str | None:
    settings = Path.home() / ".claude-mem" / "settings.json"
    if not settings.exists():
        return None
    try:
        data = json.loads(settings.read_text(encoding="utf-8"))
        env = data.get("env") or data
        port = env.get("CLAUDE_MEM_WORKER_PORT")
        return str(port) if port else None
    except (json.JSONDecodeError, OSError):
        return None


def _worker_base() -> str:
    port = os.environ.get("CLAUDE_MEM_WORKER_PORT") or _load_settings_port() or WORKER_PORT
    host = os.environ.get("CLAUDE_MEM_WORKER_HOST", WORKER_HOST)
    return f"http://{host}:{port}"


def _question_title(qid: int) -> str:
    return f"{QUESTION_TITLE_PREFIX}{qid}"


def _delete_observations(*, question_id: int | None, full_session: bool) -> int:
    if not MEM_DB.exists():
        return 0
    conn = sqlite3.connect(MEM_DB)
    try:
        if full_session:
            cur = conn.execute(
                "DELETE FROM observations WHERE memory_session_id = ?",
                (MEMORY_SESSION_ID,),
            )
        elif question_id is not None:
            cur = conn.execute(
                "DELETE FROM observations WHERE memory_session_id = ? AND (title = ? OR title = ?)",
                (MEMORY_SESSION_ID, _question_title(question_id), PROFILE_TITLE),
            )
        else:
            return 0
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def _observation(
    *,
    title: str,
    subtitle: str,
    facts: list[str],
    narrative: str,
    created_at: str,
    created_at_epoch: int,
    prompt_number: int = 0,
) -> dict:
    # text — treść dla Chroma/search (facts w JSON bywają słabiej trafiane)
    text_body = f"{title}\n{subtitle}\n" + "\n".join(facts)
    return {
        "memory_session_id": MEMORY_SESSION_ID,
        "project": PROJECT,
        "text": text_body,
        "type": "discovery",
        "title": title,
        "subtitle": subtitle,
        "facts": json.dumps(facts, ensure_ascii=False),
        "narrative": narrative,
        "concepts": json.dumps(["user-profile", "archetypy-diagnoza"], ensure_ascii=False),
        "files_read": json.dumps([str(JSON_PATH)], ensure_ascii=False),
        "files_modified": "[]",
        "prompt_number": prompt_number,
        "discovery_tokens": 0,
        "created_at": created_at,
        "created_at_epoch": created_at_epoch,
    }


def _profile_facts(rows: list[dict]) -> list[str]:
    facts: list[str] = []
    ids = {r.get("id") for r in rows if isinstance(r.get("id"), int)}
    max_id = max(ids) if ids else 0
    facts.append(f"Postęp diagnostyki KWML: {len(rows)}/100 wpisów, max id={max_id}.")

    for row in rows:
        rid = row.get("id")
        ans = (row.get("odpowiedz") or "").strip()
        if not ans or rid is None:
            continue
        low = ans.lower()
        if "adhd" in low or "atomoksetyna" in low:
            snippet = ans[:280] + ("…" if len(ans) > 280 else "")
            facts.append(f"ADHD / leki (pyt. {rid}): {snippet}")
        if rid == 43:
            m = re.search(r"~\s*(\d+)\s*kg", ans)
            if m:
                facts.append(f"Waga użytkownika (pyt. 43): ok. {m.group(1)} kg.")
            m = re.search(r"(\d+)\s*cm", ans)
            if m:
                facts.append(f"Wzrost użytkownika (pyt. 43): ok. {m.group(1)} cm.")
            m = re.search(r"(\d+)\s*lat", ans)
            if m:
                facts.append(f"Wiek użytkownika (pyt. 43): {m.group(1)} lat.")
        if rid == 27 and "70 kg" in ans:
            facts.append("Cel wagowy (pyt. 27): ok. 70 kg.")
        if "partnerk" in low or "dziewczyn" in low:
            if rid in (1, 4, 5, 20, 31, 36, 37, 100) or len(ans) > 40:
                facts.append(f"Partnerka / związek (pyt. {rid}): {ans[:200]}{'…' if len(ans) > 200 else ''}")

    return facts


def _profile_obs(rows: list[dict], created_at: str) -> dict:
    return _observation(
        title=PROFILE_TITLE,
        subtitle=f"Profil z {len(rows)} odpowiedzi (auto-sync).",
        facts=_profile_facts(rows),
        narrative=(
            "Zsynchronizowany profil z ankiety KWML. Używaj przy pytaniach typu "
            "„co wiesz o moim ADHD / wadze / partnerce”. Źródło prawdy: diagnoza_surowe_dane.json."
        ),
        created_at=created_at,
        created_at_epoch=BASE_EPOCH,
        prompt_number=0,
    )


def _question_obs(row: dict, created_at: str) -> dict | None:
    rid = row.get("id")
    q = (row.get("pytanie") or "").strip()
    a = (row.get("odpowiedz") or "").strip()
    if rid is None or not a:
        return None
    return _observation(
        title=_question_title(int(rid)),
        subtitle=q[:120] + ("…" if len(q) > 120 else ""),
        facts=[f"Pytanie: {q}", f"Odpowiedź: {a}"],
        narrative=f"Odpowiedź użytkownika — pytanie {rid} (ARCHETYPY / KWML).",
        created_at=created_at,
        created_at_epoch=BASE_EPOCH + int(rid),
        prompt_number=int(rid),
    )


def _build_observations(rows: list[dict], *, question_id: int | None) -> list[dict]:
    created_at, _ = _now()
    if question_id is not None:
        row = next((r for r in rows if r.get("id") == question_id), None)
        if not row:
            return [_profile_obs(rows, created_at)]
        obs = [_profile_obs(rows, created_at)]
        qo = _question_obs(row, created_at)
        if qo:
            obs.append(qo)
        return obs
    out = [_profile_obs(rows, created_at)]
    for row in rows:
        qo = _question_obs(row, created_at)
        if qo:
            out.append(qo)
    return out


def _post_import(observations: list[dict]) -> dict:
    base = _worker_base()
    health = urllib.request.urlopen(f"{base}/api/stats", timeout=5)
    if health.status != 200:
        raise RuntimeError(f"Worker nie odpowiada: {health.status}")

    body = json.dumps({"observations": observations}).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/api/import",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sync_to_mem(*, question_id: int | None = None, replace_all: bool = False, quiet: bool = False) -> int:
    if not JSON_PATH.exists():
        if not quiet:
            print(f"Brak {JSON_PATH.name}", file=sys.stderr)
        return 1

    rows = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        if not quiet:
            print("Ankieta pusta — pomijam sync mem.")
        return 0

    if replace_all:
        deleted = _delete_observations(question_id=None, full_session=True)
        observations = _build_observations(rows, question_id=None)
    elif question_id is not None:
        deleted = _delete_observations(question_id=question_id, full_session=False)
        observations = _build_observations(rows, question_id=question_id)
    else:
        deleted = _delete_observations(question_id=None, full_session=True)
        observations = _build_observations(rows, question_id=None)

    try:
        result = _post_import(observations)
    except urllib.error.URLError as e:
        if not quiet:
            print(f"claude-mem niedostępny ({_worker_base()}): {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        if not quiet:
            print(str(e), file=sys.stderr)
        return 1

    stats = result.get("stats", result)
    if not quiet:
        scope = f"pyt. {question_id}" if question_id else "pełny"
        print(
            f"mem sync ({scope}): usunięto {deleted}, "
            f"zaimportowano {stats.get('observationsImported', len(observations))}."
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync diagnoza JSON → claude-mem")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--replace", action="store_true", help="Usuń starą sesję i zaimportuj wszystko")
    parser.add_argument("--question-id", type=int, metavar="ID", help="Tylko jedno pytanie + profil")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    if not JSON_PATH.exists():
        print(f"Brak {JSON_PATH.name}", file=sys.stderr)
        return 1

    rows = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        print("Ankieta pusta.")
        return 0

    if args.dry_run:
        for fact in _profile_facts(rows):
            print(f"  • {fact}")
        return 0

    if args.question_id is not None:
        return sync_to_mem(question_id=args.question_id, replace_all=False, quiet=args.quiet)
    return sync_to_mem(question_id=None, replace_all=True, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
