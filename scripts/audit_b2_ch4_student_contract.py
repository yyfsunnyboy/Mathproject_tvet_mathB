# -*- coding: utf-8 -*-
"""B2 Ch4 student-runtime contract audit (presentation / answer-contract).

Produces reports/b2_ch4_student_contract_audit.json
"""

from __future__ import annotations

import importlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from core.gencode.choice_contract_validator import (
    infer_choice_answer_shape,
    validate_choice_answer_shapes,
    validate_vocational_multiple_choice,
)
from core.gencode.choice_math_display import format_choice_math_display
from core.gencode.multipart_stem_contract import extract_stem_structure, normalize_group_label

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
QA_DIR = ROOT / "scratch" / "_b2_ch4_student_runtime_qa"

SKILLS = [
    f"vh_數學B2_SubSection_4_{a}_{b}"
    for a, b in [(1, 1), (1, 2), (2, 1), (2, 2), (2, 3), (2, 4)]
]

_RAW_CARET = re.compile(r"(?<!\\)\^[^{]")
_GENERIC_LABEL = re.compile(r"^小题\s*\d+$|^小題\s*\d+$|^欄位\s*\d+$")
_BARE_NUMERIC = re.compile(r"^\d+$")
_PAREN_MARKER = re.compile(r"^[\(（]\s*\d+\s*[\)）]$")


def _is_mcq(payload: dict[str, Any]) -> bool:
    at = str(payload.get("answer_type") or "").lower()
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    if at in {"single_choice", "choice", "choice_label"}:
        return True
    if str(payload.get("presentation_mode") or ac.get("presentation_mode") or "").lower() == "single_choice":
        return True
    return bool(payload.get("choices"))


def _looks_multipart(payload: dict[str, Any], parts: list[dict[str, Any]]) -> bool:
    stem = extract_stem_structure(payload)
    if stem and len(stem.get("items") or []) >= 2:
        return True
    if len(parts) >= 2:
        return True
    return False


