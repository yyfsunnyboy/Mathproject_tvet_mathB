# -*- coding: utf-8 -*-
"""Read-only B1 3-1 source completeness / presentation feasibility audit."""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "instance" / "kumon_math.db"

EXPECTED = [
    4609, 4610, 4611, 4612, 4613, 4614, 4615, 4616, 4617, 4618, 4619, 4620,
    4621, 4622, 4623, 4624, 4625, 4626, 4627, 4628, 4629, 4630, 4631, 4632,
    4633, 4634, 4635, 4636, 4637, 4706, 4716, 4717, 4718, 4719, 4720,
]

# problem_type_id from prior audit / rule pack
PT_MAP = {}
ops_path = ROOT / "scratch" / "_b1_3_1_component_ops.json"
if ops_path.exists():
    for row in json.loads(ops_path.read_text(encoding="utf-8")).get("ops", []):
        PT_MAP[int(row["id"])] = row.get("PROBLEM_TYPE_ID")
report_path = ROOT / "scratch" / "_b1_3_1_report_data.json"
if report_path.exists():
    for row in json.loads(report_path.read_text(encoding="utf-8")).get("rows", []):
        PT_MAP[int(row["example_id"])] = row.get("problem_type_id") or PT_MAP.get(int(row["example_id"]))
# missing from rule pack
RULE = {
    4628: "polynomial_remainder_param_solve",
    4718: "polynomial_long_division",
    4719: "polynomial_remainder_param_solve",
    4720: "polynomial_long_division",
}
PT_MAP.update(RULE)

IMG_HINTS = re.compile(
    r"如下圖|如右圖|左圖|右圖|根據下圖|根據右圖|依下圖|觀察圖形|見圖|附圖|圖示|座標圖|如圖",
    re.I,
)
TABLE_HINTS = re.compile(r"依下表|根據下表|根據表格|如下表|下表|統計表|填表|表列", re.I)
CHOICE_HINTS = re.compile(
    r"下列選項|下列何者|何者正確|選出|下列哪|哪個|哪一個|\(A\)|\(B\)|\(C\)|\(D\)|"
    r"（A）|（B）|（C）|（D）|\bA\)|\bB\)|\bC\)|\bD\)|"
    r"\(A\)|（A）|-3.*\(B\)|則.*=\s*\(A\)",
    re.I,
)
PLACEHOLDER = re.compile(
    r"TODO|FIXME|PLACEHOLDER|\?\?\?|\[missing\]|\[缺圖\]|\[缺表\]",
    re.I,
)
TRUNC_TAIL = re.compile(r"(試求|求|則|為)[:：]?\s*$")
HTML_IMG = re.compile(r"<img\b|!\[.*?\]\(|uploads/question_assets|src=['\"]/?uploads/", re.I)
CHOICE_MARKERS = re.compile(
    r"(?:^|\s)[\(（]?([A-DＡ-Ｄ])[\)）\.、]\s*(.+?)(?=(?:\s*[\(（]?[A-DＡ-Ｄ][\)）\.、])|$)",
    re.S,
)

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
cols = [c[1] for c in conn.execute("PRAGMA table_info(textbook_examples)").fetchall()]
tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]

# discover asset-related tables
asset_tables = [t for t in tables if any(k in t.lower() for k in ("asset", "image", "media", "visual"))]

rows = conn.execute(
    f"SELECT * FROM textbook_examples WHERE id IN ({','.join('?' for _ in EXPECTED)}) ORDER BY id",
    EXPECTED,
).fetchall()
found = [int(r["id"]) for r in rows]
assert found == EXPECTED, (found, EXPECTED)

# try related assets by example id if table exists
def find_assets(eid: int) -> list[dict]:
    found_assets = []
    for t in asset_tables:
        tcols = [c[1] for c in conn.execute(f"PRAGMA table_info({t})").fetchall()]
        id_cols = [c for c in tcols if c in ("textbook_example_id", "example_id", "question_id", "te_id")]
        if not id_cols:
            continue
        col = id_cols[0]
        try:
            for ar in conn.execute(f"SELECT * FROM {t} WHERE {col}=?", (eid,)).fetchall():
                found_assets.append({"table": t, "row": {k: ar[k] for k in ar.keys()}})
        except Exception:
            continue
    return found_assets


