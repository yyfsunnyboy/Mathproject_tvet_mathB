# -*- coding: utf-8 -*-
"""
=============================================================================
璅∠??迂 (Module Name): core/textbook_processor.py
?隤芣? (Description): 隤脫????AI ??璅∠?嚗?鞎砍? PDF ??Word 瑼?銝剛???玨蝔?瑽??批捆嚗蒂?游? Gemini LLM ?脰??箄?????澈?臬??
?瑁?隤? (Usage): ?梁頂蝯梯矽??
?鞈? (Version): V2.0
?湔?交? (Date): 2026-01-13
蝬剛風?? (Maintainer): Math AI Project Team
=============================================================================
"""
"""
隤脫????AI ??璅∠? (Textbook Processor & AI Analyzer) - Final Complete Version

?祆芋蝯?鞎砍????賂?PDF ??Word 瑼?嚗葉?芸???隤脩?蝯???蝭??蝭?敹?敹蛛?
銝阡? Google Gemini LLM ?脰??箄??嚗?蝯?蝯??????亥??澈??

??寥?嚗?
1. 摰靽????隤方????刻圾??頛?賢? (Restore full logic)??
2. ?啣??? Word/Pandoc ??瘣?頛?(clean_pandoc_output)??
3. ?湔?桅?樴辰??Prompt (?像??瑽???
"""

import json
import re
import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET
import uuid
import platform
# import fitz  # PyMuPDF -> Moved to inside function
import time
import io
from typing import Any
# import pypandoc -> Moved to inside function
# from pypandoc.pandoc_download import download_pandoc
from google.api_core.exceptions import ResourceExhausted
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.ai_analyzer import get_model
from flask import current_app, has_app_context
import traceback
from core.code_generator import auto_generate_skill_code
from core.math_formula_normalizer import (
    detect_suspicious_formula,
    normalize_converted_docx_latex_text,
    normalize_math_text,
)
from core.math_expression_formatter import standardize_problem_latex
from core.question_image_assets import (
    attach_image_metadata,
    build_question_asset_filename,
    build_question_asset_dir,
    build_question_assets_dir,
    build_question_code,
    convert_vector_image_to_png,
    detect_image_reason,
    find_best_page_index,
    infer_source_page_for_question,
    make_page_image_asset,
    question_needs_image,
    render_pdf_page_to_image,
)
from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.textbook_structure_parser import get_structure_map
from core.utils import normalize_vocational_math_skill_id

_DOCX_IMPORT_CONTEXT: dict[str, Any] = {}

FORMULA_PLACEHOLDER_RE = re.compile(r"\[FORMULA_IMAGE_\d+\]|\[FORMULA_MISSING\]|\[WORD_EQUATION_UNPARSED\]")
TEXT_MOJIBAKE_CHARS = "嚙踐∟航輻Ｚ閰冽"
TEXT_MOJIBAKE_RE = re.compile("[" + re.escape(TEXT_MOJIBAKE_CHARS) + r"]")
LATEX_SIGNAL_GUARD_RE = re.compile(r"\\\(|\\\)|\\\[|\\\]|\\(?:frac|sqrt|left|right)\b|[\^_]")


def _norm_title_spaces(title: str) -> str:
    return re.sub(r"\s+", " ", str(title or "").strip())


def _strip_title_brackets(s: str) -> str:
    return s.strip("〔〕[]()（）")


def scan_docx_title_inventory(extracted_text: str, section_code: str | None = None) -> list[dict[str, Any]]:
    """Deterministic scan of example / practice / chapter exercise / exam titles from DOCX text."""
    text = str(extracted_text or "")
    lines = text.splitlines()
    items: list[dict[str, Any]] = []

    def _infer_section_from_line(line: str) -> str | None:
        m = re.search(r"(\d+-\d+)", line)
        return m.group(1) if m else None

    inferred_global = None
    for ln in lines:
        g = _infer_section_from_line(ln)
        if g:
            inferred_global = g
            break

    effective_section = (str(section_code).strip() if section_code else "") or (inferred_global or "")

    # --- 例題 (document-wide) ---
    for m in re.finditer(r"例(?:題)?\s*(\d{1,2})\b", text):
        n = int(m.group(1))
        raw = m.group(0).strip()
        preview = text[max(0, m.start() - 20) : m.end() + 40].replace("\n", " ")
        items.append(
            {
                "raw_title": raw,
                "canonical_title": f"例題{n}",
                "kind": "example",
                "section_code": effective_section or "",
                "exercise_block": "",
                "zone": "",
                "number": str(n),
                "source_span_preview": preview[:120],
            }
        )

    # --- 隨堂練習：「隨堂練習 n」或標題後依行首題號 ---
    for m in re.finditer(r"隨堂練習\s*(\d{1,2})\b", text):
        n = int(m.group(1))
        raw = m.group(0).strip()
        preview = text[max(0, m.start() - 12) : m.end() + 30].replace("\n", " ")
        items.append(
            {
                "raw_title": raw,
                "canonical_title": f"隨堂練習{n}",
                "kind": "in_class_practice",
                "section_code": effective_section or "",
                "exercise_block": "",
                "zone": "",
                "number": str(n),
                "source_span_preview": preview[:120],
            }
        )
    suitang_m = re.search(r"隨堂練習(?=\s*$)", text, flags=re.MULTILINE)
    if not suitang_m:
        suitang_m = re.search(r"(?m)^\s*隨堂練習\s*$", text)
    if suitang_m:
        tail = text[suitang_m.end() :]
        end_m = re.search(r"\d+-\d+習題|[〔\[]?\s*\d{2,3}\s*統測", tail)
        region = tail[: end_m.start()] if end_m else tail
        for lm in re.finditer(r"(?m)^\s*(\d{1,2})(?:[\.、\)\t]|\s+)", region):
            n = int(lm.group(1))
            raw = lm.group(0).strip()
            preview = region[max(0, lm.start() - 10) : lm.end() + 40].replace("\n", " ")
            items.append(
                {
                    "raw_title": raw,
                    "canonical_title": f"隨堂練習{n}",
                    "kind": "in_class_practice",
                    "section_code": effective_section or "",
                    "exercise_block": "",
                    "zone": "",
                    "number": str(n),
                    "source_span_preview": preview[:120],
                }
            )

    # --- 章節習題區（zone 完全依原文掃描，不依題號推測）---
    ZONE_HEADERS = ("基礎題", "進階題", "自我評量")

    i = 0
    while i < len(lines):
        line = lines[i]
        blk = re.search(r"(\d+-\d+)習題", line)
        if not blk:
            i += 1
            continue
        sec = blk.group(1)
        exercise_block = f"{sec}習題"
        current_zone = "其他"
        i += 1
        while i < len(lines):
            ln = lines[i]
            hdr = re.match(r"^\s*(\d+-\d+)習題", ln)
            if hdr and hdr.group(1) != sec:
                break
            if re.search(r"[〔\[]?\s*\d{2,3}\s*統測", ln, flags=re.IGNORECASE):
                break
            stripped = ln.strip()
            zone_hit = None
            for z in ZONE_HEADERS:
                if stripped == z or stripped.startswith(z + " ") or stripped.startswith(z + "　"):
                    zone_hit = z
                    break
            if zone_hit:
                current_zone = zone_hit
                i += 1
                continue
            mnum = re.match(r"^\s*(\d{1,2})(?:[\.、\)\t]|\s+)", ln)
            if mnum:
                n = int(mnum.group(1))
                raw = mnum.group(0).strip()
                preview = ln[:100]
                canon = f"{sec}習題 {current_zone}{n}"
                items.append(
                    {
                        "raw_title": raw,
                        "canonical_title": canon,
                        "kind": "chapter_exercise",
                        "section_code": sec,
                        "exercise_block": exercise_block,
                        "zone": current_zone,
                        "number": str(n),
                        "source_span_preview": preview,
                    }
                )
            i += 1
        continue

    # --- 統測 ---
    for m in re.finditer(r"[〔\[]?\s*(\d{2,3})\s*統測\s*([AB])\s*[〕\]]?", text, flags=re.IGNORECASE):
        y = int(m.group(1))
        suf = m.group(2).upper()
        raw = m.group(0).strip()
        preview = text[max(0, m.start() - 10) : m.end() + 30].replace("\n", " ")
        items.append(
            {
                "raw_title": raw,
                "canonical_title": f"{y}統測{suf}",
                "kind": "exam_practice",
                "section_code": effective_section or "",
                "exercise_block": "",
                "zone": "",
                "number": "",
                "source_span_preview": preview[:120],
            }
        )

    return items