def audit_family(skill: str, family: str, component: str) -> dict[str, Any]:
    mod = importlib.import_module(f"skills.{skill}")
    payload = mod.generate(seed=7, component_id=component)
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    parts = [p for p in (ac.get("parts") or []) if isinstance(p, dict)]
    stem_struct = extract_stem_structure(payload)
    stem = str(payload.get("question_text") or "")
    failures: list[str] = []
    multipart = _looks_multipart(payload, parts)

    item_texts: list[str] = []
    group_labels: list[str] = []
    if stem_struct and stem_struct.get("items"):
        for item in stem_struct["items"]:
            if not isinstance(item, dict):
                continue
            group_labels.append(normalize_group_label(item.get("group_label")))
            item_texts.append(str(item.get("text") or ""))
    else:
        group_labels = [normalize_group_label(p.get("group_label")) for p in parts if p.get("group_label")]
        item_texts = []

    display_labels = [str(p.get("display_label") or p.get("label") or "") for p in parts]
    internal_keys = [str(p.get("key") or "") for p in parts]

    if multipart:
        # Structured items should exist when generator emits ≥2 subquestions.
        if stem_struct and len(stem_struct.get("items") or []) >= 2:
            markers = [normalize_group_label(it.get("group_label"), index=i)
                       for i, it in enumerate(stem_struct["items"], 1) if isinstance(it, dict)]
            expected = [f"({i})" for i in range(1, len(markers) + 1)]
            if markers != expected:
                failures.append("MISSING_ITEM_MARKER")
            for marker in markers:
                if _BARE_NUMERIC.match(marker):
                    failures.append("BARE_NUMERIC_GROUP_LABEL")
                    break
                if marker and not _PAREN_MARKER.match(marker):
                    # Allow descriptive group labels that already include (n).
                    if not re.search(r"[\(（]\s*\d+\s*[\)）]", marker):
                        failures.append("MISSING_ITEM_MARKER")
                        break
        else:
            # Compatibility: only flag flatten when stem already shows ≥2 markers
            # but lost newlines (true flatten). Multi-answer without multi-item
            # stem (e.g. 切線一/切線二) is not MISSING_ITEM_MARKER.
            numbered = re.findall(r"[\(（]\s*\d+\s*[\)）]", stem)
            if len(numbered) >= 2 and "\n" not in stem:
                failures.append("FLATTENED_ITEM_BOUNDARY")

        # Flat stem still present without newlines is overflow risk.
        if stem_struct and stem_struct.get("items") and len(stem_struct["items"]) >= 2:
            pass
        elif parts and len(stem) > 120 and re.findall(r"[\(（]\s*\d+\s*[\)）]", stem) and "\n" not in stem:
            failures.append("HORIZONTAL_OVERFLOW")
            failures.append("FLATTENED_ITEM_BOUNDARY")

        for label in display_labels:
            text = label.strip()
            if not text:
                failures.append("EMPTY_DISPLAY_LABEL")
                break
            if _BARE_NUMERIC.match(text) or _PAREN_MARKER.match(text):
                failures.append("AMBIGUOUS_DISPLAY_LABEL")
                break
            if _GENERIC_LABEL.match(text):
                failures.append("AMBIGUOUS_DISPLAY_LABEL")
                break

        # Group markers on field_groups / part group_label must not be bare digits.
        groups = ((ac.get("ui_contract") or {}).get("field_groups") if isinstance(ac.get("ui_contract"), dict) else None) or []
        for g in groups:
            gl = str((g or {}).get("group_label") or "").strip()
            if _BARE_NUMERIC.match(gl):
                failures.append("BARE_NUMERIC_GROUP_LABEL")
                break

        for part in parts:
            label = str(part.get("display_label") or part.get("label") or "")
            key = str(part.get("key") or "")
            if label.replace(" ", "") == key.replace("_", "") and "_" in key and not re.search(r"[\u4e00-\u9fff]", label):
                failures.append("INTERNAL_KEY_EXPOSED")
                break
            gl = str(part.get("group_label") or "").strip()
            if _BARE_NUMERIC.match(gl):
                failures.append("BARE_NUMERIC_GROUP_LABEL")
                break

    # Generic labels (all families)
    for part in parts:
        label = str(part.get("display_label") or part.get("label") or "")
        if _GENERIC_LABEL.match(label.strip()):
            failures.append("AMBIGUOUS_DISPLAY_LABEL")
            break

    # MCQ raw math / shape
    if _is_mcq(payload):
        choices = list(payload.get("choices") or [])
        for choice in choices:
            if not isinstance(choice, dict):
                continue
            display = str(choice.get("display") or choice.get("text") or choice.get("value") or "")
            value = str(choice.get("value") or choice.get("text") or "")
            rendered = format_choice_math_display(display or value)
            if _RAW_CARET.search(display) and "$" not in display and r"\(" not in display:
                failures.append("RAW_CHOICE_MATH")
                break
            if re.search(r"[xy]\^", value) and "$" not in rendered and r"\(" not in rendered:
                failures.append("RAW_CHOICE_MATH")
                break
        shape_errs = validate_choice_answer_shapes(
            {
                **payload,
                "semantic_answer": ac.get("semantic_answer") or payload.get("semantic_answer") or payload.get("display_answer"),
                "curriculum_profile": "vocational_high_b",
            }
        )
        if "vocational_choice_shape_mismatch" in shape_errs:
            failures.append("CHOICE_SHAPE_MISMATCH")
        voc = validate_vocational_multiple_choice(
            {**payload, "curriculum_profile": "vocational_high_b"},
            skill_id=skill,
        )
        if any(x in voc for x in ("vocational_choice_semantic_duplicate", "vocational_multi_correct")):
            failures.append("CHOICE_SHAPE_MISMATCH")

    status = "PASS" if not failures else "BLOCKED"
    return {
        "family_id": family,
        "skill_id": skill,
        "component_id": component,
        "final_status": status,
        "multipart": multipart,
        "group_count": len(stem_struct.get("items") or []) if stem_struct else len({p.get("group_label") for p in parts if p.get("group_label")} or parts),
        "item_texts": item_texts,
        "group_labels": group_labels,
        "internal_keys": internal_keys,
        "display_labels": display_labels,
        "failures": sorted(set(failures)),
        "stem_has_newlines": "\n" in stem,
        "has_stem_structure": bool(stem_struct and stem_struct.get("items")),
        "part_debug": [
            {
                "key": p.get("key"),
                "display_label": p.get("display_label") or p.get("label"),
                "group_label": p.get("group_label"),
                "expected_answer": p.get("expected_answer"),
            }
            for p in parts
        ],
        "field_groups": ((ac.get("ui_contract") or {}).get("field_groups") if isinstance(ac.get("ui_contract"), dict) else None),
        "choice_debug": [
            {
                "label": c.get("label"),
                "value": c.get("value") or c.get("text"),
                "display": format_choice_math_display(c.get("display") or c.get("text") or c.get("value")),
                "shape": infer_choice_answer_shape(c.get("value") or c.get("text")),
            }
            for c in (payload.get("choices") or [])
            if isinstance(c, dict)
        ][:4],
        "representative_stem": stem[:240],
        "stem_structure": stem_struct,
    }