def parse_choices_from_text(text: str) -> list[tuple[str, str]]:
    # Normalize fullwidth
    t = text.replace("（", "(").replace("）", ")")
    # Pattern like (A)-3 (B)-1 or (A) 1 (B) 2
    parts = re.findall(
        r"\(([A-D])\)\s*([^()]*?)(?=\(([A-D])\)|$)",
        t,
    )
    out = []
    for m in re.finditer(r"\(([A-D])\)\s*", t):
        label = m.group(1)
        start = m.end()
        nxt = re.search(r"\(([A-D])\)\s*", t[start:])
        end = start + nxt.start() if nxt else len(t)
        body = t[start:end].strip().rstrip("。．.;；,，")
        if body:
            out.append((label, body))
    # dedupe by label keep first
    seen = set()
    uniq = []
    for lab, body in out:
        if lab in seen:
            continue
        seen.add(lab)
        uniq.append((lab, body))
    return uniq


def extract_embedded_choices_field(row) -> list:
    for key in ("choices", "options", "choice_list", "answer_choices", "mc_options"):
        if key in cols and row[key]:
            raw = row[key]
            if isinstance(raw, str):
                try:
                    data = json.loads(raw)
                    if isinstance(data, list):
                        return data
                except Exception:
                    return [raw]
            if isinstance(raw, list):
                return raw
    return []


def filesystem_assets(eid: int, skill: str) -> list[str]:
    hits = []
    # common locations
    patterns = [
        ROOT / "uploads" / "question_assets",
        ROOT / "static" / "question_assets",
        ROOT / "instance" / "uploads" / "question_assets",
    ]
    for base in patterns:
        if not base.exists():
            continue
        for p in base.rglob(f"*{eid}*"):
            if p.is_file():
                hits.append(str(p.relative_to(ROOT)).replace("\\", "/"))
        # also search by limited depth for folder named with id
        for p in base.rglob("*"):
            if p.is_file() and f"/{eid}/" in str(p).replace("\\", "/"):
                hits.append(str(p.relative_to(ROOT)).replace("\\", "/"))
    return sorted(set(hits))[:20]