def map_returned_import_title(
    title: str,
    *,
    section_code: str | None = None,
    inventory_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Map AI-returned title string to canonical form; never guess exercise zone from number alone."""
    raw = _norm_title_spaces(str(title or ""))
    inv = list(inventory_items or [])
    s_compact = re.sub(r"\s+", "", raw)
    s_compact = _strip_title_brackets(s_compact)

    m = re.match(r"^例(?:題)?(\d+)$", s_compact)
    if m:
        return {
            "returned_raw": raw,
            "returned_canonical": f"例題{int(m.group(1))}",
            "mapping_method": "direct_example",
            "needs_review": False,
        }

    m = re.match(r"^隨堂練習(\d+)$", s_compact)
    if m:
        return {
            "returned_raw": raw,
            "returned_canonical": f"隨堂練習{int(m.group(1))}",
            "mapping_method": "direct_practice",
            "needs_review": False,
        }

    m = re.match(r"^(\d{2,3})統測([AB])$", s_compact, flags=re.IGNORECASE)
    if m:
        return {
            "returned_raw": raw,
            "returned_canonical": f"{int(m.group(1))}統測{m.group(2).upper()}",
            "mapping_method": "direct_exam",
            "needs_review": False,
        }

    m = re.match(r"^習題(\d+)$", s_compact)
    if m:
        num = m.group(1)
        cands = [it for it in inv if it.get("kind") == "chapter_exercise" and str(it.get("number", "")) == num]
        if len(cands) == 1:
            return {
                "returned_raw": raw,
                "returned_canonical": str(cands[0].get("canonical_title", "")),
                "mapping_method": "exercise_context_map",
                "needs_review": False,
            }
        sc = str(section_code or "").strip() or ""
        fallback = f"{sc}習題 題{num}" if sc else f"習題 題{num}"
        return {
            "returned_raw": raw,
            "returned_canonical": fallback,
            "mapping_method": "fallback_unresolved",
            "needs_review": True,
        }

    m = re.match(r"^(\d+-\d+)習題(基礎題|進階題|自我評量|其他)(\d+)$", s_compact)
    if m:
        return {
            "returned_raw": raw,
            "returned_canonical": f"{m.group(1)}習題 {m.group(2)}{int(m.group(3))}",
            "mapping_method": "exercise_context_map",
            "needs_review": False,
        }

    return {
        "returned_raw": raw,
        "returned_canonical": raw,
        "mapping_method": "fallback_unresolved",
        "needs_review": True,
    }


def canonicalize_import_title(
    title: str,
    section_code: str | None = None,
    inventory_items: list[dict[str, Any]] | None = None,
    *,
    exercise_zone_map: dict[int, str] | None = None,
) -> str:
    """Normalize title for inventory; optional inventory_items disambiguates 「習題 n」."""
    meta = map_returned_import_title(
        title,
        section_code=section_code,
        inventory_items=inventory_items,
    )
    if exercise_zone_map and meta.get("mapping_method") == "fallback_unresolved":
        s_compact = re.sub(r"\s+", "", _norm_title_spaces(title))
        s_compact = _strip_title_brackets(s_compact)
        m = re.match(r"^習題(\d+)$", s_compact)
        if m and section_code:
            num = int(m.group(1))
            zone = exercise_zone_map.get(num)
            if zone:
                return f"{section_code}習題 {zone}{num}"
    return str(meta.get("returned_canonical") or "").strip() or str(title or "").strip()


def scan_expected_titles_from_converted_text(extracted_text: str) -> list[str]:
    items = scan_docx_title_inventory(extracted_text)
    return sorted({str(it.get("canonical_title", "")).strip() for it in items if str(it.get("canonical_title", "")).strip()})


def collect_returned_titles_from_parsed_data(parsed_data: dict[str, Any]) -> list[str]:
    titles: list[str] = []
    for ch in (parsed_data or {}).get("chapters", []) or []:
        for sec in (ch or {}).get("sections", []) or []:
            for concept in (sec or {}).get("concepts", []) or []:
                for ex in (concept or {}).get("examples", []) or []:
                    t = ex.get("title") or ex.get("source_description") or ""
                    if str(t).strip():
                        titles.append(str(t).strip())
                for pq in (concept or {}).get("practice_questions", []) or []:
                    t = pq.get("title") or pq.get("source_description") or ""
                    if str(t).strip():
                        titles.append(str(t).strip())
    return titles


def build_title_inventory(
    expected_titles: list[str],
    returned_titles: list[str],
    section_code: str = "",
    *,
    inventory_items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    inv_list = list(inventory_items or [])
    sc = str(section_code or "").strip()
    if sc == "unknown":
        sc = ""

    expected_raw = [str(t).strip() for t in expected_titles if str(t).strip()]
    expected_norm = sorted(
        {
            canonicalize_import_title(t, section_code=sc or None, inventory_items=inv_list)
            for t in expected_raw
        }
    )

    returned_raw = [str(t).strip() for t in returned_titles if str(t).strip()]
    returned_mappings = [
        map_returned_import_title(t, section_code=sc or None, inventory_items=inv_list) for t in returned_raw
    ]
    returned_norm = sorted(
        {str(m.get("returned_canonical") or "").strip() for m in returned_mappings if str(m.get("returned_canonical") or "").strip()}
    )

    expected_set = set(expected_norm)
    returned_set = set(returned_norm)
    missing = sorted(expected_set - returned_set)
    extra = sorted(returned_set - expected_set)
    return {
        "expected_titles_raw": expected_raw,
        "expected_titles_canonical": expected_norm,
        "returned_titles_raw": returned_raw,
        "returned_titles_canonical": returned_norm,
        "missing_titles_canonical": missing,
        "extra_titles_canonical": extra,
        "expected_titles_count": len(expected_norm),
        "returned_titles_count": len(returned_norm),
        "missing_titles_count": len(missing),
        "extra_titles_count": len(extra),
        "inventory_items": inv_list,
        "returned_title_mappings": returned_mappings,
    }


def _md_table_row(cells: list[str]) -> str:
    esc = [str(c or "").replace("|", "\\|").replace("\n", " ") for c in cells]
    return "| " + " | ".join(esc) + " |"


def write_title_inventory_report(report_path: str, *, volume: str, section: str, allow_partial_import: bool, write_aborted: bool, inv: dict[str, Any], warning: str = "") -> None:
    lines = [
        "# Title Inventory Report",
        "",
        "## Summary",
        f"- volume: `{volume}`",
        f"- section: `{section}`",
        f"- expected_titles_count: `{inv.get('expected_titles_count', 0)}`",
        f"- returned_titles_count: `{inv.get('returned_titles_count', 0)}`",
        f"- missing_titles_count: `{inv.get('missing_titles_count', 0)}`",
        f"- extra_titles_count: `{inv.get('extra_titles_count', 0)}`",
        f"- allow_partial_import: `{str(bool(allow_partial_import)).lower()}`",
        f"- write_aborted: `{str(bool(write_aborted)).lower()}`",
        f"- warning: `{warning}`",
        "",
    ]
    inv_items = inv.get("inventory_items") or []
    if inv_items:
        lines.append("## Inventory Items")
        lines.append(_md_table_row(["raw_title", "canonical_title", "kind", "section_code", "exercise_block", "zone", "number", "preview"]))
        lines.append(_md_table_row(["---"] * 8))
        for it in inv_items:
            lines.append(
                _md_table_row(
                    [
                        str(it.get("raw_title", "")),
                        str(it.get("canonical_title", "")),
                        str(it.get("kind", "")),
                        str(it.get("section_code", "")),
                        str(it.get("exercise_block", "")),
                        str(it.get("zone", "")),
                        str(it.get("number", "")),
                        str(it.get("source_span_preview", ""))[:200],
                    ]
                )
            )
        lines.append("")

    mappings = inv.get("returned_title_mappings") or []
    if mappings:
        lines.append("## Returned Title Mapping")
        lines.append(_md_table_row(["returned_raw", "returned_canonical", "mapping_method", "needs_review"]))
        lines.append(_md_table_row(["---"] * 4))
        for m in mappings:
            lines.append(
                _md_table_row(
                    [
                        str(m.get("returned_raw", "")),
                        str(m.get("returned_canonical", "")),
                        str(m.get("mapping_method", "")),
                        str(m.get("needs_review", False)).lower(),
                    ]
                )
            )
        lines.append("")

    lines.extend(
        [
            "## Expected Titles Raw",
        ]
    )
    for t in inv.get("expected_titles_raw", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Expected Titles Canonical")
    for t in inv.get("expected_titles_canonical", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Returned Titles Raw")
    for t in inv.get("returned_titles_raw", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Returned Titles Canonical")
    for t in inv.get("returned_titles_canonical", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Missing Titles Canonical")
    for t in inv.get("missing_titles_canonical", []):
        lines.append(f"- {t}")
    lines.append("")
    lines.append("## Extra Titles Canonical")
    for t in inv.get("extra_titles_canonical", []):
        lines.append(f"- {t}")
    out = os.path.abspath(report_path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines) + "\n")


def detect_curriculum_volume_warning(curriculum: str, volume: str, publisher: str = "") -> str:
    c = str(curriculum or "").strip().lower()
    v = str(volume or "").strip()
    p = str(publisher or "").strip().lower()
    if re.search(r"數學\s*B[1-4]\b", v, flags=re.IGNORECASE) and c == "general" and (not p or "longteng" in p):
        return f"[IMPORT WARNING] volume={v} but curriculum=general; vocational mathB import expected."
    return ""
def _has_text_mojibake(text: str) -> bool:
    t = str(text or "")
    if not t:
        return False
    if TEXT_MOJIBAKE_RE.search(t):
        return True
    if t.count("?") >= 3 and (t.count("?") / max(1, len(t))) > 0.04:
        return True
    return any(0xE000 <= ord(ch) <= 0xF8FF for ch in t)


def _is_low_value_import_field(value: str) -> bool:
    t = str(value or "").strip()
    if not t:
        return True
    return t in {"?", "??", "N/A", "n/a", "None", "none", "null", "-"}


def score_problem_text_quality(text) -> dict:
    """Score imported problem text so duplicate merge does not replace good LaTeX with placeholders."""
    t = str(text or "").strip()
    placeholder_count = len(FORMULA_PLACEHOLDER_RE.findall(t))
    formula_image_count = len(re.findall(r"\[FORMULA_IMAGE_\d+\]", t))
    formula_missing_count = t.count("[FORMULA_MISSING]")
    mojibake = _has_text_mojibake(t)
    latex_patterns = [
        r"\\\(.+?\\\)",
        r"\$.+?\$",
        r"\\leq?|\\geq?",
        r"\\frac",
        r"\\sqrt",
        r"\|x\|",
        r"\|[^|]+\|",
    ]
    latex_signal_count = sum(1 for pat in latex_patterns if re.search(pat, t))
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", t))
    only_placeholder = bool(t) and not re.sub(FORMULA_PLACEHOLDER_RE, "", t).strip()
    too_short = len(t) < 6

    score = 50
    score += latex_signal_count * 18
    if placeholder_count == 0:
        score += 20
    score += min(cjk_count, 20)
    if re.search(r"[??嚗?嚗?.;嚗", t):
        score += 4
    score -= formula_image_count * 35
    score -= formula_missing_count * 45
    if mojibake:
        score -= 60
    if too_short:
        score -= 20
    if only_placeholder:
        score -= 60

    return {
        "score": int(score),
        "placeholder_count": placeholder_count,
        "formula_image_count": formula_image_count,
        "formula_missing_count": formula_missing_count,
        "latex_signal_count": latex_signal_count,
        "mojibake_detected": mojibake,
        "too_short": too_short,
        "only_placeholder": only_placeholder,
        "length": len(t),
    }


def should_replace_problem_text(existing_text, incoming_text) -> tuple[bool, dict, dict]:
    existing_quality = score_problem_text_quality(existing_text)
    incoming_quality = score_problem_text_quality(incoming_text)
    return incoming_quality["score"] > existing_quality["score"], existing_quality, incoming_quality

# (???炎?亙歇蝘駁)

# ==============================================================================
# [靽?] ?典??祉? LaTeX ?靽桀儔?賢?
# ==============================================================================
def sanitize_gemini_json_text(raw: str) -> str:
    r"""
    靽桀儔 Gemini ? JSON 銝剖虜閬??澆?????

    瘜冽?嚗?
    ?撘??json.loads ????raw text??
    摰??桃??芣霈?raw text ??? JSON??
    json.loads ??敺?Python 摮葡銝剔? LaTeX ?府隞?舀迤撣詨??蝺?
    靘?鞈?摨急?敺?閰脣???\(x+1\)嚗???\\(x+1\\)??
    """
    if raw is None:
        return raw

    text = str(raw).strip()

    # 蝘駁 Markdown code fence
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # ?瑕??憭惜 JSON object嚗?芋??敺?隤芣???
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    # 靽桀儔?? JSON escape??
    # JSON ?? escape ?芣?嚗?
    # \" \\ \/ \b \f \n \r \t \uXXXX
    # ?嗡? LaTeX escape嚗?憒?\( \) \[ \] \frac \binom \times \cdot
    # ?賡?閬 raw JSON 鋆∟?????蝺?json.loads 敺??????桀?????
    # ???虜閬?LaTeX ?賭誘??隞日??剖?憟賣?? JSON escape
    # (靘? \binom, \frac, \times)嚗??json.loads ????嗅??憯?MathJax??
    latex_commands = (
        "binom|frac|times|cdot|sum|prod|sqrt|left|right|over|overline|underline|"
        "vec|hat|bar|lim|to|infty|sin|cos|tan|cot|sec|csc|log|ln|"
        "alpha|beta|gamma|delta|theta|lambda|mu|pi|sigma|omega|phi|rho|tau|"
        "Delta|Sigma"
    )
    text = re.sub(rf'(?<!\\)\\(?=(?:{latex_commands})\b|[()\[\]{{}}])', r'\\\\', text)

    text = re.sub(r'(?<!\\)\\(?!["\\/bfnrtu])', r'\\\\', text)

    return text


def safe_load_gemini_json(raw: str):
    r"""
    摰閫?? Gemini ? JSON??
    ???json.loads??
    ?亙仃??靽桀儔 LaTeX escape 敺? json.loads??
    """
    raw_text = str(raw).strip() if raw is not None else raw
    fixed = sanitize_gemini_json_text(raw)

    try:
        parsed = json.loads(raw)
        if fixed != raw_text:
            try:
                sanitized_parsed = json.loads(fixed)
                try:
                    current_app.logger.info("[TEXTBOOK IMPORTER] Gemini JSON parsed after LaTeX escape sanitize.")
                except RuntimeError:
                    pass
                return sanitized_parsed
            except json.JSONDecodeError:
                return parsed
        return parsed
    except json.JSONDecodeError as first_error:
        try:
            current_app.logger.debug(
                "[TEXTBOOK IMPORTER] Gemini first json.loads failed at "
                f"line {first_error.lineno}, col {first_error.colno}, pos {first_error.pos}: "
                f"{first_error.msg}"
            )
        except RuntimeError:
            pass
        try:
            parsed = json.loads(fixed)
            try:
                current_app.logger.info("[TEXTBOOK IMPORTER] Gemini JSON parsed after LaTeX escape sanitize.")
            except RuntimeError:
                pass
            return parsed
        except json.JSONDecodeError as second_error:
            try:
                _log_gemini_json_parse_failed_after_sanitize(first_error, second_error, raw)
            except RuntimeError:
                pass
            preview = str(raw)[:800] if raw is not None else ""
            raise ValueError(
                "Gemini JSON parse failed after sanitize. "
                f"First error: {first_error}. "
                f"Second error: {second_error}. "
                f"Raw preview: {preview}"
            ) from second_error


def _log_gemini_json_parse_failed_after_sanitize(first_error, second_error, raw):
    preview = str(raw)[:800] if raw is not None else ""
    current_app.logger.error(
        "[TEXTBOOK IMPORTER] Gemini JSON parse failed after sanitize. "
        f"First error: {first_error}. "
        f"Second error: {second_error}. "
        f"Raw preview: {preview}"
    )


def fix_common_latex_errors(text):
    """
    靽桀儔 AI/Pandoc 頧?敺虜閬? LaTeX 隤??航炊?泵?瞍?(憓撥??
    ?嚗?閫?豢迤擃?????瘥??泵????璅???
    """
    if not text: return text
    
    # 0. ?箇?皜?
    text = text.replace("嚗?", "")
    text = re.sub(r'(\S)\s*\$\$', r'\1', text)
    text = text.replace('*e*', 'e')
    text = re.sub(r'(?<!\\)->', r' \\to ', text)
    text = re.sub(r'(?<!\\)infty(?![a-zA-Z])', r'\\infty', text)

    # 1. ?賣?迂甇????(Trig & Log)
    funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp']
    pattern_funcs = r'(?<!\\)\b(' + '|'.join(funcs) + r')\b'
    text = re.sub(pattern_funcs, r'\\\1', text)
    text = re.sub(r'\\(sin|cos|tan|log|ln)\(', r'\\\1 (', text) # 靽桀儔暺?

    # 2. 撣?摮??函?靽桀儔
    greeks = ['alpha', 'beta', 'gamma', 'delta', 'theta', 'lambda', 'mu', 'pi', 'sigma', 'omega', 'phi', 'rho', 'tau', 'Delta', 'Sigma']
    pattern_greeks = r'(?<!\\)\b(' + '|'.join(greeks) + r')\b(?![a-zA-Z])'
    text = re.sub(pattern_greeks, r'\\\1', text)

    # 3. ????頛?
    sets = ['subset', 'subseteq', 'cup', 'cap', 'emptyset', 'forall', 'exists']
    for s in sets: text = re.sub(rf'(?<!\\)\b{s}\b', rf'\\{s}', text)
    text = re.sub(r'\s+in\s+', r' \\in ', text)

    # 4. Lim, Sqrt, Frac (璅?靽桀儔)
    text = re.sub(r'lim_\{n\s*(?:\\to|->)\s*(?:\\)?infty\}', r'\\lim_{n \\to \\infty}', text)
    text = re.sub(r'(?<!\\)lim(?![a-zA-Z])', r'\\lim', text)
    text = re.sub(r'(?:\\)?sqrt\s*(\d+|[a-zA-Z])', r'\\sqrt{\1}', text)
    text = re.sub(r'(?<![a-zA-Z\\])sqrt(?![a-zA-Z0-9\{])', r'\\sqrt', text)
    text = re.sub(r'frac(\d+)(\d+)', r'\\frac{\1}{\2}', text)

    # 5. ?? (Vectors)
    text = re.sub(r'vec([A-Z]{2})', r'\\overrightarrow{\1}', text) # vecAB -> \overrightarrow{AB}
    text = re.sub(r'vec\s*([a-z])\b', r'\\vec{\1}', text)

    # 6. 撣貉?蝚西?
    text = re.sub(r'(\d+)\s*circ', r'\1^{\\circ}', text)
    text = re.sub(r'angle([A-Z0-9]{2,3})', r'\\angle \1', text)
    for op in ['pm', 'times', 'div', 'approx', 'leq', 'geq', 'neq']:
        text = re.sub(rf'(?<![a-zA-Z\\]){op}(?![a-zA-Z])', rf'\\{op}', text)

    # 7. 甈⊥??璅?(Superscript & Subscript)
    text = re.sub(r'(?<!\$)\b((\w+|\([^)]+\))\^(\{[\w-]+\}|[\w-]+))\b(?!\$)', r'$\1$', text) # x^2 -> $x^2$
    text = re.sub(r'(?<!\$)\b([a-zA-Z])_(\{[\w-]+\}|[\w]+)\b(?!\$)', r'$\1_{\2}$', text)   # a_n -> $a_{n}$
   
    # 4. 靽格迤撣貉? OCR/Pandoc ?航炊
    replacements = {
            '\\[': '$$', '\\]': '$$',  # 撠?\[ \] 蝯曹?頧 $$
            '\\(': '$', '\\)': '$',    # 撠?\( \) 蝯曹?頧 $
            'div ': '\\div '           # 撣貉??航炊嚗iv 瘝???
        }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# ==============================================================================
# [NEW] 撠皜??賢?嚗?? Word (Pandoc) 頛詨??摮???
# ==============================================================================
def clean_pandoc_output(text):
    """
    ??擉啁?/Word撠??撠?Pandoc 頧? Word 瑼??畾撘脰?皜???
    甇文撘?◤ .docx 瘚??澆嚗?撠??蔣??PDF/OCR 瘚???
    """
    if not text: return text

    # 1. 靽桀儔 Pandoc ?Ｙ?????璅漲?貊泵??(^{\^{\circ}} -> ^{\circ})
    text = text.replace(r'^{\^{\circ}}', r'^{\circ}')
    
    # 2. 蝯曹?撠?\( ... \) 頧???$ ... $ (MathJax ?湔??
    # ? Word 頧??皞?LaTeX 銵?詨??澆?嚗??典?蝡舫＊蝷箸? $ 瘥??
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)

    # 3. 靽桀儔 sqrt (Pandoc ???撓??sqrt 2 ????\sqrt{2})
    # ?ㄐ?芸??靽??耨敺抬??踹?隤文??
    text = re.sub(r'(?:\\)?sqrt\s+(\d+|[a-zA-Z])\b', r'\\sqrt{\1}', text)
    
    return text


def _xml_local_name(tag: str) -> str:
    if not tag:
        return ""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _omml_node_to_latex(node) -> str:
    name = _xml_local_name(node.tag)
    if name == "t":
        return str(node.text or "")
    if name in ("oMath", "oMathPara"):
        return "".join(_omml_node_to_latex(child) for child in list(node)).strip()
    if name == "f":
        num = node.find(".//{*}num")
        den = node.find(".//{*}den")
        num_txt = "".join(_omml_node_to_latex(c) for c in list(num)) if num is not None else ""
        den_txt = "".join(_omml_node_to_latex(c) for c in list(den)) if den is not None else ""
        return f"\\frac{{{num_txt}}}{{{den_txt}}}" if (num_txt or den_txt) else ""
    if name == "sSub":
        e = node.find(".//{*}e")
        sub = node.find(".//{*}sub")
        e_txt = "".join(_omml_node_to_latex(c) for c in list(e)) if e is not None else ""
        s_txt = "".join(_omml_node_to_latex(c) for c in list(sub)) if sub is not None else ""
        return f"{e_txt}_{{{s_txt}}}" if e_txt else ""
    if name == "sSup":
        e = node.find(".//{*}e")
        sup = node.find(".//{*}sup")
        e_txt = "".join(_omml_node_to_latex(c) for c in list(e)) if e is not None else ""
        s_txt = "".join(_omml_node_to_latex(c) for c in list(sup)) if sup is not None else ""
        return f"{e_txt}^{{{s_txt}}}" if e_txt else ""
    if name == "sSubSup":
        e = node.find(".//{*}e")
        sub = node.find(".//{*}sub")
        sup = node.find(".//{*}sup")
        e_txt = "".join(_omml_node_to_latex(c) for c in list(e)) if e is not None else ""
        sub_txt = "".join(_omml_node_to_latex(c) for c in list(sub)) if sub is not None else ""
        sup_txt = "".join(_omml_node_to_latex(c) for c in list(sup)) if sup is not None else ""
        return f"{e_txt}_{{{sub_txt}}}^{{{sup_txt}}}" if e_txt else ""
    return "".join(_omml_node_to_latex(child) for child in list(node))


def _normalize_omml_latex(latex_text: str) -> str:
    s = re.sub(r"\s+", " ", str(latex_text or "").strip())
    # Common textbook notation: P with superscript/subscript means permutation P(n,r)
    s = re.sub(r"P\^\{(\d+)\}_\{(\d+)\}", r"P(\1,\2)", s)
    s = re.sub(r"P_\{(\d+)\}\^\{(\d+)\}", r"P(\2,\1)", s)
    return s.strip()


def convert_omml_to_latex(omml_xml: str) -> str:
    root = ET.fromstring(omml_xml)
    latex = _omml_node_to_latex(root)
    return _normalize_omml_latex(latex)


def _extract_docx_image_placeholder(run_el, paragraph_state):
    """Return [FORMULA_IMAGE_N] placeholders for every image reference found in *run_el*.

    Handles two embedding mechanisms:
    - DrawingML  : ``<a:blip>`` inside ``<w:drawing>`` (standard Word inline image).
    - VML / OLE  : ``<v:imagedata>`` inside ``<w:object>`` / ``<w:pict>``
                   ??used by MathType (Equation.DSMT4) and legacy OLE equations.
                   Previously these returned ``""`` (silently dropped the formula
                   position).  Now they produce a ``[FORMULA_IMAGE_N]`` placeholder
                   so that the paragraph text keeps the formula slot visible to
                   downstream Gemini parsing.
    """
    image_blips = run_el.findall(".//{*}blip")
    vml_imagedata = run_el.findall(".//{*}imagedata")  # MathType OLE / VML preview
    if not image_blips and not vml_imagedata:
        return ""
    placeholders = []
    for _ in image_blips:
        paragraph_state["formula_image_count"] += 1
        placeholders.append(f"[FORMULA_IMAGE_{paragraph_state['formula_image_count']}]")
        paragraph_state["needs_formula_review"] = True
    for _ in vml_imagedata:
        paragraph_state["formula_image_count"] += 1
        placeholders.append(f"[FORMULA_IMAGE_{paragraph_state['formula_image_count']}]")
        paragraph_state["needs_formula_review"] = True
    return "".join(placeholders)


def extract_docx_paragraph_with_equations(paragraph) -> str:
    state = {
        "equations": 0,
        "equation_failures": 0,
        "needs_formula_review": False,
        "formula_image_count": 0,
    }
    pieces = []
    p_el = paragraph._p
    for child in list(p_el):
        cname = _xml_local_name(child.tag)
        if cname == "r":
            run_text = []
            for rchild in list(child):
                rname = _xml_local_name(rchild.tag)
                if rname == "t":
                    run_text.append(str(rchild.text or ""))
                elif rname in ("oMath", "oMathPara"):
                    state["equations"] += 1
                    try:
                        latex = convert_omml_to_latex(ET.tostring(rchild, encoding="unicode"))
                        if latex:
                            run_text.append(f"\\({latex}\\)")
                            current_app.logger.info(f"[DOCX EQUATION] converted latex={latex}")
                        else:
                            raise ValueError("empty_latex")
                    except Exception:
                        state["equation_failures"] += 1
                        state["needs_formula_review"] = True
                        run_text.append("[WORD_EQUATION_UNPARSED]")
                elif rname in ("drawing", "object", "pict"):
                    run_text.append(_extract_docx_image_placeholder(child, state))
            pieces.append("".join(run_text))
        elif cname in ("oMath", "oMathPara"):
            state["equations"] += 1
            try:
                latex = convert_omml_to_latex(ET.tostring(child, encoding="unicode"))
                if latex:
                    pieces.append(f"\\({latex}\\)")
                else:
                    raise ValueError("empty_latex")
            except Exception:
                state["equation_failures"] += 1
                state["needs_formula_review"] = True
                pieces.append("[WORD_EQUATION_UNPARSED]")
    text = "".join(pieces).strip()
    paragraph._math_meta = state
    return text or str(paragraph.text or "").strip()


def extract_docx_table_with_equations(table) -> str:
    lines = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            segs = []
            for p in cell.paragraphs:
                seg = extract_docx_paragraph_with_equations(p)
                if seg:
                    segs.append(seg)
            cells.append(" ".join(segs).strip())
        lines.append(" | ".join(cells).strip())
    return "\n".join(lines).strip()


def extract_converted_latex_docx(file_path: str) -> tuple[dict[int, str], dict[str, Any]]:
    """Extract DOCX text in document order for pre-converted MathType->LaTeX DOCX."""
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(file_path)
    ordered_chunks: list[str] = []
    paragraph_count = 0
    table_count = 0

    for block in doc.element.body.iterchildren():
        if block.tag.endswith("}p"):
            para = Paragraph(block, doc)
            text = str(para.text or "").strip()
            paragraph_count += 1
            if text:
                ordered_chunks.append(text)
        elif block.tag.endswith("}tbl"):
            table_count += 1
            tbl = Table(block, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for p in cell.paragraphs:
                        text = str(p.text or "").strip()
                        if text:
                            ordered_chunks.append(text)
    merged = "\n".join(ordered_chunks).strip()
    return {1: merged} if merged else {}, {
        "paragraph_count": paragraph_count,
        "table_count": table_count,
    }


def detect_converted_latex_docx(text: str) -> dict[str, Any]:
    t = str(text or "")
    latex_signal_count = 0
    latex_signal_count += len(re.findall(r"\$[^$\n]+\$", t))
    latex_signal_count += len(re.findall(r"\\\([^)\n]+\\\)", t))
    latex_signal_count += len(re.findall(r"\\\[[^\]\n]+\\\]", t))
    latex_signal_count += len(re.findall(r"\\(?:frac|sqrt|le|ge|binom|times|pm)\b", t))
    placeholder_count = len(re.findall(r"\[FORMULA_IMAGE_\d+\]|\[FORMULA_MISSING\]", t))
    is_converted = latex_signal_count >= 3 and placeholder_count <= 1
    return {
        "is_converted_latex_docx": bool(is_converted),
        "latex_signal_count": int(latex_signal_count),
        "formula_placeholder_count": int(placeholder_count),
    }


def build_docx_media_relationship_map(docx_path: str, extracted_media_dir: str) -> dict[str, dict[str, str]]:
    rel_map: dict[str, dict[str, str]] = {}
    try:
        with zipfile.ZipFile(docx_path, "r") as zf:
            rel_xml = zf.read("word/_rels/document.xml.rels")
        rel_root = ET.fromstring(rel_xml)
        for rel in rel_root.findall(".//{*}Relationship"):
            rid = rel.attrib.get("Id")
            target = rel.attrib.get("Target", "")
            rtype = rel.attrib.get("Type", "")
            if not rid or "image" not in rtype.lower():
                continue
            filename = os.path.basename(target)
            extracted_path = os.path.join(extracted_media_dir, filename).replace("\\", "/")
            rel_map[rid] = {
                "target_ref": target,
                "content_type": _guess_image_content_type(filename),
                "extracted_path": extracted_path,
            }
    except Exception:
        return {}
    return rel_map


def _guess_image_content_type(filename: str) -> str:
    ext = os.path.splitext(str(filename or ""))[1].lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".wmf": "image/x-wmf",
        ".emf": "image/x-emf",
    }.get(ext, "application/octet-stream")


def _docx_image_original_format(path_or_name: str, content_type: str = "") -> str:
    ext = os.path.splitext(str(path_or_name or ""))[1].lower().lstrip(".")
    if ext in ("wmf", "emf", "png", "jpg", "jpeg"):
        return "jpeg" if ext == "jpg" else ext
    ctype = str(content_type or "").lower()
    if "wmf" in ctype:
        return "wmf"
    if "emf" in ctype:
        return "emf"
    if "png" in ctype:
        return "png"
    if "jpeg" in ctype or "jpg" in ctype:
        return "jpeg"
    return "unknown"


def extract_docx_image_rids_from_paragraph(paragraph) -> list[str]:
    rids = []
    p_el = paragraph._p
    for blip in p_el.findall(".//{*}blip"):
        rid = blip.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed")
        if rid:
            rids.append(rid)
    for imagedata in p_el.findall(".//{*}imagedata"):
        rid = imagedata.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")
        if rid:
            rids.append(rid)
    return rids


def _is_question_start_text(text: str) -> bool:
    t = str(text or "").strip()
    if not t:
        return False
    if classify_non_question_block(t) in ("concept_explanation", "figure_caption", "narration"):
        return False
    heading_patterns = [
        r"^\s*靘s*憿?\s*\d+",
        r"^\s*?典?蝺渡?\s*\d+",
        r"^\s*?箇?憿s*\d+",
        r"^\s*?脤?憿s*\d+",
        r"^\s*(?:\d+\s*-\s*\d+\s*)?蝧?(?:\s*?箇?憿\s*?脤?憿??\s*\d*",
        r"^\s*?芣?閰?",
        r"^\s*(蝯望葫鋆策蝡蝯望葫憿??|摮豢葫憿??|??皜祇?)\s*\d*",
        r"^\s*憿\s*\d+",
        r"^\s*\d+[\s\.\)]",
    ]
    return any(re.search(p, t) for p in heading_patterns)


_STRUCTURAL_BOUNDARY_PATTERNS = [
    r"^\s*第\s*\d+\s*章",
    r"^\s*\d+\s*[^\d\s].*$",
    r"^\s*\d+\s*-\s*\d+\s+[^\s].*$",
    r"^\s*\d+\s*-\s*\d+\s*\.\s*\d+\s*[^\s].*$",
    r"^\s*例(?:題)?\s*\d+",
    r"^\s*隨堂練習\s*\d+",
    r"^\s*(?:\d+\s*-\s*\d+\s*)?習題",
    r"^\s*基礎題\s*\d*",
    r"^\s*進階題\s*\d*",
    r"^\s*自我評量",
    r"^\s*(?:統測|學測)",
]


def is_structural_boundary_line(line: str) -> bool:
    t = str(line or "").strip()
    if not t:
        return False
    return any(re.search(p, t) for p in _STRUCTURAL_BOUNDARY_PATTERNS)


_NON_QUESTION_EXPLANATION_CUES = (
    "說明",
    "觀念",
    "範例解析",
    "解題",
    "補充",
    "備註",
    "提示",
    "概念",
    "答案",
    "解答",
    "附註",
)

_QUESTION_VERBS = (
    "求",
    "解",
    "算",
    "證明",
    "判斷",
    "比較",
    "化簡",
    "計算",
    "作圖",
    "試求",
    "求出",
)


def _is_figure_caption_line(text: str) -> bool:
    t = str(text or "").strip()
    return bool(re.search(r"^(?:圖|表)\s*\d+", t))


def classify_non_question_block(text: str) -> str | None:
    t = str(text or "").strip()
    if not t:
        return "narration"
    if t == "[BLOCK_IMAGE]" or _is_figure_caption_line(t):
        return "figure_caption"

    has_explain = any(cue in t for cue in _NON_QUESTION_EXPLANATION_CUES) or bool(re.search(r"^(?:說明|解題|觀念)\b", t))
    has_question_verb = any(v in t for v in _QUESTION_VERBS)
    if has_explain and not has_question_verb:
        return "concept_explanation"
    if "[BLOCK_IMAGE]" in t and not has_question_verb:
        return "figure_caption"
    return None


def segment_question_block_text(problem_text: str, question_title: str = "") -> tuple[str, dict]:
    text = str(problem_text or "")
    lines = [ln for ln in text.splitlines()]
    kept: list[str] = []
    dropped_reason = ""
    started = False

    for idx, raw_line in enumerate(lines):
        line = str(raw_line or "").strip()
        if not line:
            if started:
                kept.append(raw_line)
            continue
        if idx == 0:
            kept.append(raw_line)
            started = True
            continue
        if is_structural_boundary_line(line):
            if question_title and _extract_question_title_from_text(line) == str(question_title).replace(" ", ""):
                kept.append(raw_line)
                started = True
                continue
            dropped_reason = f"stopped question block at structural boundary: {line}"
            break
        kind = classify_non_question_block(line)
        if kind == "figure_caption":
            dropped_reason = "detected figure caption, skipped from question text"
            break
        kept.append(raw_line)
        started = True

    result = "\n".join(kept).strip()
    meta = {"changed": result != text.strip(), "reason": dropped_reason}
    return result, meta


def _extract_question_title_from_text(text: str) -> str:
    t = str(text or "").strip()
    for pat in [
        r"(蝯望葫鋆策蝡s*\d+)",
        r"(?典?蝺渡?\s*\d+)",
        r"(靘?\s*\d+)",
        r"(?箇?憿s*\d+)",
        r"(?脤?憿s*\d+)",
        r"(?芣?閰?[^\s嚗*)",
        r"((?:\d+-\d+\s*)?蝧?\s*\d*)",
    ]:
        m = re.search(pat, t)
        if m:
            return m.group(1).replace(" ", "")
    # Bare-numbered exercise: "5 閫??蝑?..." / "1. 閰行?..." ??return bare number string
    m = re.search(r"^(\d+)[\s\.\)]", t)
    if m:
        return m.group(1)
    return t[:20] or ""


def _is_formula_question_text(text: str) -> bool:
    t = str(text or "")
    return any(k in t for k in ("求", "解", "方程", "不等式", "函數"))


def _is_image_question_text(text: str) -> bool:
    t = str(text or "")
    return any(k in t for k in ("憒?", "?喳?", "??", "璉撘???", "?", "?耦"))


_QUESTION_LABEL_RE = re.compile(
    r"((?:例(?:題)?|隨堂練習|基礎題|進階題|統測|學測|"
    r"(?:\d+\s*-\s*\d+\s*)?習題)\s*\d+)"
)

# Used to validate bare-number exercise blocks vs. concept-heading blocks.
_QUESTION_VERB_IN_BLOCK_RE = re.compile(
    r"求|解|算|證明|判斷|化簡|計算|作圖|試求|求出"
)
_CONCEPT_CUES_RE = re.compile(
    r"觀念|說明|解題|補充|重點|定義|性質"
)

# Map Gemini label keywords to DOCX key label keywords (must be same type to match).
_LABEL_TYPE_MAP = {
    "例題": "例題",
    "隨堂練習": "隨堂練習",
    "基礎題": "基礎題",
    "進階題": "進階題",
    "統測": "統測",
}


def _normalize_docx_question_title_key(title: str) -> str:
    """Normalize question title key for DOCX mapping lookups."""
    t = re.sub(r"\s+", "", str(title or "").strip())
    if not t:
        return ""
    # Alias: "靘?" and "靘?1" are equivalent.
    t = re.sub(r"^靘??!憿?(\d+)$", r"靘?\1", t)
    return t


def _build_docx_title_aliases(title: str, *, include_bare_number: bool = False) -> list[str]:
    """Build ordered alias candidates for title-to-block / title-to-asset matching."""
    raw = str(title or "").strip()
    ns = _normalize_docx_question_title_key(raw)
    aliases: list[str] = []

    def _add(v: str):
        vv = _normalize_docx_question_title_key(v)
        if vv and vv not in aliases:
            aliases.append(vv)

    _add(raw)
    _add(ns)

    # Prefix stripping alias: "1-1蝧? ?箇?憿?" -> "?箇?憿?"
    m = _QUESTION_LABEL_RE.search(ns)
    if m:
        _add(m.group(1))

    # 靘? / 靘?alias
    m_ex = re.search(r"^例題?(\d+)$", ns)
    if m_ex:
        _add(f"例題{m_ex.group(1)}")
    m_ex_short = re.search(r"^例(\d+)$", re.sub(r"\s+", "", raw))
    if m_ex_short:
        _add(f"例題{m_ex_short.group(1)}")

    if include_bare_number:
        # Bare number alias for exercise area fallback.
        m_num = re.search(r"(\d+)$", ns)
        if m_num:
            _add(m_num.group(1))
    return aliases


def _extract_label_and_number(title: str) -> tuple[str | None, str | None]:
    t = _normalize_docx_question_title_key(title)
    for label in ("例題", "隨堂練習", "基礎題", "進階題", "統測"):
        m = re.search(rf"^{re.escape(label)}(\d+)$", t)
        if m:
            return label, m.group(1)
    # "例" alias
    m = re.search(r"^例(\d+)$", re.sub(r"\s+", "", str(title or "").strip()))
    if m:
        return "例題", m.group(1)
    return None, None


def _normalize_docx_key_for_scan(raw_key: str) -> str:
    return _normalize_docx_question_title_key(str(raw_key or ""))


def _find_docx_prefix_match(title: str, source_map: dict):
    """Find key by normalized-prefix match, preserving label type."""
    if not isinstance(source_map, dict) or not source_map:
        return None
    label, num = _extract_label_and_number(title)
    if not label or not num:
        return None
    expected = f"{label}{num}"
    expected_short = f"例{num}" if label == "例題" else None
    for k, v in source_map.items():
        kn = _normalize_docx_key_for_scan(k)
        if not kn:
            continue
        if kn.startswith(expected):
            return v
        if expected_short and kn.startswith(expected_short):
            return v
    return None


def _find_exercise_section_key(source_map: dict) -> str:
    if not isinstance(source_map, dict):
        return ""
    for k in source_map.keys():
        kn = _normalize_docx_key_for_scan(k)
        if kn and re.search(r"(?:\d+-\d+)?蝧?$", kn):
            return str(k)
    return ""


def _is_safe_exercise_block(block_text: str, num: str) -> bool:
    """Return True only when *block_text* is a genuine bare-numbered exercise.

    A safe exercise block:
    - Starts with ``N<space>`` (NOT ``N.`` which signals a concept-heading).
    - Contains at least one unambiguous question verb.
    - Does NOT read as a pure concept heading (no concept cues without a verb).

    This guard prevents bare-number key "1" from being erroneously paired with
    concept paragraphs like "1.銝?撘????扯釭??.
    """
    t = str(block_text or "").strip()
    # Must begin with the exact number followed by a space (not period/comma).
    if not re.match(rf"^{re.escape(num)}\s", t):
        return False
    if not _QUESTION_VERB_IN_BLOCK_RE.search(t):
        return False
    return True


def _lookup_docx_formula_block(title: str, formula_blocks: dict) -> str:
    """High-confidence lookup for a raw DOCX formula block by Gemini question title.

    Strategies (all high-confidence):
    1. Exact match after stripping spaces.
    2. Strip leading section prefix and match the trailing label token exactly
       (e.g. "1-1蝧? ?箇?憿?" ??look up "?箇?憿?").
    3. Same-type label number match: trailing number N and same label type
       (e.g. title "?箇?憿?" searches only for keys "?箇?憿?", never "靘?5").
    4. Safe bare-number match: key is bare number N, block content starts with
       "N " (space, NOT period) and contains a question verb.

    Returns empty string when no high-confidence match is found.
    Deliberately does NOT perform cross-type number matching or unrestricted
    bare-number lookup, which caused concept paragraphs to be misassigned.
    """
    if not title or not formula_blocks:
        return ""
    title_ns = _normalize_docx_question_title_key(title)

    # Strategy 1: exact + title aliases (靘?/靘?1/靘? 1...)
    for alias in _build_docx_title_aliases(title, include_bare_number=False):
        v = formula_blocks.get(alias)
        if v:
            return v
    v = formula_blocks.get(str(title))
    if v:
        return v

    # Strategy 2: strip section prefix ??exact label lookup
    m = _QUESTION_LABEL_RE.search(title_ns)
    label_key = m.group(1).replace(" ", "") if m else None
    if label_key:
        v = formula_blocks.get(label_key)
        if v:
            return v
    v = _find_docx_prefix_match(title, formula_blocks)
    if v:
        return v

    # Strategy 3: same-type label + number (only match within the same label type)
    m2 = re.search(r"(\d+)$", title_ns)
    if m2:
        num = m2.group(1)
        title_label_type = None
        for kw in _LABEL_TYPE_MAP:
            if kw in title_ns:
                title_label_type = kw
                break
        if title_label_type:
            same_type_key = title_label_type + num
            v = formula_blocks.get(same_type_key)
            if v:
                return v

        # Strategy 4: safe bare-number key (N<space> + question verb required)
        v = formula_blocks.get(num)
        if v and _is_safe_exercise_block(v, num):
            return v

    # Strategy 5: exercise-section fallback
    t = _normalize_docx_question_title_key(title)
    if re.search(r"(?:\d+-\d+)?蝧?.*(?:?箇?憿?脤?憿?\d+$", t):
        sec_key = _find_exercise_section_key(formula_blocks)
        if sec_key:
            return str(formula_blocks.get(sec_key) or "")

    return ""


_COORD_GUARD_SECTION_RE = re.compile(r"1\s*-\s*2|平面坐標|坐標平面|坐標幾何")
_COORD_GUARD_TEXT_RE = re.compile(r"坐標|平面|距離|中點|象限|點")


def _is_b1_coordinate_context(volume: str, section_title: str, problem_text: str) -> bool:
    vol = str(volume or "")
    sec = str(section_title or "")
    text = str(problem_text or "")
    is_b1 = ("B1" in vol.upper()) or ("數學B1" in vol)
    if not is_b1:
        return False
    if _COORD_GUARD_SECTION_RE.search(sec):
        return True
    return bool(_COORD_GUARD_TEXT_RE.search(text))


def _normalize_coordinate_point_notation(text: str) -> str:
    """Normalize OCR/LaTeX-mangled coordinate point labels into A(x,y)-style forms."""
    out = str(text or "")
    label = r"([ABCPQR])"
    idx = r"([A-Za-z0-9+\-*/^()]+)"
    def _coord_sup_sub(lbl: str, sup: str, sub: str) -> str:
        # B1 regression: C^y_x should map to C(x,y); P^a_b should map to P(a,b).
        if str(lbl).upper() == "C":
            return f"{lbl}({sub},{sup})"
        return f"{lbl}({sup},{sub})"
    out = re.sub(
        rf"(?:\{{\s*\}}\s*)?\^\{{\s*{idx}\s*\}}\s*{label}\s*_\{{\s*{idx}\s*\}}",
        lambda m: f"{m.group(2)}({m.group(1)},{m.group(3)})",
        out,
    )
    out = re.sub(
        rf"{label}\s*\^\{{\s*{idx}\s*\}}\s*_\{{\s*{idx}\s*\}}",
        lambda m: _coord_sup_sub(m.group(1), m.group(2), m.group(3)),
        out,
    )
    out = re.sub(
        rf"{label}\s*_\{{\s*{idx}\s*\}}\s*\^\{{\s*{idx}\s*\}}",
        lambda m: f"{m.group(1)}({m.group(3)},{m.group(2)})",
        out,
    )
    out = re.sub(
        rf"{label}\s*\^\s*{idx}\s*_\s*{idx}",
        lambda m: _coord_sup_sub(m.group(1), m.group(2), m.group(3)),
        out,
    )
    out = re.sub(
        rf"{label}\s*_\s*{idx}\s*\^\s*{idx}",
        lambda m: f"{m.group(1)}({m.group(3)},{m.group(2)})",
        out,
    )
    return out


def _lookup_docx_question_assets(title: str, q_assets: dict) -> list:
    """High-confidence lookup for question assets by Gemini question title.

    Mirrors the same four high-confidence strategies as
    :func:`_lookup_docx_formula_block`.  Cross-type and unrestricted bare-number
    lookups are intentionally excluded.
    """
    if not title or not q_assets:
        return []
    title_ns = _normalize_docx_question_title_key(title)

    # Strategy 1: exact + title aliases
    for alias in _build_docx_title_aliases(title, include_bare_number=True):
        v = q_assets.get(alias)
        if v:
            return v
    v = q_assets.get(str(title))
    if v:
        return v

    # Strategy 2: strip section prefix
    m = _QUESTION_LABEL_RE.search(title_ns)
    label_key = m.group(1).replace(" ", "") if m else None
    if label_key:
        v = q_assets.get(label_key)
        if v:
            return v

    # Strategy 3: same-type label + number
    m2 = re.search(r"(\d+)$", title_ns)
    if m2:
        num = m2.group(1)
        title_label_type = None
        for kw in _LABEL_TYPE_MAP:
            if kw in title_ns:
                title_label_type = kw
                break
        if title_label_type:
            same_type_key = title_label_type + num
            v = q_assets.get(same_type_key)
            if v:
                return v

        # Strategy 4: safe bare-number
        v = q_assets.get(num)
        # q_assets keys are produced from detected question starts, so bare-number key
        # here is already a question-level anchor and can be safely used.
        if v:
            return v

    # Strategy 5: same-label prefix key (e.g. key="靘? ?貊?銝?.." for title "靘? 1")
    v = _find_docx_prefix_match(title, q_assets)
    if v:
        mapped = []
        for a in (v or []):
            aa = dict(a)
            aa.setdefault("mapping_status", "prefix_match")
            mapped.append(aa)
        return mapped

    # Strategy 6: exercise section fallback (e.g. only key="1-1蝧?")
    t = _normalize_docx_question_title_key(title)
    if re.search(r"(?:\d+-\d+)?蝧?.*(?:?箇?憿?脤?憿?\d+$", t):
        sec_key = _find_exercise_section_key(q_assets)
        if sec_key:
            fallback_assets = []
            for a in (q_assets.get(sec_key) or []):
                aa = dict(a)
                aa.setdefault("mapping_status", "exercise_section_fallback")
                fallback_assets.append(aa)
            if fallback_assets:
                return fallback_assets

    return []


def attach_docx_media_to_question_blocks(blocks):
    question_assets: dict[str, list[dict[str, Any]]] = {}
    orphan_images: list[dict[str, Any]] = []
    image_kw = [
        "圖", "表", "下圖", "上圖", "右圖", "左圖", "如圖",
        "題圖", "示意圖", "座標圖", "函數圖", "幾何圖",
    ]

    question_points: list[dict[str, Any]] = []
    image_blocks: list[dict[str, Any]] = []
    for b in blocks:
        if b.get("type") == "paragraph":
            txt = str(b.get("text", "") or "")
            if _is_question_start_text(txt):
                title = _extract_question_title_from_text(txt)
                q = {
                    "title": title,
                    "block_index": int(b.get("block_index") or 0),
                    "text": txt,
                    "has_image_kw": any(k in txt for k in image_kw),
                    "has_formula_kw": _is_formula_question_text(txt),
                }
                question_points.append(q)
                question_assets.setdefault(title, [])
        elif b.get("type") == "image":
            image_blocks.append(dict(b))

    for img in image_blocks:
        img_idx = int(img.get("block_index") or 0)
        if not question_points:
            orphan_images.append(img)
            continue

        prev_q = None
        next_q = None
        for q in question_points:
            if q["block_index"] <= img_idx:
                prev_q = q
            elif q["block_index"] > img_idx and next_q is None:
                next_q = q
                break

        attached = False
        def _classify_asset(asset_obj, q):
            ext = os.path.splitext(str(asset_obj.get("path") or ""))[1].lower().lstrip(".")
            # Treat as formula_asset when:
            # (a) WMF/EMF image adjacent to a formula-keyword question, OR
            # (b) image originated from a paragraph that contained [FORMULA_IMAGE_N]
            is_ole_formula = asset_obj.get("is_formula_placeholder_source", False)
            if (ext in ("wmf", "emf") and q.get("has_formula_kw")) or is_ole_formula:
                asset_obj["media_kind"] = "formula_asset"
                asset_obj["asset_type"] = "word_formula_image"
                reason = "ole_formula_placeholder_source" if is_ole_formula else "formula_question_block"
                if has_app_context():
                    current_app.logger.info(
                        f"[DOCX MEDIA CLASSIFY] rid={asset_obj.get('rid')} kind=formula_asset reason={reason}"
                    )
                m = re.search(r"\[FORMULA_IMAGE_(\d+)\]", str(q.get("text", "") or ""))
                if m:
                    asset_obj["placeholder_index"] = int(m.group(1))
                    asset_obj["placeholder_token"] = f"[FORMULA_IMAGE_{m.group(1)}]"
                asset_obj["original_path"] = str(asset_obj.get("path") or "")
                asset_obj["original_format"] = _docx_image_original_format(
                    asset_obj.get("path") or "", str(asset_obj.get("content_type") or "")
                )
            else:
                asset_obj["media_kind"] = "image_asset"
                asset_obj["asset_type"] = "word_embedded_image"
                reason = "question_contains_image_kw" if q.get("has_image_kw") else "default_image_asset"
                if has_app_context():
                    current_app.logger.info(
                        f"[DOCX MEDIA CLASSIFY] rid={asset_obj.get('rid')} kind=image_asset reason={reason}"
                    )

        # Case 1: image before first question; attach when image/formula kw OR OLE formula image.
        if prev_q is None and next_q is not None:
            img_ext = os.path.splitext(str(img.get("path") or ""))[1].lower().lstrip(".")
            is_ole_img = img.get("is_formula_placeholder_source", False)
            if next_q["has_image_kw"] or next_q["has_formula_kw"] or is_ole_img or img_ext in ("wmf", "emf"):
                asset = dict(img)
                asset["image_attach_reason"] = "near_next_question"
                asset["needs_image_review"] = True
                _classify_asset(asset, next_q)
                question_assets.setdefault(next_q["title"], []).append(asset)
                attached = True
            else:
                orphan_images.append(img)
                continue

        # Case 2: image after a known question and before next question.
        if not attached and prev_q is not None and next_q is not None:
            d_prev = abs(img_idx - prev_q["block_index"])
            d_next = abs(next_q["block_index"] - img_idx)
            if d_prev == d_next:
                shared_prev = dict(img)
                shared_next = dict(img)
                shared_prev["image_attach_reason"] = "shared_nearby_image"
                shared_prev["needs_image_review"] = True
                shared_prev["shared_image"] = True
                shared_next["image_attach_reason"] = "shared_nearby_image"
                shared_next["needs_image_review"] = True
                shared_next["shared_image"] = True
                _classify_asset(shared_prev, prev_q)
                _classify_asset(shared_next, next_q)
                question_assets.setdefault(prev_q["title"], []).append(shared_prev)
                question_assets.setdefault(next_q["title"], []).append(shared_next)
                attached = True
            elif next_q["has_image_kw"] and d_next <= d_prev:
                asset = dict(img)
                asset["image_attach_reason"] = "near_next_question"
                asset["needs_image_review"] = True
                _classify_asset(asset, next_q)
                question_assets.setdefault(next_q["title"], []).append(asset)
                attached = True
            elif prev_q["has_image_kw"] and d_prev < d_next:
                asset = dict(img)
                asset["image_attach_reason"] = "near_prev_question"
                asset["needs_image_review"] = True
                _classify_asset(asset, prev_q)
                question_assets.setdefault(prev_q["title"], []).append(asset)
                attached = True
            else:
                asset = dict(img)
                asset["image_attach_reason"] = "image_inside_question_block"
                asset["needs_image_review"] = True
                _classify_asset(asset, prev_q)
                question_assets.setdefault(prev_q["title"], []).append(asset)
                attached = True

        # Case 3: image after last question -> attach to the latest question.
        if not attached and prev_q is not None and next_q is None:
            asset = dict(img)
            asset["image_attach_reason"] = "image_inside_question_block"
            asset["needs_image_review"] = True
            _classify_asset(asset, prev_q)
            question_assets.setdefault(prev_q["title"], []).append(asset)
            attached = True

        if not attached:
            orphan_images.append(img)

    return question_assets, orphan_images


def build_docx_question_formula_context(blocks):
    question_blocks: dict[str, str] = {}
    current_title = None
    buffer = []
    for b in blocks or []:
        btype = b.get("type")
        if btype == "paragraph":
            txt = str(b.get("text", "") or "").strip()
            if not txt:
                continue
            if _is_question_start_text(txt):
                if current_title and buffer:
                    question_blocks[current_title] = "\n".join(buffer).strip()
                current_title = _extract_question_title_from_text(txt)
                buffer = [txt]
            elif current_title and is_structural_boundary_line(txt):
                if buffer:
                    question_blocks[current_title] = "\n".join(buffer).strip()
                current_title = None
                buffer = []
            elif current_title:
                buffer.append(txt)
        elif btype == "image" and current_title:
            buffer.append("[BLOCK_IMAGE]")
    if current_title and buffer:
        question_blocks[current_title] = "\n".join(buffer).strip()
    return question_blocks


def _safe_title_for_filename(title: str) -> str:
    t = re.sub(r"\s+", "", str(title or "").strip())
    t = re.sub(r"[\\/:*?\"<>|]", "_", t)
    return t[:40] or "untitled"


def _copy_docx_asset_to_question_assets(src_path: str, dst_dir: str, filename: str) -> str | None:
    try:
        import shutil
        if not src_path:
            return None
        if not os.path.isabs(src_path):
            src_abs = os.path.join(current_app.root_path, src_path)
        else:
            src_abs = src_path
        if not os.path.exists(src_abs):
            return None
        os.makedirs(dst_dir, exist_ok=True)
        dst_abs = os.path.join(dst_dir, filename)
        shutil.copy2(src_abs, dst_abs)
        return dst_abs
    except Exception:
        return None


def parse_volume(volume_str: str):
    """Parse vocational math volume label into (subject, volume_number). Never raises re.error."""
    text = str(volume_str or "").strip()
    if not text:
        return None, None

    subject: str | None = None
    vol_num: int | None = None

    try:
        # 數學B1、數學 B2、數學b4
        m = re.search(r"數學\s*([AB])\s*(\d+)", text, re.IGNORECASE)
        if m:
            return m.group(1).upper(), int(m.group(2))

        # B1、A2（單字邊界避免誤判過長字串中的片段）
        m = re.search(r"\b([AB])\s*(\d+)\b", text, re.IGNORECASE)
        if m:
            return m.group(1).upper(), int(m.group(2))

        zh_map = {"一": 1, "二": 2, "三": 3, "四": 4}
        for zh, num in zh_map.items():
            if zh + "冊" in text:
                vol_num = num
                break

        if "數學B" in text or "B" in text.upper():
            subject = "B"
        elif "數學A" in text or "A" in text.upper():
            subject = "A"

        return subject, vol_num
    except re.error:
        return None, None


def normalize_json_text_before_parse(text):
    """Normalize JSON text before parsing."""
    if not text:
        return text

    normalized = str(text)
    # 撌脩獢?嚗頝唾?望?????雿葉?摮??寧銝剜?撘??踹??游? JSON 摮葡
    # keep legacy cleanup no-op when source token is corrupted
    normalized = normalized.replace('"銝????拙予??銝????', "")
    return normalized


def sanitize_detailed_solution_text(text, max_chars=500):
    """Sanitize detailed solution text for storage."""
    if text is None:
        return ""

    cleaned = str(text).strip()
    if not cleaned:
        return ""

    banned_phrases = [
        "Let's trace",
        "Let's re-do",
        "This is not",
        "English chain-of-thought",
        "?岫?航炊??",
        "憭活???典?",
    ]
    for phrase in banned_phrases:
        cleaned = cleaned.replace(phrase, "")

    # ?芯???敺?隢挾嚗????憭葉??挾??
    paragraph_parts = [p.strip() for p in re.split(r"\n{2,}", cleaned) if p.strip()]
    if paragraph_parts:
        cleaned = paragraph_parts[-1]

    if len(cleaned) > max_chars:
        cleaned = cleaned[-max_chars:]

    return cleaned.strip()


def process_textbook_file(
    file_path,
    curriculum_info,
    queue,
    skip_code_gen=False,
    outline_only=False,
    toc_pages=5,
    import_policy=None,
    optional_enrich_pdf_path=None,
):
    """Process textbook file and import parsed content."""

    try:
        import_policy = dict(import_policy or {})
        execution_arch = str(import_policy.get("execution_arch", "native") or "native").strip().lower()
        if execution_arch in ("x86", "x64"):
            runtime_arch = "x64" if "64" in str(platform.architecture()[0]) else "x86"
            if runtime_arch != execution_arch:
                message = f"Execution architecture mismatch: requested={execution_arch}, runtime={runtime_arch}"
                current_app.logger.error(message)
                if queue:
                    queue.put(f"ERROR: {message}")
                return {"status": "error", "message": message}
        if optional_enrich_pdf_path and queue:
            queue.put("INFO: optional enrich PDF path provided")
        # ======================================================
        # [NEW] ?脣?嚗炎?交?衣 Word ?怠???瑼?(隞?~$ ?)
        # ======================================================
        filename = os.path.basename(file_path)
        if filename.startswith("~$"):
            message = f"Skip Word temporary file: {filename}"
            current_app.logger.warning(message)
            if queue:
                queue.put(f"WARN: {message}")
            return {"status": "skipped", "message": message}
        # ======================================================

        # 甇仿? 1: 敺?PDF/Word ???批捆
        content_by_page = extract_content_from_file(
            file_path,
            queue,
            max_pages=toc_pages if outline_only else None,
            import_policy=import_policy,
        )

        # [V2.5] ?遣蝡?瑽芋撘?
        if outline_only:
            volume_val = str(curriculum_info.get('volume', ''))
            curr_val = str(curriculum_info.get('curriculum', ''))
            
            parsed_data = None
            structure_source = "pdf_toc"

            # ?岫 AI TOC 閫??
            if content_by_page:
                toc_json_string = call_gemini_for_toc(content_by_page, curriculum_info, queue)
                if toc_json_string:
                    toc_json_string = normalize_json_text_before_parse(toc_json_string)
                    parsed_data = parse_ai_response(toc_json_string, queue)
                    if parsed_data and parsed_data.get('chapters'):
                        message = "AI TOC extraction succeeded"
                        current_app.logger.info(message)
                        queue.put(f"SUCCESS: {message}")
                        
                        # [V2.6] 蝘駁 OutlinePlaceholder ?摩嚗漱?勗??典神?亙撘???
                        pass
            
            # ??AI 閫??憭望?嚗???YAML Fallback
            if not parsed_data:
                struct_map = get_structure_map(curr_val, volume_val)
                if struct_map and struct_map.data:
                    message = f"AI 閫??憭望???批捆嚗??YAML 蝯??啣? ({volume_val})..."
                    current_app.logger.info(message)
                    queue.put(f"INFO: {message}")
                    structure_source = "yaml_fallback"
                    
                    # 撠?YAML 頧???parsed_data ?澆?
                    yaml_chapters = struct_map.data.get('chapters', [])
                    parsed_chapters = []
                    for ch in yaml_chapters:
                        ch_title = f"{ch.get('index')} {ch.get('title')}"
                        sections = []
                        for sec in ch.get('sections', []):
                            sec_title = f"{sec.get('code')} {sec.get('title')}"
                            sections.append({
                                "section_title": sec_title,
                                "concepts": [] # [V2.6] 銝??閬?Placeholder concept
                            })
                        parsed_chapters.append({
                            "chapter_title": ch_title,
                            "sections": sections
                        })
                    parsed_data = {"chapters": parsed_chapters}
            
            if parsed_data:
                result = import_outline_structure_only(
                    parsed_data,
                    curriculum_info,
                    queue,
                    source_file_path=file_path
                )
                return {
                    "status": "success", 
                    "message": f"?桅??嗆?撱箇?摰? (靘?: {structure_source})", 
                    "structure_source": structure_source,
                    "skipped_skills": True,
                    "skipped_examples": True,
                    "skipped_practices": True,
                    "skipped_code_generation": True,
                    **result
                }
            else:
                return {"status": "error", "message": "Failed to parse outline from PDF and YAML fallback."}

        if not content_by_page:
            message = "Failed to extract content from file."
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {"status": "error", "message": "Content extraction failed."}

        raw_content_by_page = dict(content_by_page)
        docx_formula_source_mode = str(
            ((_DOCX_IMPORT_CONTEXT or {}).get("docx_formula_source_mode") or "")
        ).strip()
        content_by_page = _normalize_extracted_content_math(
            content_by_page,
            queue,
            docx_formula_source_mode=docx_formula_source_mode,
        )
        page_analysis_payload = _build_page_analysis_payload(
            raw_content_by_page,
            content_by_page,
            file_path=file_path,
            queue=queue,
        )

        # 甇仿? 2: ?澆 AI ?脰???
        ai_json_result_string = call_gemini_for_analysis(
            content_by_page,
            curriculum_info,
            queue,
            page_analysis_payload=page_analysis_payload,
            import_policy=import_policy,
        )
        # 甇仿? 3: 閫?? AI ???JSON 摮葡
        if ai_json_result_string is None:
            return {"status": "error", "message": "AI analysis failed."}
        if not ai_json_result_string:
            return {"status": "error", "message": "AI returned empty response."}

        ai_json_result_string = normalize_json_text_before_parse(ai_json_result_string)
        parsed_data = parse_ai_response(ai_json_result_string, queue)
        if not parsed_data:
            return {"status": "error", "message": "Failed to parse AI JSON response."}

        parsed_data = _mark_needs_review_for_low_quality_pages(parsed_data, page_analysis_payload)
        parsed_data = _normalize_parsed_textbook_math(
            parsed_data,
            queue,
            docx_formula_source_mode=docx_formula_source_mode,
        )

        # 甇仿? 4: 撠圾???????亥??澈
        if docx_formula_source_mode == "converted_docx_latex":
            extracted_text = "\n".join(str(v or "") for _k, v in sorted((content_by_page or {}).items()))
            file_meta = parse_textbook_filename_metadata(file_path)
            section_code = str(file_meta.get("section_code", "") or "unknown").replace(" ", "")
            volume = str(curriculum_info.get("volume", "") or "unknown").replace(" ", "")
            sc_for_scan = None if section_code == "unknown" else section_code
            inventory_items = scan_docx_title_inventory(extracted_text, section_code=sc_for_scan)
            expected_titles = sorted({str(it.get("canonical_title", "")).strip() for it in inventory_items if it.get("canonical_title")})
            returned_titles = collect_returned_titles_from_parsed_data(parsed_data)
            inv = build_title_inventory(
                expected_titles,
                returned_titles,
                section_code=section_code,
                inventory_items=inventory_items,
            )
            allow_partial_import = bool(import_policy.get("allow_partial_import", False))
            write_aborted = False
            report_name = f"{volume}_{section_code}_title_inventory_report.md"
            report_path = os.path.join("reports", "import_debug", report_name)
            volume_raw = str(curriculum_info.get("volume", "") or "")
            curriculum_raw = str(curriculum_info.get("curriculum", "") or "")
            publisher_raw = str(parse_textbook_filename_metadata(file_path).get("publisher", "") or "")
            warn = detect_curriculum_volume_warning(curriculum_raw, volume_raw, publisher_raw)
            if warn:
                current_app.logger.warning(warn)
                if queue is not None:
                    queue.put(f"WARN: {warn}")
            write_title_inventory_report(
                report_path,
                volume=volume,
                section=section_code,
                allow_partial_import=allow_partial_import,
                write_aborted=write_aborted,
                inv=inv,
                warning=warn,
            )
            current_app.logger.info("[IMPORT INVENTORY GUARD] report_only=true")
            current_app.logger.info(f"[IMPORT INVENTORY GUARD] expected_titles_count={inv.get('expected_titles_count', 0)}")
            current_app.logger.info(f"[IMPORT INVENTORY GUARD] returned_titles_count={inv.get('returned_titles_count', 0)}")
            current_app.logger.info(f"[IMPORT INVENTORY GUARD] missing_titles_count={inv.get('missing_titles_count', 0)}")
            current_app.logger.info(f"[IMPORT INVENTORY GUARD] allow_partial_import={str(allow_partial_import).lower()}")
            if queue is not None:
                queue.put("INFO: [IMPORT INVENTORY GUARD] report_only=true")
                queue.put(f"INFO: [IMPORT INVENTORY GUARD] expected_titles_count={inv.get('expected_titles_count', 0)}")
                queue.put(f"INFO: [IMPORT INVENTORY GUARD] returned_titles_count={inv.get('returned_titles_count', 0)}")
                queue.put(f"INFO: [IMPORT INVENTORY GUARD] missing_titles_count={inv.get('missing_titles_count', 0)}")
                queue.put(f"INFO: [IMPORT INVENTORY GUARD] report_path={report_path}")

        result = save_to_database(
            parsed_data,
            curriculum_info,
            queue,
            source_file_path=file_path,
            content_by_page=content_by_page,
            outline_only=outline_only,
            import_policy=import_policy,
            optional_enrich_pdf_path=optional_enrich_pdf_path,
        )
        try:
            temp_dir = (_DOCX_IMPORT_CONTEXT or {}).get("temp_media_dir")
            if temp_dir and bool(current_app.config.get("CLEAN_ORPHAN_DOCX_MEDIA", True)):
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
                current_app.logger.info(f"[DOCX MEDIA CLEANUP] removed orphan temp dir={temp_dir}")
        except Exception:
            pass

        skills_count = result.get('skills_processed', 0)
        curriculums_count = result.get('curriculums_added', 0)
        examples_count = result.get('examples_added', 0)
        practice_count = result.get('practice_questions_imported', 0)
        in_class_practice_count = result.get('in_class_practices_imported', 0)
        chapter_exercises_count = result.get('chapter_exercises_imported', 0)
        self_assessments_count = result.get('self_assessments_imported', 0)
        exam_practices_count = result.get('exam_practices_imported', 0)
        other_practices_count = result.get('other_practices_imported', 0)
        practice_needs_review_count = result.get('practice_questions_needs_review', 0)
        practice_skipped_count = result.get('duplicates_skipped', result.get('practice_questions_skipped', 0))
        processed_skill_ids = result.get('processed_skill_ids', [])

        message = (
            f"Import complete: skills={skills_count}, curriculums={curriculums_count}, "
            f"examples={examples_count}, practices={practice_count}, in_class={in_class_practice_count}, "
            f"chapter_exercises={chapter_exercises_count}, self_assessment={self_assessments_count}, "
            f"exam={exam_practices_count}, other={other_practices_count}, "
            f"needs_review={practice_needs_review_count}, skipped={practice_skipped_count}"
        )
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")

        # 甇仿? 5: ?芸????粹?蝔?蝣?(?舫)
        code_gen_status = "skipped"
        if skip_code_gen:
            message = "Skip code generation by request."
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")
        elif processed_skill_ids:
            queue.put(f"INFO: start code generation for {len(processed_skill_ids)} skills")
            for idx, skill_id in enumerate(processed_skill_ids):
                queue.put(f"INFO: [{idx+1}/{len(processed_skill_ids)}] 甇??? {skill_id}.py ...")
                try:
                    # [靽格迤] ???啣?亦???踝?撘瑕?瑁? Architect ????啁? Prompt
                    success, msg = auto_generate_skill_code(skill_id, queue, force_architect_refresh=True)
                    if success:
                        queue.put(f"INFO: {skill_id} code generated")
                    else:
                        queue.put(f"WARN: {skill_id} code generation failed")
                except Exception as e:
                    queue.put(f"ERROR: ?? {skill_id} ?????航炊: {e}")
                    current_app.logger.error(f"Generate Error {skill_id}: {e}")
                
                time.sleep(2) # Rate Limit
            code_gen_status = f"{len(processed_skill_ids)} generated"

        return {
            "status": "success", 
            "message": (f"隤脫????交???\n"
                        f"?啣?/?湔??? {skills_count} ?n"
                        f"?啣?隤脩?蝬梯?: {curriculums_count} 蝑n"
                        f"?啣?隤脫靘?: {examples_count} 蝑n"
                        f"?啣?蝺渡?憿? {practice_count} 蝑n"
                        f"?典?蝺渡?: {in_class_practice_count} 蝑n"
                        f"蝺渡?憿?銴: {practice_needs_review_count} 蝑n"
                        f"蝺渡?憿?? {practice_skipped_count} 蝑n"
                        f"?芸???蝔?蝣? {code_gen_status}")
        }

    except Exception as e:
        current_app.logger.error(f"??隤脫?????隤? {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"??憭望?: {str(e)}"}

# --- ???詨捆???---
process_textbook_pdf = process_textbook_file

def extract_content_from_file(file_path, queue, max_pages=None, import_policy=None):
    """Extract text content from PDF or Word files."""
    message = f"甇?敺?{file_path} ???批捆..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    global _DOCX_IMPORT_CONTEXT
    _DOCX_IMPORT_CONTEXT = {}
    content_by_page = {}
    import_policy = dict(import_policy or {})
    
    try:
        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            # --- PDF ???摩 (蝬剜??見) ---
            import fitz  # PyMuPDF
            from PIL import Image
            import pytesseract
            
            # Wand ?臭??虜閬?蝻箏仃憟辣嚗?亥???
            try:
                from wand.image import Image as WandImage
            except ImportError:
                WandImage = None

            ocr_import_error_logged = False
            tesseract_not_found_error_logged = False
            doc = fitz.open(file_path)
            for i, page in enumerate(doc.pages()):
                if max_pages and i >= max_pages:
                    break
                page_text = page.get_text("text")

                # ?菜葫憭批?擃?憿?
                blocks = page.get_text("blocks")
                large_font_texts = []
                large_font_threshold = 20
                for b in blocks:
                    try:
                        text = b[4]
                        first_line = page.get_text("dict", clip=b[:4])['blocks'][0]['lines'][0]
                        font_size = first_line['spans'][0]['size']
                        if font_size > large_font_threshold:
                            large_font_texts.append(text.strip())
                    except (IndexError, KeyError):
                        continue
                for large_text in large_font_texts:
                    if large_text and large_text not in page_text:
                        page_text = large_text + "\n" + page_text

                # OCR ??
                try:
                    from pytesseract import TesseractNotFoundError

                    tesseract_path = current_app.config.get('TESSERACT_CMD')
                    if tesseract_path:
                        pytesseract.pytesseract.tesseract_cmd = tesseract_path

                    pix = page.get_pixmap()
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_text = pytesseract.image_to_string(img, lang='chi_tra')
                    page_text += "\nOCR Extracted: " + ocr_text.strip()
                except ImportError:
                    if not ocr_import_error_logged:
                        message = "OCR dependencies missing: pytesseract/Pillow"
                        current_app.logger.warning(message)
                        queue.put(f"WARN: {message}")
                        ocr_import_error_logged = True
                except TesseractNotFoundError:
                    if not tesseract_not_found_error_logged:
                        message = "Tesseract-OCR not found"
                        current_app.logger.error(message)
                        queue.put(f"ERROR: {message}")
                        tesseract_not_found_error_logged = True
                except Exception as ocr_e:
                    current_app.logger.warning(f"??{i+1} OCR ????隤? {ocr_e}")

                content_by_page[i + 1] = page_text
            doc.close()

        elif file_extension in ['.docx', '.doc']:
            docx_formula_source_mode = str(import_policy.get("docx_formula_source_mode", "auto_detect") or "auto_detect").strip()
            if docx_formula_source_mode == "converted_docx_latex":
                content_by_page, doc_meta = extract_converted_latex_docx(file_path)
                extracted_text = str((content_by_page or {}).get(1, "") or "")
                detect_meta = detect_converted_latex_docx(extracted_text)
                _DOCX_IMPORT_CONTEXT = {
                    "docx_formula_source_mode": docx_formula_source_mode,
                    "is_converted_latex_docx": True,
                    "latex_signal_count": int(detect_meta.get("latex_signal_count", 0)),
                    "formula_placeholder_count": int(detect_meta.get("formula_placeholder_count", 0)),
                    "question_assets": {},
                    "question_formula_blocks": {},
                    "formula_assets_extraction_skipped": True,
                    "ocr_skipped": True,
                    "pix2tex_skipped": True,
                    "doc_meta": doc_meta,
                }
                queue.put("INFO: docx_formula_source_mode=converted_docx_latex")
                queue.put("INFO: formula_assets_extraction_skipped=true")
                queue.put("INFO: ocr_skipped=true")
                queue.put("INFO: pix2tex_skipped=true")
                queue.put(f"INFO: is_converted_latex_docx={True}")
                queue.put(f"INFO: latex_signal_count={detect_meta.get('latex_signal_count', 0)}")
                queue.put(f"INFO: formula_placeholder_count={detect_meta.get('formula_placeholder_count', 0)}")
                return content_by_page
            # --- Word (.docx) ???摩 ---
            message = "Start extracting Word (.docx) content"
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")

            try:
                from docx import Document
                from docx.table import Table
                from docx.text.paragraph import Paragraph
                try:
                    import pypandoc
                except ImportError:
                    pypandoc = None

                doc = Document(file_path)
                job_id = uuid.uuid4().hex[:12]
                media_rel_root = os.path.join("uploads", "tmp_docx_media", job_id)
                media_abs_root = os.path.join(current_app.root_path, media_rel_root)
                media_leaf_rel = os.path.join(media_rel_root, "media")
                media_leaf_abs = os.path.join(current_app.root_path, media_leaf_rel)
                os.makedirs(media_leaf_abs, exist_ok=True)
                if pypandoc is not None:
                    try:
                        pypandoc.convert_file(
                            file_path,
                            'markdown',
                            extra_args=['--wrap=none', f'--extract-media={media_abs_root}']
                        )
                    except Exception:
                        pass
                rel_map = build_docx_media_relationship_map(file_path, media_leaf_rel)
                text_chunks = []
                ordered_blocks = []
                paragraphs_count = 0
                equations_count = 0
                equation_failures = 0
                formula_image_count = 0

                for idx, block in enumerate(doc.element.body.iterchildren()):
                    if block.tag.endswith('}p'):
                        para = Paragraph(block, doc)
                        paragraphs_count += 1
                        ptxt = extract_docx_paragraph_with_equations(para)
                        meta = getattr(para, "_math_meta", {}) or {}
                        equations_count += int(meta.get("equations", 0) or 0)
                        equation_failures += int(meta.get("equation_failures", 0) or 0)
                        formula_image_count += int(meta.get("formula_image_count", 0) or 0)
                        if int(meta.get("equations", 0) or 0) > 0:
                            current_app.logger.info(f"[DOCX EQUATION] detected type=omml paragraph_index={idx}")
                        if int(meta.get("equation_failures", 0) or 0) > 0:
                            current_app.logger.warning(
                                f"[DOCX EQUATION WARNING] conversion failed paragraph_index={idx}"
                            )
                        para_has_formula_placeholder = bool(
                            re.search(r"\[FORMULA_IMAGE_\d+\]", ptxt or "")
                        )
                        if ptxt:
                            text_chunks.append(ptxt)
                            ordered_blocks.append({"type": "paragraph", "text": ptxt, "block_index": len(ordered_blocks) + 1})
                        for rid in extract_docx_image_rids_from_paragraph(para):
                            info = rel_map.get(rid, {})
                            ordered_blocks.append(
                                {
                                    "type": "image",
                                    "rid": rid,
                                    "path": info.get("extracted_path"),
                                    "content_type": info.get("content_type", "application/octet-stream"),
                                    "target_ref": info.get("target_ref"),
                                    "block_index": len(ordered_blocks) + 1,
                                    # Flag: this image is the OLE/VML preview for a formula
                                    # placeholder produced in the same paragraph.
                                    "is_formula_placeholder_source": para_has_formula_placeholder,
                                }
                            )
                    elif block.tag.endswith('}tbl'):
                        table = Table(block, doc)
                        ttxt = extract_docx_table_with_equations(table)
                        if ttxt:
                            text_chunks.append(ttxt)
                            ordered_blocks.append({"type": "paragraph", "text": ttxt, "block_index": len(ordered_blocks) + 1})

                cleaned_chunks = []
                for chunk in text_chunks:
                    c = str(chunk or "")
                    c_wo = re.sub(r"\[FORMULA_IMAGE_\d+\]", "", c).strip()
                    if not c_wo:
                        continue
                    cleaned_chunks.append(c)
                extracted_text = "\n".join(cleaned_chunks).strip()
                detect_meta = detect_converted_latex_docx(extracted_text)
                q_assets, orphan_images = attach_docx_media_to_question_blocks(ordered_blocks)
                formula_blocks = build_docx_question_formula_context(ordered_blocks)
                for o in orphan_images:
                    current_app.logger.warning(f"[DOCX IMAGE WARNING] orphan image ignored path={o.get('path')}")
                _DOCX_IMPORT_CONTEXT = {
                    "media_rel_map": rel_map,
                    "ordered_blocks": ordered_blocks,
                    "question_assets": q_assets,
                    "question_formula_blocks": formula_blocks,
                    "orphan_images": orphan_images,
                    "temp_media_dir": media_abs_root,
                    "docx_formula_source_mode": docx_formula_source_mode,
                    "is_converted_latex_docx": bool(detect_meta.get("is_converted_latex_docx", False)),
                    "latex_signal_count": int(detect_meta.get("latex_signal_count", 0)),
                    "formula_placeholder_count": int(detect_meta.get("formula_placeholder_count", 0)),
                    "formula_assets_extraction_skipped": False,
                    "ocr_skipped": False,
                    "pix2tex_skipped": False,
                }

                if formula_image_count > 0:
                    current_app.logger.info(f"[DOCX EQUATION IMAGE] saved path=[FORMULA_IMAGE_*] count={formula_image_count}")
                current_app.logger.info(
                    f"[DOCX IMPORT] paragraphs={paragraphs_count} equations={equations_count} equation_failures={equation_failures}"
                )
                content_by_page[1] = extracted_text


            except (OSError, RuntimeError) as e:
                error_str = str(e)
                # ????瑼???摰摮??摰隤方???(Exit Code 63)
                if 'exitcode "63"' in error_str or 'Did not find end of central directory' in error_str:
                    warn_msg = "WARN: DOCX file may be corrupted (Pandoc Exit 63)"
                    current_app.logger.warning(warn_msg)
                    queue.put(warn_msg)
                    return {}
                
                error_msg = f"Pandoc processing failed: {e}"
                current_app.logger.error(error_msg)
                queue.put(f"ERROR: {error_msg}")

        else:
            message = f"Unsupported file type: {file_extension}. Please use .pdf or .docx."
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {}

        message = f"Extracted {len(content_by_page)} page(s) from {file_extension}."
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")
        return content_by_page

    except Exception as e:
        message = f"??瑼??批捆???隤?(Exception): {e}"
        current_app.logger.error(message)
        import traceback
        traceback.print_exc()
        queue.put(f"ERROR: {message}")
        return {}

def _sanitize_and_parse_json(s: str, queue=None):
    """Sanitize and parse AI JSON response text."""
    if not s:
        return None, "", s, []

    original = s
    
    # ===== 蝚?0 甇伐?????憪???閰喟敦鞈? =====
    current_app.logger.debug(f"[JSON_DEBUG] ?????瑕漲: {len(s)} 摮泵")
    
    # ===== 蝚?1 甇伐?蝘駁 code fence wrapper =====
    s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s, flags=re.MULTILINE).strip()
    
    # ===== 蝚?2 甇伐?蝘駁??蝭??批摮? =====
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    
    # ===== 蝚?3 甇伐????航??BOM =====
    if s.startswith('\ufeff'): s = s[1:]
    
    # ===== 蝚?4 甇伐??岫憭車??蝺耨敺拍???=====
    candidates = []
    
    # 蝑 0: ??嚗?蝘駁 control chars / fences嚗?
    candidates.append(("raw", s))
    
    # 蝑 1: 靽???escape - ?芸?敺銝?? JSON escape ???? escape
    escaped_conservative = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    candidates.append(("靽? escape", escaped_conservative))
    
    # 蝑 2: 瞈??escape - ??迨蝡????賡???
    escaped_aggressive = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', s)
    candidates.append(("瞈??escape", escaped_aggressive))
    
    # 蝑 3: ?敺?摨?- ??????賡???
    escaped_brutal = s.replace('\\', '\\\\')
    candidates.append(("?游? escape", escaped_brutal))
    
    # 蝑 4: ?岫?曉蝚砌???{ ??敺???} ??銝?
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        substr = s[first_brace:last_brace + 1]
        candidates.append(("?? {} 摮葡", substr))
        candidates.append(("?? {} 摮葡 + 靽? escape", re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', substr)))

    attempts = []
    for strategy_name, cand in candidates:
        try:
            obj = json.loads(cand)
            current_app.logger.info(f"[JSON_SUCCESS] 雿輻蝑 '{strategy_name}' ??閫?? JSON")
            return obj, cand, original, attempts
        except json.JSONDecodeError as e:
            snippet = (cand[:200] + '...') if len(cand) > 200 else cand
            error_detail = f"{e.msg} at line {e.lineno}, col {e.colno}"
            attempts.append((strategy_name, snippet, error_detail))
            current_app.logger.debug(f"[JSON_FAIL] 蝑 '{strategy_name}' 憭望?: {error_detail}")

    if queue is not None:
        queue.put(f"ERROR: JSON 閫??憭望?嚗?閰?{len(attempts)} 蝔桃??伐?嚗底閬撩??亥?")
    
    if candidates:
        return None, candidates[-1][1], original, [(s, e, d) for s, _, (_, _, d) in zip([c[0] for c in candidates], [], attempts)]
    else:
        return None, "", original, attempts


def _call_gemini_with_retry(model, analysis_prompt, queue=None, context_message='AI ??', parse_json=False):
    max_retries = 3
    retry_delay = 2

    def _validate_json_completeness(text):
        cleaned_text = re.sub(r'^```(?:json)?\s*|\s*```$', '', str(text or ''), flags=re.MULTILINE).strip()
        if not cleaned_text.startswith("{"):
            return False, "missing_opening_brace", cleaned_text
        if not cleaned_text.endswith("}"):
            return False, "missing_closing_brace", cleaned_text
        if re.search(r'\]\s*\}\s*$', cleaned_text, flags=re.DOTALL) is None:
            return False, "missing_json_tail", cleaned_text
        fixed_text = sanitize_gemini_json_text(cleaned_text)
        try:
            json.loads(cleaned_text)
            if fixed_text != cleaned_text:
                json.loads(fixed_text)
                current_app.logger.info("[TEXTBOOK IMPORTER] Gemini JSON parsed after LaTeX escape sanitize.")
                return True, "ok_sanitized", fixed_text
            return True, "ok", cleaned_text
        except json.JSONDecodeError as first_error:
            current_app.logger.debug(
                "[TEXTBOOK IMPORTER] Gemini first json.loads failed at "
                f"line {first_error.lineno}, col {first_error.colno}, pos {first_error.pos}: "
                f"{first_error.msg}"
            )
            try:
                json.loads(fixed_text)
                current_app.logger.info("[TEXTBOOK IMPORTER] Gemini JSON parsed after LaTeX escape sanitize.")
                return True, "ok_sanitized", fixed_text
            except json.JSONDecodeError as second_error:
                _log_gemini_json_parse_failed_after_sanitize(first_error, second_error, cleaned_text)
                return False, "json_decode_failed", cleaned_text

    for attempt in range(1, max_retries + 1):
        try:
            if not hasattr(model, "generate_content"):
                current_app.logger.error(f"[_call_gemini_with_retry] invalid model type: {type(model).__name__}")
                return None

            if queue is not None:
                queue.put(f"INFO: {context_message} attempt {attempt}/{max_retries}")

            generation_config = {
                "temperature": 0.2,
                "max_output_tokens": 65536,
            }
            if parse_json:
                generation_config["response_mime_type"] = "application/json"

            response = model.generate_content(
                analysis_prompt,
                generation_config=generation_config,
            )

            raw_text = getattr(response, "text", "")
            result_text = str(raw_text or "").strip()
            if result_text:
                current_app.logger.info(f"Gemini response length = {len(result_text)}")
                current_app.logger.info(f"first 300 chars = {result_text[:300]}")
                current_app.logger.info(f"last 300 chars = {result_text[-300:]}")
                if parse_json:
                    is_valid_json, fail_reason, _ = _validate_json_completeness(result_text)
                    if is_valid_json:
                        return result_text
                    if queue is not None and fail_reason == "missing_closing_brace":
                        queue.put("WARNING: Gemini JSON missing closing brace")
                    if queue is not None:
                        queue.put("WARNING: Gemini JSON validation failed, retrying")
                    if attempt >= max_retries:
                        raise RuntimeError("Gemini JSON failed after retries")
                    time.sleep(retry_delay * attempt)
                    continue
                return result_text

            candidates = getattr(response, "candidates", None)
            if candidates:
                parts = []
                for cand in candidates:
                    content = getattr(cand, "content", None)
                    if not content:
                        continue
                    for p in getattr(content, "parts", []) or []:
                        t = getattr(p, "text", None)
                        if t:
                            parts.append(t)
                merged = "\n".join(parts).strip()
                if merged:
                    current_app.logger.info(f"Gemini response length = {len(merged)}")
                    current_app.logger.info(f"first 300 chars = {merged[:300]}")
                    current_app.logger.info(f"last 300 chars = {merged[-300:]}")
                    if parse_json:
                        is_valid_json, fail_reason, _ = _validate_json_completeness(merged)
                        if is_valid_json:
                            return merged
                        if queue is not None and fail_reason == "missing_closing_brace":
                            queue.put("WARNING: Gemini JSON missing closing brace")
                        if queue is not None:
                            queue.put("WARNING: Gemini JSON retry")
                        if attempt >= max_retries:
                            raise RuntimeError("Gemini JSON failed after retries")
                        time.sleep(retry_delay * attempt)
                        continue
                    return merged

            raise RuntimeError("Gemini output merge failed")

        except ResourceExhausted as e:
            if attempt >= max_retries:
                err_type = type(e).__name__
                err_msg = str(e) or repr(e)
                tb = traceback.format_exc()
                current_app.logger.error(f"_call_gemini_with_retry ?潛??航炊: [{err_type}] {err_msg}\n{tb}")
                if queue is not None:
                    queue.put(f"ERROR: Gemini ?澆憭望?: [{err_type}] {err_msg}")
                raise
            time.sleep(retry_delay * attempt)

        except Exception as e:
            err_type = type(e).__name__
            err_msg = str(e) or repr(e)
            tb = traceback.format_exc()

            current_app.logger.error(f"_call_gemini_with_retry ?潛??航炊: [{err_type}] {err_msg}\n{tb}")
            if queue is not None:
                queue.put(f"ERROR: Gemini ?澆憭望?: [{err_type}] {err_msg}")

            raise

def call_gemini_for_toc(content_by_page, curriculum_info, queue):
    """Call Gemini to extract chapter/section TOC."""
    message = "--- ?? AI ?桅?閫??瘚? ---"
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    prompt = "TOC extraction prompt"
    try:
        from core.ai_analyzer import get_model
        model = get_model()
        response = _call_gemini_with_retry(model, prompt + "\n" + content_by_page, queue=queue)
        return response
    except Exception as e:
        current_app.logger.error(f"call_gemini_for_toc failed: {e}")
        return None

def call_gemini_for_analysis(content_by_page, curriculum_info, queue, page_analysis_payload=None, import_policy=None):
    """Call Gemini to analyze extracted textbook content."""
    message = "--- ?? AI ??瘚? ---"
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    # ==========================
    # 1. ?葉摨瑁???Prompt (靽??見)
    # ==========================
    prompt_jh_kangxuan = "Analyze textbook content and return JSON."

    # ==========================
    # 2. ?桅?樴辰??Prompt (靽格迤???游之憿??蝭?)
    # ==========================
    prompt_sh_longteng = "Analyze textbook content and return JSON."

    # ==========================
    # 3. ???Prompt
    # ==========================

    prompt_generic = "Analyze textbook content and return JSON."


    prompt_vh_mathB4 = "Analyze textbook content and return JSON."

    curriculum = curriculum_info.get('curriculum', '').strip()
    publisher = curriculum_info.get('publisher', '').strip()
    volume = str(curriculum_info.get('volume', '')).strip()
    subject, vol_num = parse_volume(volume)
    is_vocational_mathb = curriculum == 'vocational' and subject == 'B'
    debug_message = (
        f"DEBUG: curriculum='{curriculum}', publisher='{publisher}', volume='{volume}', "
        f"parsed_subject='{subject}', parsed_volume={vol_num}"
    )
    current_app.logger.info(debug_message)
    queue.put(debug_message)

    if curriculum == 'junior_high' and publisher == 'kangxuan':
        base_prompt = prompt_jh_kangxuan
        queue.put("INFO: use junior_high kangxuan prompt")
    elif is_vocational_mathb:
        base_prompt = prompt_vh_mathB4
        queue.put(f"INFO: 撌脤??擃?詨飛{subject}{vol_num} 撠??璅∪?")
    elif curriculum == 'sh_longteng' or (curriculum == 'general' and publisher == 'longteng'):
        base_prompt = prompt_sh_longteng
        queue.put("INFO: use longteng/general prompt")
    else:
        base_prompt = prompt_generic
        queue.put("INFO: use generic prompt")

    try:
        model = get_model("architect")
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e) or repr(e)
        tb = traceback.format_exc()

        current_app.logger.error(f"AI ??憭望?: [{err_type}] {err_msg}\n{tb}")
        if "Gemini API Key" in err_msg or "API_KEY" in err_msg:
            queue.put("ERROR: Missing Gemini API Key.")
        else:
            queue.put(f"ERROR: AI ??憭望?: [{err_type}] {err_msg}")
        return None
    if page_analysis_payload:
        blocks = []
        for k in sorted(page_analysis_payload.keys(), key=lambda x: int(x)):
            p = page_analysis_payload[k]
            block = (
                f"--- Page {k} ---\n"
                f"[RAW PDF TEXT]\n{p.get('raw_text','')}\n\n"
                f"[NORMALIZED TEXT]\n{p.get('normalized_text','')}\n\n"
                f"[VISION OCR TEXT]\n{p.get('vision_ocr_text') or ''}\n\n"
                f"[FORMULA WARNINGS]\n{', '.join(p.get('formula_warnings', [])) or 'none'}\n"
            )
            blocks.append(block)
        full_content = "\n".join(blocks)
    else:
        full_content = "\n".join([f"--- Page {k} ---\n{v}" for k, v in content_by_page.items()])
    
    json_example = "{}"
    if is_vocational_mathb:
        json_example = "{}"

    import_policy = dict(import_policy or {})
    docx_formula_source_mode = str(import_policy.get("docx_formula_source_mode", "auto_detect") or "auto_detect").strip()
    converted_latex_prompt_rules = ""
    if docx_formula_source_mode == "converted_docx_latex":
        converted_latex_prompt_rules = "converted_docx_latex rules enabled"

    # 動態組裝：必須帶入 base_prompt、JSON 範例、LaTeX 規則與全文，避免僅送死字串造成幻覺目錄
    analysis_prompt = (
        f"{base_prompt}\n\n"
        f"【請嚴格依照以下 JSON 範例格式結構輸出，嚴禁自行發明論文或無關的目錄結構】\n"
        f"{json_example}\n\n"
        f"{converted_latex_prompt_rules}\n\n"
        f"【以下是需要您切分、LaTeX化並結構化解析的課本標準文本內容】\n"
        f"{full_content}"
    )

    try:
        ai_response = _call_gemini_with_retry(
            model, 
            analysis_prompt, 
            queue, 
            context_message="??隤脫蝯???",
            parse_json=True
        )
        return ai_response
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e) or repr(e)
        tb = traceback.format_exc()

        current_app.logger.error(f"AI ??憭望?: [{err_type}] {err_msg}\n{tb}")
        queue.put(f"ERROR: AI ??憭望?: [{err_type}] {err_msg}")
        return None

def parse_ai_response(ai_data_or_string, queue):
    """Parse AI response payload into dict."""
    if isinstance(ai_data_or_string, dict):
        return ai_data_or_string
    text = str(ai_data_or_string or "").strip()
    if not text:
        return None
    try:
        return safe_load_gemini_json(text)
    except Exception:
        if queue is not None:
            queue.put("ERROR: parse_ai_response failed")
        return None


def snake_to_pascal_case(snake_case_string):
    """Convert snake_case or kebab-case to PascalCase."""
    if not snake_case_string:
        return ""
    return ''.join(word.capitalize() for word in re.split('_|-', str(snake_case_string)))

def clean_skill_en_name(raw_en_name, queue=None):
    """Clean skill english name and keep PascalCase suffix if present."""
    if not raw_en_name:
        return ""
    match = re.search(r'[A-Z]', raw_en_name)
    if match:
        start_index = match.start()
        return raw_en_name[start_index:]
    return raw_en_name


def _formula_context_label(path):
    return " / ".join(str(p) for p in path if p is not None and str(p).strip())


def _normalize_extracted_content_math(content_by_page, queue=None, docx_formula_source_mode: str = ""):
    """Normalize extracted page text before Gemini sees OCR/PDF math artifacts."""
    if not isinstance(content_by_page, dict):
        return content_by_page

    normalized_pages = {}
    for page_no, page_text in content_by_page.items():
        if not isinstance(page_text, str):
            normalized_pages[page_no] = page_text
            continue

        if docx_formula_source_mode == "converted_docx_latex":
            normalized_pages[page_no] = page_text
            continue
        check = detect_suspicious_formula(page_text)
        normalized_text = normalize_math_text(page_text)
        if check.get("is_suspicious"):
            reasons = ",".join(check.get("reasons", []))
            log_msg = f"[FORMULA CHECK] suspicious formula detected in extracted page={page_no} reasons={reasons}"
            current_app.logger.warning(log_msg)
            if queue is not None:
                queue.put(f"WARN: {log_msg}")

        if normalized_text != page_text:
            current_app.logger.info(
                f"[FORMULA NORMALIZE] extracted_page={page_no} before={page_text[:120]!r} after={normalized_text[:120]!r}"
            )

        normalized_pages[page_no] = normalized_text

    return normalized_pages


def score_extracted_page_quality(page_text: str) -> dict:
    text = str(page_text or "")
    length = len(text.strip())
    weird = len(re.findall(r"[嚙賤?領?歹蕭]", text))
    symbols = len(re.findall(r"[#嚗?]{2,}", text))
    score = 1.0
    if length < 40:
        score -= 0.35
    if weird > 0:
        score -= min(0.35, weird * 0.03)
    if symbols > 0:
        score -= min(0.25, symbols * 0.05)
    score = max(0.0, min(1.0, score))
    return {
        "score": score,
        "is_low_quality": score < 0.60,
        "length": length,
        "weird_char_count": weird,
        "artifact_symbol_count": symbols,
    }


def _render_page_image_temp(pdf_path: str, page_no_1based: int) -> str | None:
    try:
        import fitz
    except Exception:
        return None
    try:
        tmp_dir = os.path.join("reports", "tmp_vision_ocr")
        os.makedirs(tmp_dir, exist_ok=True)
        out = os.path.join(tmp_dir, f"page_{int(page_no_1based):04d}.png")
        doc = fitz.open(pdf_path)
        try:
            page = doc.load_page(int(page_no_1based) - 1)
            pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), alpha=False)
            pix.save(out)
        finally:
            doc.close()
        return out
    except Exception:
        return None


def _vision_ocr_page_text(pdf_path: str, page_no_1based: int, queue=None) -> str | None:
    image_path = _render_page_image_temp(pdf_path, page_no_1based)
    if not image_path:
        return None
    try:
        from PIL import Image
    except Exception:
        return None
    try:
        model = get_model("vision_analyzer")
        prompt = "Extract text from this textbook page image and return plain text."
        img = Image.open(image_path)
        resp = model.generate_content([prompt, img], generation_config={"temperature": 0.0, "max_output_tokens": 65536})
        text = str(getattr(resp, "text", "") or "").strip()
        if text:
            return text
    except Exception as e:
        if queue is not None:
            queue.put(f"WARN: Vision OCR failed on page {page_no_1based}: {e}")
    return None


def _build_page_analysis_payload(raw_pages, normalized_pages, file_path, queue=None):
    payload = {}
    enable_vision = bool(current_app.config.get("ENABLE_VISION_OCR_FALLBACK", False))
    is_pdf = str(file_path or "").lower().endswith(".pdf")
    for page_no, normalized_text in (normalized_pages or {}).items():
        raw_text = (raw_pages or {}).get(page_no, normalized_text)
        formula_check = detect_suspicious_formula(raw_text)
        quality = score_extracted_page_quality(raw_text)
        reasons = set(formula_check.get("reasons", []))
        low_quality = bool(quality.get("is_low_quality"))
        if "suspicious_factorial" in reasons or "suspicious_pdf_artifact" in reasons:
            low_quality = True
        vision_text = None
        needs_review = False
        if low_quality and enable_vision and is_pdf:
            vision_text = _vision_ocr_page_text(file_path, int(page_no), queue=queue)
            if not vision_text:
                needs_review = True
        elif low_quality:
            needs_review = True
        payload[page_no] = {
            "raw_text": raw_text,
            "normalized_text": normalized_text,
            "vision_ocr_text": vision_text,
            "formula_warnings": list(reasons),
            "quality": quality,
            "is_low_quality": low_quality,
            "needs_review": needs_review,
        }
    return payload


def _normalize_imported_math_value(
    value,
    *,
    section_title="",
    source_description="",
    field_name="",
    queue=None,
    docx_formula_source_mode: str = "",
):
    if value is None or not isinstance(value, str):
        return value, None

    suspicious = detect_suspicious_formula(value)
    if docx_formula_source_mode == "converted_docx_latex":
        if has_app_context():
            current_app.logger.info(
                f"[FORMULA NORMALIZE SKIP] converted_docx_latex_preserve_latex=true field={field_name}"
            )
        return value, {
            "is_suspicious": bool(suspicious.get("reasons")),
            "reasons": list(dict.fromkeys(suspicious.get("reasons", []))),
            "suggestions": suspicious.get("suggestions", []),
            "normalized_preview": value,
        }

    normalized = normalize_math_text(value)
    suspicious_after = detect_suspicious_formula(normalized)
    reasons = list(dict.fromkeys(suspicious.get("reasons", []) + suspicious_after.get("reasons", [])))

    if reasons:
        label = _formula_context_label([section_title, source_description, field_name])
        log_msg = f"[FORMULA CHECK] suspicious formula detected in {label} reasons={reasons}"
        current_app.logger.warning(log_msg)
        if queue is not None:
            queue.put(f"WARN: {log_msg}")

    if normalized != value:
        current_app.logger.info(
            f"[FORMULA NORMALIZE] field={field_name} before={value[:120]!r} after={normalized[:120]!r}"
        )

    return normalized, {
        "is_suspicious": bool(reasons),
        "reasons": reasons,
        "suggestions": suspicious.get("suggestions", []) + suspicious_after.get("suggestions", []),
        "normalized_preview": normalized,
    }


def _normalize_parsed_textbook_math(parsed_data, queue=None, docx_formula_source_mode: str = ""):
    """Normalize known textbook JSON text fields before DB persistence."""
    if not isinstance(parsed_data, dict):
        return parsed_data

    for chapter in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections", []) or []:
            if not isinstance(section, dict):
                continue
            section_title = section.get("section_title", "")
            for concept in section.get("concepts", []) or []:
                if not isinstance(concept, dict):
                    continue

                for key in ("concept_description", "concept_paragraph"):
                    if isinstance(concept.get(key), str):
                        concept[key], check = _normalize_imported_math_value(
                            concept[key],
                            section_title=section_title,
                            source_description=concept.get("concept_name", ""),
                            field_name=key,
                            queue=queue,
                            docx_formula_source_mode=docx_formula_source_mode,
                        )
                        if check and check.get("is_suspicious"):
                            concept["needs_review"] = True
                            concept["parse_warning"] = ";".join(check.get("reasons", []))

                for ex in concept.get("examples", []) or []:
                    if not isinstance(ex, dict):
                        continue
                    source_description = ex.get("source_description", "example")
                    for key in (
                        "problem_text",
                        "problem",
                        "correct_answer",
                        "answer",
                        "detailed_solution",
                        "solution",
                        "hint",
                        "hints",
                    ):
                        if isinstance(ex.get(key), str):
                            ex[key], check = _normalize_imported_math_value(
                                ex[key],
                                section_title=section_title,
                                source_description=source_description,
                                field_name=key,
                                queue=queue,
                                docx_formula_source_mode=docx_formula_source_mode,
                            )
                            if check and check.get("is_suspicious"):
                                ex["needs_review"] = True
                                existing_warning = str(ex.get("parse_warning", "") or "").strip()
                                reasons = ";".join(check.get("reasons", []))
                                ex["parse_warning"] = ";".join(filter(None, [existing_warning, reasons]))
                    for sq in ex.get("sub_questions", []) or []:
                        if not isinstance(sq, dict):
                            continue
                        for key in ("problem", "answer", "solution"):
                            if isinstance(sq.get(key), str):
                                sq[key], _ = _normalize_imported_math_value(
                                    sq[key],
                                    section_title=section_title,
                                    source_description=source_description,
                                    field_name=f"sub_questions.{key}",
                                    queue=queue,
                                    docx_formula_source_mode=docx_formula_source_mode,
                                )

                for practice in concept.get("practice_questions", []) or []:
                    if not isinstance(practice, dict):
                        continue
                    for key in ("question", "problem_text", "solution", "answer", "hint", "hints"):
                        if isinstance(practice.get(key), str):
                            practice[key], check = _normalize_imported_math_value(
                                practice[key],
                                section_title=section_title,
                                source_description="practice",
                                field_name=key,
                                queue=queue,
                                docx_formula_source_mode=docx_formula_source_mode,
                            )
                            if check and check.get("is_suspicious"):
                                practice["needs_review"] = True
                                practice["parse_warning"] = ";".join(check.get("reasons", []))
                    for sq in practice.get("sub_questions", []) or []:
                        if not isinstance(sq, dict):
                            continue
                        for key in ("problem", "answer", "solution"):
                            if isinstance(sq.get(key), str):
                                sq[key], _ = _normalize_imported_math_value(
                                    sq[key],
                                    section_title=section_title,
                                    source_description="practice",
                                    field_name=f"sub_questions.{key}",
                                    queue=queue,
                                    docx_formula_source_mode=docx_formula_source_mode,
                                )

    return parsed_data


def _first_non_empty_str(mapping, keys):
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


ALLOWED_SOURCE_TYPES = {
    "textbook_example",
    "in_class_practice",
    "chapter_exercise",
    "basic_exercise",
    "advanced_exercise",
    "self_assessment",
    "exam_practice",
    "generated_question",
    "student_uploaded",
    "textbook_practice",
}

CHAPTER_EXERCISE_TYPES = {
    "chapter_exercise",
    "basic_exercise",
    "advanced_exercise",
}

_SUPERSCRIPT_TRANS = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻", "0123456789+-")
_SUBSCRIPT_TRANS = str.maketrans("₀₁₂₃₄₅₆₇₈₉₊₋", "0123456789+-")


def normalize_fill_blank_artifacts(text: str) -> tuple[str, dict]:
    original = str(text or "")
    out = original
    log = {"changed": False, "reasons": []}

    # Instruction semantic normalization first.
    before = out
    out = re.sub(r"(求|解|計算)\s*(?:\(\s*\)|_{2,})\s*", r"\1 ", out)
    if out != before:
        log["changed"] = True
        log["reasons"].append("normalized fill-blank instruction text")

    # Generic blank symbols/slots normalization.
    blank_patterns = [
        r"[?﹦＿]",
        r"\(\s*\)",
        r"_+",
        r"_{2,}",
    ]
    before = out
    for pat in blank_patterns:
        out = re.sub(pat, "[BLANK]", out)
    out = re.sub(r"(?:\s*\[BLANK\]\s*){2,}", " [BLANK] ", out)
    out = re.sub(r"\s+", " ", out).strip()
    if out != before:
        log["changed"] = True
        log["reasons"].append("normalized fill blank symbol to [BLANK]")

    return out, log


def _contains_perm_comb_formula(text: str) -> bool:
    t = str(text or "")
    return bool(
        re.search(
            r"(?:"
            r"\{\s*\}\s*\^\s*\{?\s*\d+\s*\}?\s*[PC]\s*_\s*\{?\s*\d+\s*\}?|"
            r"[PC]\s*\^\s*\{?\s*\d+\s*\}?\s*_\s*\{?\s*\d+\s*\}?|"
            r"[PC]\s*_\s*\{?\s*\d+\s*\}?\s*\^\s*\{?\s*\d+\s*\}?|"
            r"[?兜嗽笨喇?菊?猾?鉛+\s*[PC]\s*[??????????+|"
            r"[PC]\s*[??????????+\s*[?兜嗽笨喇?菊?猾?鉛+"
            r")",
            t,
        )
    )


def is_answer_blank_placeholder_context(raw_block: str, problem_text: str) -> bool:
    block = str(raw_block or "")
    text = str(problem_text or "")
    combined = f"{block}\n{text}"
    instruction_hit = bool(re.search(r"(求|解|計算|試求)", combined))
    formula_hit = _contains_perm_comb_formula(combined)
    placeholder_count = len(re.findall(r"\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]", block))
    subq_count = len(re.findall(r"\(\s*\d+\s*\)", combined))
    formula_with_placeholder = bool(
        re.search(
            r"(?:[PC].{0,24}(?:\[\s*FORMULA_IMAGE_\d+\]|\[\s*WORD_EQUATION_UNPARSED\])|"
            r"(?:\[\s*FORMULA_IMAGE_\d+\]|\[\s*WORD_EQUATION_UNPARSED\]).{0,24}[PC])",
            block,
        )
    )
    placeholder_close_to_subq = bool(subq_count and placeholder_count and abs(placeholder_count - subq_count) <= 1)
    return bool(instruction_hit and formula_hit and (formula_with_placeholder or placeholder_close_to_subq))


def normalize_permutation_combination_notation(
    text: str, *, volume: str = "", section_title: str = ""
) -> tuple[str, dict]:
    original = str(text or "")
    out = original
    log = {"changed": False, "reasons": []}
    coord_guard = _is_b1_coordinate_context(volume=volume, section_title=section_title, problem_text=original)
    if coord_guard:
        guarded = _normalize_coordinate_point_notation(out)
        if guarded != out:
            log["changed"] = True
            log["reasons"].append("normalized coordinate point notation in B1 coordinate context")
            out = guarded

    # e.g., ?感??/ ?嵩??
    def _replace_pre(match):
        n = match.group(1).translate(_SUPERSCRIPT_TRANS)
        op = match.group(2)
        r = match.group(3).translate(_SUBSCRIPT_TRANS)
        return f"{op}^{{{n}}}_{{{r}}}"

    out = re.sub(r"([?兜嗽笨喇?菊?猾?嫖?蒸+)\s*([PC])\s*([????????????+)", _replace_pre, out)

    # e.g., P? / C?
    def _replace_post(match):
        op = match.group(1)
        r = match.group(2).translate(_SUBSCRIPT_TRANS)
        n = match.group(3).translate(_SUPERSCRIPT_TRANS)
        return f"{op}^{{{n}}}_{{{r}}}"

    out = re.sub(r"([PC])\s*([????????????+)\s*([?兜嗽笨喇?菊?猾?嫖?蒸+)", _replace_post, out)

    # e.g., P^7_3 / C^7_3
    out = re.sub(r"\b([PC])\s*\^\s*\{?\s*([0-9]+)\s*\}?\s*_\s*\{?\s*([0-9]+)\s*\}?", r"\1^{\2}_{\3}", out)

    # e.g., P_3^7 / C_3^7
    out = re.sub(r"\b([PC])\s*_\s*\{?\s*([0-9]+)\s*\}?\s*\^\s*\{?\s*([0-9]+)\s*\}?", r"\1^{\3}_{\2}", out)

    # e.g., {}^{7}P_{3} / {}^7P_3 / { }^{7} P_{3}
    out = re.sub(
        r"(?:\{\s*\}\s*)?\^\s*\{?\s*([0-9]+)\s*\}?\s*([PC])\s*_\s*\{?\s*([0-9]+)\s*\}?",
        r"\2^{\1}_{\3}",
        out,
    )

    # e.g., P(5,3) / C(8,2) (numeric params only; keep probability forms like P(A), P(A|B))
    # In B1 coordinate context, C(1,2)/P(a,b) should remain point notation.
    if not coord_guard:
        out = re.sub(r"\b([PC])\s*\(\s*([0-9]+)\s*,\s*([0-9]+)\s*\)", r"\1^{\2}_{\3}", out)

    if out != original:
        log["changed"] = True
        log["reasons"].append("normalized permutation notation to P^{n}_{r}/C^{n}_{r}")
    return out, log


def normalize_probability_event_notation(text: str) -> tuple[str, dict]:
    original = str(text or "")
    out = original
    log = {"changed": False, "reasons": []}

    token = r"[A-Za-z](?:'|\\prime)?"
    inner_re = re.compile(
        rf"^\s*({token})(?:\s*(\\cup|\\cap|\\setminus|\||-|或|且)\s*({token}))?\s*$"
    )
    outer_re = re.compile(r"P\s*\(\s*([^()]+?)\s*\)")

    def _canon_token(tok: str) -> str:
        t = str(tok or "").strip()
        t = re.sub(r"\s+", "", t)
        t = t.replace("\\prime", "'")
        return t

    def _already_inline_math(src: str, start: int, end: int) -> bool:
        left = src[max(0, start - 8):start]
        right = src[end:end + 8]
        return bool(re.search(r"\\\(\s*$", left) and re.search(r"^\s*\\\)", right))

    def _replace(match: re.Match) -> str:
        nonlocal out
        start, end = match.span()
        if _already_inline_math(out, start, end):
            return match.group(0)
        inner = match.group(1)
        m = inner_re.match(inner)
        if not m:
            return match.group(0)
        lhs = _canon_token(m.group(1))
        op = m.group(2)
        rhs = _canon_token(m.group(3)) if m.group(3) else None
        if not op:
            return rf"\(P({lhs})\)"
        op_map = {
            "∪": r"\cup",
            "∩": r"\cap",
            r"\cup": r"\cup",
            r"\\cup": r"\cup",
            r"\cap": r"\cap",
            r"\\cap": r"\cap",
            r"\setminus": r"\setminus",
            r"\\setminus": r"\setminus",
        }
        op_canon = op_map.get(op, op)
        return rf"\(P({lhs} {op_canon} {rhs})\)"

    out = outer_re.sub(_replace, out)

    if out != original:
        log["changed"] = True
        log["reasons"].append("normalized probability event notation to inline LaTeX")
    return out, log


def _is_subsection_heading_line(line: str) -> bool:
    t = str(line or "").strip()
    return bool(re.search(r"^\s*\d+\s*-\s*\d+\s*\.\s*\d+\s*[^\s].*$", t))


def repair_missing_single_variable_text(problem_text: str) -> tuple[str, dict]:
    text = str(problem_text or "")
    repair = {"applied": False, "symbol": None, "reason": ""}
    if not text.strip():
        repair["reason"] = "empty_text"
        return text, repair

    missing_slots = []
    if re.search(r"設\s*\?", text):
        missing_slots.append("subject")
    if re.search(r"=\s*\?", text):
        missing_slots.append("value")
    if not missing_slots:
        repair["reason"] = "no_missing_variable_slot"
        return text, repair

    symbols = set(re.findall(r"(?<![A-Za-z])[A-Za-z](?![A-Za-z])", text))
    candidates = sorted(sym for sym in symbols if sym.isalpha() and sym.lower() in "nmxyab")
    if len(candidates) != 1:
        repair["reason"] = "non_unique_candidate_variable"
        return text, repair

    sym = candidates[0]
    fixed = text
    if "subject" in missing_slots:
        fixed = re.sub(r"設\s*\?", f"設 {sym} ", fixed, count=1)
    if "value" in missing_slots:
        fixed = re.sub(r"=\s*\?", f"= {sym} ", fixed, count=1)

    if fixed != text:
        repair["applied"] = True
        repair["symbol"] = sym
        repair["reason"] = f"filled missing variable with unique symbol {sym}"
    else:
        repair["reason"] = "pattern_not_replaced"
    return fixed, repair


def validate_problem_block_purity(problem: dict) -> dict:
    if not isinstance(problem, dict):
        return problem
    text = str(problem.get("problem_text", "") or problem.get("problem", "") or "").strip()
    if not text:
        return problem

    lines = [ln.strip() for ln in text.splitlines() if str(ln or "").strip()]
    if any(_is_subsection_heading_line(ln) for ln in lines):
        problem["needs_review"] = True
        problem["block_boundary_error"] = True

    explanation_cues = _NON_QUESTION_EXPLANATION_CUES + ("銝膩",)
    problem_verbs = _QUESTION_VERBS
    explanation_hits = sum(1 for cue in explanation_cues if cue in text)
    has_problem_verb = any(v in text for v in problem_verbs)
    if explanation_hits >= 2 and not has_problem_verb:
        problem["needs_review"] = True
        problem["likely_concept_explanation"] = True

    formula_placeholders = (
        r"\[FORMULA_MISSING\]",
        r"\[FORMULA_IMAGE_\d+\]",
        r"\[WORD_EQUATION_UNPARSED\]",
        r"\[BLOCK_IMAGE\]",
    )
    has_formula_gap = any(re.search(p, text) for p in formula_placeholders)
    readable_text = re.sub(r"\[[A-Z_0-9]+\]", " ", text)
    readable_text = re.sub(r"\s+", " ", readable_text).strip()
    if has_formula_gap and (len(readable_text) < 8 or not has_problem_verb):
        problem["needs_review"] = True
        problem["formula_missing"] = True
        logs = problem.get("repair_log", [])
        if not isinstance(logs, list):
            logs = [str(logs)]
        logs.append("marked formula_missing due to formula placeholder")
        problem["repair_log"] = logs

    # ??憿憿凳/?賊?畾撩嚗????蝻箏撘?銝?葫?批捆
    set_question_hint = bool(re.search(r"(集合|子集|交集|聯集)", text))
    has_choice_labels = len(re.findall(r"\([A-Da-d]\)", text)) >= 2
    has_set_notation = bool(re.search(r"[\{\}U∩∪]|A\s*[∩∪\\]\s*B|A\s*-\s*B", text))
    if set_question_hint and has_choice_labels and not has_set_notation:
        problem["needs_review"] = True
        problem["formula_missing"] = True
        logs = problem.get("repair_log", [])
        if not isinstance(logs, list):
            logs = [str(logs)]
        logs.append("marked formula_missing due to missing set notation/options")
        problem["repair_log"] = logs

    if "[BLANK]" in text:
        problem["has_answer_blank"] = True
        problem["question_format"] = "fill_blank"
        logs = problem.get("repair_log", [])
        if not isinstance(logs, list):
            logs = [str(logs)]
        logs.append("preserved [BLANK] as fill blank, not formula missing")
        problem["repair_log"] = logs

    if problem.get("skill_id") and problem.get("block_boundary_error"):
        problem["needs_review"] = True
        problem["skill_boundary_mismatch"] = True

    if re.search(r"(表格|統計表|列表|table)", text, flags=re.IGNORECASE):
        has_table_payload = bool(re.search(r"\d", text) and re.search(r"[|嚚???]", text))
        if not has_table_payload and not re.search(r"\[[A-Z_]*TABLE[A-Z_0-9]*\]", text):
            problem["needs_review"] = True
            problem["needs_table_review"] = True
            logs = problem.get("repair_log", [])
            if not isinstance(logs, list):
                logs = [str(logs)]
            logs.append("table-dependent question without enough table content")
            problem["repair_log"] = logs

    if re.search(r"銝?|憒?|??", text) and re.search(r"?賣見瘜雿車?賣見", text):
        if not (
            problem.get("has_image")
            or "[BLOCK_IMAGE]" in text
            or "[IMAGE_" in text
        ):
            problem["needs_review"] = True
            logs = problem.get("repair_log", [])
            if not isinstance(logs, list):
                logs = [str(logs)]
            logs.append("image-dependent sampling question without image evidence")
            problem["repair_log"] = logs
    return problem


def classify_practice_source_bucket(source_type: str) -> str:
    st = str(source_type or "").strip().lower()
    if st == "in_class_practice":
        return "in_class_practice"
    if st in CHAPTER_EXERCISE_TYPES:
        return "chapter_exercise"
    if st == "self_assessment":
        return "self_assessment"
    if st == "exam_practice":
        return "exam_practice"
    return "other_practice"


def get_question_title(item: dict) -> str:
    if not isinstance(item, dict):
        return ""
    return _first_non_empty_str(
        item,
        ("practice_title", "example_title", "title", "display_name", "name", "source_title", "source_description"),
    )


_SECTION_EXPOSITION_TITLE_EXACT = frozenset({
    "觀念整理", "觀念", "整理", "說明", "重點", "補充",
    "觀念說明", "整理說明", "章節說明", "概念說明",
})

_SECTION_EXPOSITION_TITLE_RE = re.compile(
    r"^(?:觀念整理|觀念說明|整理說明|章節說明|概念說明|觀念\s*\d*|說明\s*\d*)$"
)


def _is_section_exposition_title(title: str) -> bool:
    """Return True when *title* looks like a section-exposition label (not a real question).

    Catches Gemini-generated source_description values like '隤脫??批捆' that represent
    narrative textbook passages rather than examples, exercises, or practices.
    These must NOT be saved as textbook_example records.
    """
    t = str(title or "").strip()
    if not t:
        return False
    # Exact known exposition labels
    if t in _SECTION_EXPOSITION_TITLE_EXACT:
        return True
    # Regex: starts with exposition keywords, no digits or question-type suffix
    if _SECTION_EXPOSITION_TITLE_RE.match(t):
        return True
    return False


def normalize_source_type_by_title(item: dict, default_source_type: str = "textbook_example") -> str:
    title = get_question_title(item)
    raw_source_type = str(item.get("source_type", "") or "").strip().lower() if isinstance(item, dict) else ""
    reason = ""

    # Section exposition titles are not importable question records.
    if _is_section_exposition_title(title):
        normalized = "section_exposition"
        reason = "title_is_section_exposition"
        if isinstance(item, dict):
            item["source_type"] = normalized
            try:
                current_app.logger.info(
                    f"[SOURCE TYPE] title={title!r} normalized_source_type={normalized} reason={reason}"
                )
            except Exception:
                pass
        return normalized

    if "?典?蝺渡?" in title:
        normalized = "in_class_practice"
        reason = "title_contains_?典?蝺渡?"
    elif ("蝡?芣?閰?" in title) or ("?芣?閰?" in title) or bool(re.search(r"蝚枯s*\d+\s*蝡s*?芣?閰?", title)):
        normalized = "self_assessment"
        reason = "title_contains_?芣?閰?"
    elif any(k in title for k in ("統測", "學測")):
        normalized = "exam_practice"
        reason = "title_contains_exam"
    elif "基礎題" in title:
        normalized = "basic_exercise"
        reason = "title_contains_basic_exercise"
    elif "進階題" in title:
        normalized = "advanced_exercise"
        reason = "title_contains_advanced_exercise"
    elif "習題" in title:
        normalized = "textbook_practice"
        reason = "title_contains_practice"
    elif "例題" in title:
        normalized = "textbook_practice"
        reason = "title_contains_example"
    elif "蝧?" in title:
        normalized = "chapter_exercise"
        reason = "title_contains_蝧?"
    elif re.search(r"^\s*例(?:題)?\s*\d+", title):
        normalized = "textbook_example"
        reason = "title_matches_example"
    elif raw_source_type in ALLOWED_SOURCE_TYPES:
        normalized = raw_source_type
        reason = "item_source_type_allowed"
    else:
        fallback = str(default_source_type or "textbook_example").strip().lower() or "textbook_example"
        if raw_source_type and raw_source_type not in ALLOWED_SOURCE_TYPES:
            normalized = "textbook_practice"
            reason = "invalid_source_type_fallback_textbook_practice"
            if isinstance(item, dict):
                item["needs_review"] = True
        else:
            normalized = fallback
            reason = "default_source_type"

    if isinstance(item, dict):
        item["source_type"] = normalized
        try:
            current_app.logger.info(
                f"[SOURCE TYPE] title={title or '<empty>'} raw_source_type={raw_source_type or 'None'} "
                f"normalized_source_type={normalized} reason={reason}"
            )
        except Exception:
            pass
    return normalized


_SOURCE_TYPE_QUALITY_RANK = {
    "basic_exercise": 60,
    "advanced_exercise": 58,
    "chapter_exercise": 56,
    "in_class_practice": 54,
    "exam_practice": 52,
    "self_assessment": 50,
    "textbook_example": 48,
    "textbook_practice": 46,
}


def _normalize_title_for_dedupe(title: str) -> str:
    t = re.sub(r"\s+", "", str(title or "").strip())
    t = re.sub(r"^靘??!憿?(\d+)$", r"靘?\1", t)
    return t


def _build_intra_import_dedupe_key(section_title: str, source_type: str, title: str) -> str:
    sec = _normalize_title_for_dedupe(section_title)
    st = str(source_type or "").strip().lower()
    tt = _normalize_title_for_dedupe(title)
    return f"{sec}|{st}|{tt}"


def _score_intra_import_item(item: dict, source_type: str = "", title: str = "", q_assets: dict | None = None) -> int:
    st = str(source_type or "").strip().lower()
    score = _SOURCE_TYPE_QUALITY_RANK.get(st, 0)
    text = str(item.get("problem_text", "") or item.get("problem", "") or "")
    if re.search(r"\[FORMULA_IMAGE_\d+\]", text):
        score += 100
    if "[FORMULA_MISSING]" in text:
        score += 10
    if item.get("needs_formula_review") is True:
        score += 8
    score += min(len(text), 400) // 4
    if isinstance(item.get("formula_assets"), list) and item.get("formula_assets"):
        score += 80
    if q_assets:
        title_assets = _lookup_docx_question_assets(title, q_assets) or []
        formula_assets = [a for a in title_assets if str(a.get("media_kind", "")) == "formula_asset"]
        if formula_assets:
            score += 70 + min(len(formula_assets), 20)
    return score


def _dedupe_intra_import_section_items(section_data: dict, q_assets: dict | None = None) -> int:
    """Deduplicate repeated questions within one section before DB write.

    Returns merged duplicate count.
    """
    concepts = section_data.get("concepts", []) if isinstance(section_data, dict) else []
    if not isinstance(concepts, list) or not concepts:
        return 0

    # Gather all candidates with location pointers.
    all_entries = []
    for ci, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            continue
        for bucket_name, default_st in (("examples", "textbook_example"), ("practice_questions", "in_class_practice")):
            arr = concept.get(bucket_name, [])
            if not isinstance(arr, list):
                continue
            for ii, item in enumerate(arr):
                if not isinstance(item, dict):
                    continue
                title = get_question_title(item) or ""
                source_type = normalize_source_type_by_title(item, default_source_type=default_st)
                key = _build_intra_import_dedupe_key(
                    section_data.get("section_title", ""),
                    source_type,
                    title,
                )
                score = _score_intra_import_item(item, source_type=source_type, title=title, q_assets=q_assets)
                all_entries.append(
                    {
                        "concept_idx": ci,
                        "bucket": bucket_name,
                        "item_idx": ii,
                        "item": item,
                        "title": title,
                        "source_type": source_type,
                        "key": key,
                        "score": score,
                    }
                )

    if not all_entries:
        return 0

    # Pick winner per dedupe key.
    best_by_key = {}
    for e in all_entries:
        prev = best_by_key.get(e["key"])
        if prev is None or e["score"] > prev["score"]:
            best_by_key[e["key"]] = e

    keep_locs = {
        (e["concept_idx"], e["bucket"], e["item_idx"])
        for e in best_by_key.values()
    }
    removed = 0
    for ci, concept in enumerate(concepts):
        if not isinstance(concept, dict):
            continue
        for bucket_name in ("examples", "practice_questions"):
            arr = concept.get(bucket_name, [])
            if not isinstance(arr, list):
                continue
            new_arr = []
            for ii, item in enumerate(arr):
                if (ci, bucket_name, ii) in keep_locs:
                    new_arr.append(item)
                else:
                    removed += 1
            concept[bucket_name] = new_arr
    return removed


def dedupe_intra_import_parsed_data(parsed_data: dict, q_assets: dict | None = None) -> tuple[dict, int]:
    """Deduplicate duplicate questions within the same AI JSON payload."""
    if not isinstance(parsed_data, dict):
        return parsed_data, 0
    total_removed = 0
    for chapter in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections", []) or []:
            if not isinstance(section, dict):
                continue
            total_removed += _dedupe_intra_import_section_items(section, q_assets=q_assets)
    return parsed_data, total_removed


def _normalize_sub_questions(raw_sub_questions):
    normalized = []
    if not isinstance(raw_sub_questions, list):
        return normalized
    for idx, item in enumerate(raw_sub_questions, start=1):
        if not isinstance(item, dict):
            continue
        sq_problem_raw = _first_non_empty_str(item, ("problem_text", "problem", "question"))
        sq_problem, _ = standardize_problem_latex(sq_problem_raw)
        sq_problem, _ = normalize_probability_event_notation(sq_problem)
        normalized.append(
            {
                "label": _first_non_empty_str(item, ("label", "index", "no", "number")) or str(idx),
                "problem": sq_problem,
                "answer": _first_non_empty_str(item, ("correct_answer", "answer")),
                "solution": _first_non_empty_str(item, ("detailed_solution", "solution")),
            }
        )
    return normalized


def _render_sub_questions_problem(problem_text, sub_questions):
    if not sub_questions:
        return (problem_text or "").strip()
    lines = [str(problem_text or "").strip()] if str(problem_text or "").strip() else []
    for sq in sub_questions:
        label = str(sq.get("label", "") or "").strip()
        p = str(sq.get("problem", "") or "").strip()
        if p:
            lines.append(f"({label}) {p}" if label else p)
    return "\n".join(lines).strip()


def _render_sub_questions_answer(answer_text, sub_questions):
    if not sub_questions:
        return (answer_text or "").strip()
    parts = []
    for sq in sub_questions:
        label = str(sq.get("label", "") or "").strip()
        ans = str(sq.get("answer", "") or "").strip()
        if ans:
            parts.append(f"({label}) {ans}" if label else ans)
    return "\n".join(parts) if parts else (answer_text or "").strip()


def _render_sub_questions_solution(solution_text, sub_questions):
    if not sub_questions:
        return (solution_text or "").strip()
    lines = [str(solution_text or "").strip()] if str(solution_text or "").strip() else []
    for sq in sub_questions:
        label = str(sq.get("label", "") or "").strip()
        s = str(sq.get("solution", "") or "").strip()
        p = str(sq.get("problem", "") or "").strip()
        a = str(sq.get("answer", "") or "").strip()
        if s:
            lines.append(f"({label}) {s}" if label else s)
        elif p or a:
            lines.append(f"({label}) {p} = {a}".strip() if label else f"{p} = {a}".strip())
    return "\n".join(lines).strip()


def _normalize_textbook_question_structure(parsed_data, queue=None):
    """
    Normalize AI output structure so examples/practice_questions are consistently separable.
    - examples: independent textbook examples
    - practice_questions: independent in-class practices / exercises
    - backward compatibility: example.followup_practices -> concept.practice_questions
    """
    if not isinstance(parsed_data, dict):
        return parsed_data

    for chapter in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections", []) or []:
            if not isinstance(section, dict):
                continue
            for concept in section.get("concepts", []) or []:
                if not isinstance(concept, dict):
                    continue

                normalized_examples = []
                extracted_practices = []

                for ex in concept.get("examples", []) or []:
                    if not isinstance(ex, dict):
                        continue

                    example_title = _first_non_empty_str(ex, ("example_title", "source_description", "title"))
                    problem_text = _first_non_empty_str(ex, ("problem_text", "problem", "question"))
                    answer = _first_non_empty_str(ex, ("correct_answer", "answer"))
                    solution = _first_non_empty_str(ex, ("detailed_solution", "solution"))
                    source_type = normalize_source_type_by_title(ex, default_source_type="textbook_example")
                    source_page = ex.get("source_page", ex.get("page"))
                    page_index = ex.get("page_index")
                    sub_questions = _normalize_sub_questions(ex.get("sub_questions", []))

                    ex_normalized = dict(ex)
                    ex_normalized["source_description"] = example_title or ex_normalized.get("source_description", "靘?")
                    if problem_text:
                        ex_normalized["problem_text"] = problem_text
                    if answer:
                        ex_normalized["correct_answer"] = answer
                    if solution:
                        ex_normalized["detailed_solution"] = solution
                    ex_normalized["source_type"] = source_type if source_type else "textbook_example"
                    ex_normalized["source_page"] = source_page if source_page is not None else None
                    ex_normalized["page_index"] = page_index if page_index is not None else None
                    if sub_questions:
                        ex_normalized["sub_questions"] = sub_questions
                        ex_normalized["problem_text"] = _render_sub_questions_problem(problem_text, sub_questions)
                        ex_normalized["correct_answer"] = _render_sub_questions_answer(answer, sub_questions)
                        ex_normalized["detailed_solution"] = _render_sub_questions_solution(solution, sub_questions)
                    if source_type == "textbook_example":
                        normalized_examples.append(ex_normalized)
                    else:
                        extracted_practices.append(ex_normalized)

                    for fp in ex.get("followup_practices", []) or []:
                        if not isinstance(fp, dict):
                            continue
                        p_title = _first_non_empty_str(fp, ("practice_title", "title", "source_description"))
                        p_problem = _first_non_empty_str(fp, ("problem_text", "problem", "question"))
                        p_answer = _first_non_empty_str(fp, ("correct_answer", "answer"))
                        p_solution = _first_non_empty_str(fp, ("detailed_solution", "solution"))
                        p_source_type = normalize_source_type_by_title(fp, default_source_type="in_class_practice")
                        linked_example_title = _first_non_empty_str(fp, ("linked_example_title",)) or ex_normalized["source_description"]
                        p_source_page = fp.get("source_page", fp.get("page"))
                        p_page_index = fp.get("page_index")

                        practice_item = dict(fp)
                        practice_item["source_description"] = p_title or "?典?蝺渡?"
                        if p_problem:
                            practice_item["problem_text"] = p_problem
                        if p_answer:
                            practice_item["correct_answer"] = p_answer
                        if p_solution:
                            practice_item["detailed_solution"] = p_solution
                        practice_item["source_type"] = p_source_type
                        practice_item["linked_example_title"] = linked_example_title
                        practice_item["source_page"] = p_source_page if p_source_page is not None else None
                        practice_item["page_index"] = p_page_index if p_page_index is not None else None
                        if not practice_item.get("skill_id") and ex_normalized.get("skill_id"):
                            practice_item["skill_id"] = ex_normalized.get("skill_id")
                        extracted_practices.append(practice_item)

                normalized_practices = []
                for practice in (concept.get("practice_questions", []) or []) + extracted_practices:
                    if not isinstance(practice, dict):
                        continue
                    p_title = _first_non_empty_str(practice, ("practice_title", "source_description", "title"))
                    p_problem = _first_non_empty_str(practice, ("problem_text", "problem", "question"))
                    p_answer = _first_non_empty_str(practice, ("correct_answer", "answer"))
                    p_solution = _first_non_empty_str(practice, ("detailed_solution", "solution"))
                    p_source_type = normalize_source_type_by_title(practice, default_source_type="in_class_practice")
                    linked_example_title = _first_non_empty_str(practice, ("linked_example_title",))
                    p_source_page = practice.get("source_page", practice.get("page"))
                    p_page_index = practice.get("page_index")
                    sub_questions = _normalize_sub_questions(practice.get("sub_questions", []))

                    normalized_practice = dict(practice)
                    normalized_practice["source_description"] = p_title or normalized_practice.get("source_description", "?典?蝺渡?")
                    if p_problem:
                        normalized_practice["problem_text"] = p_problem
                    if p_answer:
                        normalized_practice["correct_answer"] = p_answer
                    if p_solution:
                        normalized_practice["detailed_solution"] = p_solution
                    normalized_practice["source_type"] = p_source_type
                    if linked_example_title:
                        normalized_practice["linked_example_title"] = linked_example_title
                    normalized_practice["source_page"] = p_source_page if p_source_page is not None else None
                    normalized_practice["page_index"] = p_page_index if p_page_index is not None else None
                    if sub_questions:
                        normalized_practice["sub_questions"] = sub_questions
                        normalized_practice["problem_text"] = _render_sub_questions_problem(p_problem, sub_questions)
                        normalized_practice["correct_answer"] = _render_sub_questions_answer(p_answer, sub_questions)
                        normalized_practice["detailed_solution"] = _render_sub_questions_solution(p_solution, sub_questions)

                    normalized_practices.append(normalized_practice)

                concept["examples"] = normalized_examples
                concept["practice_questions"] = normalized_practices
                if isinstance(concept.get("self_assessment_questions"), list):
                    normalized_sa = []
                    for q in concept.get("self_assessment_questions", []) or []:
                        if not isinstance(q, dict):
                            continue
                        qn = dict(q)
                        qn["source_type"] = normalize_source_type_by_title(qn, default_source_type="self_assessment")
                        qn["source_page"] = q.get("source_page", q.get("page", None))
                        qn["page_index"] = q.get("page_index", None)
                        normalized_sa.append(qn)
                    concept["self_assessment_questions"] = normalized_sa
                    concept["practice_questions"].extend(normalized_sa)
                if isinstance(concept.get("exercises"), list):
                    normalized_exercises = []
                    for q in concept.get("exercises", []) or []:
                        if not isinstance(q, dict):
                            continue
                        qn = dict(q)
                        qn["source_type"] = normalize_source_type_by_title(qn, default_source_type="chapter_exercise")
                        normalized_exercises.append(qn)
                    concept["exercises"] = normalized_exercises
                    concept["practice_questions"].extend(normalized_exercises)

    return parsed_data


def _mark_needs_review_for_low_quality_pages(parsed_data, page_analysis_payload):
    if not isinstance(parsed_data, dict) or not isinstance(page_analysis_payload, dict):
        return parsed_data
    flagged = {int(k) for k, v in page_analysis_payload.items() if isinstance(v, dict) and v.get("needs_review")}
    if not flagged:
        return parsed_data
    for chapter in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter, dict):
            continue
        for section in chapter.get("sections", []) or []:
            if not isinstance(section, dict):
                continue
            for concept in section.get("concepts", []) or []:
                if not isinstance(concept, dict):
                    continue
                for bucket in ("examples", "practice_questions", "self_assessment_questions"):
                    for q in concept.get(bucket, []) or []:
                        if not isinstance(q, dict):
                            continue
                        sp = q.get("source_page")
                        try:
                            sp_int = int(sp) if sp is not None else None
                        except Exception:
                            sp_int = None
                        if sp_int in flagged:
                            q["needs_review"] = True
                            prev = str(q.get("parse_warning", "") or "").strip()
                            extra = "low_quality_page_without_vision_ocr"
                            q["parse_warning"] = ";".join(filter(None, [prev, extra]))
    return parsed_data


def is_non_skill_bucket(concept_name, clean_en_id):
    """Return whether a concept bucket should not generate skill records."""
    name = (concept_name or "").strip()
    en_id = (clean_en_id or "").strip().lower()
    non_skill_names = {
        "蝧?",
        "蝡?隞晶",
        "??蝯?璁?",
    }
    non_skill_en_ids = {
        "chapterintroduction",
        "exercises",
        "practice",
        "review",
    }
    return name in non_skill_names or en_id in non_skill_en_ids


def remap_mathb_non_skill_examples(section_title, concept_name, clean_en_id, example):
    """Remap known non-skill examples in B4 section 1-1 to concrete skills."""
    section = (section_title or "").strip()
    if "1-1" not in section and "排列組合基本原理" not in section:
        return None

    non_skill = is_non_skill_bucket(concept_name, clean_en_id)
    if not non_skill:
        return None

    problem_type = str(example.get("problem_type", "") or "").strip().lower()
    subskill_tag = str(example.get("subskill_tag", "") or "").strip().lower()
    source_description = str(example.get("source_description", "") or "").strip().lower()
    problem_text = str(example.get("problem_text", "") or "").strip().lower()

    zh_hints = "".join([
        str(example.get("source_description", "") or ""),
        str(example.get("problem_text", "") or ""),
    ])
    signal = " ".join([problem_type, subskill_tag, source_description, problem_text])

    if (
        "tree_diagram" in signal
        or "樹狀圖" in zh_hints
        or "??" in zh_hints
    ):
        return "TreeDiagramCounting"

    if (
        "addition_principle" in signal
        or "??閮?" in zh_hints
        or "????" in zh_hints
    ):
        return "AdditionPrinciple"

    if (
        "factorial" in signal
        or "??" in zh_hints
        or "n!" in signal
        or "n!" in zh_hints.lower()
    ):
        return "FactorialNotation"

    if (
        "multiplication_principle" in signal
        or "divisor_counting" in signal
        or "mixed_counting" in signal
        or "甇???詨" in zh_hints
        or "甇仿?閮" in zh_hints
        or "銋???" in zh_hints
    ):
        return "MultiplicationPrinciple"

    # ?⊥??斗??閮剜飛?乩?瘜???
    return "MultiplicationPrinciple"


def remap_mathb21_non_skill_examples(section_title, concept_name, clean_en_id, example):
    section = (section_title or "").strip()
    if "2-1" not in section and "排列組合" not in section:
        return None
    if not is_non_skill_bucket(concept_name, clean_en_id):
        return None

    text = " ".join(
        [
            str(example.get("problem_type", "") or ""),
            str(example.get("subskill_tag", "") or ""),
            str(example.get("source_description", "") or ""),
            str(example.get("problem_text", "") or ""),
        ]
    )
    zh = text

    if re.search(r"聯集|交集|補集", zh):
        return "EventOperations"
    if re.search(r"事件|樣本點|機率", zh):
        return "EventConcepts"
    if re.search(r"樣本空間|樣本", zh):
        return "SampleSpace"
    if re.search(r"集合|子集|全集|元素", zh):
        return "SetOperations"
    if re.search(r"容斥|計數|元素個數", zh):
        return "SetCountingInclusionExclusion"
    if re.search(r"集合|子集|補集|空集|全集", zh):
        return "SetBasicConcepts"

    # 2-1 ?⊥??斗??摰??唳蝭銝餉遘 skill
    return "SampleSpace"


def remap_mathb31_non_skill_examples(section_title, concept_name, clean_en_id, example):
    section = (section_title or "").strip()
    if "3-1" not in section and "圓排列" not in section:
        return None
    if not is_non_skill_bucket(concept_name, clean_en_id):
        return None

    text = " ".join(
        [
            str(example.get("problem_type", "") or ""),
            str(example.get("subskill_tag", "") or ""),
            str(example.get("source_description", "") or ""),
            str(example.get("problem_text", "") or ""),
        ]
    )
    if re.search(r"蝪∪?冽??賣見|蝟餌絞?賣見|?惜?冽??賣見|?刻?賣見|?賣見?寞?", text):
        return "SamplingMethods"
    if re.search(r"瘥黎擃璅?|瘥黎擃|璅??腮?格|?賣|?賣見", text):
        return "SamplingSurvey"
    if re.search(r"蝯梯???蝢尚?膩蝯梯?|?刻?蝯梯?|鞈???|鞈??渡?|鞈???|蝯梯?", text):
        return "MeaningOfStatistics"
    return "MeaningOfStatistics"


def remap_mathb32_non_skill_examples(section_title, concept_name, clean_en_id, example):
    section = (section_title or "").strip()
    if "3-2" not in section and "蝯梯?鞈??渡?" not in section:
        return None
    if not is_non_skill_bucket(concept_name, clean_en_id):
        return None
    text = " ".join(
        [
            str(example.get("problem_type", "") or ""),
            str(example.get("subskill_tag", "") or ""),
            str(example.get("source_description", "") or ""),
            str(example.get("problem_text", "") or ""),
        ]
    )
    if re.search(r"累積|累積次數|累積分配", text):
        return "CumulativeFrequencyDistribution"
    if re.search(r"長條圖|直方圖|折線圖|圓餅圖", text):
        return "FrequencyDistributionGraphs"
    if re.search(r"圖表|讀圖|資料判讀", text):
        return "StatisticalChartReading"
    if re.search(r"平均|中位數|眾數|變異", text):
        return "DataOrganizationAndTables"
    return "DataOrganizationAndTables"


def remap_mathb33_non_skill_examples(section_title, concept_name, clean_en_id, example):
    section = (section_title or "").strip()
    if "3-3" not in section and "統計圖表" not in section:
        return None
    if not is_non_skill_bucket(concept_name, clean_en_id):
        return None
    text = " ".join(
        [
            str(example.get("problem_type", "") or ""),
            str(example.get("subskill_tag", "") or ""),
            str(example.get("source_description", "") or ""),
            str(example.get("problem_text", "") or ""),
        ]
    )
    if re.search(r"??撟喳?|摮詨?|甈|蝭?腮SUMPRODUCT|???蜀", text):
        return "WeightedMean"
    if re.search(r"?刻?|??雿|??雿?|IQR|Q_1|Q_3", text):
        return "DispersionMeasures"
    if re.search(r"霈?腮璅?撌徑瘥?璅?撌徑璅?璅?撌徑?Ｗ?撌徑?|sigma|s\^2|?\^2", text):
        return "VarianceAndStandardDeviation"
    if re.search(r"蝺扯??撟喟宏|隡貊葬|隤輯|x'|ax\+b|x'_i", text):
        return "LinearTransformationOfData"
    if re.search(r"撣豢???|撣豢??脩?|68.?95.?99\.?7|銝??皞榆|?拙?皞榆|銝?皞榆", text):
        return "NormalDistributionAndEmpiricalRule"
    if re.search(r"瘞矽|靽∪?瘞湔?|?賣見隤文榆|隤文榆蝭?|瘥?瘥?", text):
        return "OpinionPollInterpretation"
    if re.search(r"撟喳??腮銝凋??腮?暹|\\bar\{x\}|弮|mu|Me|Mo", text):
        return "CentralTendencyMeasures"
    return "CentralTendencyMeasures"


def extract_self_assessment_section_context(*texts: str) -> str:
    merged = "\n".join(str(t or "") for t in texts if str(t or "").strip())
    m = re.search(r"(\d+\s*-\s*\d+)\s*([^\n]*)", merged)
    if m:
        sec = re.sub(r"\s+", "", m.group(1))
        return sec
    if "?渡???" in merged:
        return "1-2"
    if "排列組合基本原理" in merged:
        return "1-1"
    if "蝯???蝢抵?閮?" in merged:
        return "1-4"
    if "蝯?" in merged:
        return "1-3"
    if "絕對值與根號" in merged:
        return "1-5"
    return ""


def infer_mathb4_self_assessment_skill(section_context: str, title: str, problem_text: str) -> dict:
    sec = str(section_context or "").strip()
    text = f"{title or ''}\n{problem_text or ''}"
    result = {
        "clean_en_id": "",
        "problem_type": "",
        "subskill_tag": "",
        "matched": False,
    }
    if not sec:
        return result

    if sec == "1-1":
        if re.search(r"?望??雿?遙銝雿???訾???瑞?.{0,8}憟喟?.{0,8}?遙", text):
            result.update({"clean_en_id": "AdditionPrinciple", "problem_type": "addition_principle", "subskill_tag": "general", "matched": True})
            return result
        if re.search(r"$^", text):
            result.update({"clean_en_id": "MultiplicationPrinciple", "problem_type": "multiplication_principle", "subskill_tag": "mixed_application", "matched": True})
            return result
        if re.search(r"$^", text):
            result.update({"clean_en_id": "MultiplicationPrinciple", "problem_type": "multiplication_principle", "subskill_tag": "role_assignment", "matched": True})
            return result
        if re.search(r"$^", text):
            result.update({"clean_en_id": "MultiplicationPrinciple", "problem_type": "multiplication_principle", "subskill_tag": "number_restriction", "matched": True})
            return result
        result.update({"clean_en_id": "MultiplicationPrinciple", "problem_type": "multiplication_principle", "subskill_tag": "mixed_application"})
        return result

    if sec == "1-2" or "?渡???" in text:
        if re.search(r"$^", text):
            result.update({"clean_en_id": "PermutationOfDistinctObjects", "problem_type": "permutation", "subskill_tag": "number_restriction", "matched": True})
            return result
        if re.search(r"摮??蝺??銝?擐?|敹??思?", text):
            result.update({"clean_en_id": "PermutationOfDistinctObjects", "problem_type": "permutation", "subskill_tag": "number_restriction", "matched": True})
            return result
        if re.search(r"撌∟艘|頝舐?|??|??????銋?", text):
            result.update({"clean_en_id": "PermutationOfDistinctObjects", "problem_type": "permutation", "subskill_tag": "mixed_application", "matched": True})
            return result
        result.update({"clean_en_id": "PermutationOfDistinctObjects", "problem_type": "permutation", "subskill_tag": "mixed_application"})
        return result

    return result


def infer_mathb4_ch2_self_assessment_skill(chapter_title: str, section_title: str, title: str, problem_text: str) -> dict:
    text = f"{chapter_title or ''}\n{section_title or ''}\n{title or ''}\n{problem_text or ''}"
    result = {
        "skill_id": "",
        "problem_type": "",
        "subskill_tag": "",
    }
    if not ((("2" in str(chapter_title or "")) and ("璈?" in str(chapter_title or ""))) or ("?芣?閰?" in str(title or ""))):
        return result

    if re.search(r"璇辣璈?|撌脩??隞嗥???{0,12}璇辣銝P\s*\(\s*[A-Za-z]\s*\|\s*[A-Za-z]\s*\)", text):
        result.update({"skill_id": "vh_?詨飛B4_ConditionalProbability", "problem_type": "conditional_probability", "subskill_tag": "general"})
        return result
    if re.search(r"$^", text):
        result.update({"skill_id": "vh_?詨飛B4_IndependentEvents", "problem_type": "independent_events", "subskill_tag": "mixed_application"})
        return result
    if re.search(r"???慝??|?脣???慝?砍像|撟喳??脣", text):
        if re.search(r"?脣|?砍像|撟喳?", text):
            result.update({"skill_id": "vh_?詨飛B4_ApplicationsOfExpectation", "problem_type": "expectation_application", "subskill_tag": "mixed_application"})
        else:
            result.update({"skill_id": "vh_?詨飛B4_MathematicalExpectation", "problem_type": "expectation", "subskill_tag": "general"})
        return result
    if re.search(r"??|??|摮??摮?|\\subset|\\cap|\\cup|蝛粹??摰?", text) and not re.search(r"P\s*\(", text):
        result.update({"skill_id": "vh_?詨飛B4_BasicConceptsOfSets", "problem_type": "set_concepts", "subskill_tag": "general"})
        return result
    if re.search(r"P\s*\(\s*[A-Za-z](?:'|\\prime)?\s*(?:\\cup|\\cap|?泜?尚\||-|\\setminus)?\s*[A-Za-z]?(?:'|\\prime)?\s*\)|鈭鈭辣璈?|???砍?", text):
        result.update({"skill_id": "vh_?詨飛B4_ProbabilityProperties", "problem_type": "probability_operations", "subskill_tag": "general"})
        return result
    if re.search(r"$^", text):
        result.update({"skill_id": "vh_?詨飛B4_SampleSpaceAndEvents", "problem_type": "event_operations", "subskill_tag": "general"})
        return result
    return result


def infer_mathb4_ch3_self_assessment_skill(chapter_title: str, section_title: str, title: str, problem_text: str) -> dict:
    text = f"{chapter_title or ''}\n{section_title or ''}\n{title or ''}\n{problem_text or ''}"
    result = {"skill_id": "", "problem_type": "", "subskill_tag": ""}
    if not ((("3" in str(chapter_title or "")) and ("蝯梯?" in str(chapter_title or ""))) or ("?芣?閰?" in str(title or ""))):
        return result

    if re.search(r"?刻?|??雿?|IQR|??雿|Q_1|Q_3", text):
        result.update({"skill_id": "vh_?詨飛B4_DispersionMeasures", "problem_type": "dispersion_measures", "subskill_tag": "general"})
        return result
    if re.search(r"霈?腮璅?撌徑瘥?璅?撌徑璅?璅?撌徑sigma|?|s\^2|?\^2", text):
        result.update({"skill_id": "vh_?詨飛B4_VarianceAndStandardDeviation", "problem_type": "variance_std", "subskill_tag": "general"})
        return result
    if re.search(r"蝺扯??撟喟宏|隡貊葬|隤輯|瘥?鞈??瘥?鞈?皜瘥?鞈?銋x'|ax\+b", text):
        result.update({"skill_id": "vh_?詨飛B4_LinearTransformationOfData", "problem_type": "linear_transformation", "subskill_tag": "general"})
        return result
    return result


_MATHB4_CHART_SKILLS = {
    "vh_?詨飛B4_DataOrganizationAndTables",
    "vh_?詨飛B4_FrequencyDistributionGraphs",
    "vh_?詨飛B4_CumulativeFrequencyDistribution",
    "vh_?詨飛B4_StatisticalChartReading",
}


def _is_mathb4_chart_target(section_title: str, skill_id: str) -> bool:
    return ("3-2" in str(section_title or "")) or (str(skill_id or "") in _MATHB4_CHART_SKILLS)


def _extract_chart_metadata_for_mathb4_32(problem_text: str, raw_block: str = "") -> dict:
    text = str(problem_text or "")
    block = str(raw_block or "")
    merged = f"{text}\n{block}"
    rows = []
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:[-~嚚\s*(\d+(?:\.\d+)?))?\s*[:嚗嚚?\s]+\s*(\d+(?:\.\d+)?)", merged):
        start = m.group(1)
        end = m.group(2)
        val = m.group(3)
        label = f"{start}-{end}" if end else start
        try:
            rows.append((label, float(val)))
        except Exception:
            continue

    chart_type = None
    if re.search(r"隞乩?蝝舐?甈⊥|隞乩?蝝舐?甈⊥|蝝舐?甈⊥??", merged):
        chart_type = "cumulative_frequency_distribution"
    elif re.search(r"$^", merged):
        chart_type = "frequency_distribution_graph"
    elif re.search(r"$^", merged):
        chart_type = "statistical_chart_reading"
    elif re.search(r"甈⊥??銵育蝯?|蝯葉暺蝯?|?刻?", merged):
        chart_type = "data_organization_table"

    if chart_type and len(rows) >= 2:
        return {
            "requires_chart": True,
            "chart_type": chart_type,
            "chart_data": {
                "labels": [x[0] for x in rows],
                "values": [x[1] for x in rows],
            },
            "chart_renderable": True,
        }
    return {}

_REVIEW_SECTION_RE = re.compile(
    r"review|自我評量|複習|總複習|測驗|能力指標",
    re.IGNORECASE,
)


def _is_review_section_title(section_title: str) -> bool:
    """Return True when *section_title* represents a review / self-assessment section
    that should be excluded from the curriculum outline skeleton.

    Rationale: sections like '1-review ?芣?閰?', '2-review 銴?' are not formal
    teaching units.  They must not pollute the outline used for adaptive routing.
    Self-assessment *questions* (source_type=self_assessment) are unaffected because
    they are handled inside ``save_to_database``, not here.
    """
    t = str(section_title or "").strip()
    if not t:
        return False
    return bool(_REVIEW_SECTION_RE.search(t))


def import_outline_structure_only(parsed_data, curriculum_info, queue, source_file_path=None):
    """Import outline structure only into SkillCurriculum."""
    try:
        from models import db, SkillCurriculum
        current_app.logger.info(" -> [OutlineOnly] ??撱箇?蝡??桅?...")
        
        # 撘瑕皜 session 銝剔?隞颱? pending 霈嚗??autoflush 閫貊????SkillInfo ?航炊
        db.session.rollback()
        
        filename_meta = parse_textbook_filename_metadata(source_file_path) if source_file_path else {}
        volume_val = str(curriculum_info.get('volume', ''))
        curr_val = str(curriculum_info.get('curriculum', ''))
        is_vocational_mathb = (curr_val == 'vocational' and 'B' in volume_val)
        
        # ????蝯??啣??
        struct_map_obj = get_structure_map(curr_val, volume_val)

        chapters_created = 0
        sections_created = 0
        sections_updated = 0
        
        # ?冽餈質馱撌脰???蝡?嚗??銴?蝞?
        processed_chapters = set()

        chapters = parsed_data.get('chapters', [])
        for ch_data in chapters:
            raw_ch_title = ch_data.get('chapter_title', '?芸??蝭').strip()
            
            # 蝡??迂??
            chapter_title = raw_ch_title
            
            sections = ch_data.get('sections', [])
            for sec_data in sections:
                sec_title = sec_data.get('section_title', '').strip()

                # Skip review / ?芣?閰? / 銴? sections ??these are not formal teaching
                # sections and should not appear in the curriculum outline.
                if _is_review_section_title(sec_title):
                    current_app.logger.info(
                        f"[OutlineOnly] skip review section: {sec_title!r}"
                    )
                    continue

                # 撠?蝯??啣?
                sec_code = ""
                # ?岫敺?蝭璅??? 1-1, 1-2 蝑誨蝣?
                match_code = re.search(r'(\d+-\d+)', sec_title)
                if match_code:
                    sec_code = match_code.group(1)
                
                structure_meta = None
                if struct_map_obj and sec_code:
                    structure_meta = struct_map_obj.get_metadata(sec_code)
                
                # 瘙箏??蝯?蝭璅?
                final_ch_title = chapter_title
                if structure_meta and structure_meta.get('chapter_title'):
                    final_ch_title = structure_meta['chapter_title']
                
                # 瘙箏??蝯?蝭璅?
                final_sec_title = sec_title
                if structure_meta and structure_meta.get('section_title'):
                    final_sec_title = structure_meta['section_title']

                # 瘙箏? skill_id (???箇?揣撘?銝遣蝡?SkillInfo)
                # 雿輻 SectionTitle ?Ｙ???ID嚗???outline ?韌隞亥霅
                clean_sec_title = re.sub(r'[^a-zA-Z0-9]', '', final_sec_title)
                if not clean_sec_title:
                    clean_sec_title = "UnknownSection"
                temp_skill_id = f"outline_{curr_val}_{volume_val}_{clean_sec_title}"
                
                # 瑼Ｘ撠??臬摮
                existing_curr = SkillCurriculum.query.filter_by(
                    curriculum=curr_val,
                    volume=volume_val,
                    chapter=final_ch_title,
                    section=final_sec_title
                ).first()
                
                if not existing_curr:
                    new_curr = SkillCurriculum(
                        skill_id=temp_skill_id,
                        curriculum=curr_val,
                        grade=int(curriculum_info.get('grade', 10)),
                        volume=volume_val,
                        chapter=final_ch_title,
                        section=final_sec_title,
                        display_order=0 
                    )
                    db.session.add(new_curr)
                    sections_created += 1
                    if final_ch_title not in processed_chapters:
                        chapters_created += 1
                        processed_chapters.add(final_ch_title)
                else:
                    sections_updated += 1
        
        db.session.commit()
        return {
            "chapters_created": chapters_created,
            "sections_created": sections_created,
            "sections_updated": sections_updated
        }
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[import_outline_structure_only] 憭望?: {e}")
        raise e


def save_to_database(
    parsed_data,
    curriculum_info,
    queue,
    source_file_path=None,
    content_by_page=None,
    outline_only=False,
    import_policy=None,
    optional_enrich_pdf_path=None,
):
    """Save parsed AI content into database."""
    message = "甇?撠??瑽神?亥??澈..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")
    skills_processed = 0
    curriculums_added = 0
    chapters_created = 0
    chapters_updated = 0
    sections_created = 0
    sections_updated = 0
    examples_added = 0
    practice_questions_imported = 0
    in_class_practices_imported = 0
    chapter_exercises_imported = 0
    self_assessments_imported = 0
    exam_practices_imported = 0
    other_practices_imported = 0
    practice_questions_needs_review = 0
    practice_questions_skipped = 0
    duplicates_skipped_count = 0
    updated_duplicates = 0
    processed_skill_ids = []
    detected_titles = []
    in_class_nums = []
    missing_image_questions = []
    docx_attached_count = 0
    docx_direct_display_images = 0
    docx_vector_images = 0
    docx_conversion_success = 0
    docx_conversion_failed = 0
    docx_conversion_pending = 0
    docx_formula_assets_count = 0
    docx_formula_needs_review_count = 0
    merge_guard_kept_existing = 0
    merge_guard_updated_incoming = 0
    docx_copied_to_question_assets = 0
    formula_asset_persist_cache: dict[str, str] = {}
    docx_formula_blocks = {}
    is_pdf_source = str(source_file_path or "").lower().endswith(".pdf")
    is_docx_source = str(source_file_path or "").lower().endswith((".docx", ".doc"))
    converted_latex_import = (
        str(import_policy.get("docx_formula_source_mode", "") or "").strip() == "converted_docx_latex"
        or bool((_DOCX_IMPORT_CONTEXT or {}).get("formula_assets_extraction_skipped"))
    )
    if is_docx_source:
        ctx = _DOCX_IMPORT_CONTEXT or {}
        q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
        docx_formula_blocks = ctx.get("question_formula_blocks", {}) if isinstance(ctx, dict) else {}
        attached_asset_count = sum(len(v or []) for v in q_assets.values()) if isinstance(q_assets, dict) else 0
        current_app.logger.info(f"[DOCX IMAGE DEBUG] attached_asset_count={attached_asset_count}")
        if isinstance(q_assets, dict):
            for t, assets in q_assets.items():
                for a in (assets or []):
                    current_app.logger.info(
                        f"[DOCX IMAGE DEBUG] attached title={t} source_type={a.get('media_kind', 'unknown')} "
                        f"asset_type={a.get('asset_type', 'unknown')} path={a.get('path')}"
                    )
    parsed_data, intra_import_duplicates_merged = dedupe_intra_import_parsed_data(
        parsed_data,
        q_assets=q_assets if is_docx_source else None,
    )
    if intra_import_duplicates_merged > 0:
        current_app.logger.info(
            f"[INTRA IMPORT DEDUPE] merged_duplicates={intra_import_duplicates_merged}"
        )
        queue.put(f"INFO: [INTRA IMPORT DEDUPE] merged_duplicates={intra_import_duplicates_merged}")
    page_image_cache = {}
    import_policy = dict(import_policy or {})
    auto_fill_threshold = float(import_policy.get("auto_fill_confidence_threshold", 0.85) or 0.85)
    auto_fill_threshold = max(0.0, min(1.0, auto_fill_threshold))
    def _count_latex_and_placeholder_records(data):
        latex_re = re.compile(r"\\\(|\\\)|\\\[|\\\]|\\(?:frac|sqrt|left|right)\b|[\^_]")
        placeholder_re = re.compile(r"\[FORMULA_IMAGE_\d+\]|\[FORMULA_MISSING\]")
        latex_count = 0
        placeholder_count = 0
        def _record_text_has_latex(*parts):
            joined = "\n".join(str(p or "") for p in parts)
            return bool(latex_re.search(joined))
        for ch in (data or {}).get("chapters", []) or []:
            for sec in (ch or {}).get("sections", []) or []:
                for concept in (sec or {}).get("concepts", []) or []:
                    concept_has_latex = _record_text_has_latex(
                        concept.get("concept_description", ""),
                        concept.get("concept_paragraph", ""),
                    )
                    if concept_has_latex:
                        latex_count += 1
                    for ex in (concept or {}).get("examples", []) or []:
                        txt = str((ex or {}).get("problem_text", "") or "")
                        if _record_text_has_latex(
                            ex.get("problem_text", ""),
                            ex.get("problem", ""),
                            ex.get("correct_answer", ""),
                            ex.get("answer", ""),
                            ex.get("detailed_solution", ""),
                            ex.get("solution", ""),
                        ):
                            latex_count += 1
                        if placeholder_re.search(txt):
                            placeholder_count += 1
                    for pq in (concept or {}).get("practice_questions", []) or []:
                        txt = str((pq or {}).get("problem_text", "") or "")
                        if _record_text_has_latex(
                            pq.get("question", ""),
                            pq.get("problem_text", ""),
                            pq.get("answer", ""),
                            pq.get("solution", ""),
                        ):
                            latex_count += 1
                        if placeholder_re.search(txt):
                            placeholder_count += 1
        return latex_count, placeholder_count

    records_with_latex, records_with_placeholder = _count_latex_and_placeholder_records(parsed_data)
    
    # [NEW] 瑼?閫??????
    filename_meta = parse_textbook_filename_metadata(source_file_path) if source_file_path else {}
    
    # [NEW] ??蝯??啣?撠?璈 (Structure Map Alignment)
    structure_meta = None
    structure_alignment_failed = False
    volume_val = str(curriculum_info.get('volume', ''))
    curr_val = str(curriculum_info.get('curriculum', ''))
    if filename_meta.get('section_code') and curr_val == 'vocational' and 'B' in volume_val:
        struct_map = get_structure_map(curr_val, volume_val)
        if struct_map:
            structure_meta = struct_map.get_metadata(filename_meta['section_code'])
            if structure_meta:
                current_app.logger.info(f"[STRUCTURE_MAP] Aligned to: {structure_meta}")
            else:
                current_app.logger.warning(f"[STRUCTURE_MAP] No match for {filename_meta['section_code']}")
                structure_alignment_failed = True
    
    if filename_meta:
        current_app.logger.info(f"[FILENAME_META] parsed: {filename_meta}")

    prefix_map = {
        'junior_high': 'jh_',
        'general': 'gh_',
        'vocational': 'vh_'
    }
    curriculum = curriculum_info.get('curriculum', '')
    volume = str(curriculum_info.get('volume', '')).strip()
    subject, vol_num = parse_volume(volume)
    is_vocational_math = curriculum == 'vocational' and subject is not None and vol_num is not None
    is_vocational_mathb = is_vocational_math and subject == 'B'
    prefix = prefix_map.get(curriculum, '')

    # [V2.6] ?擃摮?B 蝟餃?嚗?澆?朣???暺?
    existing_anchor_section = None
    if is_vocational_mathb and filename_meta.get('section_code') and not outline_only:
        s_code = filename_meta['section_code']
        # 撠?Ｘ??桅?蝭暺?(靘? 1-1 xxx)
        existing_anchor_section = SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curriculum,
            SkillCurriculum.volume == volume,
            SkillCurriculum.section.like(f"{s_code} %")
        ).first()
        
        if existing_anchor_section:
            current_app.logger.info(f"[ALIGNMENT] Found existing anchor section: {existing_anchor_section.section}")
            if not structure_meta:
                structure_meta = {}
            # 撘瑕撠?structure_meta 鋆??Ｘ?璅?鞈?嚗??蝥?銴遣蝡?璅?銝???
            structure_meta['chapter_title'] = existing_anchor_section.chapter
            structure_meta['section_title'] = existing_anchor_section.section
            # 璅?撠???嚗??蝥粥??filename_meta fallback
            structure_alignment_failed = False
        else:
            # ?曆??唳??暺?璅?撠?憭望?
            message = f"Missing aligned section for code {s_code}; fallback may be used."
            current_app.logger.warning(f"[ALIGNMENT] {message}")
            queue.put(f"WARNING: {message}")
            structure_alignment_failed = True

    def _extract_title_number(text):
        if not text:
            return None
        match = re.search(r'(\d+)', str(text))
        return int(match.group(1)) if match else None

    def _sq_field_for_hash(value):
        raw = str(value or "")
        if converted_latex_import:
            text = raw
        else:
            text = normalize_math_text(raw)
        return re.sub(r"\s+", " ", text.replace("[FORMULA_MISSING]", "[FORMULA_TOKEN]")).strip()

    def _normalize_problem_hash(problem_text, sub_questions=None, source_type="", title=""):
        if converted_latex_import:
            normalized = re.sub(r"\s+", " ", str(problem_text or "")).strip()
        else:
            normalized = normalize_math_text(str(problem_text or ""))
        # Treat [FORMULA_IMAGE_N] and [FORMULA_MISSING] as same placeholder class
        # to prevent duplicate imports caused only by placeholder token style.
        normalized = re.sub(r"\[FORMULA_IMAGE_\d+\]", "[FORMULA_TOKEN]", normalized)
        normalized = normalized.replace("[FORMULA_MISSING]", "[FORMULA_TOKEN]")
        normalized = normalized.replace("[WORD_EQUATION_UNPARSED]", "[FORMULA_TOKEN]")
        normalized = re.sub(r"\s+", " ", normalized).strip()
        sq_norm = []
        for sq in sub_questions or []:
            if not isinstance(sq, dict):
                continue
            sq_norm.append(
                {
                    "label": str(sq.get("label", "") or "").strip(),
                    "problem": _sq_field_for_hash(sq.get("problem", "")),
                    "answer": _sq_field_for_hash(sq.get("answer", "")),
                    "solution": _sq_field_for_hash(sq.get("solution", "")),
                }
            )
        payload = {
            "source_type": str(source_type or "").strip().lower(),
            "title": str(title or "").strip(),
            "problem": normalized,
            "sub_questions": sq_norm,
        }
        return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    def validate_problem_formula_not_hallucinated(item_title: str, item: dict, problem_text: str, raw_block: str):
        text = str(problem_text or "")
        block = str(raw_block or "")
        has_placeholder = bool(
            re.search(r"\[FORMULA_MISSING\]|\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]|\[UNREADABLE_FORMULA\]", block)
        )
        if is_docx_source:
            current_app.logger.info(f"[DOCX FORMULA SOURCE] title={item_title} raw_block={block[:240]}")
        has_problem_placeholder = bool(
            re.search(r"\[FORMULA_MISSING\]|\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]|\[UNREADABLE_FORMULA\]", text)
        )
        if has_placeholder:
            current_app.logger.warning(f"[DOCX FORMULA WARNING] formula placeholder found title={item_title}")
        if has_placeholder or has_problem_placeholder:
            item["needs_review"] = True
            item["needs_formula_review"] = True
            item["formula_missing"] = True
        if has_placeholder and _contains_perm_comb_formula(text):
            has_ocr_source = bool(item.get("formula_ocr_source"))
            if not has_ocr_source:
                if is_answer_blank_placeholder_context(block, text):
                    normalized_text, blank_meta = normalize_fill_blank_artifacts(text)
                    item["has_answer_blank"] = True
                    item["question_format"] = "fill_blank"
                    item["needs_review"] = True
                    item["needs_formula_review"] = False
                    item["formula_missing"] = False
                    item["formula_hallucination_risk"] = False
                    logs = item.get("repair_log", [])
                    if not isinstance(logs, list):
                        logs = [str(logs)]
                    logs.append("formula placeholders treated as answer blanks")
                    logs.extend(blank_meta.get("reasons", []))
                    item["repair_log"] = logs
                    current_app.logger.info(
                        f"[DOCX FORMULA BLANK] title={item_title} treat placeholders as answer blank"
                    )
                    return normalized_text
                current_app.logger.warning(f"[DOCX FORMULA WARNING] formula missing before AI title={item_title}")
                fallback_text = text
                fallback_text = re.sub(
                    r"(?:\{\s*\}\s*\^\s*\{?\s*\d+\s*\}?\s*[PC]\s*_\s*\{?\s*\d+\s*\}?|"
                    r"[PC]\s*\^\s*\{?\s*\d+\s*\}?\s*_\s*\{?\s*\d+\s*\}?|"
                    r"[PC]\s*_\s*\{?\s*\d+\s*\}?\s*\^\s*\{?\s*\d+\s*\}?|"
                    r"\b[PC]\s*\(\s*\d+\s*,\s*\d+\s*\))",
                    "[FORMULA_MISSING]",
                    fallback_text,
                )
                item["needs_review"] = True
                item["needs_formula_review"] = True
                item["formula_missing"] = True
                item["formula_hallucination_risk"] = True
                item["parse_warning"] = "formula generated by AI without source"
                if re.search(r"$^", fallback_text):
                    item["problem_unusable"] = True
                return fallback_text
        if has_placeholder and not _contains_perm_comb_formula(text):
            fallback_text = text
            if "[FORMULA_MISSING]" not in fallback_text:
                fallback_text = f"{fallback_text} [FORMULA_MISSING]".strip()
            item["needs_review"] = True
            item["needs_formula_review"] = True
            item["formula_missing"] = True
            if re.search(r"$^", fallback_text):
                item["problem_unusable"] = True
            return fallback_text
        return text

    def extract_formula_images_for_question_block(item_title: str):
        """Legacy hook kept for compatibility; formula OCR is metadata-only now.

        OCR fallback is handled in _build_docx_formula_assets_metadata after the
        formula asset has a readable png/jpeg display_path or converted_path.
        This helper intentionally does not return OCR text for problem_text
        replacement.
        """
        _ = item_title
        return []

    def _build_source_description(title, source_type, linked_example_title=None, needs_review=False, dedupe_hash="", section_context=None):
        title_text = str(title or "").strip() or "untitled"
        parts = [f"source_type={source_type}"]
        if section_context:
            parts.append(f"section={section_context}")
        if linked_example_title:
            parts.append(f"linked_example={linked_example_title}")
        if needs_review:
            parts.append("needs_review=true")
        if dedupe_hash:
            parts.append(f"dedupe={dedupe_hash}")
        return f"{title_text} [{' | '.join(parts)}]"

    def _infer_linked_example_title(practice_title, linked_example_title, saved_titles, needs_review):
        linked = str(linked_example_title or "").strip() or None
        review = bool(needs_review)
        if linked:
            return linked, review
        practice_num = _extract_title_number(practice_title)
        if practice_num is not None:
            inferred = f"靘?{practice_num}"
            if inferred in saved_titles:
                return inferred, review
            if saved_titles:
                return saved_titles[-1], True
            return None, True
        if saved_titles:
            return saved_titles[-1], True
        return None, True

    def _build_image_metadata(
        question_title,
        question_text,
        chapter_title,
        section_title,
        source_type,
        question_code,
        force_has_image=False,
        image_description="",
        source_page=None,
        page_index=None,
        item_payload=None,
    ):
        has_formula_image_placeholder = bool(re.search(r"\[FORMULA_IMAGE_\d+\]", str(question_text or "")))
        if not force_has_image and not has_formula_image_placeholder and not question_needs_image(question_text, ai_has_image=force_has_image):
            return None
        reason = image_description or detect_image_reason(question_text)
        current_app.logger.info(f"[QUESTION IMAGE] needs image title={question_title} source_page={source_page}")
        if queue is not None:
            queue.put(f"INFO: [QUESTION IMAGE] needs image title={question_title} source_page={source_page}")

        metadata = {
            "has_image": True,
            "needs_image_review": True,
            "image_assets": [],
        }
        if has_formula_image_placeholder:
            metadata["needs_formula_review"] = True
            metadata["formula_asset_type"] = "image_formula"
        infer_item = dict(item_payload or {})
        infer_item.setdefault("source_description", question_title)
        infer_item.setdefault("problem_text", question_text)
        infer_item.setdefault("has_image", bool(force_has_image))
        infer_item.setdefault("image_description", image_description or "")
        infer_item["source_page"] = source_page
        infer_item["page_index"] = page_index
        inferred_source_page, infer_reason = infer_source_page_for_question(
            infer_item,
            extracted_pages=content_by_page or {},
            section_title=section_title,
            concept_name=concept_name,
        )
        if inferred_source_page is not None and infer_reason != "explicit_source_page":
            current_app.logger.info(
                f"[QUESTION IMAGE] inferred source_page title={question_title} source_page={inferred_source_page} reason={infer_reason}"
            )
            if queue is not None:
                queue.put(
                    f"INFO: [QUESTION IMAGE] inferred source_page title={question_title} source_page={inferred_source_page} reason={infer_reason}"
                )

        if inferred_source_page is None:
            metadata["image_warning"] = "missing_source_page"
            current_app.logger.info(f"[QUESTION IMAGE] missing image asset title={question_title} reason=missing_source_page")
            if queue is not None:
                queue.put(f"INFO: [QUESTION IMAGE] missing image asset title={question_title} reason=missing_source_page")
            return metadata

        if not is_pdf_source:
            return metadata

        page_number = int(inferred_source_page)

        rel_dir, abs_dir, chapter_id, section_id = build_question_assets_dir(
            curriculum_info, chapter_title, section_title
        )
        filename = f"page_{int(page_number):03d}.png"
        abs_path = os.path.join(abs_dir, filename)
        rel_path = os.path.join(rel_dir, filename)
        cache_key = (os.path.abspath(str(source_file_path or "")), int(page_number), os.path.abspath(abs_dir))
        try:
            if cache_key in page_image_cache and os.path.exists(page_image_cache[cache_key]):
                reused_abs = page_image_cache[cache_key]
                rel_path = os.path.relpath(reused_abs, current_app.root_path)
                current_app.logger.info(f"[QUESTION IMAGE] reused page image path={rel_path}")
                if queue is not None:
                    queue.put(f"INFO: [QUESTION IMAGE] reused page image path={rel_path}")
            else:
                render_pdf_page_to_image(source_file_path, int(page_number) - 1, abs_path, dpi=200)
                page_image_cache[cache_key] = abs_path
                current_app.logger.info(f"[QUESTION IMAGE] rendered page image path={rel_path}")
                if queue is not None:
                    queue.put(f"INFO: [QUESTION IMAGE] rendered page image path={rel_path}")
            metadata["image_assets"].append(
                make_page_image_asset(
                    reason=reason,
                    rel_image_path=rel_path,
                    page_index=int(page_number) - 1,
                )
            )
            metadata["image_assets"][0]["source_page"] = int(page_number)
            metadata["image_assets"][0]["image_description"] = image_description or ""
            if infer_reason != "explicit_source_page":
                metadata["image_assets"][0]["source_page_inferred"] = True
                metadata["image_assets"][0]["source_page_infer_reason"] = infer_reason
                metadata["needs_image_review"] = True
        except Exception as e:
            current_app.logger.warning(f"[QUESTION IMAGE] render failed question={question_title} err={e}")
        return metadata

    def _build_docx_assets_metadata(question_title, chapter_title, section_title, source_type, question_text=""):
        ctx = _DOCX_IMPORT_CONTEXT or {}
        q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
        all_candidates = _lookup_docx_question_assets(str(question_title or ""), q_assets)
        candidates = [a for a in (all_candidates or []) if str(a.get("media_kind", "image_asset")) == "image_asset"]
        if not candidates:
            combo = f"{question_title} {question_text}"
            if any(k in str(combo or "") for k in ("憒?", "?喳?", "??", "璉撘???", "?")):
                return {"has_image": True, "image_assets": [], "image_warning": "missing_docx_image_asset", "needs_review": True}
            return None
        rel_dir = build_question_asset_dir(
            curriculum=curriculum_info.get("curriculum", "unknown"),
            publisher=curriculum_info.get("publisher", "unknown"),
            volume=curriculum_info.get("volume", "unknown"),
            chapter_title=chapter_title,
            section_title=section_title,
            source_filename=os.path.basename(str(source_file_path or "")),
        )
        abs_dir = os.path.join(current_app.root_path, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        current_app.logger.info(f"[QUESTION ASSET] dir={rel_dir}")
        image_assets = []
        for idx, asset in enumerate(candidates, start=1):
            src_rel = str(asset.get("path") or "")
            ext = (os.path.splitext(src_rel)[1].lower() or ".bin").lstrip(".")
            problem_key = str(question_title or "") + "|" + str(source_type or "") + "|" + str(asset.get("block_index") or "")
            qhash = hashlib.sha1(problem_key.encode("utf-8")).hexdigest()[:8]
            filename = build_question_asset_filename(
                source_type=source_type,
                question_title=question_title,
                question_id_or_dedupe=qhash,
                fig_index=idx,
                ext=ext,
            )
            copied_abs = _copy_docx_asset_to_question_assets(src_rel, abs_dir, filename)
            if not copied_abs:
                continue
            rel_path = os.path.join(rel_dir, filename).replace("\\", "/")
            current_app.logger.info(
                f"[DOCX IMAGE] attached title={question_title} original={src_rel} question_asset={rel_path}"
            )
            needs_conv = ext in ("wmf", "emf")
            display_path = rel_path
            converted_path = None
            conv_error = None
            needs_review = False
            if needs_conv:
                png_filename = os.path.splitext(filename)[0] + ".png"
                png_abs = os.path.join(abs_dir, png_filename)
                png_rel = os.path.join(rel_dir, png_filename).replace("\\", "/")
                current_app.logger.info(f"[DOCX IMAGE] convert start input={copied_abs} output={png_abs}")
                ok, err = convert_vector_image_to_png(copied_abs, png_abs)
                if ok:
                    current_app.logger.info(f"[DOCX IMAGE] convert success output={png_abs}")
                    display_path = png_rel
                    converted_path = png_rel
                    needs_conv = False
                else:
                    current_app.logger.warning(f"[DOCX IMAGE WARNING] convert failed input={copied_abs} error={err}")
                    display_path = None
                    conv_error = err
                    needs_review = True
            image_assets.append(
                {
                    "asset_type": "word_embedded_image",
                    "source": "docx",
                    "path": rel_path,
                    "display_path": display_path,
                    "converted_path": converted_path,
                    "original_path": src_rel.replace("\\", "/"),
                    "content_type": asset.get("content_type", _guess_image_content_type(filename)),
                    "original_format": ext if ext in ("wmf", "emf") else None,
                    "needs_image_conversion": needs_conv,
                    "needs_image_review": needs_review,
                    "conversion_error": conv_error,
                    "image_attach_reason": asset.get("image_attach_reason", "image_inside_question_block"),
                }
            )
        if image_assets:
            return {"has_image": True, "image_assets": image_assets}
        return {"has_image": True, "image_assets": [], "image_warning": "missing_docx_image_asset", "needs_review": True}

    def _build_docx_formula_assets_metadata(question_title, question_text=""):
        ctx = _DOCX_IMPORT_CONTEXT or {}
        q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
        all_candidates = _lookup_docx_question_assets(str(question_title or ""), q_assets)
        formula_candidates = [a for a in (all_candidates or []) if str(a.get("media_kind", "")) == "formula_asset"]
        has_formula_placeholder = bool(re.search(r"\[FORMULA_IMAGE_\d+\]|\[FORMULA_MISSING\]", str(question_text or "")))
        if not formula_candidates and has_formula_placeholder:
            # Global conservative fallback: if this question contains formula placeholder and
            # DOCX extracted any formula assets, do not leave formula_assets empty.
            global_formula_candidates = []
            if isinstance(q_assets, dict):
                for _k, _arr in q_assets.items():
                    for _a in (_arr or []):
                        if str(_a.get("media_kind", "")) == "formula_asset":
                            aa = dict(_a)
                            aa.setdefault("mapping_status", "global_formula_fallback")
                            global_formula_candidates.append(aa)
                            # keep fallback small and deterministic
                            if len(global_formula_candidates) >= 3:
                                break
                    if len(global_formula_candidates) >= 3:
                        break
            formula_candidates = global_formula_candidates
        if not formula_candidates:
            return None
        current_app.logger.info(f"[DOCX FORMULA ASSET] attached title={question_title} count={len(formula_candidates)}")
        rel_dir_base = build_question_asset_dir(
            curriculum=curriculum_info.get("curriculum", "unknown"),
            publisher=curriculum_info.get("publisher", "unknown"),
            volume=curriculum_info.get("volume", "unknown"),
            chapter_title=chapter_title,
            section_title=section_title,
            source_filename=os.path.basename(str(source_file_path or "")),
        )
        rel_dir = os.path.join(rel_dir_base, "formula_assets").replace("\\", "/")
        abs_dir = os.path.join(current_app.root_path, rel_dir)
        os.makedirs(abs_dir, exist_ok=True)
        placeholder_tokens = re.findall(r"\[FORMULA_IMAGE_(\d+)\]", str(question_text or ""))
        raw_block = _lookup_docx_formula_block(str(question_title or ""), docx_formula_blocks)
        if not placeholder_tokens:
            placeholder_tokens = re.findall(r"\[FORMULA_IMAGE_(\d+)\]", str(raw_block or ""))
        assets = []
        ocr_enabled = bool(current_app.config.get("ENABLE_DOCX_FORMULA_OCR_FALLBACK", False))
        ocr_model = None
        for idx, a in enumerate(formula_candidates, start=1):
            src_rel = str(a.get("path") or "")
            content_type = str(a.get("content_type") or _guess_image_content_type(src_rel))
            original_format = _docx_image_original_format(src_rel, content_type)
            ext = os.path.splitext(src_rel)[1].lower().lstrip(".") or original_format or "bin"
            if ext == "jpeg":
                ext = "jpg"
            src_abs = src_rel if os.path.isabs(src_rel) else os.path.join(current_app.root_path, src_rel)
            asset_hash = ""
            if src_abs and os.path.exists(src_abs):
                try:
                    with open(src_abs, "rb") as fsrc:
                        asset_hash = hashlib.sha1(fsrc.read()).hexdigest()
                except Exception:
                    asset_hash = ""
            if not asset_hash:
                fallback_key = f"{src_rel}|{a.get('rid')}|{a.get('block_index') or idx}"
                asset_hash = hashlib.sha1(fallback_key.encode("utf-8")).hexdigest()

            token_index = int(placeholder_tokens[idx - 1]) if idx - 1 < len(placeholder_tokens) else idx
            section_code = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff_-]+", "", str(section_title or "").strip())[:24] or "section"
            title_key = _safe_title_for_filename(str(question_title or ""))[:24]
            original_name = os.path.basename(src_rel) or f"asset_{idx}.{ext}"
            filename = f"{section_code}_{title_key}_{token_index}_{asset_hash[:8]}_{original_name}"
            rel_path = formula_asset_persist_cache.get(asset_hash)
            copied_abs = None
            if not rel_path:
                copied_abs = _copy_docx_asset_to_question_assets(src_rel, abs_dir, filename)
                if copied_abs:
                    rel_path = os.path.join(rel_dir, filename).replace("\\", "/")
                    formula_asset_persist_cache[asset_hash] = rel_path

            display_path = None
            converted_path = None
            conversion_status = "persisted" if rel_path else "failed"
            conversion_error = None
            if original_format in ("png", "jpeg"):
                display_path = rel_path
                if conversion_status != "failed":
                    conversion_status = "not_required"
            elif original_format in ("wmf", "emf") and rel_path:
                copied_abs = copied_abs or os.path.join(current_app.root_path, rel_path)
                png_filename = os.path.splitext(filename)[0] + ".png"
                png_abs = os.path.join(abs_dir, png_filename)
                png_rel = os.path.join(rel_dir, png_filename).replace("\\", "/")
                try:
                    ok, err = convert_vector_image_to_png(copied_abs, png_abs)
                except Exception as exc:
                    ok, err = False, str(exc)
                if ok:
                    display_path = png_rel
                    converted_path = png_rel
                    conversion_status = "success"
                else:
                    conversion_status = "failed"
                    conversion_error = err or "conversion_failed"
            elif not rel_path:
                conversion_status = "failed"
                conversion_error = "source_asset_not_found"

            token = f"[FORMULA_IMAGE_{token_index}]"
            asset_meta = {
                "source": "docx",
                "asset_type": str(a.get("asset_type") or "word_formula_image"),
                "original_path": rel_path,
                "path": rel_path,
                "display_path": display_path,
                "content_type": content_type,
                "original_format": original_format,
                "placeholder_token": token,
                "placeholder_index": token_index,
                "persist_status": "persisted" if rel_path else "failed",
                "old_temp_path": src_rel.replace("\\", "/"),
                "asset_hash": asset_hash,
                "conversion_status": conversion_status,
                "converted_path": converted_path,
                "rid": a.get("rid"),
                "image_attach_reason": a.get("image_attach_reason"),
                "is_formula_placeholder_source": bool(a.get("is_formula_placeholder_source", False)),
            }
            if a.get("mapping_status"):
                asset_meta["mapping_status"] = a.get("mapping_status")
            if conversion_error:
                asset_meta["conversion_error"] = conversion_error
            if ocr_enabled:
                ocr_rel = converted_path or display_path
                if ocr_rel and _docx_image_original_format(ocr_rel, content_type) in ("png", "jpeg"):
                    try:
                        from PIL import Image
                        if ocr_model is None:
                            ocr_model = get_model("vision_analyzer")
                        ocr_abs = ocr_rel if os.path.isabs(ocr_rel) else os.path.join(current_app.root_path, ocr_rel)
                        with Image.open(ocr_abs) as img:
                            prompt = (
                                "Transcribe only the math formula visible in this image. "
                                "Do not solve the problem, do not add explanation, and do not infer or invent missing numbers. "
                                "If the formula is unreadable, return [UNREADABLE_FORMULA]."
                            )
                            resp = ocr_model.generate_content(
                                [prompt, img],
                                generation_config={"temperature": 0.0, "max_output_tokens": 512},
                            )
                        ocr_text = str(getattr(resp, "text", "") or "").strip()
                        if ocr_text:
                            asset_meta["formula_ocr_text"] = ocr_text
                            asset_meta["formula_ocr_source"] = ocr_rel
                            asset_meta["formula_ocr_status"] = "success"
                        else:
                            asset_meta["formula_ocr_status"] = "failed"
                    except Exception as exc:
                        asset_meta["formula_ocr_status"] = "failed"
                        asset_meta["formula_ocr_error"] = str(exc)
            assets.append(asset_meta)
        placeholders = [a["placeholder_token"] for a in assets]
        meta = {
            "formula_assets": assets,
            "formula_placeholders": placeholders,
            "needs_formula_review": True,
            "formula_missing": True,
            "needs_review": True,
        }
        if any(a.get("formula_ocr_status") for a in assets):
            meta["formula_ocr_status"] = "success" if any(a.get("formula_ocr_status") == "success" for a in assets) else "failed"
            meta["formula_ocr_text"] = [a.get("formula_ocr_text") for a in assets if a.get("formula_ocr_text")]
            meta["formula_ocr_source"] = [a.get("formula_ocr_source") for a in assets if a.get("formula_ocr_source")]
        current_app.logger.warning(f"[DOCX FORMULA WARNING] formula_asset_requires_review title={question_title}")
        return meta

    def _build_math_metadata(raw_text, standardized_meta, needs_review=False):
        confidence = 0.9
        if needs_review or standardized_meta.get("needs_review", False):
            confidence = 0.4
        auto_fill_applied = confidence >= auto_fill_threshold
        review_required = confidence < auto_fill_threshold
        meta = {
            "math_format": "standard_latex",
            "raw_problem_backup": str(raw_text or ""),
            "math_warnings": list(standardized_meta.get("warnings", [])),
            "needs_review": bool(needs_review or standardized_meta.get("needs_review", False) or review_required),
            "import_confidence": confidence,
            "auto_fill_threshold": auto_fill_threshold,
            "auto_fill_applied": bool(auto_fill_applied),
            "review_required_by_confidence": bool(review_required),
            "import_source_priority": "docx_primary",
            "optional_enrich_pdf_path": optional_enrich_pdf_path or "",
            "rollback_metadata": {
                "preserved": bool(import_policy.get("preserve_rollback_metadata", True)),
                "policy": {
                    "execution_arch": import_policy.get("execution_arch", "native"),
                    "docx_primary": bool(import_policy.get("docx_primary", True)),
                    "pdf_optional_enrich": bool(import_policy.get("pdf_optional_enrich", True)),
                    "auto_post_ocr_ai": bool(import_policy.get("auto_post_ocr_ai", True)),
                    "auto_backfill_high_confidence": bool(import_policy.get("auto_backfill_high_confidence", True)),
                    "review_low_confidence": bool(import_policy.get("review_low_confidence", True)),
                },
            },
        }
        return meta

    def _load_record_metadata(record_obj):
        raw = getattr(record_obj, "notes", None)
        if isinstance(raw, str) and raw.strip():
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, dict):
                    return parsed
            except Exception:
                return {}
        return {}

    def _dedupe_formula_assets(existing_assets, incoming_assets):
        merged = []
        seen = set()
        for arr in (existing_assets or [], incoming_assets or []):
            for a in arr or []:
                if not isinstance(a, dict):
                    continue
                key = (
                    str(a.get("original_path") or ""),
                    str(a.get("placeholder_token") or ""),
                    str(a.get("path") or ""),
                )
                if key in seen:
                    continue
                seen.add(key)
                merged.append(dict(a))
        return merged

    def _merge_duplicate_existing_record(
        existing_record,
        *,
        incoming_problem_text="",
        incoming_meta=None,
        incoming_correct_answer="",
        incoming_detailed_solution="",
        title="",
    ):
        """Merge richer duplicate payload into existing textbook_examples row.

        Returns (changed: bool, reason: str).
        """
        nonlocal merge_guard_kept_existing, merge_guard_updated_incoming
        changed = False
        reasons = []
        incoming_meta = dict(incoming_meta or {})
        existing_meta = _load_record_metadata(existing_record)

        existing_formula_assets = existing_meta.get("formula_assets", []) if isinstance(existing_meta, dict) else []
        incoming_formula_assets = incoming_meta.get("formula_assets", []) if isinstance(incoming_meta, dict) else []
        merged_formula_assets = _dedupe_formula_assets(existing_formula_assets, incoming_formula_assets)
        if len(merged_formula_assets) > len(existing_formula_assets):
            existing_meta["formula_assets"] = merged_formula_assets
            placeholders = [a.get("placeholder_token") for a in merged_formula_assets if a.get("placeholder_token")]
            if placeholders:
                existing_meta["formula_placeholders"] = sorted({str(p) for p in placeholders})
            changed = True
            reasons.append("formula_assets")

        for flag in ("needs_review", "needs_formula_review", "formula_missing"):
            if incoming_meta.get(flag) is True and existing_meta.get(flag) is not True:
                existing_meta[flag] = True
                changed = True
                reasons.append(flag)

        existing_problem_text = str(getattr(existing_record, "problem_text", "") or "")
        new_problem_text = str(incoming_problem_text or "")
        replace_problem_text, existing_quality, incoming_quality = should_replace_problem_text(
            existing_problem_text,
            new_problem_text,
        )
        title_for_log = str(title or getattr(existing_record, "source_description", "") or "").strip()
        if replace_problem_text and new_problem_text:
            existing_record.problem_text = new_problem_text
            changed = True
            reasons.append("problem_text_incoming_better")
            current_app.logger.info(
                f"[MERGE GUARD] updated_incoming_better_problem_text title={title_for_log} "
                f"existing_score={existing_quality['score']} incoming_score={incoming_quality['score']}"
            )
            merge_guard_updated_incoming += 1
        elif new_problem_text and existing_problem_text != new_problem_text:
            current_app.logger.info(
                f"[MERGE GUARD] kept_existing_better_problem_text title={title_for_log} "
                f"existing_score={existing_quality['score']} incoming_score={incoming_quality['score']}"
            )
            merge_guard_kept_existing += 1

        existing_answer = str(getattr(existing_record, "correct_answer", "") or "").strip()
        incoming_answer = str(incoming_correct_answer or "").strip()
        if _is_low_value_import_field(existing_answer) and not _is_low_value_import_field(incoming_answer):
            existing_record.correct_answer = incoming_answer
            changed = True
            reasons.append("correct_answer_incoming_nonblank")

        existing_solution = str(getattr(existing_record, "detailed_solution", "") or "").strip()
        incoming_solution = sanitize_detailed_solution_text(str(incoming_detailed_solution or ""), max_chars=500)
        if _is_low_value_import_field(existing_solution) and not _is_low_value_import_field(incoming_solution):
            existing_record.detailed_solution = incoming_solution
            changed = True
            reasons.append("detailed_solution_incoming_nonblank")

        if changed and existing_meta:
            attach_image_metadata(existing_record, existing_meta)
        return changed, ("+".join(sorted(set(reasons))) if reasons else "metadata_merge")

    def _extract_dedupe_from_source_description(source_description_text: str) -> str:
        m = re.search(r"dedupe=([0-9a-fA-F]+)", str(source_description_text or ""))
        return str(m.group(1)).lower() if m else ""

    def _extract_title_from_source_description(source_description_text: str) -> str:
        text = str(source_description_text or "")
        return text.split(" [", 1)[0].strip()

    def _iter_scope_existing_rows(curriculum, volume, chapter, section):
        q = TextbookExample.query.filter_by(
            source_curriculum=curriculum,
            source_volume=str(volume),
            source_chapter=chapter,
            source_section=section,
        )
        if hasattr(q, "all"):
            try:
                return q.all()
            except Exception:
                pass
        rows = getattr(q, "rows", None)
        filters = getattr(q, "filters", {})
        if isinstance(rows, list):
            out = []
            for row in rows:
                if all(getattr(row, k, None) == v for k, v in (filters or {}).items()):
                    out.append(row)
            return out
        return []

    def _find_existing_duplicate_by_dedupe(curriculum, volume, chapter, section, title, dedupe_hash):
        target_title = str(title or "").strip()
        target_hash = str(dedupe_hash or "").strip().lower()
        if not target_hash:
            for row in _iter_scope_existing_rows(curriculum, volume, chapter, section):
                sd = str(getattr(row, "source_description", "") or "")
                if _extract_title_from_source_description(sd) == target_title:
                    return row
            return None
        for row in _iter_scope_existing_rows(curriculum, volume, chapter, section):
            sd = str(getattr(row, "source_description", "") or "")
            if _extract_dedupe_from_source_description(sd) != target_hash:
                continue
            row_title = _extract_title_from_source_description(sd)
            if row_title == target_title:
                return row
        for row in _iter_scope_existing_rows(curriculum, volume, chapter, section):
            sd = str(getattr(row, "source_description", "") or "")
            if _extract_dedupe_from_source_description(sd) == target_hash:
                return row
        for row in _iter_scope_existing_rows(curriculum, volume, chapter, section):
            sd = str(getattr(row, "source_description", "") or "")
            if _extract_title_from_source_description(sd) == target_title:
                return row
        return None

    def _determine_target_skill_id(base_clean_en_id, section_title, concept_name, example_obj):
        target_clean_en_id = base_clean_en_id
        if str(target_clean_en_id or "") == "DispersionAndLinearTransformation":
            target_clean_en_id = "DispersionMeasures"
        if str(target_clean_en_id or "") == "ProbabilityOperations":
            target_clean_en_id = "ProbabilityProperties"
        if is_vocational_mathb and is_non_skill_bucket(concept_name, base_clean_en_id):
            remapped_33_en_id = remap_mathb33_non_skill_examples(
                section_title=section_title,
                concept_name=concept_name,
                clean_en_id=base_clean_en_id,
                example=example_obj
            )
            if remapped_33_en_id:
                target_clean_en_id = remapped_33_en_id
            remapped_32_en_id = remap_mathb32_non_skill_examples(
                section_title=section_title,
                concept_name=concept_name,
                clean_en_id=base_clean_en_id,
                example=example_obj
            )
            if remapped_32_en_id:
                target_clean_en_id = remapped_32_en_id
            remapped_31_en_id = remap_mathb31_non_skill_examples(
                section_title=section_title,
                concept_name=concept_name,
                clean_en_id=base_clean_en_id,
                example=example_obj
            )
            if remapped_31_en_id:
                target_clean_en_id = remapped_31_en_id
            remapped_21_en_id = remap_mathb21_non_skill_examples(
                section_title=section_title,
                concept_name=concept_name,
                clean_en_id=base_clean_en_id,
                example=example_obj
            )
            if remapped_21_en_id:
                target_clean_en_id = remapped_21_en_id
            remapped_en_id = remap_mathb_non_skill_examples(
                section_title=section_title,
                concept_name=concept_name,
                clean_en_id=base_clean_en_id,
                example=example_obj
            )
            if remapped_en_id:
                target_clean_en_id = remapped_en_id

        explicit_skill_id = str(example_obj.get("skill_id", "") or "").strip()
        if explicit_skill_id:
            return explicit_skill_id

        if is_vocational_math:
            return normalize_vocational_math_skill_id(subject, vol_num, target_clean_en_id)
        return f"{prefix}{target_clean_en_id}"

    try:
        current_app.logger.info(" -> ??撖怠鞈?摨?..")
        queue.put("INFO: -> ??撖怠鞈?摨?..")
        chapters = parsed_data.get('chapters', [])
        
        for chapter_data in chapters:
            raw_chapter = chapter_data.get('chapter_title', '?芸??蝭').strip()
            
            # === ?靽格迤 1嚗??摮蒂璅???蝭?迂 ===
            match = re.search(r'(\d+)', raw_chapter)
            if match:
                chapter_num = int(match.group(1))
            else:
                chapter_num = 999 

            # [V2.2] ?芸?雿輻??蝯??啣?撠?
            if structure_meta and structure_meta.get('chapter_index'):
                chapter_num = structure_meta['chapter_index']
                chapter_title = structure_meta['chapter_title']
            elif is_vocational_mathb and filename_meta.get('chapter_index'):
                chapter_num = filename_meta['chapter_index']
                chapter_title = filename_meta.get('chapter_title', raw_chapter)
            else:
                chapter_title = raw_chapter

            if is_vocational_mathb:
                # ?擃摮睬蝟餃?嚗?蝙?冽???瑽??
                if structure_meta and structure_meta.get('chapter_title'):
                    chapter_title = structure_meta['chapter_title']
                else:
                    chapter_title = raw_chapter
            elif match:
                clean_title = re.sub(r'^(\u55ae\u5143|Unit|\u7b2c)?\s*\d+\s*(\u55ae\u5143|\u7ae0)?\s*', '', raw_chapter).strip()
                chapter_title = f"第{chapter_num}章 {clean_title}" if clean_title else f"第{chapter_num}章"
            else:
                chapter_title = raw_chapter

            sections = chapter_data.get('sections', [])
            
            # ?葉??撠?? (靽???頛?雿?典?銝剜??瑁?)
            if curriculum_info.get('curriculum') == 'junior_high':
                chapter_title = chapter_title.replace('\n', ' ').strip()
                chapter_title = re.sub(r'^(?:Chapter|Unit|蝚?\s*(\d+)(?:\s*蝡??\s*', r'\1 ', chapter_title).strip()
                if chapter_title.isdigit():
                    try:
                        existing_chapter = SkillCurriculum.query.filter_by(
                            curriculum=curriculum_info['curriculum'],
                            grade=int(curriculum_info['grade']),
                            volume=curriculum_info['volume']
                        ).filter(SkillCurriculum.chapter.like(f"{chapter_title} %")).first()
                        if existing_chapter:
                            chapter_title = existing_chapter.chapter
                    except Exception:
                        pass
            
            for section_data in sections:
                section_title = section_data.get('section_title', '') or ''
                
                # [V2.2] ?芸?雿輻??蝯??啣?撠?
                if structure_meta and structure_meta.get('section_title'):
                    section_title = structure_meta['section_title']
                
                # [NEW] 餈質馱蝡???蝭???
                section_exists = SkillCurriculum.query.filter_by(
                    curriculum=curriculum_info.get('curriculum'),
                    volume=str(curriculum_info.get('volume', 1)),
                    chapter=chapter_title,
                    section=section_title
                ).first()
                if not section_exists:
                    sections_created += 1
                else:
                    sections_updated += 1
                
                # 蝪∪餈質馱蝡? (甇方?蝪∪???嚗?蝭?賣?閫貊雿????望擃?
                chapter_exists_any = SkillCurriculum.query.filter_by(
                    curriculum=curriculum_info.get('curriculum'),
                    volume=str(curriculum_info.get('volume', 1)),
                    chapter=chapter_title
                ).first()
                if not chapter_exists_any:
                    chapters_created += 1 # ?ㄐ?嗅祕?臬遣蝡?銝???急迨蝡??蝝??
                else:
                    chapters_updated += 1
                if is_vocational_mathb and (
                    ("3-1" in str(section_title or ""))
                    or ("3-2" in str(section_title or ""))
                    or ("3-3" in str(section_title or ""))
                ):
                    chapter_title = chapter_title.replace("第4章", "第3章")
                concepts = section_data.get('concepts', [])
                
                for concept_order, concept in enumerate(concepts, start=1):
                    concept_name = concept.get('concept_name', '未命名概念').strip()
                    concept_en_id = concept.get('concept_en_id', 'Unknown')
                    concept_paragraph = concept.get('concept_paragraph', '未提供內容').strip()
                    
                    clean_en_id = re.sub(r'[^a-zA-Z0-9]', '', concept_en_id)
                    if clean_en_id == "DispersionAndLinearTransformation":
                        clean_en_id = "DispersionMeasures"
                    order_index = concept_order
                    skip_skill_creation = is_non_skill_bucket(concept_name, clean_en_id)

                    if is_vocational_mathb and clean_en_id == "NumberOfPositiveDivisors":
                        clean_en_id = "MultiplicationPrinciple"
                        concept_name = "乘法原理"
                        concept_paragraph = "乘法原理"

                    if is_vocational_mathb:
                        mathb_1_1_order_map = {
                            "TreeDiagramCounting": 1,
                            "AdditionPrinciple": 2,
                            "MultiplicationPrinciple": 3,
                            "FactorialNotation": 4,
                        }
                        order_index = mathb_1_1_order_map.get(clean_en_id, concept_order)
                    if is_vocational_math:
                        final_skill_id = normalize_vocational_math_skill_id(subject, vol_num, clean_en_id)
                        skill_id_msg = f"INFO: vocational math skill_id = {final_skill_id}"
                        current_app.logger.info(skill_id_msg)
                        queue.put(skill_id_msg)
                    else:
                        final_skill_id = f"{prefix}{clean_en_id}"
                    
                    # [V2.5] ?遣蝡?瑽芋撘?撘瑕雿輻 PlaceholderSkill 銝西歲???株???賜敦蝭
                    if outline_only:
                        final_skill_id = f"{prefix}OutlinePlaceholder"
                        # 蝣箔? Placeholder SkillInfo 摮
                        if not SkillInfo.query.get(final_skill_id):
                            db.session.add(SkillInfo(
                                skill_id=final_skill_id,
                                skill_ch_name="[Outline] Placeholder",
                                skill_en_name="OutlinePlaceholder",
                                is_active=False
                            ))
                            skills_processed += 1
                        
                        if final_skill_id not in processed_skill_ids:
                            processed_skill_ids.append(final_skill_id)
                        
                        # 撱箇? SkillCurriculum
                        existing_curr = SkillCurriculum.query.filter_by(
                            skill_id=final_skill_id,
                            chapter=chapter_title,
                            section=section_title
                        ).first()
                        if not existing_curr:
                            new_curr = SkillCurriculum(
                                skill_id=final_skill_id,
                                curriculum=curriculum_info.get('curriculum'),
                                grade=int(curriculum_info.get('grade', 10)),
                                volume=str(curriculum_info.get('volume', 1)),
                                chapter=chapter_title,
                                section=section_title,
                                paragraph=concept_paragraph,
                                display_order=(
                                    structure_meta.get('display_order_base', chapter_num * 10000)
                                    if structure_meta
                                    else (chapter_num * 10000 + (int(filename_meta.get('section_index') or 0) * 100))
                                ) + concept_order
                            )
                            db.session.add(new_curr)
                            curriculums_added += 1
                        continue # 頝喲?敺?????桀?亥???賣??

                    if not skip_skill_creation:
                        # === SkillInfo ?啣?/?湔 (蝬剜???頛? ===
                        existing_skill = SkillInfo.query.get(final_skill_id)
                        if not existing_skill:
                            new_skill = SkillInfo(
                                skill_id=final_skill_id,
                                skill_en_name=clean_en_id,
                                skill_ch_name=concept_name,
                                category = section_title,
                                description=concept.get('concept_description', ''),
                                input_type='text',
                                gemini_prompt=f"Generate math problems about {concept_name}.",
                                is_active=True,
                                order_index=order_index
                            )
                            db.session.add(new_skill)
                            skills_processed += 1
                            processed_skill_ids.append(final_skill_id)
                        else:
                            existing_skill.skill_en_name = clean_en_id
                            existing_skill.skill_ch_name = concept_name
                            existing_skill.category = section_title
                            existing_skill.description = concept.get('concept_description', existing_skill.description)
                            existing_skill.order_index = order_index
                            if not existing_skill.gemini_prompt:
                                existing_skill.gemini_prompt = f"Generate math problems about {concept_name}."
                        
                        # === SkillCurriculum ?啣? (?嚗??交迤蝣箇? display_order) ===
                        existing_curr = SkillCurriculum.query.filter_by(
                            skill_id=final_skill_id,
                            chapter=chapter_title,
                            section=section_title
                        ).first()
                        
                        if not existing_curr:
                            # [V2.6] ?交?擃摮睬銝?朣仃??蝳迫撱箇??啁??暺?(?踹? 1_- ??1-1_-)
                            if is_vocational_mathb and structure_alignment_failed:
                                current_app.logger.warning(f"[ALIGNMENT] Skip creating new curriculum node for {section_title}")
                            else:
                                new_curr = SkillCurriculum(
                                    skill_id=final_skill_id,
                                    curriculum=curriculum_info.get('curriculum'),
                                    grade=int(curriculum_info.get('grade', 10)),
                                    volume=str(curriculum_info.get('volume', 1)),
                                    chapter=chapter_title,
                                    section=section_title,
                                    paragraph=concept_paragraph,
                                    display_order=(
                                        structure_meta.get('display_order_base', chapter_num * 10000)
                                        if structure_meta
                                        else (chapter_num * 10000 + (int(filename_meta.get('section_index') or 0) * 100))
                                    ) + skills_processed
                                )
                                db.session.add(new_curr)
                                curriculums_added += 1
                    else:
                        queue.put(
                            f"INFO: skip skill creation for concept='{concept_name}' ({clean_en_id}); keep examples import."
                        )

                    # === 憿撖怠嚗???source_type 甇???????頝舐 ===
                    saved_example_skill_map = {}
                    saved_example_order = []
                    saved_example_titles = []
                    concept_known_pages = []
                    for _bucket in ("examples", "practice_questions"):
                        for _q in concept.get(_bucket, []) or []:
                            if not isinstance(_q, dict):
                                continue
                            sp = _q.get("source_page")
                            pi = _q.get("page_index")
                            try:
                                if sp is not None:
                                    concept_known_pages.append(int(sp))
                                elif pi is not None:
                                    concept_known_pages.append(int(pi) + 1)
                            except Exception:
                                continue
                    for ex_idx, ex in enumerate(concept.get('examples', []), start=1):
                        problem_text = ex.get('problem_text')
                        if not problem_text:
                            continue

                        example_title = get_question_title(ex) or "靘?"
                        detected_titles.append(example_title)
                        source_type = normalize_source_type_by_title(ex, default_source_type="textbook_example")

                        # Skip section exposition entries (e.g. title='隤脫??批捆').
                        if source_type == "section_exposition":
                            current_app.logger.info(
                                f"[SKIP] section_exposition title={example_title!r} not saved as textbook_example"
                            )
                            continue

                        target_skill_id = _determine_target_skill_id(clean_en_id, section_title, concept_name, ex)

                        sub_questions = ex.get("sub_questions", []) if isinstance(ex.get("sub_questions", []), list) else []
                        db_problem_text_raw = _render_sub_questions_problem(problem_text, sub_questions)
                        segmented_text, seg_meta = segment_question_block_text(db_problem_text_raw, question_title=example_title)
                        if seg_meta.get("changed"):
                            logs = ex.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            if seg_meta.get("reason"):
                                logs.append(seg_meta.get("reason"))
                            ex["repair_log"] = logs
                            db_problem_text_raw = segmented_text
                        block_kind = classify_non_question_block(db_problem_text_raw)
                        if block_kind in ("concept_explanation", "figure_caption", "narration"):
                            logs = ex.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.append(f"detected {block_kind}, not imported as textbook_example")
                            ex["repair_log"] = logs
                            current_app.logger.info(
                                f"[DOCX BLOCK FILTER] skip example title={example_title} kind={block_kind}"
                            )
                            continue
                        converted_latex_mode = (
                            str((_DOCX_IMPORT_CONTEXT or {}).get("docx_formula_source_mode", "") or "").strip()
                            == "converted_docx_latex"
                        )
                        if not converted_latex_mode:
                            blank_norm_text, blank_meta = normalize_fill_blank_artifacts(db_problem_text_raw)
                            perm_norm_text, perm_meta = normalize_permutation_combination_notation(
                                blank_norm_text,
                                volume=str(curriculum_info.get("volume", "") or ""),
                                section_title=section_title,
                            )
                            db_problem_text_raw = perm_norm_text
                            if blank_meta.get("changed") or perm_meta.get("changed"):
                                logs = ex.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(blank_meta.get("reasons", []))
                                logs.extend(perm_meta.get("reasons", []))
                                ex["repair_log"] = logs
                        raw_formula_block = _lookup_docx_formula_block(str(example_title), docx_formula_blocks)
                        if raw_formula_block and re.search(r"\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]", raw_formula_block):
                            ex["needs_review"] = True
                            ex["needs_formula_review"] = True
                            ex["formula_missing"] = True
                        db_problem_text_raw = validate_problem_formula_not_hallucinated(
                            example_title, ex, db_problem_text_raw, raw_formula_block
                        )
                        if not converted_latex_mode:
                            repaired_text, repair_meta = repair_missing_single_variable_text(db_problem_text_raw)
                            if repair_meta.get("applied"):
                                db_problem_text_raw = repaired_text
                                logs = ex.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.append(repair_meta.get("reason"))
                                ex["repair_log"] = logs
                            elif repair_meta.get("reason") == "non_unique_candidate_variable":
                                ex["needs_review"] = True
                        if converted_latex_mode:
                            latex_fix = normalize_converted_docx_latex_text(db_problem_text_raw)
                            db_problem_text = str(latex_fix.get("text", db_problem_text_raw) or db_problem_text_raw)
                            ex_math_meta = {}
                            current_app.logger.info(
                                "[FORMULA NORMALIZE SKIP] converted_docx_latex_preserve_latex=true field=problem_text"
                            )
                            if latex_fix.get("changes"):
                                current_app.logger.info(
                                    f"[LATEX INLINE NORMALIZE] title={example_title} changes={len(latex_fix.get('changes', []))}"
                                )
                        else:
                            db_problem_text_norm = normalize_math_text(db_problem_text_raw)
                            db_problem_text, ex_math_meta = standardize_problem_latex(db_problem_text_norm)
                        if not converted_latex_mode:
                            db_problem_text_post, post_perm_meta = normalize_permutation_combination_notation(
                                db_problem_text,
                                volume=str(curriculum_info.get("volume", "") or ""),
                                section_title=section_title,
                            )
                            if post_perm_meta.get("changed"):
                                logs = ex.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(post_perm_meta.get("reasons", []))
                                ex["repair_log"] = logs
                                current_app.logger.info(
                                    f"[PERM COMB POST NORMALIZE] title={example_title} before={db_problem_text} after={db_problem_text_post}"
                                )
                            db_problem_text, post_blank_meta = normalize_fill_blank_artifacts(db_problem_text_post)
                            if post_blank_meta.get("changed"):
                                logs = ex.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(post_blank_meta.get("reasons", []))
                                ex["repair_log"] = logs
                        db_problem_text, prob_meta = normalize_probability_event_notation(db_problem_text)
                        if prob_meta.get("changed"):
                            logs = ex.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.extend(prob_meta.get("reasons", []))
                            ex["repair_log"] = logs
                        if re.search(r"P\(|C\(|P\^|C\^|\{\}\^|\{\}\^\{\\\(|\\\(\{\}\^|\\\(\{\}\^\{", str(db_problem_text_raw or "")):
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={example_title} before={db_problem_text_norm}")
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={example_title} after={db_problem_text}")
                        db_answer = _render_sub_questions_answer(ex.get('correct_answer', ''), sub_questions)
                        db_solution = _render_sub_questions_solution(ex.get('detailed_solution', ''), sub_questions)
                        needs_review = bool(ex.get("needs_review", False)) or structure_alignment_failed
                        ex["problem_text"] = db_problem_text
                        ex = validate_problem_block_purity(ex)
                        needs_review = bool(ex.get("needs_review", False)) or structure_alignment_failed
                        linked_example_title = None
                        if source_type == "in_class_practice":
                            linked_example_title, needs_review = _infer_linked_example_title(
                                example_title,
                                ex.get("linked_example_title"),
                                saved_example_titles,
                                needs_review,
                            )
                            ex["linked_example_title"] = linked_example_title
                        dedupe_hash = _normalize_problem_hash(
                            db_problem_text, sub_questions=sub_questions, source_type=source_type, title=example_title
                        )
                        source_description = _build_source_description(
                            example_title,
                            source_type=source_type,
                            linked_example_title=linked_example_title,
                            needs_review=needs_review,
                            dedupe_hash=dedupe_hash
                        )

                        existing_ex = TextbookExample.query.filter_by(
                            skill_id=target_skill_id,
                            source_curriculum=curriculum_info.get('curriculum'),
                            source_volume=str(curriculum_info.get('volume')),
                            source_chapter=chapter_title,
                            source_section=section_title,
                            source_description=source_description
                        ).first()
                        if not existing_ex:
                            existing_ex = TextbookExample.query.filter_by(
                                source_curriculum=curriculum_info.get('curriculum'),
                                source_volume=str(curriculum_info.get('volume')),
                                source_chapter=chapter_title,
                                source_section=section_title,
                                source_description=source_description
                            ).first()
                        if not existing_ex:
                            existing_ex = _find_existing_duplicate_by_dedupe(
                                curriculum_info.get('curriculum'),
                                curriculum_info.get('volume'),
                                chapter_title,
                                section_title,
                                example_title,
                                dedupe_hash,
                            )

                        if source_type == "textbook_example":
                            title_num = _extract_title_number(example_title)
                            if title_num is not None:
                                saved_example_skill_map[title_num] = target_skill_id
                            saved_example_order.append((example_title, target_skill_id))
                            saved_example_titles.append(example_title)

                        if existing_ex:
                            duplicate_meta = {}
                            duplicate_formula_meta = None
                            if is_docx_source:
                                duplicate_formula_meta = _build_docx_formula_assets_metadata(
                                    example_title, question_text=db_problem_text
                                )
                            if duplicate_formula_meta:
                                duplicate_meta.update(duplicate_formula_meta)
                            for k in ("needs_review", "needs_formula_review", "formula_missing"):
                                if ex.get(k) is True:
                                    duplicate_meta[k] = True

                            changed, _reason = _merge_duplicate_existing_record(
                                existing_ex,
                                incoming_problem_text=db_problem_text,
                                incoming_meta=duplicate_meta,
                                incoming_correct_answer=db_answer,
                                incoming_detailed_solution=db_solution,
                                title=example_title,
                            )
                            if changed:
                                updated_duplicates += 1
                                current_app.logger.info(
                                    f"[PRACTICE IMPORT] updated duplicate title={example_title} reason=metadata_merge"
                                )
                            else:
                                duplicates_skipped_count += 1
                                current_app.logger.info(
                                    f"[PRACTICE IMPORT] skipped duplicate title={example_title} reason=dedupe_match"
                                )
                            continue

                        try:
                            difficulty_level = int(ex.get('difficulty_level', 1))
                        except Exception:
                            difficulty_level = 1

                        new_ex = TextbookExample(
                            skill_id=target_skill_id,
                            source_curriculum=curriculum_info.get('curriculum'),
                            source_volume=str(curriculum_info.get('volume')),
                            source_chapter=chapter_title,
                            source_section=section_title,
                            source_paragraph=concept_name,
                            source_description=source_description,
                            problem_text=db_problem_text,
                            problem_type=(structure_meta.get('type') if structure_meta and structure_meta.get('type') else ex.get('problem_type', source_type or 'calculation')),
                            correct_answer=db_answer,
                            detailed_solution=sanitize_detailed_solution_text(db_solution, max_chars=500),
                            difficulty_level=difficulty_level
                        )
                        chapter_rel_dir, _, chapter_id, section_id = build_question_assets_dir(
                            curriculum_info, chapter_title, section_title
                        )
                        _ = chapter_rel_dir  # keep naming consistent, not used here
                        example_code = build_question_code(chapter_id, section_id, "example", ex_idx)
                        image_meta = None
                        if is_pdf_source:
                            image_meta = _build_image_metadata(
                                question_title=example_title,
                                question_text=db_problem_text,
                                chapter_title=chapter_title,
                                section_title=section_title,
                                source_type=source_type,
                                question_code=example_code,
                                force_has_image=bool(ex.get("has_image", False)),
                                image_description=str(ex.get("image_description", "") or ""),
                                source_page=ex.get("source_page"),
                                page_index=ex.get("page_index"),
                                item_payload={**ex, "_neighbor_source_pages": concept_known_pages},
                            )
                        if is_docx_source:
                            docx_meta = _build_docx_assets_metadata(
                                example_title, chapter_title, section_title, source_type, question_text=db_problem_text
                            )
                            if docx_meta:
                                image_meta = dict(image_meta or {})
                                image_meta.update(docx_meta)
                            if not converted_latex_mode:
                                formula_meta = _build_docx_formula_assets_metadata(example_title, question_text=db_problem_text)
                                if formula_meta:
                                    image_meta = dict(image_meta or {})
                                    image_meta.update(formula_meta)
                        if image_meta:
                            attached = attach_image_metadata(new_ex, image_meta)
                            if attached:
                                current_app.logger.info(f"{'[DOCX IMAGE]' if is_docx_source else '[QUESTION IMAGE]'} metadata attached question={example_title}")
                                if is_docx_source:
                                    img_assets = image_meta.get("image_assets", []) if isinstance(image_meta, dict) else []
                                    docx_attached_count += len(img_assets)
                                    docx_copied_to_question_assets += len(img_assets)
                                    for ia in img_assets:
                                        if ia.get("display_path"):
                                            docx_direct_display_images += 1
                                        if ia.get("original_format") in ("wmf", "emf"):
                                            docx_vector_images += 1
                                        if ia.get("converted_path"):
                                            docx_conversion_success += 1
                                        if ia.get("needs_image_conversion") is True and not ia.get("display_path"):
                                            docx_conversion_failed += 1
                                    formula_assets = image_meta.get("formula_assets", []) if isinstance(image_meta, dict) else []
                                    if formula_assets:
                                        docx_formula_assets_count += len(formula_assets)
                                        if image_meta.get("needs_formula_review"):
                                            docx_formula_needs_review_count += 1
                                    for fa in formula_assets:
                                        if fa.get("conversion_status") == "success":
                                            docx_conversion_success += 1
                                        elif fa.get("conversion_status") == "failed":
                                            docx_conversion_failed += 1
                                        elif fa.get("conversion_status") == "pending":
                                            docx_conversion_pending += 1
                            else:
                                current_app.logger.info(
                                    "[QUESTION IMAGE] detected but no metadata field available table=textbook_examples"
                                )
                        if is_docx_source and isinstance(image_meta, dict) and image_meta.get("has_image") and not image_meta.get("image_assets"):
                            reason = image_meta.get("image_warning", "unknown")
                            missing_image_questions.append((example_title, source_type, reason))
                            current_app.logger.info(
                                f"[DOCX IMAGE DEBUG] missing_image_candidate title={example_title} source_type={source_type} reason={reason}"
                            )
                        math_meta = _build_math_metadata(db_problem_text_raw, ex_math_meta, needs_review=needs_review)
                        if _is_mathb4_chart_target(section_title, target_skill_id):
                            chart_meta = _extract_chart_metadata_for_mathb4_32(db_problem_text, db_problem_text_raw)
                            if chart_meta:
                                math_meta.update(chart_meta)
                            elif re.search(r"$^", str(db_problem_text or "")):
                                ex["has_image"] = True
                                ex["needs_image_review"] = True
                                ex["needs_review"] = True
                                ex["missing_docx_image_asset"] = True
                                math_meta["needs_review"] = True
                        for k in (
                            "needs_formula_review",
                            "formula_missing",
                            "formula_hallucination_risk",
                            "parse_warning",
                            "problem_unusable",
                            "block_boundary_error",
                            "likely_concept_explanation",
                            "skill_boundary_mismatch",
                            "has_answer_blank",
                            "question_format",
                            "needs_image_review",
                            "missing_docx_image_asset",
                            "needs_table_review",
                            "repair_log",
                        ):
                            if ex.get(k) is not None:
                                math_meta[k] = ex.get(k)
                        attach_image_metadata(new_ex, math_meta)
                        if re.search(r"[PC]\s*\(|[PC]\s*\^|[PC]\s*_|[?兜嗽笨喇?菊?猾?嫖??????????", str(db_problem_text or "")):
                            current_app.logger.info(f"[DB WRITE CHECK] title={example_title} problem_text={db_problem_text}")
                        db.session.add(new_ex)
                        if source_type == "textbook_example":
                            examples_added += 1
                        else:
                            practice_questions_imported += 1
                            summary_bucket = classify_practice_source_bucket(source_type)
                            if summary_bucket == "in_class_practice":
                                in_class_practices_imported += 1
                            elif summary_bucket == "chapter_exercise":
                                chapter_exercises_imported += 1
                            elif summary_bucket == "self_assessment":
                                self_assessments_imported += 1
                            elif summary_bucket == "exam_practice":
                                exam_practices_imported += 1
                                current_app.logger.info(
                                    f"[EXAM PRACTICE IMPORT] detected title={example_title} source_type={source_type} skill_id={target_skill_id}"
                                )
                            else:
                                other_practices_imported += 1
                            if needs_review:
                                practice_questions_needs_review += 1

                    # === ?典?蝺渡?/蝺渡?憿??函?撖怠 ===
                    self_assessment_section_context = ""
                    for practice_idx, practice in enumerate(concept.get('practice_questions', []) or [], start=1):
                        if not isinstance(practice, dict):
                            continue

                        practice_title = get_question_title(practice) or "?典?蝺渡?"
                        source_type = normalize_source_type_by_title(practice, default_source_type="in_class_practice")
                        if source_type == "self_assessment":
                            context_candidate = extract_self_assessment_section_context(
                                practice_title,
                                practice.get("source_description", ""),
                                practice.get("problem_text", ""),
                                practice.get("problem", ""),
                            )
                            if context_candidate:
                                self_assessment_section_context = context_candidate

                        practice_problem = str(
                            practice.get("problem_text", "") or practice.get("problem", "") or practice.get("question", "")
                        ).strip()
                        if not practice_problem:
                            if source_type == "self_assessment":
                                practice_problem = f"{practice_title} 憿凳蝻箏仃 [FORMULA_MISSING]"
                                practice["needs_review"] = True
                                practice["needs_formula_review"] = True
                                practice["formula_missing"] = True
                                logs = practice.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.append("preserved self_assessment item with missing stem")
                                practice["repair_log"] = logs
                            else:
                                continue

                        detected_titles.append(practice_title)
                        sub_questions = practice.get("sub_questions", []) if isinstance(practice.get("sub_questions", []), list) else []
                        practice_problem_raw = _render_sub_questions_problem(practice_problem, sub_questions)
                        segmented_text, seg_meta = segment_question_block_text(practice_problem_raw, question_title=practice_title)
                        if seg_meta.get("changed"):
                            logs = practice.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            if seg_meta.get("reason"):
                                logs.append(seg_meta.get("reason"))
                            practice["repair_log"] = logs
                            practice_problem_raw = segmented_text
                        block_kind = classify_non_question_block(practice_problem_raw)
                        if block_kind in ("concept_explanation", "figure_caption", "narration"):
                            logs = practice.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.append(f"detected {block_kind}, skipped from question text")
                            practice["repair_log"] = logs
                            current_app.logger.info(
                                f"[DOCX BLOCK FILTER] skip practice title={practice_title} kind={block_kind}"
                            )
                            continue
                        converted_latex_mode = (
                            str((_DOCX_IMPORT_CONTEXT or {}).get("docx_formula_source_mode", "") or "").strip()
                            == "converted_docx_latex"
                        )
                        if not converted_latex_mode:
                            blank_norm_text, blank_meta = normalize_fill_blank_artifacts(practice_problem_raw)
                            perm_norm_text, perm_meta = normalize_permutation_combination_notation(
                                blank_norm_text,
                                volume=str(curriculum_info.get("volume", "") or ""),
                                section_title=section_title,
                            )
                            practice_problem_raw = perm_norm_text
                            if blank_meta.get("changed") or perm_meta.get("changed"):
                                logs = practice.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(blank_meta.get("reasons", []))
                                logs.extend(perm_meta.get("reasons", []))
                                practice["repair_log"] = logs
                        raw_formula_block = _lookup_docx_formula_block(str(practice_title), docx_formula_blocks)
                        if raw_formula_block and re.search(r"\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]", raw_formula_block):
                            practice["needs_review"] = True
                            practice["needs_formula_review"] = True
                            practice["formula_missing"] = True
                        practice_problem_raw = validate_problem_formula_not_hallucinated(
                            practice_title, practice, practice_problem_raw, raw_formula_block
                        )
                        if not converted_latex_mode:
                            repaired_text, repair_meta = repair_missing_single_variable_text(practice_problem_raw)
                            if repair_meta.get("applied"):
                                practice_problem_raw = repaired_text
                                logs = practice.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.append(repair_meta.get("reason"))
                                practice["repair_log"] = logs
                            elif repair_meta.get("reason") == "non_unique_candidate_variable":
                                practice["needs_review"] = True
                        if converted_latex_mode:
                            latex_fix = normalize_converted_docx_latex_text(practice_problem_raw)
                            practice_problem = str(latex_fix.get("text", practice_problem_raw) or practice_problem_raw)
                            practice_math_meta = {}
                            current_app.logger.info(
                                "[FORMULA NORMALIZE SKIP] converted_docx_latex_preserve_latex=true field=problem_text"
                            )
                            if latex_fix.get("changes"):
                                current_app.logger.info(
                                    f"[LATEX INLINE NORMALIZE] title={practice_title} changes={len(latex_fix.get('changes', []))}"
                                )
                        else:
                            practice_problem_norm = normalize_math_text(practice_problem_raw)
                            practice_problem, practice_math_meta = standardize_problem_latex(practice_problem_norm)
                        if not converted_latex_mode:
                            practice_problem_post, post_perm_meta = normalize_permutation_combination_notation(
                                practice_problem,
                                volume=str(curriculum_info.get("volume", "") or ""),
                                section_title=section_title,
                            )
                            if post_perm_meta.get("changed"):
                                logs = practice.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(post_perm_meta.get("reasons", []))
                                practice["repair_log"] = logs
                                current_app.logger.info(
                                    f"[PERM COMB POST NORMALIZE] title={practice_title} before={practice_problem} after={practice_problem_post}"
                                )
                            practice_problem, post_blank_meta = normalize_fill_blank_artifacts(practice_problem_post)
                            if post_blank_meta.get("changed"):
                                logs = practice.get("repair_log", [])
                                if not isinstance(logs, list):
                                    logs = [str(logs)]
                                logs.extend(post_blank_meta.get("reasons", []))
                                practice["repair_log"] = logs
                        practice_problem, prob_meta = normalize_probability_event_notation(practice_problem)
                        if prob_meta.get("changed"):
                            logs = practice.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.extend(prob_meta.get("reasons", []))
                            practice["repair_log"] = logs
                        if re.search(r"$^", str(practice_problem or "")):
                            practice["has_image"] = True
                            practice["needs_image_review"] = True
                            practice["needs_review"] = True
                            if "[BLOCK_IMAGE]" not in str(practice_problem_raw or "") and "[IMAGE_" not in str(practice_problem_raw or ""):
                                practice["missing_docx_image_asset"] = True
                        if re.search(r"$^", str(practice_problem or "")):
                            practice["has_image"] = True
                            if "[BLOCK_IMAGE]" not in str(practice_problem_raw or "") and "[IMAGE_" not in str(practice_problem_raw or ""):
                                practice["missing_docx_image_asset"] = True
                                practice["needs_image_review"] = True
                                practice["needs_review"] = True
                        if re.search(r"P\(|C\(|P\^|C\^|\{\}\^|\{\}\^\{|\\\(\{\}\^|\\\(\{\}\^\{", str(practice_problem_raw or "")):
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={practice_title} before={practice_problem_norm}")
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={practice_title} after={practice_problem}")
                        practice_answer = _render_sub_questions_answer(practice.get('correct_answer', ''), sub_questions)
                        practice_solution = _render_sub_questions_solution(practice.get('detailed_solution', ''), sub_questions)
                        linked_example_title = str(practice.get("linked_example_title", "") or "").strip() or None
                        needs_review = bool(practice.get("needs_review", False))
                        practice["problem_text"] = practice_problem
                        practice = validate_problem_block_purity(practice)
                        needs_review = bool(practice.get("needs_review", False))
                        if source_type == "in_class_practice":
                            linked_example_title, needs_review = _infer_linked_example_title(
                                practice_title, linked_example_title, saved_example_titles, needs_review
                            )

                        target_skill_id = str(practice.get("skill_id", "") or "").strip()
                        if not target_skill_id:
                            if source_type == "self_assessment" and is_vocational_mathb and vol_num == 4:
                                mapped_ch3 = infer_mathb4_ch3_self_assessment_skill(
                                    chapter_title, section_title, practice_title, practice_problem
                                )
                                sa_section_context = self_assessment_section_context or extract_self_assessment_section_context(section_title)
                                mapped_ch2 = infer_mathb4_ch2_self_assessment_skill(
                                    chapter_title, section_title, practice_title, practice_problem
                                )
                                if mapped_ch3.get("skill_id"):
                                    target_skill_id = mapped_ch3.get("skill_id")
                                    practice["problem_type"] = mapped_ch3.get("problem_type") or practice.get("problem_type", "")
                                    practice["subskill_tag"] = mapped_ch3.get("subskill_tag") or practice.get("subskill_tag", "")
                                elif mapped_ch2.get("skill_id"):
                                    target_skill_id = mapped_ch2.get("skill_id")
                                    practice["problem_type"] = mapped_ch2.get("problem_type") or practice.get("problem_type", "")
                                    practice["subskill_tag"] = mapped_ch2.get("subskill_tag") or practice.get("subskill_tag", "")
                                else:
                                    mapped = infer_mathb4_self_assessment_skill(sa_section_context, practice_title, practice_problem)
                                    if mapped.get("clean_en_id"):
                                        target_skill_id = f"vh_?詨飛B4_{mapped['clean_en_id']}"
                                        practice["problem_type"] = mapped.get("problem_type") or practice.get("problem_type", "")
                                        practice["subskill_tag"] = mapped.get("subskill_tag") or practice.get("subskill_tag", "")
                                    else:
                                        target_skill_id = _determine_target_skill_id(clean_en_id, section_title, concept_name, practice)
                            else:
                                linked_num = _extract_title_number(linked_example_title) if linked_example_title else None
                                if linked_num is not None and linked_num in saved_example_skill_map:
                                    target_skill_id = saved_example_skill_map[linked_num]
                                elif len({sid for _, sid in saved_example_order}) == 1 and saved_example_order:
                                    target_skill_id = saved_example_order[0][1]
                                elif saved_example_order:
                                    target_skill_id = saved_example_order[-1][1]
                                    needs_review = True
                                    warn_msg = (
                                        f"[PRACTICE IMPORT WARNING] title={practice_title} reason=missing_exact_linked_example"
                                    )
                                    current_app.logger.warning(warn_msg)
                                    queue.put(f"WARN: {warn_msg}")
                                else:
                                    target_skill_id = _determine_target_skill_id(clean_en_id, section_title, concept_name, practice)
                                    needs_review = True
                                    warn_msg = (
                                        f"[PRACTICE IMPORT WARNING] title={practice_title} reason=missing_linked_example"
                                    )
                                    current_app.logger.warning(warn_msg)
                                    queue.put(f"WARN: {warn_msg}")

                        log_msg = (
                            f"[PRACTICE IMPORT] detected title={practice_title} source_type={source_type} "
                            f"linked_example={linked_example_title} skill_id={target_skill_id}"
                        )
                        current_app.logger.info(log_msg)
                        queue.put(f"INFO: {log_msg}")
                        if source_type == "exam_practice":
                            current_app.logger.info(
                                f"[EXAM PRACTICE IMPORT] detected title={practice_title} source_type={source_type} skill_id={target_skill_id}"
                            )

                        dedupe_hash = _normalize_problem_hash(
                            practice_problem, sub_questions=sub_questions, source_type=source_type, title=practice_title
                        )
                        source_description = _build_source_description(
                            practice_title,
                            source_type=source_type or "in_class_practice",
                            linked_example_title=linked_example_title,
                            needs_review=needs_review,
                            dedupe_hash=dedupe_hash,
                            section_context=self_assessment_section_context if source_type == "self_assessment" else None,
                        )

                        existing_practice = TextbookExample.query.filter_by(
                            skill_id=target_skill_id,
                            source_curriculum=curriculum_info.get('curriculum'),
                            source_volume=str(curriculum_info.get('volume')),
                            source_chapter=chapter_title,
                            source_section=section_title,
                            source_description=source_description
                        ).first()
                        if not existing_practice:
                            existing_practice = TextbookExample.query.filter_by(
                                source_curriculum=curriculum_info.get('curriculum'),
                                source_volume=str(curriculum_info.get('volume')),
                                source_chapter=chapter_title,
                                source_section=section_title,
                                source_description=source_description
                            ).first()
                        if not existing_practice:
                            existing_practice = _find_existing_duplicate_by_dedupe(
                                curriculum_info.get('curriculum'),
                                curriculum_info.get('volume'),
                                chapter_title,
                                section_title,
                                practice_title,
                                dedupe_hash,
                            )
                        if existing_practice:
                            duplicate_meta = {}
                            duplicate_formula_meta = None
                            if is_docx_source:
                                duplicate_formula_meta = _build_docx_formula_assets_metadata(
                                    practice_title, question_text=practice_problem
                                )
                            if duplicate_formula_meta:
                                duplicate_meta.update(duplicate_formula_meta)
                            for k in ("needs_review", "needs_formula_review", "formula_missing"):
                                if practice.get(k) is True:
                                    duplicate_meta[k] = True

                            changed, _reason = _merge_duplicate_existing_record(
                                existing_practice,
                                incoming_problem_text=practice_problem,
                                incoming_meta=duplicate_meta,
                                incoming_correct_answer=practice_answer,
                                incoming_detailed_solution=practice_solution,
                                title=practice_title,
                            )
                            if changed:
                                updated_duplicates += 1
                                update_msg = (
                                    f"[PRACTICE IMPORT] updated duplicate title={practice_title} reason=metadata_merge"
                                )
                                current_app.logger.info(update_msg)
                                queue.put(f"INFO: {update_msg}")
                            else:
                                practice_questions_skipped += 1
                                duplicates_skipped_count += 1
                                skip_msg = (
                                    f"[PRACTICE IMPORT] skipped duplicate title={practice_title} reason=dedupe_match"
                                )
                                current_app.logger.info(skip_msg)
                                queue.put(f"INFO: {skip_msg}")
                            continue

                        try:
                            difficulty_level = int(practice.get('difficulty_level', 1))
                        except Exception:
                            difficulty_level = 1

                        practice_row = TextbookExample(
                            skill_id=target_skill_id,
                            source_curriculum=curriculum_info.get('curriculum'),
                            source_volume=str(curriculum_info.get('volume')),
                            source_chapter=chapter_title,
                            source_section=section_title,
                            source_paragraph=concept_name,
                            source_description=source_description,
                            problem_text=practice_problem,
                            problem_type=practice.get('problem_type', 'in_class_practice'),
                            correct_answer=practice_answer,
                            detailed_solution=sanitize_detailed_solution_text(practice_solution, max_chars=500),
                            difficulty_level=difficulty_level
                        )
                        chapter_rel_dir, _, chapter_id, section_id = build_question_assets_dir(
                            curriculum_info, chapter_title, section_title
                        )
                        _ = chapter_rel_dir
                        practice_code = build_question_code(chapter_id, section_id, "practice", practice_idx)
                        image_meta = None
                        if is_pdf_source:
                            image_meta = _build_image_metadata(
                                question_title=practice_title,
                                question_text=practice_problem,
                                chapter_title=chapter_title,
                                section_title=section_title,
                                source_type=source_type,
                                question_code=practice_code,
                                force_has_image=bool(practice.get("has_image", False)),
                                image_description=str(practice.get("image_description", "") or ""),
                                source_page=practice.get("source_page"),
                                page_index=practice.get("page_index"),
                                item_payload={**practice, "_neighbor_source_pages": concept_known_pages},
                            )
                        if is_docx_source:
                            docx_meta = _build_docx_assets_metadata(
                                practice_title, chapter_title, section_title, source_type, question_text=practice_problem
                            )
                            if docx_meta:
                                image_meta = dict(image_meta or {})
                                image_meta.update(docx_meta)
                            if not converted_latex_mode:
                                formula_meta = _build_docx_formula_assets_metadata(practice_title, question_text=practice_problem)
                                if formula_meta:
                                    image_meta = dict(image_meta or {})
                                    image_meta.update(formula_meta)
                        if image_meta:
                            attached = attach_image_metadata(practice_row, image_meta)
                            if attached:
                                current_app.logger.info(f"{'[DOCX IMAGE]' if is_docx_source else '[QUESTION IMAGE]'} metadata attached question={practice_title}")
                                if is_docx_source:
                                    img_assets = image_meta.get("image_assets", []) if isinstance(image_meta, dict) else []
                                    docx_attached_count += len(img_assets)
                                    docx_copied_to_question_assets += len(img_assets)
                                    for ia in img_assets:
                                        if ia.get("display_path"):
                                            docx_direct_display_images += 1
                                        if ia.get("original_format") in ("wmf", "emf"):
                                            docx_vector_images += 1
                                        if ia.get("converted_path"):
                                            docx_conversion_success += 1
                                        if ia.get("needs_image_conversion") is True and not ia.get("display_path"):
                                            docx_conversion_failed += 1
                                    formula_assets = image_meta.get("formula_assets", []) if isinstance(image_meta, dict) else []
                                    if formula_assets:
                                        docx_formula_assets_count += len(formula_assets)
                                        if image_meta.get("needs_formula_review"):
                                            docx_formula_needs_review_count += 1
                                    for fa in formula_assets:
                                        if fa.get("conversion_status") == "success":
                                            docx_conversion_success += 1
                                        elif fa.get("conversion_status") == "failed":
                                            docx_conversion_failed += 1
                                        elif fa.get("conversion_status") == "pending":
                                            docx_conversion_pending += 1
                            else:
                                current_app.logger.info(
                                    "[QUESTION IMAGE] detected but no metadata field available table=textbook_examples"
                                )
                        if is_docx_source and isinstance(image_meta, dict) and image_meta.get("has_image") and not image_meta.get("image_assets"):
                            reason = image_meta.get("image_warning", "unknown")
                            missing_image_questions.append((practice_title, source_type, reason))
                            current_app.logger.info(
                                f"[DOCX IMAGE DEBUG] missing_image_candidate title={practice_title} source_type={source_type} reason={reason}"
                            )
                        math_meta = _build_math_metadata(practice_problem_raw, practice_math_meta, needs_review=needs_review)
                        if _is_mathb4_chart_target(section_title, target_skill_id):
                            chart_meta = _extract_chart_metadata_for_mathb4_32(practice_problem, practice_problem_raw)
                            if chart_meta:
                                math_meta.update(chart_meta)
                            elif re.search(r"$^", str(practice_problem or "")):
                                practice["has_image"] = True
                                practice["needs_image_review"] = True
                                practice["needs_review"] = True
                                practice["missing_docx_image_asset"] = True
                                math_meta["needs_review"] = True
                        for k in (
                            "needs_formula_review",
                            "formula_missing",
                            "formula_hallucination_risk",
                            "parse_warning",
                            "problem_unusable",
                            "block_boundary_error",
                            "likely_concept_explanation",
                            "skill_boundary_mismatch",
                            "has_answer_blank",
                            "question_format",
                            "needs_image_review",
                            "missing_docx_image_asset",
                            "needs_table_review",
                            "repair_log",
                        ):
                            if practice.get(k) is not None:
                                math_meta[k] = practice.get(k)
                        attach_image_metadata(practice_row, math_meta)
                        if re.search(r"[PC]\s*\(|[PC]\s*\^|[PC]\s*_|[?兜嗽笨喇?菊?猾?嫖??????????", str(practice_problem or "")):
                            current_app.logger.info(f"[DB WRITE CHECK] title={practice_title} problem_text={practice_problem}")
                        db.session.add(practice_row)

                        practice_questions_imported += 1
                        summary_bucket = classify_practice_source_bucket(source_type)
                        if summary_bucket == "in_class_practice":
                            in_class_practices_imported += 1
                            n = _extract_title_number(practice_title)
                            if n is not None:
                                in_class_nums.append(n)
                        elif summary_bucket == "chapter_exercise":
                            chapter_exercises_imported += 1
                        elif summary_bucket == "self_assessment":
                            self_assessments_imported += 1
                        elif summary_bucket == "exam_practice":
                            exam_practices_imported += 1
                        else:
                            other_practices_imported += 1
                        if needs_review:
                            practice_questions_needs_review += 1
                        saved_msg = (
                            f"[PRACTICE IMPORT] saved independent question title={practice_title} "
                            f"table=textbook_examples id=pending_commit"
                        )
                        current_app.logger.info(saved_msg)
                        queue.put(f"INFO: {saved_msg}")

        db.session.commit()
        if is_docx_source:
            ctx = _DOCX_IMPORT_CONTEXT or {}
            current_app.logger.info(f"[DOCX MODE] docx_formula_source_mode={ctx.get('docx_formula_source_mode', 'auto_detect')}")
            current_app.logger.info(f"[DOCX MODE] is_converted_latex_docx={bool(ctx.get('is_converted_latex_docx', False))}")
            current_app.logger.info(f"[DOCX MODE] latex_signal_count={int(ctx.get('latex_signal_count', 0) or 0)}")
            current_app.logger.info(f"[DOCX MODE] formula_placeholder_count={int(ctx.get('formula_placeholder_count', 0) or 0)}")
            current_app.logger.info(f"[DOCX MODE] formula_assets_extraction_skipped={bool(ctx.get('formula_assets_extraction_skipped', False))}")
            current_app.logger.info(f"[DOCX MODE] ocr_skipped={bool(ctx.get('ocr_skipped', False))}")
            current_app.logger.info(f"[DOCX MODE] pix2tex_skipped={bool(ctx.get('pix2tex_skipped', False))}")
            current_app.logger.info(f"[DOCX MODE] records_with_latex={records_with_latex}")
            current_app.logger.info(f"[DOCX MODE] records_with_placeholder={records_with_placeholder}")
            current_app.logger.info(f"[DOCX MODE] merge_guard_kept_existing={merge_guard_kept_existing}")
            current_app.logger.info(f"[DOCX MODE] merge_guard_updated_incoming={merge_guard_updated_incoming}")
            media_total = len((ctx.get("media_rel_map") or {})) if isinstance(ctx, dict) else 0
            orphan_total = len((ctx.get("orphan_images") or [])) if isinstance(ctx, dict) else 0
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] media_total={media_total}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] attached_images={docx_attached_count}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] orphan_images={orphan_total}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] copied_to_question_assets={docx_copied_to_question_assets}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] direct_display_images={docx_direct_display_images}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] vector_images={docx_vector_images}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] conversion_success={docx_conversion_success}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] conversion_failed={docx_conversion_failed}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] conversion_pending={docx_conversion_pending}")
            current_app.logger.info(f"[FORMULA ASSET SUMMARY] formula_assets={docx_formula_assets_count}")
            current_app.logger.info(f"[FORMULA ASSET SUMMARY] needs_formula_review={docx_formula_needs_review_count}")
            current_app.logger.info(f"[DOCX IMAGE SUMMARY] missing_image_questions={len(missing_image_questions)}")
            for t, s_type, reason in missing_image_questions:
                current_app.logger.warning(
                    f"[DOCX IMAGE SUMMARY WARNING] missing_image title={t} source_type={s_type} reason={reason}"
                )
            current_app.logger.info(f"[DOCX IMPORT VALIDATION] detected_titles={len(detected_titles)}")
            current_app.logger.info(f"[DOCX IMPORT VALIDATION] examples={examples_added}")
            current_app.logger.info(f"[DOCX IMPORT VALIDATION] in_class_practices={in_class_practices_imported}")
            current_app.logger.info(f"[DOCX IMPORT VALIDATION] exercises={chapter_exercises_imported}")
            if in_class_nums:
                uniq = sorted(set(in_class_nums))
                miss = [x for x in range(uniq[0], uniq[-1] + 1) if x not in uniq]
                if miss:
                    current_app.logger.warning(
                        f"[DOCX IMPORT VALIDATION WARNING] possible missing in_class_practice numbers={miss}"
                    )
        return {
            'skills_processed': skills_processed,
            'curriculums_added': curriculums_added,
            'chapters_created': chapters_created,
            'chapters_updated': chapters_updated,
            'sections_created': sections_created,
            'sections_updated': sections_updated,
            'examples_added': examples_added,
            'practice_questions_imported': practice_questions_imported,
            'in_class_practices_imported': in_class_practices_imported,
            'chapter_exercises_imported': chapter_exercises_imported,
            'self_assessments_imported': self_assessments_imported,
            'exam_practices_imported': exam_practices_imported,
            'other_practices_imported': other_practices_imported,
            'needs_review_count': practice_questions_needs_review,
            'intra_import_duplicates_merged': intra_import_duplicates_merged,
            'practice_questions_skipped': practice_questions_skipped,
            'duplicates_skipped': duplicates_skipped_count,
            'updated_duplicates': updated_duplicates,
            'processed_skill_ids': processed_skill_ids,
            'records_with_latex': records_with_latex,
            'records_with_placeholder': records_with_placeholder,
            'merge_guard_kept_existing': merge_guard_kept_existing,
            'merge_guard_updated_incoming': merge_guard_updated_incoming,
        }
    except Exception as e:
        db.session.rollback()
        tb = traceback.format_exc()
        current_app.logger.error(f"撖怠鞈?摨怠仃?? {e}\n{tb}")
        queue.put(f"ERROR: 撖怠鞈?摨怠仃?? {e}")
        return {}








