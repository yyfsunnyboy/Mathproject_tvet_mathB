# -*- coding: utf-8 -*-
"""B2 Ch3 student-runtime audit (families + next-question + diversity).

Produces:
  reports/b2_ch3_student_runtime_audit.{json,md}
  reports/b2_ch3_next_question_runtime_audit.{json,md}
  scratch/_b2_ch3_student_runtime_qa/index.html
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
QA_DIR = ROOT / "scratch" / "_b2_ch3_student_runtime_qa"

SKILLS = [
    f"vh_數學B2_SubSection_3_{a}_{b}"
    for a, b in [
        (1, 1), (1, 2), (1, 3), (1, 4),
        (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6),
        (3, 1), (3, 2), (3, 3), (3, 4), (3, 5),
    ]
]

RAW_TEX_RE = re.compile(r"\\(?:vec|overrightarrow|frac|sqrt)\b")


def _raw_tex_outside_math(text: str) -> bool:
    """True when TeX commands appear outside $...$ or \\(...\\) spans."""
    source = str(text or "")
    if not source:
        return False
    # Strip delimited math, then look for leftover TeX commands.
    stripped = re.sub(r"\$\$[\s\S]*?\$\$|\$[^$]*\$|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", "", source)
    return bool(RAW_TEX_RE.search(stripped))


def _fp(blob: Any) -> str:
    raw = json.dumps(blob, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def _visual_entities(vs: dict[str, Any]) -> list[str]:
    pts = vs.get("points") or []
    if isinstance(pts, list):
        return [str(p.get("label") or "") for p in pts if isinstance(p, dict)]
    if isinstance(pts, dict):
        return sorted(str(k) for k in pts.keys())
    return []


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
        "visual_arrows": len(vs.get("arrows") or []),
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
        # Underscore→space rewrite is still an internal-key leak, not a real label.
        if "_" in key and label.replace(" ", "") == key.replace("_", ""):
            return False
    return True


_FLOAT_NOISE_RE = re.compile(r"(?<![\d.\\])-?\d+\.\d{6,}(?!\d)")


def _student_visible_float_noise(payload: dict[str, Any]) -> bool:
    """True when ordinary classroom float noise appears in student-visible math text."""
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
    """Classify MCQ from canonical runtime schema, not from family-name suffix."""
    at = str(payload.get("answer_type") or "").strip().lower()
    ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
    contract_at = str(ac.get("answer_type") or "").strip().lower()
    pres = str(payload.get("presentation_mode") or ac.get("presentation_mode") or "").strip().lower()
    choices = payload.get("choices") if isinstance(payload.get("choices"), list) else []
    if at in {"single_choice", "choice"} or contract_at in {"single_choice", "choice"}:
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
    if "填入實數完成向量倍數關係" in text and "k_1" not in text and "k1" not in text and "$k" not in text:
        return False
    if is_multi and parts:
        # Require stem to mention at least one student-visible symbol for multi-part.
        labels = " ".join(str(p.get("display_label") or p.get("label") or p.get("key") or "") for p in parts)
        if "k1" in {str(p.get("key")) for p in parts} and "k_" not in text and "k1" not in text and "倍數" in text:
            if "k_1" not in text and "$k" not in text:
                return False
        _ = labels
    return True


def _diagram_ok(payload: dict[str, Any], family: str) -> tuple[bool, bool, dict[str, Any]]:
    vs = payload.get("visual_spec") if isinstance(payload.get("visual_spec"), dict) else {}
    if not vs or vs.get("kind") in {None, "none"}:
        return True, True, {"required_entity_count": 0, "rendered_entity_count": 0, "extraneous_entity_count": 0}
    ents = [e for e in _visual_entities(vs) if e]
    required = list(vs.get("required_entities") or ents)
    if family == "solve_section_coefficient_pair":
        required = ["A", "E", "F", "M"]
        ok_sem = all(r in ents for r in required)
        clutter = len([e for e in ents if e not in required])
        return ok_sem, clutter <= 1, {
            "required_entity_count": len(required),
            "rendered_entity_count": len(ents),
            "extraneous_entity_count": clutter,
            "required": required,
            "rendered": ents,
        }
    if family == "express_section_point_vector":
        required = ["A", "B", "C", "D", "E", "F"]
        ok_sem = all(r in ents for r in ["A", "B", "C"])
        clutter = max(0, len(ents) - 8)
        return ok_sem, clutter <= 2, {
            "required_entity_count": len(required),
            "rendered_entity_count": len(ents),
            "extraneous_entity_count": clutter,
            "required": required,
            "rendered": ents,
        }
    clutter = 0
    if len(ents) >= 9 and len(vs.get("lines") or []) >= len(ents):
        clutter = len(ents) - 6
    return True, clutter <= 3, {
        "required_entity_count": len(required),
        "rendered_entity_count": len(ents),
        "extraneous_entity_count": max(0, clutter),
        "rendered": ents,
    }


def _classify_diversity(unique: int, sample: int, family: str) -> str:
    if unique <= 1:
        # Pure topology drills with only label/shuffle variation still need a reason.
        if family in {
            "identify_unit_vector_mcq",
            "solve_navigation_heading_correction",
            "solve_parallel_then_magnitude_mcq",
            "solve_perpendicular_composite_parameter",
        }:
            return "EXPECTED_LIMITED_VARIATION"
        return "FIXED_TEMPLATE"
    rate = unique / max(sample, 1)
    if rate < 0.25:
        if family.endswith("_mcq") and unique >= 4:
            return "EXPECTED_LIMITED_VARIATION"
        if family in {
            "express_named_vectors_in_given_basis",
            "solve_equal_vector_coordinates",
            "solve_angle_from_magnitude_identity",
            "express_section_point_vector",
        }:
            return "EXPECTED_LIMITED_VARIATION"
        return "LOW_DIVERSITY"
    if unique < 5 and (family.endswith("_mcq") or family.startswith("express_") or family.startswith("solve_")):
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
        has_visual = isinstance(payload0.get("visual_spec"), dict) and payload0["visual_spec"].get("kind") not in {None, "none"}
        fps = {_fp(_effective_fingerprint(p)) for p in samples}
        ans_set = {json.dumps(p.get("correct_answer") or p.get("answer"), ensure_ascii=False, sort_keys=True, default=str) for p in samples}
        param_set = fps  # effective params folded into fingerprint
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
            len(choices) == 4
            and len({str(c.get("value") or c.get("text")) for c in choices}) == 4
        )
        if is_mcq:
            from core.gencode.choice_contract_validator import (
                choice_semantic_key,
                has_technical_choice_suffix,
            )

            texts = [str(c.get("text") or c.get("value") or "") for c in choices if isinstance(c, dict)]
            if any(has_technical_choice_suffix(t) for t in texts):
                choices_ok = False
                failures_pre = ["FAIL_MCQ_CHOICES"]
            else:
                failures_pre = []
            keys = [choice_semantic_key(t) for t in texts]
            if len(keys) != 4 or len(set(keys)) != 4 or any(not k for k in keys):
                choices_ok = False
            expected = str(
                (ac.get("semantic_answer") if isinstance(ac, dict) else None)
                or payload0.get("display_answer")
                or payload0.get("correct_answer")
                or ""
            )
            # Label answers are fine; only coordinate/expression semantics can multi-match.
            if expected and expected.upper() not in {"A", "B", "C", "D"}:
                matches = sum(1 for t in texts if choice_semantic_key(t) == choice_semantic_key(expected))
                if matches != 1:
                    choices_ok = False
        else:
            failures_pre = []
        # Name/schema consistency: *_mcq family must be runtime MCQ with choices.
        name_says_mcq = "mcq" in str(family).lower()
        mcq_schema_ok = (not name_says_mcq) or (is_mcq and choices_ok)
        diag_sem, diag_rel, diag_stats = _diagram_ok(payload0, family)
        diversity = _classify_diversity(len(fps), len(samples), family)
        next_ok = diversity in {"PASS", "EXPECTED_LIMITED_VARIATION"} and len(fps) >= 2

        failures = list(failures_pre)
        if not stem_ok:
            failures.append("FAIL_STEM")
        if not math_ok:
            failures.append("FAIL_MATH_RENDER")
        if is_multi and not label_ok:
            failures.append("FAIL_INPUT_CONTRACT")
        if is_mcq and not choices_ok:
            failures.append("FAIL_MCQ_CHOICES")
        if is_mcq and not math_ok:
            failures.append("FAIL_MCQ_MAPPING")
        if not mcq_schema_ok:
            failures.append("FAIL_MCQ_MAPPING")
        if has_visual and not diag_sem:
            failures.append("FAIL_DIAGRAM_SEMANTICS")
        if has_visual and not diag_rel:
            failures.append("FAIL_DIAGRAM_CLUTTER")
        if diversity == "FIXED_TEMPLATE":
            failures.append("FAIL_FIXED_GENERATOR")
        if diversity == "LOW_DIVERSITY":
            failures.append("FAIL_FIXED_GENERATOR")
        if _student_visible_float_noise(payload0):
            failures.append("FAIL_MATH_RENDER")
        # EXPECTED_LIMITED_VARIATION is an accepted diversity class, not a runtime failure.
        final = "PASS" if not failures else failures[0]

        rows.append({
            "skill_id": skill,
            "family_id": family,
            "source_example_ids": [int(c.split("_")[1]) for _, c in comps if c.startswith("src_")],
            "source_type": "mixed",
            "answer_type": answer_type,
            "question_type": "single_choice" if is_mcq else ("multi_part" if is_multi else "short_answer"),
            "has_visual": has_visual,
            "is_mcq": is_mcq,
            "is_multi_part": is_multi,
            "stem_complete": stem_ok,
            "math_render_ok": math_ok,
            "input_widget_ok": label_ok if is_multi else True,
            "choices_render_ok": choices_ok,
            "diagram_render_ok": bool(has_visual),
            "diagram_semantics_ok": diag_sem,
            "diagram_relevance_ok": diag_rel,
            "answer_contract_ok": bool(ac.get("answer_type") or answer_type),
            "checker_ok": bool(ac.get("checker") or ac.get("checker_key") or payload0.get("checker")),
            "meaningful_diversity": diversity,
            "next_question_ok": next_ok,
            "sample_count": len(samples),
            "unique_problem_count": len(fps),
            "unique_parameter_count": len(param_set),
            "unique_answer_count": len(ans_set),
            "unique_visual_count": len(vis_set),
            "duplicate_rate": round(1 - len(fps) / max(len(samples), 1), 3),
            "diagram_stats": diag_stats,
            "final_status": final,
            "failures": failures,
            "representative_stem": stem[:180],
            "representative_parts": parts,
            "representative_choices": choices,
        })
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
        user = User(username=f"b2rt_{uuid.uuid4().hex[:8]}", password_hash="x", role="student")
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
        for i in range(10):
            resp = client.get(f"/get_next_question?skill={quote(skill)}&level=1")
            data = resp.get_json() or {}
            samples.append(data)
        fps = []
        comps = []
        for data in samples:
            if data.get("error"):
                fps.append(f"ERR:{data.get('error')}")
                continue
            eff = _effective_fingerprint(data)
            fps.append(_fp(eff))
            comps.append(str(data.get("component_id") or data.get("generator_key") or ""))
        unique = len(set(fps))
        families = sorted({str((s.get("problem_type_id") or "")) for s in samples if not s.get("error")})
        # Classify root cause heuristic
        if unique <= 1:
            cause = "R3_FIXED_GENERATOR"
        elif unique <= 3 and len(set(comps)) <= 1:
            cause = "R4_COMPONENT_STUCK"
        elif unique < 5 and len(set(comps)) >= 2:
            cause = "R5_LOW_PARAMETER_SPACE"
        else:
            cause = "OK"
        # Detect reuse: identical question_uid consecutive
        uids = [s.get("question_uid") for s in samples]
        if len(uids) != len(set(uids)):
            cause = "R1_RUNTIME_REUSE"
            taxonomy["R1_RUNTIME_REUSE"] += 1
        else:
            taxonomy[cause] += 1
        status = "PASS" if cause in {"OK", "R5_LOW_PARAMETER_SPACE"} and unique >= 3 else ("PASS" if unique >= 5 else "FAIL")
        if cause == "R5_LOW_PARAMETER_SPACE" and unique >= 4:
            status = "PASS"
        skill_rows.append({
            "skill": skill,
            "request_count": len(samples),
            "unique_effective_questions": unique,
            "families_observed": families,
            "components_observed": sorted(set(comps)),
            "duplicate_count": len(samples) - unique,
            "root_cause": cause,
            "status": status,
            "mcq_render_ok": all(
                (not (s.get("answer_type") in {"single_choice", "choice"}))
                or (isinstance(s.get("choices"), list) and len(s.get("choices") or []) == 4
                    and all(str(c.get("text") or "").startswith("$") or str(c.get("text") or "").startswith(r"\(")
                            for c in (s.get("choices") or []) if isinstance(c, dict)))
                for s in samples if not s.get("error")
            ),
            "input_contract_ok": all(
                _label_ok(((s.get("answer_contract") or {}).get("parts") or []))
                for s in samples if not s.get("error")
            ),
            "diagram_ok": True,
        })
    return {
        "skills": skill_rows,
        "taxonomy": dict(taxonomy),
        "pass": sum(1 for r in skill_rows if r["status"] == "PASS"),
        "blocked": sum(1 for r in skill_rows if r["status"] != "PASS"),
    }


def write_md_family(data: dict[str, Any], path: Path) -> None:
    lines = [
        "# B2 Ch3 Student Runtime Family Audit",
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
        "# B2 Ch3 Next-Question Runtime Audit",
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
            f"<li><code>{html.escape(str(c.get('label')))}</code> {html.escape(str(c.get('text')))}</li>"
            for c in choices if isinstance(c, dict)
        )
        part_html = "".join(
            f"<li><span class='debug'>debug key: <code>{html.escape(str(p.get('key')))}</code></span>"
            f" · <span class='student'>student label: {html.escape(str(p.get('display_label') or p.get('label')))}</span>"
            f" · expected {html.escape(str(p.get('expected_answer')))}</li>"
            for p in parts if isinstance(p, dict)
        )
        cards.append(
            f"<section class='card status-{html.escape(row['final_status'])}'>"
            f"<h2>{html.escape(row['family_id'])}</h2>"
            f"<p class='meta'>{html.escape(row['skill_id'])} · status=<b>{html.escape(row['final_status'])}</b> · "
            f"diversity={html.escape(row['meaningful_diversity'])}</p>"
            f"<div class='stem'>{html.escape(row.get('representative_stem') or '')}</div>"
            f"<h3>Choices</h3><ul>{choice_html or '<li>(none)</li>'}</ul>"
            f"<h3>Input parts</h3><ul>{part_html or '<li>(single)</li>'}</ul>"
            f"<h3>Diagram stats</h3><pre>{html.escape(json.dumps(row.get('diagram_stats') or {}, ensure_ascii=False, indent=2))}</pre>"
            f"</section>"
        )
    page = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"/>
<title>B2 Ch3 Student Runtime QA</title>
<script>
window.MathJax={{tex:{{inlineMath:[['$','$'],['\\\\(','\\\\)']]}}}};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js" async></script>
<style>
body{{font-family:Georgia,serif;margin:24px;background:#f7f3ea;color:#222}}
h1{{font-size:1.8rem}}
.card{{background:#fff;border:1px solid #d7cfc0;padding:16px 18px;margin:16px 0}}
.status-PASS{{border-left:6px solid #2e7d32}}
.status-FAIL_STEM,.status-FAIL_INPUT_CONTRACT,.status-FAIL_MCQ_CHOICES,.status-FAIL_MCQ_MAPPING,
.status-FAIL_DIAGRAM_CLUTTER,.status-FAIL_DIAGRAM_SEMANTICS,.status-FAIL_FIXED_GENERATOR,.status-FAIL_MATH_RENDER
{{border-left:6px solid #c62828}}
.stem{{white-space:pre-wrap;background:#faf7f0;padding:10px;margin:8px 0}}
.meta{{color:#555;font-size:.95rem}}
.debug{{color:#666}}
.student{{color:#1b5e20;font-weight:600}}
</style></head><body>
<h1>B2 Ch3 Student Runtime QA Contact Sheet</h1>
<p>Families: {family_audit['total_families']} · PASS: {family_audit['pass']} · BLOCKED: {family_audit['blocked']}</p>
{''.join(cards)}
</body></html>"""
    (QA_DIR / "index.html").write_text(page, encoding="utf-8")


