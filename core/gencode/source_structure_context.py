from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any

from core.gencode.task_families import task_family_for_task

# Canonical source types (normalize DB/import aliases).
WORKED_EXAMPLE_SOURCE_TYPES = frozenset(
    {
        "worked_example",
        "textbook_example",
        "textbook_practice",
        "exam_practice",
    }
)
IN_CLASS_PRACTICE_TYPES = frozenset({"in_class_practice"})
PRACTICE_SOURCE_TYPES = IN_CLASS_PRACTICE_TYPES | frozenset(
    {"textbook_practice", "basic_exercise", "advanced_exercise", "chapter_exercise"}
)

_RE_BRACKET_META = re.compile(r"\[([^\]]+)\]")
_RE_KV = re.compile(r"([a-z_]+)\s*=\s*([^|\]]+)", re.I)
_RE_EXAMPLE_LABEL = re.compile(r"例\s*題\s*([0-9０-９]+)", re.I)
_RE_PRACTICE_LABEL = re.compile(r"隨堂練習\s*([0-9０-９]+)", re.I)
_RE_SHORT_EXAMPLE = re.compile(r"^例\s*([0-9０-９]+)\s*$", re.I)
_DIGIT_TRANS = str.maketrans("０１２３４５６７８９", "0123456789")


def _normalize_digits(text: str) -> str:
    return str(text or "").translate(_DIGIT_TRANS).strip()


def _example_id(ex: dict[str, Any]) -> int | None:
    raw = ex.get("id") if ex.get("id") is not None else ex.get("example_id")
    try:
        return int(raw)
    except (TypeError, ValueError):
        return None


def _text_blobs(example: dict[str, Any]) -> list[str]:
    chunks: list[str] = []
    for key in (
        "title",
        "source_description",
        "note",
        "notes",
        "metadata",
        "source_label",
        "practice_title",
        "example_title",
    ):
        v = str(example.get(key, "")).strip()
        if v:
            chunks.append(v)
    return chunks


def parse_metadata_from_text(text: str) -> dict[str, str]:
    """Parse key=value tokens from bracket metadata or loose strings."""
    out: dict[str, str] = {}
    raw = str(text or "").strip()
    if not raw:
        return out
    for bracket in _RE_BRACKET_META.findall(raw):
        for m in _RE_KV.finditer(bracket):
            out[m.group(1).strip().lower()] = m.group(2).strip()
    for m in _RE_KV.finditer(raw):
        k = m.group(1).strip().lower()
        if k not in out:
            out[k] = m.group(2).strip()
    return out


def parse_example_label(text: str) -> tuple[str, int | None]:
    """Return (canonical_label, number) e.g. ('例題1', 1)."""
    t = str(text or "").strip()
    if not t:
        return "", None
    head = t.split(" [", 1)[0].strip()
    m = _RE_EXAMPLE_LABEL.search(head) or _RE_SHORT_EXAMPLE.search(head)
    if m:
        n = int(_normalize_digits(m.group(1)))
        return f"例題{n}", n
    return "", None


def parse_practice_label(text: str) -> tuple[str, int | None]:
    t = str(text or "").strip()
    if not t:
        return "", None
    head = t.split(" [", 1)[0].strip()
    m = _RE_PRACTICE_LABEL.search(head)
    if m:
        n = int(_normalize_digits(m.group(1)))
        return f"隨堂練習{n}", n
    return "", None


def normalize_source_type(raw: str, title_hint: str = "") -> str:
    st = str(raw or "").strip().lower()
    title = str(title_hint or "").strip()
    if st in WORKED_EXAMPLE_SOURCE_TYPES:
        return "worked_example"
    if st in IN_CLASS_PRACTICE_TYPES:
        return "in_class_practice"
    if st:
        return st
    if parse_practice_label(title)[0]:
        return "in_class_practice"
    if parse_example_label(title)[0]:
        return "worked_example"
    return "unknown"


