# -*- coding: utf-8 -*-
"""Chapter-wide B2 Ch3 student-practice inline math typography audit."""

from __future__ import annotations

import importlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
CSS_PATH = ROOT / "static" / "css" / "practice_math_typography.css"
INDEX_PATH = ROOT / "templates" / "index.html"

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

# Delimiters that feed the single MathJax path on practice.
_TEX_OPEN = re.compile(r"(\\\(|\\\[|\$\$|\$)")
_KATEX_HINT = re.compile(r"\bkatex\b|class=[\"'][^\"']*katex", re.I)
_RAW_HTML_MATH = re.compile(r"<(?:span|font)[^>]*(?:math|latex|formula)[^>]*>", re.I)
_FORBIDDEN_MIDDLE = re.compile(
    r"(?:#question-text|#question-choices|\.practice-math-surface)[^{]*\{[^}]*"
    r"vertical-align\s*:\s*middle\s*!important",
    re.I | re.S,
)
_FORBIDDEN_MJX_MIDDLE = re.compile(
    r"mjx-container[^{]*\{[^}]*vertical-align\s*:\s*middle\s*!important",
    re.I | re.S,
)


def _scan_payload(skill: str, family: str, surface: str, text: str) -> list[dict]:
    raw = str(text or "")
    findings: list[dict] = []
    if _KATEX_HINT.search(raw):
        findings.append({
            "skill": skill,
            "family": family,
            "surface": surface,
            "renderer": "katex_hint",
            "wrapper_classes": "",
            "computed_font_size": "",
            "computed_line_height": "",
            "vertical_align": "",
            "status": "MIXED_RENDER_PATH",
            "raw_value": raw[:180],
        })
    if _RAW_HTML_MATH.search(raw):
        findings.append({
            "skill": skill,
            "family": family,
            "surface": surface,
            "renderer": "raw_html_math",
            "wrapper_classes": "",
            "computed_font_size": "",
            "computed_line_height": "",
            "vertical_align": "",
            "status": "INLINE_DISPLAY_MIX",
            "raw_value": raw[:180],
        })
    # Unbalanced / nested $ can cause double-render loops; flag crude doubles.
    dollar_count = raw.count("$") - raw.count("\\$")
    if dollar_count % 2 != 0:
        findings.append({
            "skill": skill,
            "family": family,
            "surface": surface,
            "renderer": "mathjax_delimiters",
            "wrapper_classes": "",
            "computed_font_size": "",
            "computed_line_height": "",
            "vertical_align": "",
            "status": "DOUBLE_RENDER",
            "raw_value": f"unbalanced_dollar_count={dollar_count}",
        })
    return findings


def _contract_css_ok() -> list[dict]:
    findings: list[dict] = []
    css = CSS_PATH.read_text(encoding="utf-8")
    index = INDEX_PATH.read_text(encoding="utf-8")
    if "practice_math_typography.css" not in index:
        findings.append({
            "skill": "_contract",
            "family": "_css_link",
            "surface": "index.html",
            "renderer": "mathjax_svg",
            "wrapper_classes": "",
            "computed_font_size": "",
            "computed_line_height": "",
            "vertical_align": "",
            "status": "MIXED_RENDER_PATH",
            "raw_value": "practice_math_typography.css not linked",
        })
    for label, blob in (("css", css), ("index", index)):
        if _FORBIDDEN_MIDDLE.search(blob) or (
            label == "index" and _FORBIDDEN_MJX_MIDDLE.search(blob)
            and "practice-math-surface" in (blob[_FORBIDDEN_MJX_MIDDLE.search(blob).start():] if _FORBIDDEN_MJX_MIDDLE.search(blob) else "")
        ):
            findings.append({
                "skill": "_contract",
                "family": label,
                "surface": "stylesheet",
                "renderer": "mathjax_svg",
                "wrapper_classes": "practice-math-surface",
                "computed_font_size": "100%",
                "computed_line_height": "1.75",
                "vertical_align": "middle!important",
                "status": "BASELINE_MISMATCH",
                "raw_value": "forbidden vertical-align:middle !important on practice math",
            })
    # Dedicated check: any mjx middle !important remaining in index (practice-related).
    for m in _FORBIDDEN_MJX_MIDDLE.finditer(index):
        snippet = index[max(0, m.start() - 80): m.end() + 40]
        if "suggestion-btn" in snippet or "level-indicator" in snippet:
            continue
        findings.append({
            "skill": "_contract",
            "family": "index_mjx",
            "surface": "stylesheet",
            "renderer": "mathjax_svg",
            "wrapper_classes": "",
            "computed_font_size": "",
            "computed_line_height": "",
            "vertical_align": "middle!important",
            "status": "BASELINE_MISMATCH",
            "raw_value": snippet.replace("\n", " ")[:200],
        })
    if "font-size: 100%" not in css.replace(" ", ""):
        # tolerate spacing variants
        if "font-size:100%" not in css.replace(" ", "") and "font-size: 100%" not in css:
            findings.append({
                "skill": "_contract",
                "family": "css",
                "surface": "stylesheet",
                "renderer": "mathjax_svg",
                "wrapper_classes": "practice-math-surface",
                "computed_font_size": "",
                "computed_line_height": "",
                "vertical_align": "",
                "status": "FONT_SCALE_MISMATCH",
                "raw_value": "missing font-size:100% on inline mjx contract",
            })
    for required_id in ("question-text", "question-choices", "subquestions-container", "result-display"):
        if f'id="{required_id}"' in index and "practice-math-surface" not in index[
            index.find(f'id="{required_id}"'): index.find(f'id="{required_id}"') + 120
        ]:
            findings.append({
                "skill": "_contract",
                "family": required_id,
                "surface": required_id,
                "renderer": "mathjax_svg",
                "wrapper_classes": "",
                "computed_font_size": "",
                "computed_line_height": "",
                "vertical_align": "",
                "status": "MIXED_RENDER_PATH",
                "raw_value": f"{required_id} missing practice-math-surface class",
            })
    return findings