results = []
for row in rows:
    eid = int(row["id"])
    skill = row["skill_id"]
    text = str(row["problem_text"] or "")
    ans = str(row["correct_answer"] or "") if "correct_answer" in cols else ""
    sol = str(row["detailed_solution"] or "") if "detailed_solution" in cols else ""
    src_desc = str(row["source_description"] or "") if "source_description" in cols else ""
    ptype = str(row["problem_type"] or "") if "problem_type" in cols else ""
    pt_id = PT_MAP.get(eid, "UNKNOWN")

    db_assets = find_assets(eid)
    fs_assets = filesystem_assets(eid, skill)
    # image columns on TE
    img_cols = {}
    for c in cols:
        if any(k in c.lower() for k in ("image", "asset", "figure", "graph", "visual", "path")):
            val = row[c]
            if val not in (None, "", 0, "null", "None"):
                img_cols[c] = str(val)[:200]

    html_img = bool(HTML_IMG.search(text) or HTML_IMG.search(sol))
    asset_found = bool(db_assets or fs_assets or img_cols or html_img)
    asset_count = len(db_assets) + len(fs_assets) + len(img_cols) + (1 if html_img else 0)

    needs_image = bool(IMG_HINTS.search(text) or IMG_HINTS.search(sol))
    needs_table = bool(TABLE_HINTS.search(text) or TABLE_HINTS.search(sol))

    embedded_choices = parse_choices_from_text(text)
    field_choices = extract_embedded_choices_field(row)
    # Also check answer field for choice letter only
    choice_in_text = bool(CHOICE_HINTS.search(text)) or len(embedded_choices) >= 2
    # exam/self_assessment often choice
    source_suggests_choice = ptype in ("exam_practice", "self_assessment") and (
        "(A)" in text or "（A）" in text or choice_in_text
    )
    needs_choices = choice_in_text or source_suggests_choice or bool(field_choices)

    choices_complete = False
    choice_n = 0
    if field_choices:
        choice_n = len(field_choices)
        choices_complete = choice_n >= 2
    elif embedded_choices:
        choice_n = len(embedded_choices)
        labels = [c[0] for c in embedded_choices]
        bodies = [c[1].strip() for c in embedded_choices]
        # complete if A-D mostly present with non-empty bodies
        if choice_n >= 4 and all(bodies) and len(set(labels)) == choice_n:
            choices_complete = True
        elif choice_n >= 2 and all(bodies) and len(set(bodies)) == len(bodies):
            # partial but usable if bodies non-empty unique
            choices_complete = choice_n >= 4 or (set(labels) >= {"A", "B", "C", "D"} and all(bodies))
            if choice_n == 4 and all(bodies):
                choices_complete = True
        else:
            choices_complete = False

    # truncation heuristics
    truncated = False
    trunc_reasons = []
    if len(text.strip()) < 8:
        truncated = True
        trunc_reasons.append("question_text_too_short")
    if TRUNC_TAIL.search(text.strip()):
        truncated = True
        trunc_reasons.append("ends_with_incomplete_prompt")
    if text.count("$") % 2 == 1:
        truncated = True
        trunc_reasons.append("unbalanced_latex_dollar")
    if PLACEHOLDER.search(text):
        truncated = True
        trunc_reasons.append("placeholder")
    # mid-sentence cut like ending with \\ or unmatched
    if re.search(r"\\\\?\s*$", text.strip()) and not text.strip().endswith("。"):
        # weak signal
        pass
    if "試求" in text and re.search(r"試求[:：]?\s*$", text.strip()):
        truncated = True
        trunc_reasons.append("asks_求_but_no_object")

    # can understand without guessing?
    incomplete_refs = []
    if needs_image and not asset_found:
        incomplete_refs.append("image_ref_without_asset")
    if needs_table and not asset_found and "表" in text:
        # table may be embedded as latex/text; only missing if no tabular structure
        has_tabular = bool(re.search(r"\\begin\{tabular\}|\\begin\{array\}|<table", text, re.I))
        if not has_tabular:
            incomplete_refs.append("table_ref_without_data")

    # answer topology observation (read-only)
    topology_obs = "unknown"
    if needs_choices and choices_complete:
        topology_obs = "choice"
    elif re.search(r"（\s*1\s*）|\(1\)|（1）|試求：\s*\(1\)|：(1)", text):
        topology_obs = "multi_part"
    elif re.search(r"試求|求|則", text) and not needs_choices:
        topology_obs = "short_answer_or_expression"
    if needs_choices and not choices_complete:
        topology_obs = "choice_incomplete"

    # presentation: multi_part short_answer and choice are supported in production generally
    presentation_unsupported = False

    # classify feasibility
    evidence = []
    evidence.append(f"problem_type={ptype}")
    evidence.append(f"source_description={src_desc}")
    evidence.append(f"text_len={len(text)}")
    evidence.append(f"asset_count={asset_count}")
    if needs_image:
        evidence.append("text_has_image_cue")
    if needs_table:
        evidence.append("text_has_table_cue")
    if needs_choices:
        evidence.append(f"needs_choices choice_n={choice_n} embedded={[(a,b[:20]) for a,b in embedded_choices[:4]]}")
    if field_choices:
        evidence.append(f"field_choices_n={len(field_choices)}")
    if trunc_reasons:
        evidence.append(f"trunc={trunc_reasons}")
    if img_cols:
        evidence.append(f"te_image_cols={list(img_cols)}")
    if fs_assets:
        evidence.append(f"fs_assets={fs_assets[:3]}")
    evidence.append(f"topology_obs={topology_obs}")
    evidence.append(f"text_preview={text[:120].replace(chr(10),' ')}")

    status = None
    if needs_image and not asset_found:
        status = "IMAGE_REQUIRED_BUT_MISSING"
    elif needs_table and "table_ref_without_data" in incomplete_refs:
        status = "TABLE_REQUIRED_BUT_MISSING"
    elif needs_choices and not choices_complete:
        status = "CHOICES_INCOMPLETE"
    elif truncated or len(text.strip()) < 8:
        status = "SOURCE_INCOMPLETE"
    elif presentation_unsupported:
        status = "PRESENTATION_UNSUPPORTED"
    elif topology_obs == "unknown":
        status = "ANSWER_TOPOLOGY_UNRESOLVED"
    elif topology_obs == "choice_incomplete":
        status = "CHOICES_INCOMPLETE"
    else:
        # source looks complete enough
        status = "READY_FOR_COMPONENT"

    # refine: choice with complete embedded options → READY even if exam
    if status == "CHOICES_INCOMPLETE" and choices_complete:
        status = "READY_FOR_COMPONENT"

    # if choice needed and we have A-D with bodies from text → READY
    if needs_choices and choices_complete and status not in (
        "IMAGE_REQUIRED_BUT_MISSING",
        "TABLE_REQUIRED_BUT_MISSING",
        "SOURCE_INCOMPLETE",
    ):
        status = "READY_FOR_COMPONENT"

    # multi-part clear text without image → READY
    source_complete = status == "READY_FOR_COMPONENT"

    if status == "READY_FOR_COMPONENT":
        decision = "INCLUDE"
    elif status in (
        "IMAGE_REQUIRED_BUT_MISSING",
        "TABLE_REQUIRED_BUT_MISSING",
        "CHOICES_INCOMPLETE",
        "SOURCE_INCOMPLETE",
        "PRESENTATION_UNSUPPORTED",
    ):
        decision = "EXCLUDE"
    else:
        decision = "REVIEW"

    reason = status
    if status == "READY_FOR_COMPONENT":
        reason = "pure_text_or_complete_choices; no missing figure/table asset required"
    elif status == "CHOICES_INCOMPLETE":
        reason = f"choice cues present but choices incomplete (n={choice_n})"
    elif status == "IMAGE_REQUIRED_BUT_MISSING":
        reason = "image cue in stem but asset_count=0"
    elif status == "TABLE_REQUIRED_BUT_MISSING":
        reason = "table cue without tabular/table asset"
    elif status == "SOURCE_INCOMPLETE":
        reason = ",".join(trunc_reasons) or "incomplete stem"

    results.append(
        {
            "example_id": eid,
            "skill_id": skill,
            "problem_type_id": pt_id,
            "problem_type": ptype,
            "source_description": src_desc,
            "needs_image": needs_image,
            "needs_table": needs_table,
            "needs_choices": needs_choices,
            "asset_found": asset_found,
            "asset_count": asset_count,
            "choice_n": choice_n,
            "choices_complete": choices_complete,
            "embedded_choices": [{"label": a, "text": b} for a, b in embedded_choices],
            "source_complete": source_complete,
            "feasibility_status": status,
            "rebuild_decision": decision,
            "topology_observation": topology_obs,
            "evidence": "; ".join(evidence),
            "reason": reason,
            "correct_answer_preview": (ans or "")[:80],
            "question_text": text,
        }
    )

# counts
from collections import Counter

st = Counter(r["feasibility_status"] for r in results)
dec = Counter(r["rebuild_decision"] for r in results)

out = {
    "scope_match": found == EXPECTED,
    "te_columns": cols,
    "asset_tables": asset_tables,
    "status_counts": dict(st),
    "decision_counts": dict(dec),
    "rows": results,
}
(ROOT / "scratch" / "_b1_3_1_source_feasibility.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
)

print("scope_match", out["scope_match"], "n", len(results))
print("status", dict(st))
print("decision", dict(dec))
print("asset_tables", asset_tables)
print("te_image_like_cols", [c for c in cols if any(k in c.lower() for k in ("image", "asset", "figure", "path", "graph"))])
for r in results:
    print(
        f"{r['example_id']}\t{r['feasibility_status']}\t{r['rebuild_decision']}\t"
        f"img={r['needs_image']}/asset={r['asset_found']}\tch={r['needs_choices']}/{r['choice_n']}\t"
        f"{r['reason'][:60]}"
    )