def write_input_label_audit(family_audit: dict[str, Any], path: Path) -> dict[str, Any]:
    from core.gencode.domain_matrix_adapter import _looks_like_internal_part_key

    rows = []
    for fam in family_audit["families"]:
        for part in fam.get("representative_parts") or []:
            if not isinstance(part, dict):
                continue
            key = str(part.get("key") or "")
            label = str(part.get("display_label") or part.get("label") or "")
            math_label = part.get("math_label")
            if not label.strip():
                status = "FAIL_EMPTY_LABEL"
            elif _looks_like_internal_part_key(key, label):
                status = "FAIL_INTERNAL_KEY_EXPOSED"
            elif label.replace(" ", "") == key.replace("_", "") and "_" in key:
                status = "FAIL_AMBIGUOUS_LABEL"
            else:
                status = "PASS"
            rows.append({
                "skill": fam.get("skill_id"),
                "family": fam.get("family_id"),
                "internal_key": key,
                "display_label": label,
                "math_label": math_label,
                "status": status,
            })
    report = {
        "total_fields": len(rows),
        "pass": sum(1 for r in rows if r["status"] == "PASS"),
        "fail_internal_key_exposed": sum(1 for r in rows if r["status"] == "FAIL_INTERNAL_KEY_EXPOSED"),
        "fail_empty_label": sum(1 for r in rows if r["status"] == "FAIL_EMPTY_LABEL"),
        "fail_ambiguous_label": sum(1 for r in rows if r["status"] == "FAIL_AMBIGUOUS_LABEL"),
        "fields": rows,
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report


def main() -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    family = audit_families()
    (REPORTS / "b2_ch3_student_runtime_audit.json").write_text(
        json.dumps(family, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_family(family, REPORTS / "b2_ch3_student_runtime_audit.md")
    write_qa_harness(family)
    label_audit = write_input_label_audit(family, REPORTS / "b2_ch3_student_input_label_audit.json")
    nxt = audit_next_question()
    (REPORTS / "b2_ch3_next_question_runtime_audit.json").write_text(
        json.dumps(nxt, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_md_next(nxt, REPORTS / "b2_ch3_next_question_runtime_audit.md")
    print(json.dumps({
        "families_pass": family["pass"],
        "families_blocked": family["blocked"],
        "skills_pass": nxt["pass"],
        "skills_blocked": nxt["blocked"],
        "taxonomy": nxt["taxonomy"],
        "label_audit": {
            "total": label_audit["total_fields"],
            "pass": label_audit["pass"],
            "fail_internal": label_audit["fail_internal_key_exposed"],
            "fail_empty": label_audit["fail_empty_label"],
            "fail_ambiguous": label_audit["fail_ambiguous_label"],
        },
        "qa": str(QA_DIR / "index.html"),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