def main() -> None:
    findings = _contract_css_ok()
    family_components: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for skill in SKILLS:
        mod = importlib.import_module(f"skills.{skill}")
        for spec in getattr(mod, "GENERATOR_SPECS", []):
            fam = str(spec.get("problem_type_id") or "")
            family_components[fam].append((skill, str(spec.get("component_id") or "")))

    families_scanned = 0
    samples: list[dict] = []
    for family, comps in sorted(family_components.items()):
        skill, component = comps[0]
        mod = importlib.import_module(f"skills.{skill}")
        families_scanned += 1
        payload = mod.generate(seed=7, component_id=component)
        stem = str(payload.get("question_text") or "")
        findings.extend(_scan_payload(skill, family, "problem_stem", stem))
        for idx, choice in enumerate(payload.get("choices") or []):
            if isinstance(choice, dict):
                findings.extend(
                    _scan_payload(skill, family, f"choice[{idx}]", str(choice.get("text") or ""))
                )
        ac = payload.get("answer_contract") if isinstance(payload.get("answer_contract"), dict) else {}
        for part in ac.get("parts") or []:
            if isinstance(part, dict):
                findings.extend(
                    _scan_payload(
                        skill,
                        family,
                        f"part[{part.get('key')}].label",
                        str(part.get("display_label") or part.get("label") or ""),
                    )
                )
        samples.append({
            "skill": skill,
            "family": family,
            "surface": "problem_stem",
            "renderer": "mathjax_svg_expected",
            "wrapper_classes": "practice-math-surface",
            "computed_font_size": "100% (contract)",
            "computed_line_height": "1.75 (contract)",
            "vertical_align": "mathjax-inline (contract)",
            "status": "OK",
            "has_tex_delimiter": bool(_TEX_OPEN.search(stem)),
        })

    counts = {
        "MIXED_RENDER_PATH": sum(1 for f in findings if f["status"] == "MIXED_RENDER_PATH"),
        "FONT_SCALE_MISMATCH": sum(1 for f in findings if f["status"] == "FONT_SCALE_MISMATCH"),
        "BASELINE_MISMATCH": sum(1 for f in findings if f["status"] == "BASELINE_MISMATCH"),
        "DOUBLE_RENDER": sum(1 for f in findings if f["status"] == "DOUBLE_RENDER"),
        "INLINE_DISPLAY_MIX": sum(1 for f in findings if f["status"] == "INLINE_DISPLAY_MIX"),
    }
    report = {
        "families_scanned": families_scanned,
        "canonical_renderer": "mathjax3_svg",
        "wrapper_class": "practice-math-surface",
        "css": str(CSS_PATH.relative_to(ROOT)).replace("\\", "/"),
        "counts": counts,
        "pass": all(v == 0 for v in counts.values()),
        "findings": findings,
        "samples": samples,
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "b2_ch3_math_typography_audit.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "families_scanned": families_scanned,
        "counts": counts,
        "pass": report["pass"],
        "path": str(out),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
