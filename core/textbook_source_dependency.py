"""Cross-question source dependency of textbook rows ("承例題N").

A practice row that continues a textbook example cannot be answered alone: the data lives in the example.  This module
decides, from Stage 1 evidence only, whether a row depends on an example, which part of that example it needs, and
whether that part can be shown on its own.  It never rewrites a stem and never guesses a boundary: anything it cannot
delimit is ``blocked`` and the row must not be served or used as a standalone generation source.

Statuses: ``none`` (no relation), ``related_only`` (linked example for ordering/classification, nothing to merge),
``resolved`` (prerequisite data found and complete), ``blocked`` (depends on an example but the data is unavailable).
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Callable, Iterable

STATUS_NONE = "none"
STATUS_RELATED = "related_only"
STATUS_RESOLVED = "resolved"
STATUS_BLOCKED = "blocked"

NEED_TABLE = "example_table"
NEED_FIGURE = "example_figure"
NEED_TEXT = "example_text"

_CONTINUES_EXAMPLE_RE = re.compile(r"承\s*例\s*題\s*(\d+)")
_EXAMPLE_REFERENCE_RE = re.compile(r"例\s*題\s*\d+")
_LINKED_EXAMPLE_RE = re.compile(r"linked_example=([^|\]\s]+)")
_TITLE_SUFFIX_RE = re.compile(r"\s*\[.*$", re.S)
# First sub-question of the example: everything before it is the shared setup the continuing row relies on.
_FIRST_SUBQUESTION_RE = re.compile(r"(?m)^[ \t\u3000]*[（(]\s*1\s*[)）]")
_TABLE_RE = re.compile(r"\\begin\{(?:array|tabular)\}")
_FIGURE_CUE_RE = re.compile(r"[如下右左上]\s*圖|圖\s*[(（]?[a-zA-Z0-9]|(?:分布|散布|長條|直方|折線|圓形|示意|坐標)圖")
_DATA_RE = re.compile(r"\d|\\\(|\$")


def _notes_dict(notes: Any) -> dict[str, Any]:
    if isinstance(notes, dict):
        return notes
    if isinstance(notes, str) and notes.strip():
        try:
            parsed = json.loads(notes)
        except (TypeError, ValueError):
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def row_title(source_description: Any) -> str:
    return _TITLE_SUFFIX_RE.sub("", str(source_description or "")).strip()


def _example_label(number: str) -> str:
    return f"例題{int(number)}"


def detect_source_dependency(problem_text: Any, notes: Any, source_description: Any = "") -> dict[str, Any]:
    """Classify the row's relation to an example without touching any other row."""
    text = str(problem_text or "")
    recorded = _notes_dict(notes).get("source_dependency")
    recorded = recorded if isinstance(recorded, dict) and recorded.get("kind") == "continues_example" else None
    cues = sorted({_example_label(m.group(1)) for m in _CONTINUES_EXAMPLE_RE.finditer(text)})
    linked = _LINKED_EXAMPLE_RE.search(str(source_description or ""))
    if not recorded and not cues:
        if linked:
            return {"status": STATUS_RELATED, "linked_example": linked.group(1)}
        return {"status": STATUS_NONE}
    recorded_title = str((recorded or {}).get("example_title") or "").strip()
    titles = sorted(set(cues) | ({recorded_title} if recorded_title else set()))
    out = {
        "kind": "continues_example",
        "example_title": titles[0] if len(titles) == 1 else "",
        "evidence": "notes.source_dependency" if recorded else "stem_continuation_cue",
        "stem_cues": cues,
    }
    if len(titles) != 1:
        return {**out, "status": STATUS_BLOCKED, "reason": "example_reference_conflict", "referenced": titles}
    return {**out, "status": "pending"}


def has_source_dependency_signal(problem_text: Any, notes: Any) -> bool:
    """Cheap pre-check so rows without any continuation evidence never pay for a lookup."""
    if _CONTINUES_EXAMPLE_RE.search(str(problem_text or "")):
        return True
    return '"source_dependency"' in str(notes or "") if isinstance(notes, str) else "source_dependency" in _notes_dict(notes)


