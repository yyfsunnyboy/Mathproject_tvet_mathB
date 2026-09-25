# -*- coding: utf-8 -*-
"""Audit B2 Ch3 student-facing numeric / vector display cleanliness."""

from __future__ import annotations

import importlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

SKILLS = [
    "vh_數學B2_SubSection_3_1_1",
    "vh_數學B2_SubSection_3_1_2",
    "vh_數學B2_SubSection_3_1_3",
    "vh_數學B2_SubSection_3_1_4",
    "vh_數學B2_SubSection_3_2_1",
    "vh_數學B2_SubSection_3_2_2",
    "vh_數學B2_SubSection_3_2_3",
    "vh_數學B2_SubSection_3_2_4",
    "vh_數學B2_SubSection_3_2_5",
    "vh_數學B2_SubSection_3_2_6",
    "vh_數學B2_SubSection_3_3_1",
    "vh_數學B2_SubSection_3_3_2",
    "vh_數學B2_SubSection_3_3_3",
    "vh_數學B2_SubSection_3_3_4",
    "vh_數學B2_SubSection_3_3_5",
]

FLOAT_NOISE_RE = re.compile(r"(?<![\d.\\])-?\d+\.\d{6,}(?!\d)")
NEG_ZERO_RE = re.compile(r"(?<![\d.])-0(?:\.0+)?(?!\d)")
TRIVIAL_VEC_RE = re.compile(r"(?<![\d.])-?1\\(?:vec|overrightarrow)\{")


def _scan_text(skill: str, family: str, field: str, text: str) -> list[dict]:
    raw = str(text or "")
    findings = []
    for m in FLOAT_NOISE_RE.finditer(raw):
        findings.append({
            "skill": skill,
            "family": family,
            "field": field,
            "raw_value": m.group(0),
            "display_value": m.group(0),
            "status": "FLOAT_NOISE",
        })
    for m in NEG_ZERO_RE.finditer(raw):
        findings.append({
            "skill": skill,
            "family": family,
            "field": field,
            "raw_value": m.group(0),
            "display_value": m.group(0),
            "status": "NEGATIVE_ZERO",
        })
    for m in TRIVIAL_VEC_RE.finditer(raw):
        findings.append({
            "skill": skill,
            "family": family,
            "field": field,
            "raw_value": m.group(0),
            "display_value": m.group(0),
            "status": "TRIVIAL_VECTOR_COEFFICIENT",
        })
    return findings


def main() -> None:
    family_components: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for skill in SKILLS:
        mod = importlib.import_module(f"skills.{skill}")
        for spec in getattr(mod, "GENERATOR_SPECS", []):
            fam = str(spec.get("problem_type_id") or "")
            family_components[fam].append((skill, str(spec.get("component_id") or "")))

    findings: list[dict] = []
    families_scanned = 0
    for family, comps in sorted(family_components.items()):
        skill, component = comps[0]
        mod = importlib.import_module(f"skills.{skill}")
        families_scanned += 1
        for seed in range(8):
            payload = mod.generate(seed=seed, component_id=component)
            findings.extend(_scan_text(skill, family, "question_text", payload.get("question_text") or ""))
            for idx, choice in enumerate(payload.get("choices") or []):
                if isinstance(choice, dict):
                    findings.extend(_scan_text(skill, family, f"choice[{idx}].text", choice.get("text") or ""))
                    findings.extend(_scan_text(skill, family, f"choice[{idx}].display", choice.get("display") or ""))
            ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
            for part in ac.get("parts") or []:
                if isinstance(part, dict):
                    findings.extend(_scan_text(skill, family, f"part[{part.get('key')}].label", part.get("display_label") or part.get("label") or ""))

    counts = {
        "FLOAT_NOISE": sum(1 for f in findings if f["status"] == "FLOAT_NOISE"),
        "NEGATIVE_ZERO": sum(1 for f in findings if f["status"] == "NEGATIVE_ZERO"),
        "TRIVIAL_VECTOR_COEFFICIENT": sum(1 for f in findings if f["status"] == "TRIVIAL_VECTOR_COEFFICIENT"),
    }
    report = {
        "families_scanned": families_scanned,
        "seeds_per_family": 8,
        "counts": counts,
        "pass": all(v == 0 for v in counts.values()),
        "findings": findings,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "b2_ch3_student_numeric_display_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"families_scanned": families_scanned, "counts": counts, "pass": report["pass"], "path": str(out)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