def parse_structure_fields(example: dict[str, Any]) -> dict[str, Any]:
    """Extract structure fields from an example row (generic parser)."""
    meta: dict[str, str] = {}
    for blob in _text_blobs(example):
        meta.update(parse_metadata_from_text(blob))

    title_head = ""
    for blob in _text_blobs(example):
        if blob:
            title_head = blob.split(" [", 1)[0].strip()
            break

    source_type = normalize_source_type(
        str(example.get("source_type", "")).strip() or meta.get("source_type", ""),
        title_head,
    )
    example_label, example_number = parse_example_label(title_head)
    practice_label, practice_number = parse_practice_label(title_head)

    linked_raw = str(meta.get("linked_example", "")).strip() or str(example.get("linked_example", "")).strip()
    linked_label, linked_num = parse_example_label(linked_raw)
    if not linked_label and linked_raw:
        linked_label = linked_raw.split(" [", 1)[0].strip()

    section_order_raw = (
        example.get("section_order")
        or example.get("display_order")
        or example.get("rowid")
        or example.get("order")
    )
    try:
        section_order = int(section_order_raw) if section_order_raw is not None else 0
    except (TypeError, ValueError):
        section_order = 0

    return {
        "source_type": source_type,
        "example_label": example_label,
        "practice_label": practice_label,
        "linked_example": linked_label,
        "section_order": section_order,
        "example_number": example_number,
        "practice_number": practice_number,
        "linked_example_number": linked_num,
        "title_head": title_head,
        "raw_metadata": meta,
    }


def _compact_summary(ex: dict[str, Any], fields: dict[str, Any] | None = None) -> dict[str, Any]:
    f = fields or parse_structure_fields(ex)
    return {
        "example_id": _example_id(ex),
        "source_type": f.get("source_type", ""),
        "example_label": f.get("example_label", ""),
        "practice_label": f.get("practice_label", ""),
        "section_order": f.get("section_order", 0),
        "title_head": f.get("title_head", ""),
    }


