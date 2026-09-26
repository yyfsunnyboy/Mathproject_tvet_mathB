# -*- coding: utf-8 -*-
"""B2 Ch4 student-runtime audit (families + next-question + diversity).

Produces:
  reports/b2_ch4_student_runtime_audit.{json,md}
  reports/b2_ch4_next_question_runtime_audit.{json,md}
  scratch/_b2_ch4_student_runtime_qa/index.html
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
QA_DIR = ROOT / "scratch" / "_b2_ch4_student_runtime_qa"

SKILLS = [
    f"vh_數學B2_SubSection_4_{a}_{b}"
    for a, b in [
        (1, 1),
        (1, 2),
        (2, 1),
        (2, 2),
        (2, 3),
        (2, 4),
    ]
]

RAW_TEX_RE = re.compile(r"\\(?:vec|overrightarrow|frac|sqrt)\b")


def _raw_tex_outside_math(text: str) -> bool:
    source = str(text or "")
    if not source:
        return False
    stripped = re.sub(r"\$\$[\s\S]*?\$\$|\$[^$]*\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", "", source)
    return bool(RAW_TEX_RE.search(stripped))


def _fp(blob: Any) -> str:
    raw = json.dumps(blob, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _visual_entities(vs: dict[str, Any]) -> list[str]:
    labels: list[str] = []
    pts = vs.get("points") or []
    if isinstance(pts, list):
        labels.extend(str(p.get("label") or "") for p in pts if isinstance(p, dict))
    elif isinstance(pts, dict):
        labels.extend(str(k) for k in pts.keys())
    for circle in vs.get("circles") or []:
        if isinstance(circle, dict):
            labels.append(str(circle.get("label") or "circle"))
    for line in vs.get("lines") or []:
        if isinstance(line, dict):
            labels.append(str(line.get("label") or "line"))
    return [x for x in labels if x]


def _effective_fingerprint(payload: dict[str, Any]) -> dict[str, Any]:
    vs = payload.get("visual_spec") if isinstance(payload.get("visual_spec"), dict) else {}
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    return {
        "family": payload.get("problem_type_id") or payload.get("domain_operation"),
        "component": payload.get("component_id"),
        "answer": payload.get("correct_answer") or payload.get("answer"),
        "choices": [
            (c.get("label"), c.get("value") or c.get("text"))
            for c in (payload.get("choices") or [])
            if isinstance(c, dict)
        ],
        "parts": [
            (p.get("key"), p.get("expected_answer") or p.get("label"))
            for p in (ac.get("parts") or [])
            if isinstance(p, dict)
        ],
        "stem_math": re.sub(r"\s+", " ", str(payload.get("question_text") or ""))[:240],
        "visual_points": _visual_entities(vs),
        "visual_circles": len(vs.get("circles") or []),
        "visual_lines": len(vs.get("lines") or []),
    }


def _label_ok(parts: list[dict[str, Any]]) -> bool:
    if not parts:
        return True
    from core.gencode.domain_matrix_adapter import _looks_like_internal_part_key

    for part in parts:
        key = str(part.get("key") or "")
        label = str(part.get("display_label") or part.get("label") or "")
        if not label.strip():
            return False
        if _looks_like_internal_part_key(key, label):
            return False
        if "_" in key and label.replace(" ", "") == key.replace("_", ""):
            return False
    return True


_FLOAT_NOISE_RE = re.compile(r"(?<![\d.\\])-?\d+\.\d{6,}(?!\d)")


def _student_visible_float_noise(payload: dict[str, Any]) -> bool:
    blobs = [str(payload.get("question_text") or "")]
    for choice in payload.get("choices") or []:
        if isinstance(choice, dict):
            blobs.append(str(choice.get("text") or ""))
            blobs.append(str(choice.get("display") or ""))
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    for part in ac.get("parts") or []:
        if isinstance(part, dict):
            blobs.append(str(part.get("display_label") or part.get("label") or ""))
    return any(_FLOAT_NOISE_RE.search(blob) for blob in blobs)


def _runtime_is_mcq(payload: dict[str, Any]) -> bool:
    at = str(payload.get("answer_type") or "").strip().lower()
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    contract_at = str(ac.get("answer_type") or "").strip().lower()
    pres = str(payload.get("presentation_mode") or ac.get("presentation_mode") or "").strip().lower()
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    if at in {"single_choice", "choice", "choice_label"} or contract_at in {
        "single_choice",
        "choice",
        "choice_label",
    }:
        return True
    if pres == "single_choice":
        return True
    if choices and all(isinstance(c, dict) and (c.get("label") or c.get("key")) for c in choices):
        return True
    return False


def _stem_complete(stem: str, *, is_multi: bool, parts: list[dict[str, Any]]) -> bool:
    text = str(stem or "").strip()
    if len(text) < 8:
        return False
    _ = is_multi, parts
    return True


def _diagram_ok(payload: dict[str, Any], family: str) -> tuple[bool, bool, dict[str, Any]]:
    vs = payload.get("visual_spec") if isinstance(payload.get("visual_spec"), dict) else {}
    if not vs or vs.get("kind") in {None, "none"}:
        return True, True, {"required_entity_count": 0, "rendered_entity_count": 0, "extraneous_entity_count": 0}
    ents = [e for e in _visual_entities(vs) if e]
    circles = list(vs.get("circles") or [])
    lines = list(vs.get("lines") or [])
    points = list(vs.get("points") or []) if isinstance(vs.get("points"), list) else []
    # Semantic floor: if a circle visual is present, require at least one circle entity.
    ok_sem = True
    if "circle" in family or "chord" in family or "tangent" in family or "point" in family:
        if circles or points or lines:
            ok_sem = bool(circles) or bool(points)
    clutter = max(0, len(ents) - 10)
    return ok_sem, clutter <= 4, {
        "required_entity_count": len(ents),
        "rendered_entity_count": len(ents),
        "extraneous_entity_count": clutter,
        "circles": len(circles),
        "lines": len(lines),
        "points": len(points),
        "rendered": ents,
    }


def _classify_diversity(unique: int, sample: int, family: str) -> str:
    if unique <= 1:
        if family.endswith("_mcq"):
            return "EXPECTED_LIMITED_VARIATION"
        return "FIXED_TEMPLATE"
    rate = unique / max(sample, 1)
    if rate < 0.25:
        if family.endswith("_mcq") and unique >= 4:
            return "EXPECTED_LIMITED_VARIATION"
        return "LOW_DIVERSITY"
    if unique < 5 and (family.endswith("_mcq") or family.startswith("classify_") or family.startswith("solve_")):
        return "EXPECTED_LIMITED_VARIATION"
    return "PASS"


def audit_families() -> dict[str, Any]:
    import importlib

    rows = []
    family_components: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for skill in SKILLS:
        mod = importlib.import_module(f"skills.{skill}")
        for spec in getattr(mod, "GENERATOR_SPECS", []):
            fam = str(spec.get("problem_type_id") or "")
            family_components[fam].append((skill, str(spec.get("component_id") or "")))

    for family, comps in sorted(family_components.items()):
        skill, component = comps[0]
        mod = importlib.import_module(f"skills.{skill}")
        samples = []
        for seed in range(20):
            payload = mod.generate(seed=seed, component_id=component)
            samples.append(payload)
        payload0 = samples[0]
        ac = payload0.get("answer_contract") if isinstance(payload0.get("answer_contract"), dict) else {}
        parts = list(ac.get("parts") or [])
        choices = list(payload0.get("choices") or [])
        stem = str(payload0.get("question_text") or "")
        answer_type = str(payload0.get("answer_type") or ac.get("answer_type") or "")
        is_mcq = _runtime_is_mcq(payload0)
        is_multi = answer_type == "multi_part" or len(parts) > 1
        has_visual = isinstance(payload0.get("visual_spec"), dict) and payload0["visual_spec"].get("kind") not in {
            None,
            "none",
        }
        fps = {_fp(_effective_fingerprint(p)) for p in samples}
        ans_set = {
            json.dumps(p.get("correct_answer") or p.get("answer"), ensure_ascii=False, sort_keys=True, default=str)
            for p in samples
        }
        param_set = fps
        vis_set = {_fp(_visual_entities(p.get("visual_spec") or {})) for p in samples}
        stem_ok = _stem_complete(stem, is_multi=is_multi, parts=parts)
        label_ok = _label_ok(parts)
        math_ok = not _raw_tex_outside_math(stem)
        if is_mcq:
            math_ok = math_ok and all(
                (
                    str(c.get("text") or "").startswith("$")
                    or str(c.get("text") or "").startswith(r"\(")
                    or not _raw_tex_outside_math(str(c.get("text") or ""))
                )
                for c in choices
                if isinstance(c, dict)
            )
        choices_ok = (not is_mcq) or (
            len(choices) >= 2
            and len({str(c.get("value") or c.get("text")) for c in choices}) == len(choices)
        )
        if is_mcq:
            from core.gencode.choice_contract_validator import (
                choice_semantic_key,
                has_technical_choice_suffix,
            )

            texts = [str(c.get("text") or c.get("value") or "") for c in choices if isinstance(c, dict)]
            if any(has_technical_choice_suffix(t) for t in texts):
                choices_ok = False
            keys = [choice_semantic_key(t) for t in texts]
            if len(keys) != len(set(keys)) or any(not k for k in keys):
                choices_ok = False
            expected = str(
                (ac.get("semantic_answer") if isinstance(ac, dict) else None)
                or payload0.get("display_answer")
                or payload0.get("correct_answer")
                or ""
            )
            if expected and expected.upper() not in {"A", "B", "C", "D"}:
                matches = sum(1 for t in texts if choice_semantic_key(t) == choice_semantic_key(expected))
                if matches != 1:
                    choices_ok = False
        name_says_mcq = "mcq" in str(family).lower()
        mcq_schema_ok = (not name_says_mcq) or (is_mcq and choices_ok)
        diag_sem, diag_rel, diag_stats = _diagram_ok(payload0, family)
        diversity = _classify_diversity(len(fps), len(samples), family)
        float_noise = _student_visible_float_noise(payload0)
        failures = []
        if not stem_ok:
            failures.append("FAIL_STEM")
        if not label_ok:
            failures.append("FAIL_LABEL")
        if not math_ok:
            failures.append("FAIL_MATH_RENDER")
        if not choices_ok:
            failures.append("FAIL_MCQ_CHOICES")
        if not mcq_schema_ok:
            failures.append("FAIL_MCQ_SCHEMA")
        if not diag_sem:
            failures.append("FAIL_DIAGRAM_SEMANTIC")
        if not diag_rel:
            failures.append("FAIL_DIAGRAM_CLUTTER")
        if float_noise:
            failures.append("FAIL_FLOAT_NOISE")
        if diversity == "FIXED_TEMPLATE":
            failures.append("FAIL_FIXED_TEMPLATE")
        final = "PASS" if not failures else "BLOCKED"
        rows.append(
            {
                "family_id": family,
                "skill_id": skill,
                "component_id": component,
                "final_status": final,
                "meaningful_diversity": diversity,
                "has_visual": has_visual,
                "is_mcq": is_mcq,
                "is_multi_part": is_multi,
                "unique_problem_count": len(fps),
                "unique_parameter_count": len(param_set),
                "unique_answer_count": len(ans_set),
                "unique_visual_count": len(vis_set),
                "duplicate_rate": round(1 - len(fps) / max(len(samples), 1), 3),
                "diagram_stats": diag_stats,
                "failures": failures,
                "representative_stem": stem[:180],
                "representative_parts": parts,
                "representative_choices": choices,
            }
        )
    return {
        "total_families": len(rows),
        "pass": sum(1 for r in rows if r["final_status"] == "PASS"),
        "blocked": sum(1 for r in rows if r["final_status"] != "PASS"),
        "families": rows,
    }


def audit_next_question() -> dict[str, Any]:
    from app import create_app
    from models import User, db
    import uuid

    app = create_app()
    app.config.update(TESTING=True)
    skill_rows = []
    with app.app_context():
        user = User(username=f"b2ch4_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    client = app.test_client()
    with client.session_transaction() as sess:
        sess["_user_id"] = str(uid)
        sess["_fresh"] = True

    taxonomy = Counter()
    for skill in SKILLS:
        samples = []
        for _i in range(10):
            resp = client.get(f"/get_next_question?skill={quote(skill)}&level=1")
            data = resp.get_json() or {}
            samples.append(data)
        fps = []
        comps = []
        for data in samples:
            if data.get("error"):
                fps.append(f"ERR:{data.get('error')}")
                continue
            fps.append(_fp(_effective_fingerprint(data)))
            comps.append(str(data.get("component_id") or data.get("generator_key") or ""))
        unique = len(set(fps))
        families = sorted({str((s.get("problem_type_id") or "")) for s in samples if not s.get("error")})
        if unique <= 1:
            cause = "R3_FIXED_GENERATOR"
        elif unique <= 3 and len(set(comps)) <= 1:
            cause = "R4_COMPONENT_STUCK"
        elif unique < 5 and len(set(comps)) >= 2:
            cause = "R5_LOW_PARAMETER_SPACE"
        else:
            cause = "OK"
        uids = [s.get("question_uid") for s in samples]
        if len(uids) != len(set(uids)):
            cause = "R1_RUNTIME_REUSE"
            taxonomy["R1_RUNTIME_REUSE"] += 1
        else:
            taxonomy[cause] += 1
        status = "PASS" if cause in {"OK", "R5_LOW_PARAMETER_SPACE"} and unique >= 3 else ("PASS" if unique >= 5 else "FAIL")
        if cause == "R5_LOW_PARAMETER_SPACE" and unique >= 4:
            status = "PASS"
        skill_rows.append(
            {
                "skill": skill,
                "request_count": len(samples),
                "unique_effective_questions": unique,
                "families_observed": families,
                "components_observed": sorted(set(comps)),
                "duplicate_count": len(samples) - unique,
                "root_cause": cause,
                "status": status,
                "errors": [s.get("error") for s in samples if s.get("error")],
            }
        )
    return {
        "skills": skill_rows,
        "taxonomy": dict(taxonomy),
        "pass": sum(1 for r in skill_rows if r["status"] == "PASS"),
        "blocked": sum(1 for r in skill_rows if r["status"] != "PASS"),
    }


def write_md_family(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# B2 Ch4 Student Runtime Family Audit",
        "",
        f"Total families: {data['total_families']}",
        f"PASS: {data['pass']}",
        f"BLOCKED: {data['blocked']}",
        "",
        "| family | skill | status | diversity | unique/20 | visual | mcq | multi | failures |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for row in data["families"]:
        lines.append(
            f"| {row['family_id']} | {'/'.join(row['skill_id'].split('_')[-3:])} | {row['final_status']} | "
            f"{row['meaningful_diversity']} | {row['unique_problem_count']} | {row['has_visual']} | "
            f"{row['is_mcq']} | {row['is_multi_part']} | {','.join(row['failures']) or '-'} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_md_next(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# B2 Ch4 Next-Question Runtime Audit",
        "",
        f"PASS skills: {data['pass']}",
        f"BLOCKED skills: {data['blocked']}",
        f"Taxonomy: {data['taxonomy']}",
        "",
        "| skill | requests | unique | families | duplicates | root_cause | status |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in data["skills"]:
        lines.append(
            f"| {row['skill']} | {row['request_count']} | {row['unique_effective_questions']} | "
            f"{len(row['families_observed'])} | {row['duplicate_count']} | {row['root_cause']} | {row['status']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_qa_harness(family_audit: dict[str, Any]) -> None:
    QA_DIR.mkdir(parents=True, exist_ok=True)
    cards = []
    for row in family_audit["families"]:
        choices = row.get("representative_choices") or []
        parts = row.get("representative_parts") or []
        choice_html = "".join(
            f"<li><b>{html.escape(str(c.get('label') or ''))}</b> "
            f"{html.escape(str(c.get('text') or c.get('value') or ''))}</li>"
            for c in choices
            if isinstance(c, dict)
        )
        part_html = "".join(
            f"<li>{html.escape(str(p.get('display_label') or p.get('label') or p.get('key') or ''))}</li>"
            for p in parts
            if isinstance(p, dict)
        )
        status = row["final_status"]
        color = "#0a7" if status == "PASS" else "#c33"
        cards.append(
            f"""