def split_example_setup(example_text: Any) -> tuple[str, str]:
    """Return (setup, reason).  The setup is the example stem before its first sub-question; no marker, no setup."""
    text = str(example_text or "")
    m = _FIRST_SUBQUESTION_RE.search(text)
    if not m:
        return "", "example_boundary_uncertain"
    setup = text[: m.start()].strip()
    if not setup or not _DATA_RE.search(setup) and not _FIGURE_CUE_RE.search(setup):
        return "", "example_setup_has_no_data"
    return setup, ""


def resolve_source_dependency(
    row: dict[str, Any],
    chapter_rows: Iterable[dict[str, Any]],
    *,
    image_assets_for: Callable[[Any], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Resolve the prerequisite data of ``row`` among rows of the same curriculum + volume + chapter.

    ``row`` / ``chapter_rows`` are dicts with id, source_description, problem_text, notes.  ``image_assets_for(notes)``
    returns the student-ready accepted assets of a row (defaults to the shared student asset filter).
    """
    found = detect_source_dependency(row.get("problem_text"), row.get("notes"), row.get("source_description"))
    if found["status"] != "pending":
        return found
    title = found["example_title"]
    candidates = [
        r for r in chapter_rows
        if r.get("id") != row.get("id") and row_title(r.get("source_description")) == title
    ]
    if not candidates:
        return {**found, "status": STATUS_BLOCKED, "reason": "example_not_found"}
    if len(candidates) > 1:
        return {**found, "status": STATUS_BLOCKED, "reason": "example_ambiguous",
                "example_ids": sorted(int(r.get("id") or 0) for r in candidates)}
    example = candidates[0]
    example_text = str(example.get("problem_text") or "")
    setup, reason = split_example_setup(example_text)
    base = {
        **found,
        "example_id": int(example.get("id") or 0),
        "provenance": {
            "dependent_row_id": int(row.get("id") or 0),
            "example_id": int(example.get("id") or 0),
            "example_title": title,
            "example_anchor_id": str((_notes_dict(example.get("notes")).get("question_anchor") or {}).get("anchor_id") or ""),
            "example_problem_text_sha256": hashlib.sha256(example_text.encode("utf-8")).hexdigest(),
        },
    }
    if reason:
        return {**base, "status": STATUS_BLOCKED, "reason": reason}
    needs = [NEED_TEXT]
    if _TABLE_RE.search(setup):
        needs.append(NEED_TABLE)
    assets: list[dict[str, Any]] = []
    if _FIGURE_CUE_RE.search(setup):
        needs.append(NEED_FIGURE)
        if image_assets_for is None:
            from core.question_image_assets import list_student_image_assets_from_notes as image_assets_for
        assets = list(image_assets_for(example.get("notes")) or [])
        if not assets:
            return {**base, "needs": needs, "status": STATUS_BLOCKED, "reason": "example_figure_missing"}
    fingerprint = hashlib.sha256(json.dumps([setup, [a.get("path") for a in assets]], ensure_ascii=False).encode("utf-8")).hexdigest()
    return {**base, "status": STATUS_RESOLVED, "needs": needs, "context_text": setup, "image_assets": assets,
            "fingerprint": fingerprint}


def standalone_blocked(resolution: dict[str, Any]) -> bool:
    return resolution.get("status") == STATUS_BLOCKED


def compose_practice_stem(resolution: dict[str, Any], stem: str) -> str:
    """Served stem = prerequisite setup + the untouched original stem (the DB row is never rewritten)."""
    if resolution.get("status") != STATUS_RESOLVED:
        return stem
    return f"【{resolution['example_title']}的資料】\n{resolution['context_text']}\n\n{stem}"


def merge_image_assets(own: list[dict[str, Any]], resolution: dict[str, Any]) -> list[dict[str, Any]]:
    if resolution.get("status") != STATUS_RESOLVED:
        return list(own)
    seen = {a.get("path") for a in own}
    return list(own) + [a for a in resolution.get("image_assets") or [] if a.get("path") not in seen]


def generation_contract(resolution: dict[str, Any]) -> dict[str, Any] | None:
    """What GenCode V3 must honour for a resolved dependency: generated items carry their own complete data."""
    if resolution.get("status") != STATUS_RESOLVED:
        return None
    return {
        "kind": resolution["kind"],
        "example_title": resolution["example_title"],
        "example_id": resolution["example_id"],
        "needs": list(resolution["needs"]),
        "source_setup_text": resolution["context_text"],
        "source_setup_has_figure": NEED_FIGURE in resolution["needs"],
        "self_contained_required": True,
        "fingerprint": resolution["fingerprint"],
        "provenance": dict(resolution["provenance"]),
    }


def generated_payload_dependency_issues(payload: dict[str, Any], contract: dict[str, Any]) -> list[str]:
    """A generated item of a dependent source must carry the data kinds its source borrowed, and point at no example."""
    text = str(payload.get("question_text") or payload.get("question") or "")
    issues = []
    if _EXAMPLE_REFERENCE_RE.search(text):
        issues.append("generated_stem_references_external_example")
    needs = contract.get("needs") or []
    if NEED_TABLE in needs and not (_TABLE_RE.search(text) or payload.get("table_data")):
        issues.append("generated_stem_missing_data_table")
    if NEED_FIGURE in needs and not (payload.get("visual_aids") or payload.get("image_base64") or payload.get("visual_spec")):
        issues.append("generated_item_missing_figure")
    return issues


_CHAPTER_COLUMNS = ("id", "source_description", "problem_text", "notes")


def resolve_for_model_row(te: Any) -> dict[str, Any]:
    """SQLAlchemy TextbookExample row; scope is curriculum + volume + chapter of the row itself."""
    problem_text, notes = getattr(te, "problem_text", ""), getattr(te, "notes", None)
    if not has_source_dependency_signal(problem_text, notes):
        return detect_source_dependency(problem_text, notes, getattr(te, "source_description", ""))
    from models import TextbookExample

    peers = TextbookExample.query.filter_by(
        source_curriculum=te.source_curriculum, source_volume=te.source_volume, source_chapter=te.source_chapter,
    ).all()
    as_dict = lambda r: {k: getattr(r, k, None) for k in _CHAPTER_COLUMNS}  # noqa: E731
    return resolve_source_dependency(as_dict(te), [as_dict(r) for r in peers])


def resolve_from_conn(conn: Any, textbook_example_id: int, *, problem_text_hint: Any = "") -> dict[str, Any]:
    """DB-API connection (V3 pipeline).  A dependency that cannot be looked up is blocked, never ignored."""
    cols = ", ".join(_CHAPTER_COLUMNS + ("source_curriculum", "source_volume", "source_chapter"))
    try:
        cur = conn.execute(f"SELECT {cols} FROM textbook_examples WHERE id = ?", (int(textbook_example_id),))
        names = [d[0] for d in cur.description]
        found = cur.fetchone()
    except Exception:  # noqa: BLE001 - schema without Stage 1 scope columns
        if _CONTINUES_EXAMPLE_RE.search(str(problem_text_hint or "")):
            return {"status": STATUS_BLOCKED, "kind": "continues_example", "reason": "dependency_lookup_unavailable"}
        return {"status": STATUS_NONE}
    if found is None:
        return {"status": STATUS_NONE}
    row = dict(zip(names, found))
    if not has_source_dependency_signal(row["problem_text"], row["notes"]):
        return detect_source_dependency(row["problem_text"], row["notes"], row["source_description"])
    cur = conn.execute(
        f"SELECT {', '.join(_CHAPTER_COLUMNS)} FROM textbook_examples "
        "WHERE source_curriculum IS ? AND source_volume IS ? AND source_chapter IS ?",
        (row["source_curriculum"], row["source_volume"], row["source_chapter"]),
    )
    names = [d[0] for d in cur.description]
    return resolve_source_dependency(row, [dict(zip(names, r)) for r in cur.fetchall()])
