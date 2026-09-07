# -*- coding: utf-8 -*-
"""Refined feasibility: notes assets + manual status overrides from text review."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"
EXPECTED = [
    4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620,
    4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632,
    4633, 4634, 4635, 4636, 4637, 4706, 4716, 4717, 4718, 4719, 4720,
]

PT = {}
for path in [
    ROOT / "scratch/_b1_3_1_report_data.json",
    ROOT / "scratch/_b1_3_1_component_ops.json",
]:
    if not path.exists():
        continue
    data = json.loads(path.read_text(encoding="utf-8"))
    if "rows" in data:
        for r in data["rows"]:
            PT[int(r["example_id"])] = r.get("problem_type_id")
    if "ops" in data:
        for r in data["ops"]:
            PT[int(r["id"])] = r.get("PROBLEM_TYPE_ID")
PT.update(
    {
        4628: "polynomial_remainder_param_solve",
        4718: "polynomial_long_division",
        4719: "polynomial_remainder_param_solve",
        4720: "polynomial_long_division",
    }
)

from core.question_image_assets import list_student_image_assets_from_notes

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cols = [c[1] for c in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
rows = conn.execute(
    f"SELECT * FROM textbook_examples WHERE id IN ({','.join('?' for _ in EXPECTED)}) ORDER BY id",
    EXPECTED,
).fetchall()
assert [int(r["id"]) for r in rows] == EXPECTED

IMG = re.compile(r"如下圖|如右圖|左圖|右圖|根據下圖|根據右圖|依下圖|觀察圖形|見圖|附圖|如圖")
TABLE = re.compile(r"完成下表|依下表|根據下表|根據表格|如下表|下表")
CHOICE_PARSE = re.compile(r"\(([A-D])\)\s*")


def parse_choices(text: str) -> list[tuple[str, str]]:
    t = text.replace("（", "(").replace("）", ")")
    out = []
    matches = list(CHOICE_PARSE.finditer(t))
    for i, m in enumerate(matches):
        lab = m.group(1)
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        body = t[start:end].strip().rstrip("。．.;；,，〔〕【】 ")
        # strip trailing source tags
        body = re.sub(r"〔[^〕]*〕\s*$", "", body).strip()
        out.append((lab, body))
    seen = set()
    uniq = []
    for lab, body in out:
        if lab in seen:
            continue
        seen.add(lab)
        uniq.append((lab, body))
    return uniq


results = []
for row in rows:
    eid = int(row["id"])
    text = str(row["problem_text"] or "")
    notes = row["notes"] if "notes" in cols else None
    assets = []
    try:
        assets = list_student_image_assets_from_notes(notes) or []
    except Exception:
        assets = []
    # also check notes JSON for image_assets key raw
    notes_has = False
    if isinstance(notes, str) and notes.strip():
        try:
            nj = json.loads(notes)
            if isinstance(nj, dict) and nj.get("image_assets"):
                notes_has = True
        except Exception:
            if "image" in notes.lower() or "uploads/" in notes:
                notes_has = True
    asset_found = bool(assets) or notes_has
    asset_count = len(assets)

    needs_image = bool(IMG.search(text))
    needs_table = bool(TABLE.search(text))
    has_tabular = bool(re.search(r"\\begin\{tabular\}|\\begin\{array\}|<table", text, re.I))

    choices = parse_choices(text)
    needs_choices = bool(choices) or "(A)" in text.replace("（", "(") or "（A）" in text
    choice_n = len(choices)
    bodies_ok = all(b.strip() for _, b in choices)
    labels = {a for a, _ in choices}
    choices_complete = choice_n >= 4 and bodies_ok and {"A", "B", "C", "D"} <= labels

    # truncation: ends with bare 則 / 試求 without object, or choice stem cut mid-option
    truncated = False
    trunc_reason = ""
    stripped = text.strip()
    if stripped.endswith("則") or stripped.endswith("則 "):
        truncated = True
        trunc_reason = "stem_ends_with_則_missing_ask"
    if re.search(r"係數為\s*\(A\)\s*[^\(]*$", text.replace("（", "(")) and choice_n < 4:
        truncated = True
        trunc_reason = trunc_reason or "choice_stem_truncated_after_A"

    # topology observation
    if needs_choices:
        topo = "choice" if choices_complete else "choice_incomplete"
    elif needs_table:
        topo = "table_fill"
    elif re.search(r"（\s*[1-9]\s*）|\([1-9]\)|（[1-9]）", text):
        topo = "multi_part"
    else:
        topo = "short_answer_or_expression"

    # classify
    if needs_image and not asset_found:
        status = "IMAGE_REQUIRED_BUT_MISSING"
        reason = "stem image cue but notes/image_assets empty"
    elif needs_table and not has_tabular and not asset_found:
        status = "TABLE_REQUIRED_BUT_MISSING"
        reason = "stem asks 完成下表/依下表 but no table structure or asset in source"
    elif needs_choices and not choices_complete:
        status = "CHOICES_INCOMPLETE"
        reason = f"choice markers present but incomplete (parsed={choice_n}, labels={sorted(labels)})"
    elif truncated:
        status = "SOURCE_INCOMPLETE"
        reason = trunc_reason
    elif topo == "unknown":
        status = "ANSWER_TOPOLOGY_UNRESOLVED"
        reason = "cannot determine answer topology from source"
    else:
        status = "READY_FOR_COMPONENT"
        reason = f"source stem complete; topology_obs={topo}; asset_count={asset_count}"

    if status == "READY_FOR_COMPONENT":
        decision = "INCLUDE"
    elif status in {
        "IMAGE_REQUIRED_BUT_MISSING",
        "TABLE_REQUIRED_BUT_MISSING",
        "CHOICES_INCOMPLETE",
        "SOURCE_INCOMPLETE",
        "PRESENTATION_UNSUPPORTED",
    }:
        decision = "EXCLUDE"
    else:
        decision = "REVIEW"

    evidence_parts = [
        f"source_description={row['source_description']}",
        f"problem_type={row['problem_type']}",
        f"text_len={len(text)}",
        f"needs_image={needs_image}",
        f"needs_table={needs_table}",
        f"needs_choices={needs_choices}",
        f"asset_found={asset_found}",
        f"asset_count={asset_count}",
        f"choice_n={choice_n}",
        f"choices={choices}",
        f"correct_answer_empty={not bool(str(row['correct_answer'] or '').strip())}",
        f"topology_obs={topo}",
        f"preview={stripped[:140]}",
    ]

    results.append(
        {
            "example_id": eid,
            "skill_id": row["skill_id"],
            "problem_type_id": PT.get(eid, "UNKNOWN"),
            "needs_image": needs_image,
            "needs_table": needs_table,
            "needs_choices": needs_choices,
            "asset_found": asset_found,
            "source_complete": status == "READY_FOR_COMPONENT",
            "feasibility_status": status,
            "rebuild_decision": decision,
            "evidence": "; ".join(evidence_parts),
            "reason": reason,
            "topology_observation": topo,
        }
    )

st = Counter(r["feasibility_status"] for r in results)
dec = Counter(r["rebuild_decision"] for r in results)
out = {
    "scope_match": True,
    "te_columns_relevant": [c for c in cols if c in (
        "id", "skill_id", "problem_text", "correct_answer", "detailed_solution",
        "notes", "problem_type", "source_description", "source_paragraph",
    )],
    "status_counts": dict(st),
    "decision_counts": dict(dec),
    "rows": results,
}
(ROOT / "scratch/_b1_3_1_source_feasibility.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("STATUS", dict(st))
print("DECISION", dict(dec))
for r in results:
    print(r["example_id"], r["feasibility_status"], r["rebuild_decision"], r["reason"][:70])
