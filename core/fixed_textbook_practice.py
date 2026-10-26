"""Fixed textbook practice: textbook rows that have no dynamic Generator but must still be usable on the student practice page.

A row is listed in ``configs/fixed_textbook_practice.json`` with a ``mode``:

* ``graded``   - a reviewed reference answer exists (independently derived, evidence recorded in the entry) and the payload carries a normal
                 answer contract, so the shared checker grades it exactly like a generated question;
* ``ungraded`` - no reliable automatic grading: the question, handwriting canvas and a verified step-by-step reference solution are offered and
                 no verdict, streak, mastery or mistake record is produced (``check_mode = ungraded_self_study``).

An entry is bound to the Stage 1 stem by SHA-256: if the textbook row is changed, the entry stops applying (it never grades a different question).
Nothing here writes to the database; the Stage 1 rows are only read.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[1] / "configs" / "fixed_textbook_practice.json"
_cache: dict[str, Any] = {"mtime": None, "entries": {}}


def stem_sha256(problem_text: str) -> str:
    return hashlib.sha256(str(problem_text or "").encode("utf-8")).hexdigest()


def load_entries() -> dict[int, dict[str, Any]]:
    try:
        mtime = CONFIG_PATH.stat().st_mtime_ns
    except OSError:
        return {}
    if _cache["mtime"] != mtime:
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            entries = {int(k): v for k, v in (data.get("entries") or {}).items() if isinstance(v, dict) and v.get("mode") in ("graded", "ungraded")}
        except (OSError, ValueError):
            entries = {}
        _cache.update(mtime=mtime, entries=entries)
    return _cache["entries"]


def entry_for_row(row: Any) -> dict[str, Any] | None:
    """The entry for a TextbookExample row, only if the row still carries the reviewed stem and the same skill."""
    entry = load_entries().get(int(getattr(row, "id", 0) or 0))
    if not entry:
        return None
    if str(getattr(row, "skill_id", "")) != str(entry.get("skill_id")) or stem_sha256(getattr(row, "problem_text", "")) != entry.get("problem_text_sha256"):
        return None
    return entry


def entries_for_skill(skill_id: str, rows: list[Any]) -> list[dict[str, Any]]:
    """Selector items for the practice page (id, label, graded) in textbook order."""
    out = []
    for row in sorted(rows, key=lambda r: r.id):
        entry = entry_for_row(row)
        if entry and str(entry.get("skill_id")) == str(skill_id):
            out.append({"id": row.id, "label": entry.get("label") or f"教材題 {row.id}", "graded": entry["mode"] == "graded"})
    return out


def skill_has_selfcheck_rows(rows: list[Any]) -> bool:
    """True when some row of the skill is reviewed self-check practice (no verdict): such a skill mixes graded and ungraded rows."""
    return any((entry_for_row(row) or {}).get("mode") == "ungraded" for row in rows)