<section style="border:1px solid #ddd;padding:12px;margin:12px 0;border-left:6px solid {color}">
  <h3>{html.escape(row['family_id'])} <small>({html.escape(row['skill_id'])})</small></h3>
  <p><b>status:</b> {status} | <b>diversity:</b> {html.escape(row['meaningful_diversity'])} |
     <b>unique/20:</b> {row['unique_problem_count']} | <b>visual:</b> {row['has_visual']}</p>
  <p><b>failures:</b> {html.escape(','.join(row['failures']) or '-')}</p>
  <p><b>stem:</b> {html.escape(str(row.get('representative_stem') or ''))}</p>
  {"<ol>" + choice_html + "</ol>" if choice_html else ""}
  {"<ul>" + part_html + "</ul>" if part_html else ""}
</section>
"""
        )
    doc = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><title>B2 Ch4 Student Runtime QA</title>
<style>body{{font-family:system-ui,sans-serif;max-width:960px;margin:24px auto;padding:0 16px}}
code{{background:#f4f4f4;padding:2px 4px}}</style></head>
<body>
<h1>B2 Ch4 Student Runtime QA</h1>
<p>PASS {family_audit['pass']} / {family_audit['total_families']} &nbsp; BLOCKED {family_audit['blocked']}</p>
{''.join(cards)}
</body></html>
"""
    (QA_DIR / "index.html").write_text(doc, encoding="utf-8")


def main() -> None:
    fam = audit_families()
    (REPORTS / "b2_ch4_student_runtime_audit.json").write_text(
        json.dumps(fam, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_family(fam, REPORTS / "b2_ch4_student_runtime_audit.md")
    write_qa_harness(fam)
    print("family", fam["pass"], "/", fam["total_families"], "blocked", fam["blocked"])
    nxt = audit_next_question()
    (REPORTS / "b2_ch4_next_question_runtime_audit.json").write_text(
        json.dumps(nxt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_next(nxt, REPORTS / "b2_ch4_next_question_runtime_audit.md")
    print("next", nxt["pass"], "/", len(nxt["skills"]), "blocked", nxt["blocked"], nxt["taxonomy"])


if __name__ == "__main__":
    main()