def enrich_examples_with_structure_context(
    examples: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """
    Attach source_structure_context and source_sequence_context to each example.
    Returns enriched copies and skill-level structure report.
    """
    ordered = sorted(
        [dict(ex) for ex in examples if isinstance(ex, dict)],
        key=lambda x: (
            int(parse_structure_fields(x).get("section_order", 0) or 0),
            _example_id(x) or 0,
        ),
    )
    parsed_by_id: dict[int, dict[str, Any]] = {}
    label_index: dict[str, dict[str, Any]] = {}
    for ex in ordered:
        eid = _example_id(ex)
        fields = parse_structure_fields(ex)
        if eid is not None:
            parsed_by_id[eid] = fields
        for key in (fields.get("example_label"), fields.get("practice_label"), fields.get("title_head")):
            k = str(key or "").strip()
            if k:
                label_index[k] = ex

    same_section_sequence = [_compact_summary(ex, parsed_by_id.get(_example_id(ex) or -1)) for ex in ordered]

    enriched: list[dict[str, Any]] = []
    for ex in ordered:
        eid = _example_id(ex)
        fields = parsed_by_id.get(eid) if eid is not None else parse_structure_fields(ex)
        nearby_worked: list[dict[str, Any]] = []
        for other in ordered:
            oid = _example_id(other)
            if oid == eid:
                continue
            of = parsed_by_id.get(oid) or parse_structure_fields(other)
            if of.get("source_type") == "worked_example":
                nearby_worked.append(_compact_summary(other, of))
        nearby_worked = nearby_worked[-5:]

        linked_ex: dict[str, Any] | None = None
        linked_label = str(fields.get("linked_example", "")).strip()
        if linked_label and linked_label in label_index:
            linked_row = label_index[linked_label]
            linked_ex = _compact_summary(linked_row, parsed_by_id.get(_example_id(linked_row) or -1))

        linked_practices: list[dict[str, Any]] = []
        elabel = str(fields.get("example_label", "")).strip()
        if elabel:
            for other in ordered:
                of = parsed_by_id.get(_example_id(other) or -1) or parse_structure_fields(other)
                if str(of.get("linked_example", "")).strip() == elabel:
                    linked_practices.append(_compact_summary(other, of))

        ctx = {
            "source_type": fields.get("source_type", ""),
            "example_label": fields.get("example_label", ""),
            "practice_label": fields.get("practice_label", ""),
            "linked_example": linked_label,
            "section_order": fields.get("section_order", 0),
            "example_number": fields.get("example_number"),
            "practice_number": fields.get("practice_number"),
            "nearby_worked_examples": nearby_worked,
            "linked_worked_example": linked_ex,
            "linked_practices": linked_practices,
            "same_section_sequence": same_section_sequence,
        }
        row = dict(ex)
        row["source_structure_context"] = ctx
        row["source_sequence_context"] = {
            "same_section_sequence": same_section_sequence,
            "position_in_section": next(
                (i + 1 for i, s in enumerate(same_section_sequence) if s.get("example_id") == eid),
                0,
            ),
            "total_in_section": len(same_section_sequence),
        }
        enriched.append(row)

    link_map: list[dict[str, Any]] = []
    for ex in enriched:
        ctx = ex.get("source_structure_context") or {}
        if ctx.get("practice_label") and ctx.get("linked_example"):
            link_map.append(
                {
                    "practice_label": ctx.get("practice_label"),
                    "linked_example": ctx.get("linked_example"),
                    "example_id": _example_id(ex),
                }
            )

    report = {
        "source_type_distribution": dict(
            Counter(str((ex.get("source_structure_context") or {}).get("source_type", "unknown")) for ex in enriched)
        ),
        "example_practice_link_map": link_map,
        "structure_mismatch_examples": [],
        "same_section_family_distribution": {},
    }
    return enriched, report


def build_sequence_context_for_prompt(structure_ctx: dict[str, Any], sequence_ctx: dict[str, Any] | None) -> str:
    """Compact text block for AI prompt."""
    seq = sequence_ctx if isinstance(sequence_ctx, dict) else {}
    struct = structure_ctx if isinstance(structure_ctx, dict) else {}
    lines = [
        "Textbook structure (auxiliary only — do NOT override clear current-problem meaning):",
        f"- source_type: {struct.get('source_type', '')}",
        f"- example_label: {struct.get('example_label', '')}",
        f"- practice_label: {struct.get('practice_label', '')}",
        f"- linked_example: {struct.get('linked_example', '')}",
        f"- section_order: {struct.get('section_order', '')}",
    ]
    linked = struct.get("linked_worked_example")
    if isinstance(linked, dict) and linked:
        lines.append(f"- linked_worked_example: {json_short(linked)}")
    lines.append(
        f"- position_in_section: {seq.get('position_in_section', '')}/{seq.get('total_in_section', '')}"
    )
    seq_items = struct.get("same_section_sequence") or seq.get("same_section_sequence") or []
    if seq_items:
        preview = [json_short(x) for x in seq_items[:12]]
        lines.append(f"- same_section_sequence (ordered): {preview}")
    lines.append(
        "Rules: use linked example task_family only as disambiguation; "
        "if practice conflicts with linked example semantics, set possible_structure_mismatch; "
        "never force same family from numbering alone."
    )
    return "\n".join(lines)


def json_short(obj: Any) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(obj)


def classification_sort_key(ex: dict[str, Any]) -> tuple[int, int, int]:
    """Worked examples before linked practices within the same section_order."""
    ctx = ex.get("source_structure_context") if isinstance(ex.get("source_structure_context"), dict) else {}
    st = str(ctx.get("source_type", "")).strip()
    order = int(ctx.get("section_order", 0) or 0)
    tier = 0 if st == "worked_example" else 1
    return (order, tier, _example_id(ex) or 0)


def apply_structure_confidence_adjustment(
    ai_result: dict[str, Any],
    structure_ctx: dict[str, Any],
    *,
    structure_consistency: str = "unknown",
    possible_structure_mismatch: bool = False,
) -> tuple[float, str]:
    """Small confidence nudge from structure; never changes task_family."""
    try:
        conf = float(ai_result.get("confidence", 0.0) or 0.0)
    except Exception:
        conf = 0.0
    reasons: list[str] = []
    if structure_consistency == "consistent" and structure_ctx.get("linked_example"):
        conf = min(1.0, conf + 0.05)
        reasons.append("linked_example_consistent_boost")
    if possible_structure_mismatch:
        conf = max(0.0, conf - 0.08)
        reasons.append("possible_structure_mismatch_penalty")
    st = str(structure_ctx.get("source_type", ""))
    if st == "in_class_practice" and structure_ctx.get("linked_worked_example"):
        reasons.append("structure_context_used")
    elif structure_ctx.get("same_section_sequence"):
        reasons.append("sequence_context_used")
    return conf, "; ".join(reasons) if reasons else ""


def check_linked_example_consistency(
    *,
    structure_ctx: dict[str, Any],
    current_task_family: str,
    linked_task_family: str,
) -> dict[str, Any]:
    """
    Compare practice vs linked worked example families (does not change classification).
    """
    st = str(structure_ctx.get("source_type", "")).strip()
    linked_label = str(structure_ctx.get("linked_example", "")).strip()
    linked_ex = structure_ctx.get("linked_worked_example")
    if st not in IN_CLASS_PRACTICE_TYPES and st != "in_class_practice":
        return {
            "structure_consistency": "not_applicable",
            "linked_example_id": None,
            "linked_example_task_family": linked_task_family or "",
            "requires_human_action": False,
            "possible_structure_mismatch": False,
        }
    if not linked_label:
        return {
            "structure_consistency": "unknown",
            "linked_example_id": None,
            "linked_example_task_family": "",
            "requires_human_action": False,
            "possible_structure_mismatch": False,
        }
    linked_id = linked_ex.get("example_id") if isinstance(linked_ex, dict) else None
    if not linked_task_family:
        return {
            "structure_consistency": "unknown",
            "linked_example_id": linked_id,
            "linked_example_task_family": "",
            "requires_human_action": False,
            "possible_structure_mismatch": False,
        }
    cur = str(current_task_family or "").strip()
    lnk = str(linked_task_family or "").strip()
    if cur and lnk and cur == lnk:
        return {
            "structure_consistency": "consistent",
            "linked_example_id": linked_id,
            "linked_example_task_family": lnk,
            "requires_human_action": False,
            "possible_structure_mismatch": False,
        }
    if cur and lnk and cur != lnk:
        return {
            "structure_consistency": "mismatch",
            "linked_example_id": linked_id,
            "linked_example_task_family": lnk,
            "requires_human_action": True,
            "possible_structure_mismatch": True,
        }
    return {
        "structure_consistency": "unknown",
        "linked_example_id": linked_id,
        "linked_example_task_family": lnk,
        "requires_human_action": False,
        "possible_structure_mismatch": False,
    }


def detect_possible_mixed_source_context(
    *,
    current_task_family: str,
    structure_ctx: dict[str, Any],
    section_family_counts: Counter[str],
) -> bool:
    """Current stem family differs from dominant section family — flag only, no override."""
    cur = str(current_task_family or "").strip()
    if not cur or not section_family_counts:
        return False
    dominant_family, dominant_count = section_family_counts.most_common(1)[0]
    total = sum(section_family_counts.values())
    if total < 2 or dominant_count < 2:
        return False
    if cur != dominant_family and dominant_count >= 2:
        return True
    return False


def update_structure_report(
    report: dict[str, Any],
    *,
    classifications: list[dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate skill-level structure report from per-example classification traces."""
    out = dict(report)
    mismatches: list[dict[str, Any]] = []
    fam_counter: Counter[str] = Counter()
    for row in classifications:
        if not isinstance(row, dict):
            continue
        fam = str(row.get("final_task_family", "")).strip()
        if fam:
            fam_counter[fam] += 1
        if row.get("structure_consistency") == "mismatch":
            mismatches.append(
                {
                    "example_id": row.get("example_id"),
                    "practice_label": row.get("practice_label"),
                    "linked_example": row.get("linked_example"),
                    "linked_example_id": row.get("linked_example_id"),
                    "final_task_family": fam,
                    "linked_example_task_family": row.get("linked_example_task_family"),
                }
            )
    out["structure_mismatch_examples"] = mismatches
    out["same_section_family_distribution"] = dict(fam_counter)
    return out