def write_qa(rows: list[dict[str, Any]]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for row in rows:
        color = "#0a7" if row["final_status"] == "PASS" else "#c33"
        part_rows = "".join(
            f"<tr><td>{i}</td><td><code>{(row.get('item_texts') or [''])[i] if i < len(row.get('item_texts') or []) else ''}</code></td>"
            f"<td>{(row.get('group_labels') or [''])[i] if i < len(row.get('group_labels') or []) else ''}</td>"
            f"<td><code>{p.get('key')}</code></td><td>{p.get('display_label')}</td>"
            f"<td><code>{p.get('expected_answer')}</code></td></tr>"
            for i, p in enumerate(row.get("part_debug") or [])
        )
        # Prefer stem-item oriented debug for multipart families.
        stem_rows = ""
        if row.get("has_stem_structure"):
            stem_items = (row.get("stem_structure") or {}).get("items") or []
            stem_rows = "".join(
                f"<tr><td>{idx}</td><td>{it.get('group_label')}</td>"
                f"<td><code>{it.get('text')}</code></td></tr>"
                for idx, it in enumerate(stem_items, 1)
                if isinstance(it, dict)
            )
        choice_rows = "".join(
            f"<tr><td>{c.get('label')}</td><td><code>{c.get('value')}</code></td>"
            f"<td><code>{c.get('display')}</code></td><td>{c.get('shape')}</td></tr>"
            for c in (row.get("choice_debug") or [])
        )
        cards.append(
            f"""
<section style="border:1px solid #ddd;padding:12px;margin:12px 0;border-left:6px solid {color}">
  <h3>{row['family_id']} <small>({row['skill_id']})</small></h3>
  <p><b>status:</b> {row['final_status']} | <b>multipart:</b> {row.get('multipart')} |
     <b>failures:</b> {','.join(row['failures']) or '-'} |
     <b>stem_structure:</b> {row.get('has_stem_structure')} | <b>group_count:</b> {row.get('group_count')}</p>
  <pre style="white-space:pre-wrap;background:#f7f7f7;padding:8px">{row.get('representative_stem') or ''}</pre>
  {"<h4>stem items (index / group_label / text)</h4><table border=1 cellpadding=4><tr><th>#</th><th>group</th><th>text</th></tr>" + stem_rows + "</table>" if stem_rows else ""}
  {"<h4>multipart debug (item / text / group / key / display / expected)</h4><table border=1 cellpadding=4><tr><th>i</th><th>item_text</th><th>group</th><th>key</th><th>display_label</th><th>expected</th></tr>" + part_rows + "</table>" if part_rows else ""}
  {"<h4>choice debug</h4><table border=1 cellpadding=4><tr><th>label</th><th>value</th><th>display</th><th>shape</th></tr>" + choice_rows + "</table>" if choice_rows else ""}
  <p><b>field_groups:</b> <code>{json.dumps(row.get('field_groups'), ensure_ascii=False)}</code></p>
</section>
"""
        )
    pass_n = sum(1 for r in rows if r["final_status"] == "PASS")
    multipart_n = sum(1 for r in rows if r.get("multipart"))
    doc = f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>B2 Ch4 Student Contract QA</title>
<style>body{{font-family:system-ui,sans-serif;max-width:980px;margin:24px auto;padding:0 16px}}
code{{background:#f4f4f4;padding:2px 4px}}</style></head><body>
<h1>B2 Ch4 Student Runtime Contract QA</h1>
<p>PASS {pass_n} / {len(rows)} &nbsp; BLOCKED {len(rows)-pass_n} &nbsp; multipart families {multipart_n}</p>
{''.join(cards)}
</body></html>"""
    (QA_DIR / "index.html").write_text(doc, encoding="utf-8")


def main() -> None:
    family_components: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for skill in SKILLS:
        mod = importlib.import_module(f"skills.{skill}")
        for spec in getattr(mod, "GENERATOR_SPECS", []):
            fam = str(spec.get("problem_type_id") or "")
            family_components[fam].append((skill, str(spec.get("component_id") or "")))

    rows = []
    for family, comps in sorted(family_components.items()):
        skill, component = comps[0]
        rows.append(audit_family(skill, family, component))

    counts = Counter()
    for row in rows:
        for f in row["failures"]:
            counts[f] += 1
    multipart_rows = [r for r in rows if r.get("multipart")]
    target_keys = [
        "MISSING_ITEM_MARKER",
        "FLATTENED_ITEM_BOUNDARY",
        "BARE_NUMERIC_GROUP_LABEL",
        "EMPTY_DISPLAY_LABEL",
        "AMBIGUOUS_DISPLAY_LABEL",
        "INTERNAL_KEY_EXPOSED",
        "HORIZONTAL_OVERFLOW",
    ]
    report = {
        "total_families": len(rows),
        "multipart_families": len(multipart_rows),
        "pass": sum(1 for r in rows if r["final_status"] == "PASS"),
        "blocked": sum(1 for r in rows if r["final_status"] != "PASS"),
        "failure_counts": dict(counts),
        "multipart_audit_counters": {k: int(counts.get(k, 0)) for k in target_keys},
        "families": rows,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "b2_ch4_student_contract_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    write_qa(rows)
    print(json.dumps({
        "total_families": report["total_families"],
        "multipart_families": report["multipart_families"],
        "pass": report["pass"],
        "blocked": report["blocked"],
        "multipart_audit_counters": report["multipart_audit_counters"],
        "report": str(out),
        "qa": str(QA_DIR / "index.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
