# -*- coding: utf-8 -*-
"""
Antigravity ???臬蝺楝 V2??
- 璅∪?銝 (docx_problems)嚗onverted_docx_latex DOCX 瘙箏??折??桀?乓?
- 璅∪?鈭?(pdf_outline)嚗DF ??5 ?????SkillCurriculum 憭抒雇璅孵?甇乓?
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
import traceback
from collections import deque
from difflib import SequenceMatcher
from typing import Any

from flask import current_app, has_app_context
from google.api_core.exceptions import ResourceExhausted

from core.ai_analyzer import get_model
from core.textbook_processor import (
    CONVERTED_DOCX_LATEX_JSON_RULES,
    _call_gemini_with_retry,
    detect_chapter_self_assessment_context,
    extract_section_code_from_title,
    get_question_title,
    normalize_source_type_by_title,
    parse_volume,
    safe_load_gemini_json,
)
from core.textbook_filename_parser import parse_textbook_filename_metadata
from core.utils import normalize_vocational_math_skill_id
from models import SkillCurriculum, SkillInfo, TextbookExample, db

# ---------------------------------------------------------------------------
# Regex barriers
# ---------------------------------------------------------------------------

_LEADING_TITLE_RE = re.compile(
    r"^\s*(?:例題|習題|題組|隨堂練習|章末評量)\s*\d{0,3}\s*[\s\.,、．:：-]*"
    r"|^\s*\d{1,2}\s*[\s\.,、．:：-]+"
)

# 靘?撠嚗蝡?銵?閰唾圾韏瑟?撘???.match 銵?嚗?函?銵??圾???琿?嚗?
_STRONG_SOL_START_RE = re.compile(
    r"^\s*(?:"
    r"解[:：]|\[解\]|\(解\)|"
    r"because|因此|所以|由題意|可得|故|"
    r"f\(x\)=|g\(x\)=|\["
    r")",
    re.UNICODE,
)
# ?典?嚗?憿?蝯望葫嚗?敺??亦?閫敹菔玨?絲??銵? .match ?喳?蝯蒂皞Ｘ? unassigned嚗?
_PURE_CONCEPT_LINE_RE = re.compile(
    r"^\s*(?:概念|重點整理|重要觀念|觀念補充|小結)"
)

_JSON_EXAMPLE_METADATA_ONLY = """
{
  "chapters": [
    {
      "chapter_title": "蝚?蝡???蝟餉??賣?耦",
      "sections": [
        {
          "section_title": "1-4 銝??甈∩?蝑?",
          "concepts": [
            {
              "concept_name": "銝??甈∩?蝑??圾瘜?,
              "concept_en_id": "QuadraticInequalitiesSolution",
              "concept_paragraph": "",
              "examples": [
                {
                  "id": "1",
                  "title": "靘?1",
                  "source_description": "靘?1",
                  "problem_text": "靘?1",
                  "correct_answer": "",
                  "detailed_solution": ""
                }
              ],
              "practice_questions": [
                {
                  "id": "1",
                  "title": "?典?蝺渡?1",
                  "source_description": "?典?蝺渡?1",
                  "problem_text": "?典?蝺渡?1",
                  "correct_answer": "",
                  "detailed_solution": ""
                }
              ]
            }
          ]
        }
      ]
    }
  ]
}
"""

# Phase-2 structural scan (aligned with legacy converted_docx scanner)
_SCAN_ZONE_HEADERS = ("隨堂練習", "題組", "章末評量")
_SCAN_EXERCISE_BLOCK_HDR_RE = re.compile(r"^\s*(\d+-\d+)\s*題組?\s*$")
_SCAN_ZONE_HDR_RE = re.compile(r"^\s*(隨堂練習|題組|章末評量)\s*$")
_SCAN_EXAM_MARKER_RE = re.compile(
    r"[\(\[\{【]?\s*(\d{2,3})\s*學測\s*([A-Ca-c])\s*[\)\]\}】]?",
    flags=re.IGNORECASE | re.UNICODE,
)
# 蝯望葫甇瑕?閰阡?嚗蝡????柴?撅嚗??扼?05蝯望葫A??嚗?09蝯望葫嚗ｇ?蝑???
_EXAM_BLOCK_START_RE = re.compile(r"^\s*學測\s*$", re.UNICODE)
_EXAM_SECTION_HDR_RE = re.compile(
    r"^\s*(?:學測題組|題組|學測綜合題)\s*$",
    re.UNICODE,
)
_EXAM_END_RE = re.compile(
    r".*[\(\[\{【]\s*(\d{2,3})\s*學測\s*([A-Ca-c])\s*[\)\]\}】].*",
    re.UNICODE | re.IGNORECASE,
)
# ???斗?閮擃?銝?韌 .*嚗?靘?sub 瘣楊??銵???憿凳
_EXAM_END_MARKER_STRIP_RE = re.compile(
    r"[\(\[\{【]\s*(\d{2,3})\s*學測\s*([A-Ca-c])\s*[\)\]\}】]",
    re.UNICODE | re.IGNORECASE,
)
_SCAN_KEY_LINE_RE = re.compile(r"^\s*KEY\b", re.IGNORECASE)
_SCAN_CHAPTER_EX_NUM_RE = re.compile(r"^\s*(\d{1,2})(?:[\.、．)\t]|\s+)")
_SCAN_EXAMPLE_NUM_RE = re.compile(r"例題\s*(\d{1,2})\b")
_EXAMPLE_BOUNDARY_CHARS = "；;!?。"
_SCAN_SUITANG_PREFIX_RE = re.compile(r"^\s*習題")
_SCAN_SUITANG_NUM_INLINE_RE = re.compile(r"習題[\s\.、．]*(\d{1,2})\b")
_SCAN_SUBSECTION_HEADING_RE = re.compile(r"^\s*\d+\s*-\s*\d+(?:\.\d+)?\s+\S")
_SCAN_MC_OPTION_RE = re.compile(r"^\s*[\(（]\s*([A-Da-d])\s*[\)）]")
_SCAN_SUBPART_RE = re.compile(r"^\s*[\(（]\s*\d+\s*[\)）]")

# 憿摰??銵???嚗?憿??典?嚗?憿???皜祇??瑯摮?璅?/蝛箇????
_QUESTION_BOUNDARY_RE = re.compile(
    r"^\s*(?:例題|題目\s*\d|習題|題組|\d{1,2}\s*[\.、．)\t]|\d{1,2}\s+[\u4e00-\u9fff])"
)
_QUESTION_BOUNDARY_NUM_RE = re.compile(r"^\s*(\d{1,2})(?:[\.、．)\t]|\s+)(.+)")
_CH_SA_CH_MARKER_RE = re.compile(r"CH\s*(\d+)\s*章末評量?", re.IGNORECASE)
_CH_SA_ZH_CHAPTER_RE = re.compile(r"第\s*(\d+)\s*章")
_CH_SA_SECTION_HEADING_RE = re.compile(r"^\s*(\d+-\d+)\s+(.+)$")
_CH_SA_PAGE_ONLY_RE = re.compile(r"^\s*\d{2,3}\s*$")

# Phase1 瘜典?hase2 ?芸?颲刻????憿?閮?蝜? Word ?梯?蝛箇嚗?楊??
_QUESTION_TRIGGER_PREFIX = "__NEW_QUESTION_TRIGGER__"
_DOCX_SPECIAL_SPACE_RE = re.compile(r"[\u00a0\u1680\u2000-\u200b\u202f\u205f\u3000\ufeff]")
_PHASE1_LEADING_NUM_RE = re.compile(r"^\d{1,2}(?:[\.\?)\]\s]|\b)")
_ANCHOR_EXAMPLE_ONLY_RE = re.compile(r"^\s*(?:例題|例)\s*([0-9０-９]+)\s*[_\-:：]?\s*$")
_ANCHOR_EXAMPLE_INLINE_RE = re.compile(r"^\s*(?:例題|例)\s*([0-9０-９]+)\s*[_\-:：]?\s+(.+)$")
_ANCHOR_PRACTICE_ONLY_RE = re.compile(r"^\s*(?:隨堂練習|練習)\s*([0-9０-９]+)\s*$")
_ANCHOR_PRACTICE_INLINE_RE = re.compile(r"^\s*(?:隨堂練習|練習)\s*([0-9０-９]+)\s+(.+)$")
_PRACTICE_ZONE_RE = re.compile(r"^\s*隨堂練習[\.。．…・·\s]*$")
_NUMBERED_LINE_RE = re.compile(
    r"^\s*([0-9０-９]+)\s*(?:[\.．、\)]|\s+)\s*([\s\S]+)$"
)
_SOLUTION_MARKER_ONLY_RE = re.compile(r"^\s*解\s*$")
_SOLUTION_MARKER_INLINE_RE = re.compile(r"^\s*解[:：]\s*(.*)$")
_EXERCISE_SECTION_RE = re.compile(r"^\s*(\d+-\d+)\s*習題\s*$")
_EXERCISE_LEVEL_RE = re.compile(r"^\s*(基礎題|進階題|挑戰題)\s*$")
_EXERCISE_NUM_RE = re.compile(r"^\s*([0-9０-９]{1,2})\s*[\.．、\)]?\s*([\s\S]+)$")
_EXAM_START_RE = re.compile(r"^\s*題目\s*$")
_KEY_RE = re.compile(r"^\s*KEY\s*$", re.IGNORECASE)
_EXAM_MARKER_RE = re.compile(r"[〔\[\(（【]\s*(\d{2,3})\s*統測\s*([A-Da-d])\s*[〕\]\)）】]")
_EXAM_STOP_RE = re.compile(r"^\s*(輸入訊息〉|輸入訊息>|1-1習題|基礎題)\s*$")

_DOCX_BLOCK_META: dict[str, dict[str, str]] = {}


def _normalize_docx_line_text(text: str) -> str:
    """蝯曹? Word ?臬撣貉??寞?蝛箇?箔??祉征?潘??踹?甇??瞍??"""
    t = str(text or "")
    t = _DOCX_SPECIAL_SPACE_RE.sub(" ", t)
    t = t.replace("\t", " ")
    return re.sub(r" +", " ", t).strip()


def _to_half_width_digits(s: str) -> str:
    return str(s or "").translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def _looks_like_exercise_question_start(n: str, body: str) -> bool:
    b = str(body or "").strip()
    if not b:
        return False
    if re.match(r"^[><=≤≥−\-+]", b):
        return False
    if b in {"不等式左邊", "不等式右邊", "比較大小"}:
        return False
    question_keywords = (
        "數線上",
        "已知",
        "試求",
        "解下列",
        "解不等式",
        "完成下列表格",
        "若",
        "求",
    )
    if any(k in b for k in question_keywords):
        return True
    if len(b) <= 4:
        return False
    return True


def _looks_like_practice_question_body(body: str) -> bool:
    b = str(body or "").strip()
    if not b:
        return False
    bad_prefixes = (
        "絕對值不等式性質",
        "絕對值不等式",
        "若$\\left| x \\right|",
        "\\[\\left| x-a \\right|",
    )
    if b.startswith(bad_prefixes):
        return False
    return True


def _build_anchor_blocks_v2(lines: list[str]) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    blocks: dict[str, str] = {}
    meta: dict[str, dict[str, str]] = {}
    cur_key = ""
    cur_anchor = ""
    cur_source_type = ""
    in_solution = False
    in_exam_mode = False
    in_key_mode = False
    in_practice_zone = False
    in_exercise_mode = False
    current_exercise_section = ""
    current_exercise_level = ""
    problem_lines: list[str] = []
    solution_lines: list[str] = []

    def flush_one() -> None:
        nonlocal cur_key, cur_anchor, cur_source_type, in_solution, problem_lines, solution_lines
        if not cur_key:
            return
        ptxt = _normalize_docx_line_text("\n".join(problem_lines)).strip()
        stxt = _normalize_docx_line_text("\n".join(solution_lines)).strip()
        if ptxt:
            blocks[cur_key] = ptxt
            meta[cur_key] = {
                "anchor": cur_anchor or cur_key,
                "source_type": cur_source_type or "textbook_example",
                "problem_text": ptxt,
                "detailed_solution": stxt,
            }
        cur_key = ""
        cur_anchor = ""
        cur_source_type = ""
        in_solution = False
        problem_lines = []
        solution_lines = []

    def start_block(anchor: str, source_type: str, first_problem_line: str = "") -> None:
        nonlocal cur_key, cur_anchor, cur_source_type, in_solution
        flush_one()
        cur_anchor = anchor
        cur_key = anchor
        cur_source_type = source_type
        in_solution = False
        if first_problem_line.strip():
            problem_lines.append(first_problem_line.strip())

    for raw in lines or []:
        trigger_hit, trigger_payload = _split_question_trigger(str(raw or ""))
        line = _normalize_docx_line_text(trigger_payload if trigger_hit else raw)
        if not line:
            if cur_key:
                if in_solution:
                    solution_lines.append("")
                else:
                    problem_lines.append("")
            continue

        m_ex_only = _ANCHOR_EXAMPLE_ONLY_RE.match(line)
        m_ex_inline = _ANCHOR_EXAMPLE_INLINE_RE.match(line)
        m_pr_only = _ANCHOR_PRACTICE_ONLY_RE.match(line)
        m_pr_inline = _ANCHOR_PRACTICE_INLINE_RE.match(line)
        if _EXERCISE_SECTION_RE.match(line):
            flush_one()
            in_practice_zone = False
            in_exam_mode = False
            in_key_mode = False
            in_exercise_mode = True
            current_exercise_section = _EXERCISE_SECTION_RE.match(line).group(1)
            current_exercise_level = ""
            continue
        if in_exercise_mode and _EXERCISE_LEVEL_RE.match(line):
            flush_one()
            current_exercise_level = _EXERCISE_LEVEL_RE.match(line).group(1)
            continue
        if _EXAM_START_RE.match(line):
            flush_one()
            in_exam_mode = True
            in_key_mode = False
            in_practice_zone = False
            in_exercise_mode = False
            start_block("統測題", "exam_question")
            continue
        if in_exam_mode and _KEY_RE.match(line):
            in_key_mode = True
            in_solution = True
            solution_lines.append("KEY")
            continue
        if in_exam_mode and in_key_mode and _EXAM_STOP_RE.match(line):
            flush_one()
            in_exam_mode = False
            in_key_mode = False
            continue
        if _PRACTICE_ZONE_RE.match(line):
            flush_one()
            in_practice_zone = True
            in_exam_mode = False
            in_key_mode = False
            in_exercise_mode = False
            continue

        if m_ex_only or m_ex_inline or m_pr_only or m_pr_inline:
            in_practice_zone = False
            in_exam_mode = False
            in_key_mode = False
            in_exercise_mode = False
            if m_ex_only:
                n = _to_half_width_digits(m_ex_only.group(1))
                start_block(f"例{n}", "textbook_example")
                continue
            if m_ex_inline:
                n = _to_half_width_digits(m_ex_inline.group(1))
                start_block(f"例{n}", "textbook_example", m_ex_inline.group(2))
                continue
            if m_pr_only:
                n = _to_half_width_digits(m_pr_only.group(1))
                start_block(f"隨堂練習{n}", "in_class_practice")
                continue
            if m_pr_inline:
                n = _to_half_width_digits(m_pr_inline.group(1))
                start_block(f"隨堂練習{n}", "in_class_practice", m_pr_inline.group(2))
                continue

        if in_practice_zone:
            nm = _NUMBERED_LINE_RE.match(line)
            if nm:
                n = _to_half_width_digits(nm.group(1))
                body = str(nm.group(2) or "").strip()
                if _looks_like_practice_question_body(body):
                    anchor = f"隨堂練習{n}"
                    if anchor in meta or anchor in blocks:
                        continue
                    start_block(anchor, "in_class_practice", body)
                    continue
            if (
                trigger_hit
                or _EXAM_START_RE.match(line)
                or _EXERCISE_SECTION_RE.match(line)
                or line in {"題目", "動動手", "想一想"}
                or bool(re.match(r"^\s*\d+-\d+(?:\.\d+)?\s+", line))
            ):
                in_practice_zone = False

        if in_exercise_mode:
            em = _EXERCISE_NUM_RE.match(line)
            if em:
                n = _to_half_width_digits(em.group(1))
                body = str(em.group(2) or "").strip()
                if not _looks_like_exercise_question_start(n, body):
                    if cur_key:
                        problem_lines.append(line)
                    continue
                sec = f"{current_exercise_section}習題" if current_exercise_section else "習題"
                lvl = current_exercise_level or "基礎題"
                start_block(f"{sec} {lvl} {n}", "textbook_exercise", body)
                continue

        if cur_key:
            if (
                cur_source_type == "in_class_practice"
                and not in_solution
                and len([ln for ln in problem_lines if str(ln).strip()]) >= 1
            ):
                opt_like = bool(re.match(r"^\s*[\(（]?[A-DＡ-Ｄa-dａ-ｄ0-9０-９][\)）\.．、\s]", line))
                if not opt_like:
                    flush_one()
                    # Continue to evaluate this line as a potential new anchor/heading.
                    if _PRACTICE_ZONE_RE.match(line):
                        in_practice_zone = True
                        continue
                    if _EXAM_START_RE.match(line) or _EXERCISE_SECTION_RE.match(line):
                        in_practice_zone = False
                    else:
                        continue
            if trigger_hit and cur_source_type == "textbook_example" and problem_lines:
                in_solution = True
                solution_lines.append(line)
                continue
            if in_exam_mode:
                marker = _EXAM_MARKER_RE.search(line)
                if marker:
                    year = str(marker.group(1) or "").strip()
                    cat = str(marker.group(2) or "").strip().upper()
                    cur_anchor = f"{year}統測{cat}"
                    cur_key = cur_anchor
                if in_key_mode:
                    solution_lines.append(line)
                else:
                    problem_lines.append(line)
                continue
            m_sol_inline = _SOLUTION_MARKER_INLINE_RE.match(line)
            if _SOLUTION_MARKER_ONLY_RE.match(line):
                in_solution = True
                solution_lines.append("解")
                continue
            if m_sol_inline:
                in_solution = True
                tail = str(m_sol_inline.group(1) or "").strip()
                solution_lines.append("解" + (f"\n{tail}" if tail else ""))
                continue
            if in_solution:
                solution_lines.append(line)
            else:
                problem_lines.append(line)
    flush_one()
    return blocks, meta


def phase2_mathb_section_anchor_slice(
    lines: list[str],
    *,
    section_code: str = "",
) -> dict[str, dict[str, str]]:
    """Deterministic anchor slicer for converted LaTeX DOCX (Math B)."""
    _ = section_code
    _, meta = _build_anchor_blocks_v2(lines)
    return meta


def _split_question_trigger(line: str) -> tuple[bool, str]:
    """?亙 Phase1 ?拍?璅????支蒂?瘛典?敺?撟寡???"""
    raw = str(line or "")
    if _QUESTION_TRIGGER_PREFIX not in raw:
        return False, _normalize_docx_line_text(raw)
    payload = raw.replace(_QUESTION_TRIGGER_PREFIX, "", 1).strip()
    return True, _normalize_docx_line_text(payload)


def _paragraph_has_word_numbering(para) -> bool:
    """?菜葫 OOXML ?芸?蝺刻? (w:numPr)嚗雿?p.text ?芸?詨??韌??"""
    try:
        p_pr = para._element.pPr
        if p_pr is not None and p_pr.numPr is not None:
            return True
    except Exception:
        pass
    return False


def _paragraph_is_word_list(para) -> bool:
    """畾菔?臬??Word 皜嚗葬?楊??暺?"""
    try:
        style_name = str(getattr(getattr(para, "style", None), "name", "") or "")
    except Exception:
        style_name = ""
    if any(tok in style_name for tok in ("List", "蝺刻?", "璇?", "皜", "Number")):
        return True
    if _paragraph_has_word_numbering(para):
        return True
    try:
        pf = para.paragraph_format
        if pf is not None and pf.left_indent is not None:
            try:
                if float(pf.left_indent.pt or 0) > 0:
                    return True
            except (TypeError, ValueError):
                return True
    except Exception:
        pass
    return False


def _phase1_should_inject_question_trigger(para, text_clean: str) -> bool:
    if not text_clean:
        return False
    if _paragraph_is_word_list(para):
        return True
    return bool(_PHASE1_LEADING_NUM_RE.match(text_clean))


def _extract_question_number_from_line(line: str) -> int | None:
    """敺歇瘛典?憿凳銵????1??9嚗?"""
    qn = _parse_boundary_question_number(line)
    if qn is not None:
        return qn
    m = re.search(r"(\d{1,2})", str(line or ""))
    if not m:
        return None
    n = int(m.group(1))
    return n if 1 <= n <= 99 else None


def _is_chapter_self_assessment_scope(source_scope: str) -> bool:
    return str(source_scope or "").strip() in ("chapter_self_assessment", "chapter_review")


def _normalize_exam_category(raw: str) -> str:
    """?典耦嚗?撖恍??交迤閬??箏?敶Ｗ之撖?A???"""
    c = unicodedata.normalize("NFKC", str(raw or "")).strip().upper()
    if c and c[0] in "ABC":
        return c[0]
    return "A"


def _strip_exam_end_marker_from_line(line: str) -> str:
    """?芸?銝銵??斤絞皜祉???閮?靽?璅?????憿凳嚗??摮?"""
    text = str(line or "")
    m = _EXAM_END_RE.search(text)
    if not m:
        return _normalize_docx_line_text(text)
    return _EXAM_END_MARKER_STRIP_RE.sub("", text, count=1).strip()


def _parse_exam_end_marker(line: str) -> tuple[str, str] | None:
    """敺絞皜祉????瑕? (year, category)嚗??A? ?嚗?敶Ｘ??"""
    text = str(line or "")
    m = _EXAM_END_RE.search(text)
    if not m:
        m = _SCAN_EXAM_MARKER_RE.search(text)
    if not m:
        return None
    year = str(m.group(1) or "").strip()
    category = _normalize_exam_category(m.group(2))
    if not year:
        return None
    return year, category


def _parse_boundary_question_number(line: str) -> int | None:
    """敺?擐?葫撽???1??9嚗??摮??剝???? None??"""
    m = _QUESTION_BOUNDARY_NUM_RE.match(str(line or "").strip())
    if not m:
        return None
    n = int(m.group(1))
    return n if 1 <= n <= 99 else None


def _log_info(msg: str) -> None:
    if has_app_context():
        current_app.logger.info(msg)


def _log_error(msg: str) -> None:
    if has_app_context():
        current_app.logger.error(msg)


def clean_problem_leading_title(text: str) -> str:
    """瘣楊銵?憿摰?????詨?憿?嚗???摮? (1)/(2)??"""
    t = str(text or "").strip()
    if not t:
        return ""
    prev = None
    while prev != t:
        prev = t
        t = re.sub(_LEADING_TITLE_RE, "", t, count=1).strip()
    return t


def _is_example_question_key(key: str | None) -> bool:
    return str(key or "").strip().startswith("靘?")


def _truncate_example_line_at_solution_start(line: str) -> tuple[str, bool]:
    """??憿?銵??賭葉撘瑁圾蝑絲????瑚蒂??嚗?match嚗?甇?.search嚗?"""
    raw = str(line or "")
    if not raw.strip():
        return raw, False
    m = _STRONG_SOL_START_RE.match(raw)
    if not m:
        return raw, False
    return raw[: m.start()].rstrip(), True


def _scan_find_example_inline_start(line: str) -> re.Match[str] | None:
    for m in _SCAN_EXAMPLE_NUM_RE.finditer(str(line or "")):
        if m.start() == 0:
            return m
        prefix = str(line or "")[: m.start()].rstrip()
        if not prefix or prefix[-1] in _EXAMPLE_BOUNDARY_CHARS:
            return m
    return None


def _scan_is_structure_only_line(line: str) -> bool:
    s = str(line or "").strip()
    if not s:
        return False
    if _SCAN_KEY_LINE_RE.match(s):
        return True
    if _SCAN_EXAM_MARKER_RE.search(s) and not re.search(r"[\(嚗[A-D嚗?嚗也", s):
        return True
    if _SCAN_SUBSECTION_HEADING_RE.match(s):
        return True
    if _SCAN_ZONE_HDR_RE.match(s):
        return True
    if _SCAN_EXERCISE_BLOCK_HDR_RE.match(s) or re.match(r"^\s*(\d+-\d+)\s*蝧?\s*$", s):
        return True
    ex_m = re.match(r"^\s*靘??:憿??\s*(\d{1,2})\b", s)
    if ex_m:
        return not s[ex_m.end() :].strip()
    if _SCAN_SUITANG_PREFIX_RE.match(s):
        body = _SCAN_SUITANG_PREFIX_RE.sub("", s, count=1).strip()
        body = re.sub(r"^[\s\.?汕愍+", "", body).strip()
        if _SCAN_SUITANG_NUM_INLINE_RE.search(body):
            body = _SCAN_SUITANG_NUM_INLINE_RE.sub("", body, count=1).strip()
        return not body
    return False


def _scan_finalize_question_buffer(lines: list[str], *, question_key: str = "") -> str:
    is_example = _is_example_question_key(question_key)
    kept: list[str] = []
    for ln in lines:
        s = str(ln or "").strip()
        if _SCAN_KEY_LINE_RE.match(s):
            break
        if _scan_is_structure_only_line(s):
            continue
        if is_example:
            truncated, stop = _truncate_example_line_at_solution_start(str(ln or ""))
            if truncated.strip():
                kept.append(truncated)
            if stop:
                break
        else:
            if str(ln or "").strip() or ln == "":
                kept.append(str(ln or ""))
    while kept and _scan_is_structure_only_line(str(kept[-1] or "")):
        kept.pop()
    return clean_problem_leading_title("\n".join(kept).strip())


def _scan_flush_question_block(blocks: dict[str, str], key: str | None, buf: list[str]) -> None:
    if not key:
        return
    text = _scan_finalize_question_buffer(buf, question_key=str(key))
    if text:
        blocks[str(key).strip()] = text


def _split_mixed_example_suithang_line(line: str) -> tuple[str, str] | None:
    """??銵??靘???毀蝧?嚗?典?蝺渡?璅?????head / tail??"""
    text = str(line or "").strip()
    if "?典?蝺渡?" not in text:
        return None
    ex_m = _scan_find_example_inline_start(text)
    st_m = _SCAN_SUITANG_NUM_INLINE_RE.search(text)
    if not ex_m or not st_m:
        return None
    if st_m.start() <= ex_m.start():
        return None
    head = text[: st_m.start()].rstrip()
    tail = text[st_m.start() :].strip()
    if not head or not tail:
        return None
    return head, tail


def _scan_try_start_suithang(line: str, pending_header: bool) -> tuple[str | None, str | None, bool]:
    m_inline = _SCAN_SUITANG_NUM_INLINE_RE.search(line)
    if m_inline:
        first = clean_problem_leading_title(line[m_inline.start() :])
        return f"?典?蝺渡?{int(m_inline.group(1))}", first or None, False
    if pending_header and _SCAN_CHAPTER_EX_NUM_RE.match(line):
        n = int(_SCAN_CHAPTER_EX_NUM_RE.match(line).group(1))
        return f"?典?蝺渡?{n}", line, False
    if _SCAN_SUITANG_PREFIX_RE.match(line):
        return None, None, True
    return None, None, pending_header


def _scan_line_flushes_current_block(
    line: str,
    *,
    in_chapter_exercise: bool,
    pending_suithang_header: bool = False,
) -> bool:
    if _QUESTION_TRIGGER_PREFIX in str(line or ""):
        return True
    line = _normalize_docx_line_text(line)
    if _SCAN_KEY_LINE_RE.match(line):
        return True
    if _SCAN_EXAM_MARKER_RE.search(line):
        return True
    if _SCAN_SUBSECTION_HEADING_RE.match(line):
        return True
    if _SCAN_SUITANG_PREFIX_RE.match(line):
        return True
    if _SCAN_ZONE_HDR_RE.match(line):
        return True
    if _SCAN_EXERCISE_BLOCK_HDR_RE.match(line) or re.match(r"^\s*(\d+-\d+)\s*蝧?\s*$", line):
        return True
    if re.match(r"^\s*靘??:憿??\s*(\d{1,2})\b", line):
        return True
    if _SCAN_SUITANG_NUM_INLINE_RE.search(line):
        return True
    if pending_suithang_header:
        return False
    if in_chapter_exercise and _SCAN_CHAPTER_EX_NUM_RE.match(line):
        return True
    if _QUESTION_BOUNDARY_RE.match(line):
        return True
    return False


# ---------------------------------------------------------------------------
# Phase 1
# ---------------------------------------------------------------------------


def _phase1_emit_paragraph_line(lines: list[str], para) -> None:
    """蝯?+?????斗嚗?閬?瘜典?拍???璅???"""
    text_clean = _normalize_docx_line_text(str(para.text or ""))
    if not text_clean:
        return
    if _phase1_should_inject_question_trigger(para, text_clean):
        lines.append(f"{_QUESTION_TRIGGER_PREFIX} {text_clean}")
    else:
        lines.append(text_clean)


def phase1_extract_docx_lines(file_path: str) -> list[str]:
    """Read all DOCX paragraphs and table cells into normalized lines."""
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(file_path)
    lines: list[str] = []
    for block in doc.element.body.iterchildren():
        if block.tag.endswith("}p"):
            _phase1_emit_paragraph_line(lines, Paragraph(block, doc))
        elif block.tag.endswith("}tbl"):
            tbl = Table(block, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        _phase1_emit_paragraph_line(lines, para)
    return lines


# ---------------------------------------------------------------------------
# Phase 2
# ---------------------------------------------------------------------------


def phase2_deterministic_block_slice(
    lines: list[str],
    *,
    source_scope: str = "section_textbook",
) -> dict[str, str]:
    """
    撟曆?雿????嚗ayout-Aware Deterministic Slicer嚗?
    靘?嚗?擐圾??撘瑁圾蝑絲???瘀??典?嚗?憿??芣?閰?嚗???征銵??瑯?
    """
    scope = str(source_scope or "").strip() or "section_textbook"
    is_sa_scope = _is_chapter_self_assessment_scope(scope)
    blob = "\n".join(lines)
    sa_ctx: dict[str, Any] | None = None
    if is_sa_scope or scope != "section_textbook":
        sa_ctx = detect_chapter_self_assessment_context(blob)
    if is_sa_scope and not sa_ctx:
        m_ch = _CH_SA_CH_MARKER_RE.search(blob)
        ch_num = int(m_ch.group(1)) if m_ch else 1
        sa_ctx = {
            "mode": "chapter_self_assessment",
            "chapter_num": ch_num,
            "title_prefix": f"CH{ch_num}?芣?閰?",
        }
    sa_prefix = str((sa_ctx or {}).get("title_prefix") or "CH1?芣?閰?")
    sa_started = bool(
        is_sa_scope
        and (
            "?芣?閰?" in blob
            or _CH_SA_CH_MARKER_RE.search(blob)
            or any(_QUESTION_TRIGGER_PREFIX in str(ln) for ln in lines)
        )
    )

    blocks: dict[str, str] = {}
    section_code: str | None = None
    current_zone = "?嗡?"
    in_chapter_exercise = False
    current_key: str | None = None
    is_current_example = False
    buffer: list[str] = []
    stop_extend = False
    empty_line_count = 0
    pending_lines: list[str] = []
    pending_exam_lines: list[str] = []
    awaiting_exam = False
    pending_suithang_header = False
    unassigned_buffer: list[str] = []
    in_exam_collecting = False
    exam_collect_buffer: list[str] = []

    work: deque[str] = deque(str(ln or "") for ln in lines)

    def clear_unassigned_buffer() -> None:
        nonlocal unassigned_buffer
        unassigned_buffer = []

    def _try_start_from_question_trigger(line: str) -> bool:
        """Phase1 ?拍?璅??芸???嚗???芋撘? Canonical Key??"""
        trigger_hit, payload = _split_question_trigger(line)
        if not trigger_hit:
            return False
        qn = _extract_question_number_from_line(payload)
        if is_sa_scope and sa_ctx:
            if qn is not None:
                start_key(f"{sa_prefix} 題{qn}", payload)
                return True
            fallback = payload[:12].strip() or "題目"
            start_key(f"{sa_prefix} {fallback}", payload)
            return True
        if qn is not None and in_chapter_exercise and section_code and current_zone in _SCAN_ZONE_HEADERS:
            start_key(f"{section_code}蝧? {current_zone}{qn}", payload)
            return True
        ex_m = _scan_find_example_inline_start(payload)
        if ex_m:
            body = clean_problem_leading_title(payload[ex_m.start() :])
            start_key(f"靘?{int(ex_m.group(1))}", body or None)
            return True
        st_key, st_line, _ = _scan_try_start_suithang(payload, False)
        if st_key:
            start_key(st_key, st_line)
            return True
        if _QUESTION_BOUNDARY_RE.match(payload):
            if qn is not None:
                start_key(payload[:24].strip() or f"題{qn}", payload)
                return True
        return False

    def _line_opens_new_question_block(line: str) -> bool:
        """?臬?箸憿?瑽????迨憿???current_key 蝛箇???unassigned_buffer嚗?"""
        if _QUESTION_TRIGGER_PREFIX in str(line or ""):
            return True
        s = _normalize_docx_line_text(line)
        if not s:
            return False
        if _SCAN_KEY_LINE_RE.match(s):
            return True
        if _SCAN_EXAM_MARKER_RE.search(s):
            return True
        if _SCAN_SUBSECTION_HEADING_RE.match(s):
            return True
        if _SCAN_EXERCISE_BLOCK_HDR_RE.match(s) or re.match(r"^\s*(\d+-\d+)\s*蝧?\s*$", s):
            return True
        if _SCAN_ZONE_HDR_RE.match(s):
            return True
        if _scan_find_example_inline_start(s):
            return True
        if _SCAN_SUITANG_NUM_INLINE_RE.search(s) or _SCAN_SUITANG_PREFIX_RE.match(s):
            return True
        if (
            in_chapter_exercise
            and section_code
            and current_zone in _SCAN_ZONE_HEADERS
            and _SCAN_CHAPTER_EX_NUM_RE.match(s)
        ):
            return True
        if _QUESTION_BOUNDARY_RE.match(s):
            return True
        return False

    def _collect_orphan_line(line_clean: str) -> None:
        if current_key is not None or awaiting_exam:
            return
        if _line_opens_new_question_block(line_clean):
            return
        unassigned_buffer.append(line_clean)

    def _flush_exam_collect_buffer(end_line: str | None = None) -> bool:
        """Flush collected exam block when encountering the end marker."""
        nonlocal in_exam_collecting, exam_collect_buffer, current_key, buffer, is_current_example
        nonlocal stop_extend, empty_line_count, awaiting_exam, pending_exam_lines
        if not in_exam_collecting and not exam_collect_buffer:
            return False
        end_text = str(end_line or "")
        end_m = _EXAM_END_RE.search(end_text)
        if end_m:
            year = str(end_m.group(1) or "").strip()
            category = _normalize_exam_category(end_m.group(2))
        else:
            marker = _parse_exam_end_marker(end_text)
            if not marker:
                in_exam_collecting = False
                exam_collect_buffer = []
                return False
            year, category = marker
        exam_key = f"{int(year)}蝯望葫{category}"
        stem: list[str] = list(exam_collect_buffer)
        if end_line and end_m:
            tail = _strip_exam_end_marker_from_line(end_text)
            if tail:
                stem.append(tail)
        _scan_flush_question_block(blocks, exam_key, stem)
        in_exam_collecting = False
        exam_collect_buffer = []
        current_key = None
        buffer = []
        is_current_example = False
        stop_extend = False
        empty_line_count = 0
        awaiting_exam = False
        pending_exam_lines = []
        return True

    def flush() -> None:
        nonlocal current_key, buffer, stop_extend, is_current_example, empty_line_count
        nonlocal in_exam_collecting, exam_collect_buffer
        if in_exam_collecting:
            _flush_exam_collect_buffer()
        _scan_flush_question_block(blocks, current_key, buffer)
        current_key = None
        is_current_example = False
        buffer = []
        stop_extend = False
        empty_line_count = 0

    def clear_pending_lines() -> None:
        nonlocal pending_lines
        pending_lines = []

    def _route_practice_overflow_to_unassigned(line_clean: str) -> None:
        """??憿隤脫??脩??蝯?嚗?蝯神??buffer嚗皞Ｘ? unassigned??"""
        if is_current_example or not current_key or not stop_extend:
            return
        if _line_opens_new_question_block(line_clean):
            return
        unassigned_buffer.append(line_clean)

    def append_buffer_line(line: str) -> None:
        nonlocal stop_extend
        line_clean = str(line or "")
        if stop_extend:
            _route_practice_overflow_to_unassigned(line_clean)
            return
        if not is_current_example:
            if _PURE_CONCEPT_LINE_RE.match(line_clean.strip()):
                stop_extend = True
                unassigned_buffer.append(line_clean)
                return
            if line_clean.strip() or line_clean == "":
                buffer.append(line_clean)
            return
        probe = _normalize_docx_line_text(line_clean)
        if _STRONG_SOL_START_RE.match(probe):
            head, stop = _truncate_example_line_at_solution_start(line_clean)
            if head.strip():
                buffer.append(head)
            stop_extend = True
            return
        if line_clean.strip() or line_clean == "":
            buffer.append(line_clean)

    def stash_frozen_line(line: str) -> bool:
        """靘?閰唾圾?敺???敺?銵?蝳迫撖怠 buffer ??pending??"""
        if is_current_example and current_key and stop_extend:
            return True
        return False

    def start_key(key: str, first_line: str | None = None) -> None:
        nonlocal current_key, buffer, awaiting_exam, pending_exam_lines
        nonlocal pending_suithang_header, stop_extend, is_current_example, empty_line_count
        flush()
        awaiting_exam = False
        pending_exam_lines = []
        pending_suithang_header = False
        stop_extend = False
        empty_line_count = 0
        clear_pending_lines()
        clear_unassigned_buffer()
        current_key = key
        is_current_example = _is_example_question_key(key)
        buffer = []
        if first_line:
            cleaned = clean_problem_leading_title(first_line)
            if cleaned:
                buffer.append(cleaned)

    def begin_exam_staging(line: str) -> None:
        nonlocal awaiting_exam, pending_exam_lines, pending_suithang_header
        pending_suithang_header = False
        if awaiting_exam:
            pending_exam_lines.append(line)
            return
        flush()
        staged = list(pending_lines)
        clear_pending_lines()
        awaiting_exam = True
        pending_exam_lines = staged + [line]

    while work:
        raw = work.popleft()
        line = str(raw or "")
        if _QUESTION_TRIGGER_PREFIX in line:
            if _try_start_from_question_trigger(line):
                in_chapter_exercise = False
                continue
        line = _normalize_docx_line_text(line)

        mixed = _split_mixed_example_suithang_line(line) if line else None
        if mixed:
            head_line, tail_line = mixed
            if tail_line:
                work.appendleft(tail_line)
            line = head_line.strip()
            if not line:
                continue

        if not line:
            if stash_frozen_line(""):
                continue
            if current_key and not stop_extend:
                empty_line_count += 1
                if empty_line_count < 2:
                    append_buffer_line("")
                continue
            if awaiting_exam:
                pending_exam_lines.append("")
            else:
                _collect_orphan_line("")
            continue

        if (
            current_key
            and not stop_extend
            and not is_current_example
            and empty_line_count >= 2
        ):
            stop_extend = True
            empty_line_count = 0
            _route_practice_overflow_to_unassigned(line)
            continue

        empty_line_count = 0

        if _SCAN_KEY_LINE_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            continue

        if _EXAM_SECTION_HDR_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            in_chapter_exercise = False
            continue

        if _EXAM_BLOCK_START_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            in_exam_collecting = True
            exam_collect_buffer = []
            stop_extend = False
            empty_line_count = 0
            awaiting_exam = False
            pending_exam_lines = []
            continue

        if in_exam_collecting:
            end_m = _EXAM_END_RE.search(line)
            if end_m:
                year = str(end_m.group(1) or "").strip()
                category = _normalize_exam_category(end_m.group(2))
                exam_key = f"{int(year)}蝯望葫{category}"
                tail = _strip_exam_end_marker_from_line(line)
                if tail:
                    exam_collect_buffer.append(tail)
                _scan_flush_question_block(blocks, exam_key, list(exam_collect_buffer))
                in_exam_collecting = False
                exam_collect_buffer = []
                current_key = None
                buffer = []
                is_current_example = False
                stop_extend = False
                empty_line_count = 0
                awaiting_exam = False
                pending_exam_lines = []
                continue
            if _EXAM_BLOCK_START_RE.match(line):
                exam_collect_buffer = []
                continue
            if line.strip() or line == "":
                exam_collect_buffer.append(line)
            continue

        if sa_ctx:
            if _CH_SA_PAGE_ONLY_RE.match(line):
                continue
            if _CH_SA_CH_MARKER_RE.search(line) or line == "?芣?閰?":
                sa_started = True
                flush()
                clear_pending_lines()
                pending_suithang_header = False
                continue
            if _CH_SA_ZH_CHAPTER_RE.match(line) and "蝧?" not in line:
                flush()
                continue
            sec_m = _CH_SA_SECTION_HEADING_RE.match(line)
            if (
                sec_m
                and "蝧?" not in line
                and not _QUESTION_BOUNDARY_NUM_RE.match(line)
            ):
                flush()
                sa_started = True
                continue
            if sa_started and _QUESTION_BOUNDARY_RE.match(line):
                qn = _parse_boundary_question_number(line)
                if qn is not None:
                    start_key(f"{sa_prefix} 題{qn}", line)
                    in_chapter_exercise = False
                    continue

        boundary_flush = False
        if current_key and _scan_line_flushes_current_block(
            line,
            in_chapter_exercise=in_chapter_exercise,
            pending_suithang_header=pending_suithang_header,
        ):
            flush()
            pending_suithang_header = False
            boundary_flush = True

        exam_m = _SCAN_EXAM_MARKER_RE.search(line)
        if exam_m and not _EXAM_BLOCK_START_RE.match(line):
            exam_key = f"{int(exam_m.group(1))}蝯望葫{exam_m.group(2).upper()}"
            before = line[: exam_m.start()].strip()
            after = line[exam_m.end() :].strip()
            pending_suithang_header = False

            prior_key = current_key
            if prior_key:
                _scan_flush_question_block(blocks, prior_key, buffer)

            stem: list[str] = []
            stem.extend(unassigned_buffer)
            clear_unassigned_buffer()
            stem.extend(pending_lines)
            clear_pending_lines()
            if pending_exam_lines:
                stem.extend(pending_exam_lines)
            if before:
                stem.append(before)

            pending_exam_lines = []
            awaiting_exam = False
            stop_extend = False
            current_key = exam_key
            is_current_example = False
            buffer = [ln for ln in stem if str(ln or "").strip() or ln == ""]
            if after and not _SCAN_KEY_LINE_RE.match(after):
                append_buffer_line(after)
            continue

        if _SCAN_SUBSECTION_HEADING_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            in_chapter_exercise = False
            continue

        ex_hdr = _SCAN_EXERCISE_BLOCK_HDR_RE.match(line)
        if not ex_hdr:
            blk = re.match(r"^\s*(\d+-\d+)\s*蝧?\s*$", line)
            if blk:
                ex_hdr = blk
        if ex_hdr:
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            section_code = ex_hdr.group(1)
            in_chapter_exercise = True
            current_zone = "?嗡?"
            awaiting_exam = False
            pending_exam_lines = []
            continue

        if _SCAN_ZONE_HDR_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            current_zone = _SCAN_ZONE_HDR_RE.match(line).group(1)
            in_chapter_exercise = bool(section_code)
            continue

        ex_m = _scan_find_example_inline_start(line)
        if ex_m:
            body = clean_problem_leading_title(line[ex_m.start() :])
            start_key(f"靘?{int(ex_m.group(1))}", body or None)
            in_chapter_exercise = False
            continue

        st_key, st_line, pending_suithang_header = _scan_try_start_suithang(line, pending_suithang_header)
        if st_key:
            start_key(st_key, st_line)
            in_chapter_exercise = False
            continue
        if pending_suithang_header and not _SCAN_CHAPTER_EX_NUM_RE.match(line):
            continue
        if boundary_flush and _scan_is_structure_only_line(line):
            continue

        if stash_frozen_line(line):
            continue

        if in_chapter_exercise and section_code and current_zone in _SCAN_ZONE_HEADERS:
            mnum = _SCAN_CHAPTER_EX_NUM_RE.match(line)
            if mnum:
                n = int(mnum.group(1))
                start_key(f"{section_code}蝧? {current_zone}{n}", line)
                continue
            if current_key:
                if _SCAN_SUBPART_RE.match(line):
                    append_buffer_line(line)
                    continue
                if _SCAN_MC_OPTION_RE.match(line) or awaiting_exam:
                    begin_exam_staging(line)
                    continue
                if re.match(r"^\s*閮苒s", line):
                    begin_exam_staging(line)
                    continue
                append_buffer_line(line)
                continue

        if current_key and not in_chapter_exercise:
            append_buffer_line(line)
            continue

        if awaiting_exam or pending_exam_lines or _SCAN_MC_OPTION_RE.match(line):
            if not awaiting_exam:
                begin_exam_staging(line)
            else:
                pending_exam_lines.append(line)
            continue

        _collect_orphan_line(line)

    flush()
    anchor_meta = phase2_mathb_section_anchor_slice(lines, section_code=section_code or "")
    anchor_blocks = {k: str(v.get("problem_text") or "").strip() for k, v in anchor_meta.items()}
    # Anchor-first: use explicit DOCX anchors as canonical blocks when available.
    if anchor_blocks:
        for k, v in anchor_blocks.items():
            blocks[k] = v
        global _DOCX_BLOCK_META
        _DOCX_BLOCK_META = anchor_meta
    else:
        _DOCX_BLOCK_META = {}
    return blocks


# ---------------------------------------------------------------------------
# Phase 3
# ---------------------------------------------------------------------------

_PHASE3_CHUNK_SIZE = 10


def _chunk_blocks_keys_for_phase3(blocks_keys: list[str], chunk_size: int = _PHASE3_CHUNK_SIZE) -> list[list[str]]:
    """撠?憛?key 靘摰之撠????踹??格活 Gemini JSON ??芣??"""
    keys = list(blocks_keys or [])
    size = max(1, int(chunk_size or _PHASE3_CHUNK_SIZE))
    return [keys[i : i + size] for i in range(0, len(keys), size)]


def _section_merge_key(section_title: str) -> str:
    code = extract_section_code_from_title(section_title)
    return code or str(section_title or "").strip()


def _merge_phase3_metadata_trees(accum: dict, patch: dict) -> None:
    """?蔥憭 Phase3 JSON嚗誑 update 隤??游? chapters/sections/concepts 憿?”嚗?"""
    if not isinstance(patch, dict):
        return
    acc_chapters: list[dict] = accum.setdefault("chapters", [])
    chap_by_key: dict[str, dict] = {}
    for ch in acc_chapters:
        if isinstance(ch, dict):
            k = normalize_chapter_title_for_db(str(ch.get("chapter_title", "") or "")) or str(
                ch.get("chapter_title", "") or ""
            ).strip()
            if k:
                chap_by_key[k] = ch

    for ch in patch.get("chapters") or []:
        if not isinstance(ch, dict):
            continue
        ck = normalize_chapter_title_for_db(str(ch.get("chapter_title", "") or "")) or str(
            ch.get("chapter_title", "") or ""
        ).strip()
        target = chap_by_key.get(ck)
        if target is None:
            target = {"chapter_title": ch.get("chapter_title", ""), "sections": []}
            acc_chapters.append(target)
            if ck:
                chap_by_key[ck] = target

        sec_list: list[dict] = target.setdefault("sections", [])
        sec_by_key: dict[str, dict] = {}
        for sec in sec_list:
            if isinstance(sec, dict):
                sk = _section_merge_key(str(sec.get("section_title", "") or ""))
                if sk:
                    sec_by_key[sk] = sec

        for sec in ch.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            sk = _section_merge_key(str(sec.get("section_title", "") or ""))
            tsec = sec_by_key.get(sk)
            if tsec is None:
                tsec = {"section_title": sec.get("section_title", ""), "concepts": []}
                sec_list.append(tsec)
                if sk:
                    sec_by_key[sk] = tsec

            concepts: list[dict] = tsec.setdefault("concepts", [])
            con_by_name: dict[str, dict] = {}
            for con in concepts:
                if isinstance(con, dict):
                    nk = str(con.get("concept_name", "") or "").strip()
                    if nk:
                        con_by_name[nk] = con

            for con in sec.get("concepts") or []:
                if not isinstance(con, dict):
                    continue
                nk = str(con.get("concept_name", "") or "").strip() or "UnknownConcept"
                tcon = con_by_name.get(nk)
                if tcon is None:
                    tcon = dict(con)
                    concepts.append(tcon)
                    con_by_name[nk] = tcon
                else:
                    for field in ("concept_en_id", "concept_paragraph"):
                        if not str(tcon.get(field, "") or "").strip() and con.get(field):
                            tcon[field] = con[field]
                for bucket in ("examples", "practice_questions"):
                    seen: set[str] = set()
                    merged_list: list[dict] = []
                    for item in (tcon.get(bucket) or []) + (con.get(bucket) or []):
                        if not isinstance(item, dict):
                            continue
                        title = get_question_title(item) or ""
                        if title and title in seen:
                            continue
                        if title:
                            seen.add(title)
                        merged_list.append(item)
                    tcon[bucket] = merged_list


def _build_metadata_alignment_prompt(blocks_keys: list[str], curriculum_info: dict) -> str:
    curriculum = str(curriculum_info.get("curriculum", "") or "").strip()
    volume = str(curriculum_info.get("volume", "") or "").strip()
    subject, vol_num = parse_volume(volume)
    is_vocational_mathb = curriculum == "vocational" and subject == "B"

    base_prompt = (
        "你是教材結構化助手。請根據 converted_docx_latex 的題號清單，"
        "回傳章節/概念 metadata JSON。"
    )
    title_rules = (
        "規則如下:\n"
        "1. examples 與 practice_questions 要保留 title 與 source_description。\n"
        "2. title 需是可讀、穩定的 canonical title。\n"
        "3. problem_text 不要重複 title，correct_answer/detailed_solution 可為空字串。\n"
        "4. 所有內容需對齊 DOCX 原文語意。\n"
    )
    if is_vocational_mathb:
        title_rules += "5. 高職 B 需優先對齊 section_title 與 concept_paragraph。\n"

    parts = [
        base_prompt,
        f"curriculum={curriculum} volume={volume}",
        CONVERTED_DOCX_LATEX_JSON_RULES,
        title_rules,
        f"請輸出合法 JSON，格式可參考:\n{_JSON_EXAMPLE_METADATA_ONLY}",
        "請確保每題都能對應到 metadata。",
    ]
    for key in blocks_keys:
        parts.append(f"- canonical_title={key}")
    if not blocks_keys:
        parts.append("(no titles detected ??still output JSON skeleton with empty arrays)")
    return "\n".join(parts)


def _phase3_gemini_metadata_for_keys(
    blocks_keys: list[str],
    curriculum_info: dict,
    queue,
    *,
    chunk_label: str = "",
) -> dict:
    model = get_model("architect")
    prompt = _build_metadata_alignment_prompt(blocks_keys, curriculum_info)
    ctx = "antigravity metadata alignment"
    if chunk_label:
        ctx = f"{ctx} ({chunk_label})"
    raw = _call_gemini_with_retry(
        model,
        prompt,
        queue=queue,
        context_message=ctx,
        parse_json=True,
    )
    if not raw:
        raise RuntimeError("Gemini ?芸??單???JSON")
    parsed = safe_load_gemini_json(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("Gemini JSON ?寧?暺?? object")
    return parsed


def phase3_ai_metadata_alignment(
    blocks_keys: list[str],
    curriculum_info: dict,
    queue,
) -> dict:
    """Gemini ??朣?憿?????蝡???璅?JSON嚗之?寞活?芸????蔥嚗?"""
    keys = list(blocks_keys or [])
    chunks = _chunk_blocks_keys_for_phase3(keys)
    total = len(chunks)

    if queue is not None:
        queue.put(
            f"INFO: [antigravity] Phase3 Gemini metadata alignment "
            f"(keys={len(keys)} chunks={total} chunk_size={_PHASE3_CHUNK_SIZE})"
        )

    if total <= 1:
        return _phase3_gemini_metadata_for_keys(keys, curriculum_info, queue)

    merged: dict = {"chapters": []}
    for idx, chunk in enumerate(chunks, start=1):
        label = f"chunk {idx}/{total}"
        if queue is not None:
            queue.put(f"INFO: [antigravity] Phase3 {label} keys={len(chunk)}")
        part = _phase3_gemini_metadata_for_keys(
            chunk, curriculum_info, queue, chunk_label=label
        )
        _merge_phase3_metadata_trees(merged, part)
    return merged


# ---------------------------------------------------------------------------
# Phase 4 helpers
# ---------------------------------------------------------------------------


def _sanitize_db_latex_delimiters(text: str) -> str:
    """?亙澈?? \\[ / \\] 頧 $嚗??蝡臬撥?嗆?銵???"""
    if not text:
        return ""
    return str(text).replace(r"\[", "$").replace(r"\]", "$")


def _extract_loose_question_number(title: str) -> str | None:
    """敺?Gemini ?瑟?憿?摮葡擛??瑕?憿?嚗???. ?拍?芾??艾? 9嚗?"""
    m = re.search(r"(\d+)", str(title or ""))
    return m.group(1) if m else None


def _self_assessment_admin_label(curriculum_info: dict, db_chapter: str = "") -> str:
    """?芣?閰?敺?箄?嚗嗾瘛冽???蝐歹?銝 dedupe ?釭??"""
    ch_m = re.match(r"^(\d+)", str(db_chapter or "").strip())
    ch_num: int | None = int(ch_m.group(1)) if ch_m else None
    if ch_num is None:
        _, vol_num = parse_volume(str(curriculum_info.get("volume", "") or ""))
        if isinstance(vol_num, int):
            ch_num = vol_num
    cn_map = {
        1: "一",
        2: "二",
        3: "三",
        4: "四",
        5: "五",
        6: "六",
        7: "七",
        8: "八",
        9: "九",
        10: "十",
    }
    if ch_num and ch_num in cn_map:
        return f"第{cn_map[ch_num]}章章末評量"
    return "章末評量"


def _build_source_description(
    title: str,
    source_type: str,
    *,
    linked_example_title: str | None = None,
    needs_review: bool = False,
    dedupe_hash: str = "",
    section_context: str | None = None,
    admin_label: str | None = None,
) -> str:
    if admin_label:
        return str(admin_label).strip()
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


def _normalize_problem_hash(problem_text: str, *, source_type: str = "", title: str = "") -> str:
    normalized = re.sub(r"\s+", " ", str(problem_text or "")).strip()
    payload = {
        "source_type": str(source_type or "").strip().lower(),
        "title": str(title or "").strip(),
        "problem": normalized,
        "sub_questions": [],
    }
    return hashlib.sha1(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]


def _compact_title_key(title: str) -> str:
    t = str(title or "").strip()
    t = re.sub(r"[\s_－—\-·…\.．、:：]+", "", t)
    return t


def normalize_chapter_title_for_db(chapter_title: str) -> str:
    """撠?Gemini 撣貉??洵N蝡?璅???朣 DB ???? 璅???"""
    t = str(chapter_title or "").strip()
    if not t or not t.startswith("第") or "章" not in t:
        return t
    m = re.match(r"^第\s*(\d+)\s*章\s*(.*)$", t, flags=re.UNICODE)
    if not m:
        return t
    num = str(m.group(1)).strip()
    rest = str(m.group(2) or "").strip()
    return f"{num} {rest}".strip() if rest else num


MATHB1_CHAPTER1_CANONICAL_TITLE = "1 坐標系與函數圖形"


def _import_scope_coords(curriculum_info: dict) -> dict[str, Any]:
    """隤脩雇 + 撟渡? + ? 銝?銝擃漣璅?Phase4 ?亥岷嚗神?亙?剁???"""
    return {
        "curriculum": str(curriculum_info.get("curriculum", "") or "").strip(),
        "grade": int(curriculum_info.get("grade", 10)),
        "volume": str(curriculum_info.get("volume", "") or "").strip(),
    }


def _is_vocational_math_b1(curriculum_info: dict) -> bool:
    coords = _import_scope_coords(curriculum_info)
    subject, vol_num = parse_volume(coords["volume"])
    return coords["curriculum"] == "vocational" and subject == "B" and vol_num == 1


def _force_mathb1_chapter_title(chapter_title: str, *, enabled: bool) -> str:
    if not enabled:
        return chapter_title
    if chapter_title != MATHB1_CHAPTER1_CANONICAL_TITLE:
        _log_info(
            f"[antigravity] mathb1 chapter_title forced: {chapter_title!r} "
            f"-> {MATHB1_CHAPTER1_CANONICAL_TITLE!r}"
        )
    return MATHB1_CHAPTER1_CANONICAL_TITLE


def _is_chapter_self_assessment_import(raw_chapter: str, question_blocks: dict[str, str]) -> bool:
    if "?芣?閰?" in str(raw_chapter or ""):
        return True
    return any("?芣?閰?" in str(k) for k in (question_blocks or {}))


def _row_matches_import_scope(row: TextbookExample, coords: dict[str, Any]) -> bool:
    """隞?SkillCurriculum 撟渡?嚗??亦雁摨阡?瑁楊?炊?寥?嚗??亙?閮梢?撘?撠???"""
    if str(getattr(row, "source_curriculum", "") or "") != coords["curriculum"]:
        return False
    row_vol = str(getattr(row, "source_volume", "") or "")
    if row_vol and coords.get("volume") and not _volume_labels_match(row_vol, coords["volume"]):
        return False
    skill_id = str(getattr(row, "skill_id", "") or "").strip()
    if not skill_id:
        return False
    linked = SkillCurriculum.query.filter(
        SkillCurriculum.skill_id == skill_id,
        SkillCurriculum.curriculum == coords["curriculum"],
    ).first()
    if linked is not None:
        if coords.get("volume") and not _volume_labels_match(
            str(getattr(linked, "volume", "") or ""), coords["volume"]
        ):
            return False
        return True
    return not SkillCurriculum.query.filter_by(skill_id=skill_id).first()


def _extract_title_from_source_description(source_description: str) -> str:
    return str(source_description or "").split(" [", 1)[0].strip()


def _block_key_matches_question_num(block_key: str, num: str) -> bool:
    """?砍憿? key ?臬撠???憿?嚗? CH1?芣?閰? 憿?嚗?"""
    if not num:
        return False
    k = str(block_key or "")
    if re.search(rf"憿s*{re.escape(num)}\b", k):
        return True
    if re.search(rf"(?<!\d){re.escape(num)}(?!\d)", k) and re.search(
        rf"(?:^|\s){re.escape(num)}\s*[\.\?)\t]", k
    ):
        return True
    return False


def _row_matches_self_assessment_question_number(row: TextbookExample, num: str) -> bool:
    if not num:
        return False
    parts = [
        str(getattr(row, "source_paragraph", "") or ""),
        str(getattr(row, "problem_text", "") or "")[:120],
        _extract_title_from_source_description(str(getattr(row, "source_description", "") or "")),
    ]
    blob = " ".join(parts)
    if re.search(rf"憿s*{re.escape(num)}\b", blob):
        return True
    head = str(getattr(row, "problem_text", "") or "").strip()
    return bool(re.match(rf"^{re.escape(num)}\s*[\.\?)\t]", head))


def _find_existing_by_structural_title(
    *,
    skill_id: str,
    curriculum_info: dict,
    chapter_title: str,
    section_title: str,
    source_type: str,
    title: str,
) -> TextbookExample | None:
    """隞亦?瑽漣璅?+ 憿璅?瘥??Ｘ???dedupe_hash 銝????典摰???"""
    coords = _import_scope_coords(curriculum_info)
    rows = TextbookExample.query.filter_by(
        skill_id=skill_id,
        source_curriculum=coords["curriculum"],
        source_volume=coords["volume"],
        source_chapter=chapter_title,
        source_section=section_title,
        problem_type=source_type,
    ).all()

    if source_type == "self_assessment":
        q_num = _extract_loose_question_number(title)
        if q_num:
            for row in rows:
                if not _row_matches_import_scope(row, coords):
                    continue
                if _row_matches_self_assessment_question_number(row, q_num):
                    return row
        return None

    target = _compact_title_key(title)
    if not target:
        return None
    for row in rows:
        if not _row_matches_import_scope(row, coords):
            continue
        row_title = _extract_title_from_source_description(
            str(getattr(row, "source_description", "") or "")
        )
        if _compact_title_key(row_title) == target:
            return row
    return None


_EXAM_TITLE_IN_TITLE_RE = re.compile(
    r"(\d{2,3})\s*學測\s*([A-Ca-c])",
    re.IGNORECASE | re.UNICODE,
)


def _question_title_kind(title: str) -> str:
    """憿?憭折?嚗絞皜?/ ?典? / 靘? / 蝧? / ?嗡???"""
    t = str(title or "")
    if "蝯望葫" in t:
        return "exam"
    if "?典?" in t:
        return "suitang"
    if "靘?" in t or re.search(r"靘s*\d", t):
        return "example"
    if "蝧?" in t:
        return "exercise"
    return "generic"


def _question_block_key_kind(key: str) -> str:
    k = str(key or "")
    if "蝯望葫" in k:
        return "exam"
    if "?典?" in k:
        return "suitang"
    if "靘?" in k or re.search(r"靘s*\d", k):
        return "example"
    if "蝧?" in k:
        return "exercise"
    return "generic"


def _pick_single_block_match(
    candidates: list[str],
    question_blocks: dict[str, str],
) -> tuple[str, str]:
    if not candidates:
        return "", ""
    k = min(candidates, key=lambda x: (len(str(x)), str(x)))
    body = _sanitize_db_latex_delimiters(str(question_blocks.get(k, "") or ""))
    return body.strip(), k


def _normalize_loose_text(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text or ""))
    t = re.sub(r"\\[a-zA-Z]+", " ", t)
    t = re.sub(r"[\{\}\[\]\(\)\$]", " ", t)
    t = re.sub(r"\s+", "", t)
    return t


def _contains_common_cjk_bigram(a: str, b: str) -> bool:
    a2 = re.sub(r"[^\u4e00-\u9fff]", "", a)
    b2 = re.sub(r"[^\u4e00-\u9fff]", "", b)
    if len(a2) < 2 or len(b2) < 2:
        return False
    chunks = {a2[i : i + 2] for i in range(len(a2) - 1)}
    return any(ch in b2 for ch in chunks)


def _loose_match_quality_ok(title: str, key: str) -> bool:
    nt = _normalize_loose_text(title)
    nk = _normalize_loose_text(key)
    if not nt or not nk:
        return False
    if _contains_common_cjk_bigram(nt, nk):
        return True
    if SequenceMatcher(None, nt, nk).ratio() >= 0.45:
        return True
    frag = re.sub(r"\s+", "", str(title or ""))
    frag = re.sub(r"\\[a-zA-Z]+", "", frag)
    frag = re.sub(r"[^\u4e00-\u9fff0-9A-Za-z\.\-、，,;；:：\(\)（）\[\]]", "", frag)
    frag = frag[:12].strip()
    if frag and frag in str(key or ""):
        return True
    return False


def _lookup_exam_block_loose(title: str, question_blocks: dict[str, str]) -> tuple[str, str]:
    """蝚砌?頠?蝯望葫憿???隞?撟港遢 + 蝯望葫 + ?? 撠??砍 key嚗? 111蝯望葫B嚗?"""
    raw = str(title or "")
    if "蝯望葫" not in raw and not _EXAM_TITLE_IN_TITLE_RE.search(raw):
        return "", ""

    m = _EXAM_TITLE_IN_TITLE_RE.search(raw)
    if not m:
        compact = re.sub(r"[\s_\-\.]+", "", raw).upper()
        m = re.search(r"(\d{2,3})蝯望葫([A-C嚗?嚗β)", compact, re.I)

    if not m:
        return "", ""

    year = str(m.group(1)).strip()
    category = _normalize_exam_category(m.group(2))
    needle = f"{year}蝯望葫{category}"
    hits: list[str] = []
    for k in question_blocks:
        if _question_block_key_kind(k) != "exam":
            continue
        compact_k = re.sub(r"[\s_\-\.]+", "", str(k)).upper()
        if needle in compact_k or (
            year in compact_k and "蝯望葫" in str(k) and category in compact_k
        ):
            hits.append(k)

    return _pick_single_block_match(hits, question_blocks)


def _extract_practice_number_from_title(title: str) -> str | None:
    """Extract a practice/example number from a title safely."""
    text = str(title or "").strip()
    if not text:
        return None

    head = text[:80].strip()

    patterns = [
        r"(?:隨堂練習|練習)\s*([0-9０-９]+)",
        r"(?:例題|例)\s*([0-9０-９]+)",
        r"第\s*([0-9０-９]+)\s*題",
        r"^\s*([0-9０-９]+)\s*[\.．、\)]?\s+",
        r"^[\(（]\s*([0-9０-９]+)\s*[\)）]",
    ]

    trans = str.maketrans("０１２３４５６７８９", "0123456789")

    for pat in patterns:
        try:
            m = re.search(pat, head, flags=re.IGNORECASE | re.UNICODE)
        except re.error as exc:
            try:
                current_app.logger.warning(
                    "[antigravity] skip invalid regex in _extract_practice_number_from_title: pattern=%r error=%s",
                    pat,
                    exc,
                )
            except Exception:
                pass
            continue
        if not m:
            continue
        raw = str(m.group(1) or "").translate(trans).strip()
        if not raw:
            continue
        return raw

    m = re.search(r"([0-9０-９]+)", head)
    if not m:
        return None
    return str(m.group(1) or "").translate(trans).strip() or None


def _practice_num_matches_block_key(key: str, num: str, kind: str) -> bool:
    def _safe_search(pattern: str, text: str, flags: int = 0):
        try:
            return re.search(pattern, text, flags)
        except re.error as exc:
            try:
                current_app.logger.warning(
                    "[antigravity] skip invalid regex in _practice_num_matches_block_key: pattern=%r error=%s",
                    pattern,
                    exc,
                )
            except Exception:
                pass
            return None

    k = str(key or "")
    key_kind = _question_block_key_kind(k)
    if kind != "generic" and key_kind not in (kind, "generic"):
        return False

    if kind == "suitang":
        patterns = (
            rf"隨堂練習\s*{re.escape(num)}\b",
            rf"練習\s*{re.escape(num)}\b",
            rf"第\s*{re.escape(num)}\s*題",
        )
        return any(_safe_search(p, k, re.I) for p in patterns)
    if kind == "example":
        patterns = (
            rf"例題\s*{re.escape(num)}\b",
            rf"例\s*{re.escape(num)}\b",
        )
        return any(_safe_search(p, k, re.I) for p in patterns)

    if _safe_search(rf"隨堂練習\s*{re.escape(num)}\b", k, re.I):
        return True
    if _safe_search(rf"練習\s*{re.escape(num)}\b", k, re.I):
        return True
    if _safe_search(rf"例題\s*{re.escape(num)}\b", k, re.I):
        return True
    return _block_key_matches_question_num(k, num)


def _lookup_practice_block_loose(
    title: str,
    question_blocks: dict[str, str],
    *,
    queue=None,
) -> tuple[str, str]:
    """蝚砌?頠??典?/靘? ??擐?憿? + 憿?憭折?擛?撠???"""
    kind = _question_title_kind(title)
    if kind == "exam":
        return "", ""

    num = _extract_practice_number_from_title(title)
    if not num:
        return "", ""

    hits: list[str] = []
    for k in question_blocks:
        k_kind = _question_block_key_kind(k)
        if kind != "generic" and k_kind != kind:
            continue
        match_kind = kind if kind != "generic" else k_kind
        if _practice_num_matches_block_key(k, num, match_kind):
            if not _loose_match_quality_ok(title, k):
                _log_info(
                    f"[antigravity] skip loose number match: title={title!r} key={k!r} reason=low_similarity"
                )
                if queue is not None:
                    queue.put(
                        f"INFO: [antigravity] skip loose number match: title={title!r} key={k!r} reason=low_similarity"
                    )
                continue
            hits.append(k)

    if not hits and kind == "generic":
        for match_kind in ("suitang", "example"):
            hits = [
                k
                for k in question_blocks
                if _question_block_key_kind(k) == match_kind
                and _practice_num_matches_block_key(k, num, match_kind)
                and _loose_match_quality_ok(title, k)
            ]
            if hits:
                break

    return _pick_single_block_match(hits, question_blocks)


def _lookup_question_block(
    title: str,
    question_blocks: dict[str, str],
    *,
    is_self_assessment: bool = False,
    queue=None,
) -> tuple[str, str]:
    """?‵憿凳嚗?頠?撘?撠?+ LaTeX 皜?????(block_text, matched_key)??"""
    if not title or not question_blocks:
        return "", ""

    def _pack(body: str, key: str) -> tuple[str, str]:
        return _sanitize_db_latex_delimiters(str(body or "")).strip(), key

    if title in question_blocks:
        return _pack(question_blocks[title], title)

    compact = _compact_title_key(title)
    for k, v in question_blocks.items():
        if _compact_title_key(k) == compact:
            return _pack(v, k)

    if not is_self_assessment:
        body, key = _lookup_exam_block_loose(title, question_blocks)
        if body and key:
            return body, key

        body, key = _lookup_practice_block_loose(title, question_blocks, queue=queue)
        if body and key:
            return body, key

    q_num = _extract_loose_question_number(str(title).split("\n")[0])
    if q_num:
        strong = [
            k
            for k in question_blocks
            if re.search(rf"題\s*{re.escape(q_num)}\b", str(k))
            and _loose_match_quality_ok(title, k)
        ]
        if len(strong) == 1:
            return _pack(question_blocks[strong[0]], strong[0])
        if len(strong) > 1:
            k = min(strong, key=len)
            return _pack(question_blocks[k], k)

        loose = [
            k
            for k in question_blocks
            if _block_key_matches_question_num(k, q_num) and _loose_match_quality_ok(title, k)
        ]
        if len(loose) == 1:
            return _pack(question_blocks[loose[0]], loose[0])
        if len(loose) > 1:
            prefer = [k for k in loose if re.search(rf"題\s*{re.escape(q_num)}\b", str(k))]
            pool = prefer or loose
            k = min(pool, key=len)
            return _pack(question_blocks[k], k)

    return "", ""


def _normalize_volume_key(volume: str) -> str:
    """擛?瘥??嚗摮睬1 / B1 / ?詨飛 B1 ???? key??"""
    subject, vol_num = parse_volume(str(volume or ""))
    if subject and isinstance(vol_num, int):
        return f"{subject.upper()}{vol_num}"
    compact = re.sub(r"\s+", "", str(volume or "")).upper()
    m = re.search(r"([AB])(\d+)", compact)
    if m:
        return f"{m.group(1)}{m.group(2)}"
    return compact


def _volume_labels_match(db_volume: str, form_volume: str) -> bool:
    if not db_volume or not form_volume:
        return False
    if str(db_volume).strip() == str(form_volume).strip():
        return True
    return _normalize_volume_key(db_volume) == _normalize_volume_key(form_volume)


def _section_code_boundary_matches(section_code: str, section_label: str) -> bool:
    """撠?隞?Ⅳ??蝎暹?瘥?嚗?-1 ?臬? 2-1 ??嚗?銝炊??2-10??"""
    code = unicodedata.normalize("NFKC", str(section_code or "").strip())
    label = unicodedata.normalize("NFKC", str(section_label or "").strip())
    if not code or not label.startswith(code):
        return False
    if len(label) == len(code):
        return True
    return label[len(code)] in " \t\u3000.-??"


def _resolve_section_code_for_outline_lookup(
    section_code: str,
    *,
    gemini_section_title: str = "",
) -> str:
    return unicodedata.normalize(
        "NFKC",
        str(section_code or "").strip() or extract_section_code_from_title(gemini_section_title),
    )


def _is_short_section_code_only(label: str) -> bool:
    """?撠?隞?Ⅳ嚗? 1-1嚗摰璅?????閮?prefix ?雁瘥???"""
    s = unicodedata.normalize("NFKC", str(label or "").strip())
    return bool(re.fullmatch(r"\d+-\d+", s))


def _curriculum_authority_coords(row: SkillCurriculum) -> dict[str, str]:
    """
    憭抒雇甈?摨扳?嚗銝?靘?嚗???SkillCurriculum ORM ?????箝?
    chapter / section 甈?隤??撠? chapter_title / section_title??
    """
    return {
        "skill_id": str(getattr(row, "skill_id", "") or "").strip(),
        "curriculum": str(getattr(row, "curriculum", "") or "").strip(),
        "volume": str(getattr(row, "volume", "") or "").strip(),
        "chapter_title": str(getattr(row, "chapter", "") or "").strip(),
        "section_title": str(getattr(row, "section", "") or "").strip(),
    }


def _dynamic_curriculum_lookup_by_section_code(
    curriculum_info: dict,
    section_code: str,
    *,
    hint_skill_id: str = "",
) -> SkillCurriculum | None:
    """
    ?典??之蝬梁移皞????臬 scope ??curriculum + volume + 憿?撠?隞?Ⅳ??
    隞?section.startswith(f\"{code} \") ??甈???蝳迫 LIKE %??甇?Gemini 璅?嚗?
    """
    coords = _import_scope_coords(curriculum_info)
    curr = str(coords.get("curriculum") or "").strip()
    vol = str(coords.get("volume") or "").strip()
    code = unicodedata.normalize(
        "NFKC",
        str(section_code or "").strip() or str(curriculum_info.get("section_code") or "").strip(),
    )
    if not curr or not vol or not code or code.endswith("-review"):
        return None

    prefix = f"{code} "
    candidates: list[SkillCurriculum] = (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curr,
            SkillCurriculum.volume == vol,
            SkillCurriculum.section.startswith(prefix),
        )
        .order_by(
            SkillCurriculum.display_order.asc(),
            SkillCurriculum.id.asc(),
        )
        .all()
    )
    bounded = [
        c
        for c in candidates
        if _section_code_boundary_matches(code, str(getattr(c, "section", "") or ""))
    ]
    if not bounded:
        _log_info(
            f"[antigravity][DYNAMIC] outline miss curriculum={curr!r} volume={vol!r} code={code!r}"
        )
        return None

    if len(bounded) == 1:
        hit = bounded[0]
    else:
        hint_sid = str(hint_skill_id or "").strip()

        def _pick_key(row: SkillCurriculum) -> tuple:
            sid = str(getattr(row, "skill_id", "") or "")
            return (
                0 if hint_sid and sid == hint_sid else 1,
                0 if sid.startswith("vh_") and not sid.startswith("outline_") else 1,
                len(str(getattr(row, "section", "") or "")),
                int(getattr(row, "display_order", 0) or 0),
                int(getattr(row, "id", 0) or 0),
            )

        hit = min(bounded, key=_pick_key)
        _log_info(
            f"[antigravity][DYNAMIC] code={code!r} ambiguous n={len(bounded)} "
            f"picked section={getattr(hit, 'section', '')!r}"
        )

    auth = _curriculum_authority_coords(hit)
    _log_info(
        f"[antigravity][DYNAMIC] code={code!r} -> volume={auth['volume']!r} "
        f"chapter={auth['chapter_title']!r} section={auth['section_title']!r} "
        f"skill_id={auth['skill_id']!r}"
    )
    return hit


def _lookup_curriculum_exact_three_dimensions(
    curriculum_info: dict,
    *,
    section_label: str = "",
    section_code: str = "",
    gemini_section_title: str = "",
    hint_skill_id: str = "",
) -> SkillCurriculum | None:
    """
    ?潮?湔?脩?嚗玨蝬?+ ? + 摰撠??迂銝雁摨衣移皞??潭?撠?==嚗?
    ?蝎暹??賜征銝?亦?凋誨蝣潭?嚗?隞乓code} ???prefix ?雁嚗?甇?LIKE %嚗?
    """
    coords = _import_scope_coords(curriculum_info)
    curr = str(coords.get("curriculum") or "").strip()
    vol = str(coords.get("volume") or "").strip()
    if not vol:
        return None

    code = _resolve_section_code_for_outline_lookup(
        section_code, gemini_section_title=gemini_section_title
    )
    section_exact = str(section_label or curriculum_info.get("section") or "").strip()
    if not section_exact and code:
        _, section_exact = _canonical_outline_section_title(code, gemini_section_title)
    if section_exact and _is_short_section_code_only(section_exact):
        section_exact = ""

    if section_exact:
        hit = (
            SkillCurriculum.query.filter(
                SkillCurriculum.curriculum == curr,
                SkillCurriculum.volume == vol,
                SkillCurriculum.section == section_exact,
            )
            .order_by(
                SkillCurriculum.display_order.asc(),
                SkillCurriculum.id.asc(),
            )
            .first()
        )
        if hit:
            _log_info(
                f"[antigravity][EXACT] 3D match volume={vol!r} section={section_exact!r} "
                f"skill_id={getattr(hit, 'skill_id', '')!r}"
            )
            return hit
        _log_info(
            f"[antigravity][EXACT] miss volume={vol!r} section={section_exact!r}"
        )

    if not code or not _is_short_section_code_only(code):
        return None

    prefix = f"{code} "
    candidates: list[SkillCurriculum] = (
        SkillCurriculum.query.filter(
            SkillCurriculum.curriculum == curr,
            SkillCurriculum.volume == vol,
            SkillCurriculum.section.startswith(prefix),
        )
        .order_by(
            SkillCurriculum.display_order.asc(),
            SkillCurriculum.id.asc(),
        )
        .all()
    )
    if not candidates:
        _log_info(
            f"[antigravity][EXACT] prefix fallback miss code={code!r} volume={vol!r}"
        )
        return None

    bounded = [
        c
        for c in candidates
        if _section_code_boundary_matches(code, str(getattr(c, "section", "") or ""))
    ]
    if bounded:
        candidates = bounded

    if len(candidates) == 1:
        hit = candidates[0]
    else:
        hint_sid = str(hint_skill_id or "").strip()

        def _pick_key(row: SkillCurriculum) -> tuple:
            sid = str(getattr(row, "skill_id", "") or "")
            return (
                0 if hint_sid and sid == hint_sid else 1,
                0 if sid.startswith("vh_") and not sid.startswith("outline_") else 1,
                len(str(getattr(row, "section", "") or "")),
                int(getattr(row, "display_order", 0) or 0),
                int(getattr(row, "id", 0) or 0),
            )

        hit = min(candidates, key=_pick_key)
        _log_info(
            f"[antigravity][EXACT] prefix {prefix!r} ambiguous n={len(candidates)} "
            f"picked section={getattr(hit, 'section', '')!r}"
        )

    _log_info(
        f"[antigravity][EXACT] prefix {prefix!r} -> "
        f"section(DB)={getattr(hit, 'section', '')!r} volume={getattr(hit, 'volume', '')!r}"
    )
    return hit


def _lookup_curriculum_by_authoritative_section_code(
    curriculum_info: dict,
    section_code: str,
    *,
    hint_skill_id: str = "",
) -> SkillCurriculum | None:
    """?亙? ???典???蝭隞?Ⅳ憭抒雇????"""
    return _dynamic_curriculum_lookup_by_section_code(
        curriculum_info,
        section_code,
        hint_skill_id=hint_skill_id,
    )


def _lookup_readonly_curriculum_row(
    curriculum_info: dict,
    section_code: str,
    *,
    gemini_section_title: str = "",
    skill_id: str = "",
    section_title: str = "",
) -> SkillCurriculum | None:
    """Phase4 憭抒雇?航??亥岷?亙 ???? section_code 銝駁嚗蕭??Gemini 璅?嚗?"""
    _ = gemini_section_title, section_title
    return _dynamic_curriculum_lookup_by_section_code(
        curriculum_info,
        section_code,
        hint_skill_id=skill_id,
    )


def _phase4_sync_skill_info_category(
    row: SkillCurriculum,
    skill_id: str,
) -> bool:
    """
    撘瑕 skills_info.category = 憭抒雇 section嚗RM 甈???section嚗?? section_title嚗?
    瘣? AI 隤文神??1-3 ?臭?蝑?蝭瘙⊥???
    """
    sid = str(skill_id or getattr(row, "skill_id", "") or "").strip()
    authoritative_section = str(getattr(row, "section", "") or "").strip()
    if not sid or not authoritative_section:
        return False
    skill_info = SkillInfo.query.get(sid)
    if skill_info is None:
        return False
    old = str(skill_info.category or "").strip()
    if old:
        return False
    skill_info.category = "outline"
    if old != "outline":
        _log_info(
            f"[antigravity] SkillInfo.category authority-fix skill_id={sid!r}: "
            f"{old!r} -> {'outline'!r}"
        )
        return True
    return False


def _phase4_propagate_curriculum_authority(
    example: TextbookExample,
    row: SkillCurriculum,
    *,
    skill_id: str = "",
) -> tuple[dict[str, str], bool]:
    """
    憭抒雇甈?摨扳??喳?嚗?甇?TextbookExample 撟曆?甈? + SkillsInfo.category??
    ? (authority coords, category_was_fixed)??
    """
    auth = _curriculum_authority_coords(row)
    sid = str(skill_id or auth["skill_id"] or "").strip()
    example.skill_id = sid
    example.source_curriculum = auth["curriculum"]
    example.source_volume = auth["volume"]
    example.source_chapter = auth["chapter_title"]
    example.source_section = auth["section_title"]
    _assert_textbook_geometry_not_shifted(example, auth)
    category_fixed = _phase4_sync_skill_info_category(row, sid)
    return auth, category_fixed


def _assert_textbook_geometry_not_shifted(
    example: TextbookExample,
    auth: dict[str, str],
) -> None:
    """?菜葫甈?撌衣宏嚗olume 隤文神??curriculum 蝑?嚗???撠撖急香?摮葡??"""
    curr = auth["curriculum"]
    vol = auth["volume"]
    ch = auth["chapter_title"]
    sec = auth["section_title"]
    shifted = (
        (curr and example.source_volume == curr)
        or (vol and example.source_chapter == vol)
        or (ch and example.source_section == ch and example.source_chapter != ch)
    )
    if shifted:
        _log_error(
            "[antigravity] FATAL geometry shift on TextbookExample: "
            f"volume={example.source_volume!r} chapter={example.source_chapter!r} "
            f"section={example.source_section!r} expected volume={vol!r} chapter={ch!r} "
            f"section={sec!r}"
        )
        example.source_curriculum = curr
        example.source_volume = vol
        example.source_chapter = ch
        example.source_section = sec


def _phase4_apply_authoritative_bindings(
    example: TextbookExample,
    row: SkillCurriculum,
    *,
    skill_id: str = "",
) -> None:
    """???詨捆?亙? ??_phase4_propagate_curriculum_authority??"""
    _phase4_propagate_curriculum_authority(example, row, skill_id=skill_id)


def _textbook_geometry_from_curriculum_row(
    row: SkillCurriculum,
    *,
    skill_id_override: str = "",
) -> dict[str, str]:
    """
    朣憚?⊥迤嚗extbookExample 撟曆?摨扳???SkillCurriculum 甈?銝銝撠???
    ORM: curriculum / volume / chapter / section ??憿澈: source_curriculum / source_volume /
    source_chapter / source_section嚗蝳?摨椰蝘駁雿???
    """
    sid = str(skill_id_override or getattr(row, "skill_id", "") or "").strip()
    auth = _curriculum_authority_coords(row)
    geo = {
        "skill_id": sid,
        "source_curriculum": auth["curriculum"],
        "source_volume": auth["volume"],
        "source_chapter": auth["chapter_title"],
        "source_section": auth["section_title"],
    }
    if geo["source_volume"] == geo["source_curriculum"] and geo["source_curriculum"]:
        _log_error(
            f"[antigravity] geometry column shift suspected: {geo!r} "
            f"row.volume={getattr(row, 'volume', '')!r} row.chapter={getattr(row, 'chapter', '')!r}"
        )
    return geo


def _apply_textbook_geometry_to_example(
    example: TextbookExample,
    row: SkillCurriculum,
    *,
    skill_id_override: str = "",
) -> None:
    """
    甇?儔朣憚?⊥迤嚗?亙?憭抒雇??ORM 撅祆扯釵?潘?蝳迫 dict/霈??銝剛??臭???
    chapter_title ??row.chapter嚗ection_title ??row.section??
    """
    _phase4_propagate_curriculum_authority(
        example, row, skill_id=skill_id_override or ""
    )


def _reverse_align_textbook_source_from_curriculum(
    row: SkillCurriculum,
) -> dict[str, str]:
    """???詨捆?亙? ??_textbook_geometry_from_curriculum_row??"""
    return _textbook_geometry_from_curriculum_row(row)


def _coords_from_curriculum_row(
    row: SkillCurriculum,
    curriculum_info: dict | None = None,
) -> dict[str, Any]:
    """?勗之蝬勗???撠??臬摨扳?嚗神??TextbookExample ?剁???"""
    aligned = _reverse_align_textbook_source_from_curriculum(row)
    base = _import_scope_coords(curriculum_info or {})
    return {
        "curriculum": aligned["source_curriculum"] or base["curriculum"] or "vocational",
        "volume": aligned["source_volume"] or base["volume"] or "",
        "grade": int(getattr(row, "grade", None) or base.get("grade") or 10),
    }


def _canonical_db_chapter_from_row(
    row: SkillCurriculum,
    curriculum_info: dict | None = None,
) -> str:
    """?亙澈蝡???100% 隞?DB chapter ?箸?嚗1 撘瑕撠?璅??? ??蝟餉??賣?耦??"""
    ch = str(getattr(row, "chapter", "") or "").strip()
    if not ch:
        return ch
    normalized = normalize_chapter_title_for_db(ch)
    if curriculum_info and _is_vocational_math_b1(curriculum_info):
        return _force_mathb1_chapter_title(normalized or ch, enabled=True)
    return normalized or ch


def _db_titles_from_curriculum_row(
    row: SkillCurriculum,
    curriculum_info: dict | None = None,
) -> tuple[str, str, str]:
    """Read canonical titles from SkillCurriculum row for phase4 mapping."""
    _ = curriculum_info
    return (
        str(getattr(row, "skill_id", "") or "").strip(),
        str(getattr(row, "chapter", "") or "").strip(),
        str(getattr(row, "section", "") or "").strip(),
    )


def _extract_section_code_from_block_key(block_key: str) -> str:
    m = re.search(r"(\d+-\d+)", str(block_key or ""))
    return m.group(1) if m else ""


def _resolve_authoritative_section_code(
    curriculum_info: dict,
    *,
    matched_key: str = "",
    gemini_section_code: str = "",
    title: str = "",
) -> str:
    """
    甈?撠?蝣潸圾??蝳迫?脖縑 Gemini section_title嚗?
    ?芸?摨?瑼?/?臬 scope section_code ??憿? key ??憿 title ??Gemini??
    """
    file_code = str(curriculum_info.get("section_code") or "").strip()
    if file_code and not file_code.endswith("-review"):
        return file_code

    from_key = _extract_section_code_from_block_key(matched_key)
    if from_key:
        return from_key

    from_title = extract_section_code_from_title(title)
    if from_title:
        return from_title

    return str(gemini_section_code or "").strip()


_SOURCE_DESC_POLLUTION_RE = re.compile(
    r"\s*\[(?:source_type|section|dedupe|linked_example|needs_review)=[^\]]*\]",
    re.IGNORECASE,
)


def _strip_source_description_pollution(text: str, *, fallback: str = "") -> str:
    """? [source_type=?帆section=?帆dedupe=?因 蝑?亙??豢??釭??"""
    t = str(text or "").strip()
    if not t:
        return fallback
    if " [" in t:
        t = t.split(" [", 1)[0].strip()
    t = _SOURCE_DESC_POLLUTION_RE.sub("", t).strip()
    t = re.sub(r"\s*\|+\s*$", "", t).strip()
    return t or fallback


def _phase4_clean_source_description(
    *,
    raw_description: str = "",
    title: str = "",
    source_type: str = "",
    authority_row: SkillCurriculum | None = None,
    is_self_assessment: bool = False,
    curriculum_info: dict | None = None,
    db_chapter: str = "",
) -> str:
    """
    Phase4 銋暹楊?箄?嚗迤????[source_type=?帆dedupe=?因 ?釭??
    ?∪神甇颱葉???亦蝛箏?靘之蝬望?憡?????title / source_type ???‵??
    """
    _ = curriculum_info, db_chapter
    cleaned = _strip_source_description_pollution(
        str(raw_description or title or "").strip(),
        fallback="",
    )
    if cleaned:
        return cleaned
    if authority_row is not None:
        auth = _curriculum_authority_coords(authority_row)
        if is_self_assessment:
            parts = [p for p in (auth["chapter_title"], auth["section_title"]) if p]
            if parts:
                return " ".join(parts)
        if auth["section_title"]:
            return auth["section_title"]
        if auth["chapter_title"]:
            return auth["chapter_title"]
    return str(source_type or title or "").strip()


def _normalize_source_type_v2(item: dict, raw_source_type: str = "") -> str:
    raw = str(raw_source_type or item.get("source_type") or "").strip().lower()
    zh = str(item.get("source_type") or "").strip()
    mapping = {
        "example": "textbook_example",
        "textbook_example": "textbook_example",
        "practice": "textbook_practice",
        "exercise": "textbook_practice",
        "in_class_practice": "in_class_practice",
        "self_assessment": "self_assessment",
    }
    if zh == "隨堂練習":
        return "in_class_practice"
    if zh == "例題":
        return "textbook_example"
    if raw in mapping:
        return mapping[raw]
    guess = normalize_source_type_by_title(item, default_source_type="textbook_example")
    guess_raw = str(guess or "").strip().lower()
    return mapping.get(guess_raw, "textbook_example")


def _has_balanced_pair(text: str, left: str, right: str) -> bool:
    return str(text or "").count(left) == str(text or "").count(right)


def _is_bad_fragment_title(title_or_problem_text: str) -> tuple[bool, str]:
    t = str(title_or_problem_text or "").strip()
    if not t:
        return True, "empty"
    low = t.lower()
    if low.endswith("\\") or low.endswith("\\rig") or low.endswith("\\righ") or low.endswith("\\lef") or low.endswith("\\left"):
        return True, "truncated_latex"
    if "\\left|" in t and "\\right|" not in t:
        return True, "unbalanced_left_right"
    if len(t) < 6 and not re.match(r"^\s*\d+\s*$", t):
        return True, "too_short"
    if re.match(r"^\s*\d+\.\s*\\\[\s*\\left\|.*<\s*$", t):
        return True, "latex_opening_only"
    if not _has_balanced_pair(t, "\\left(", "\\right)") or not _has_balanced_pair(t, "\\left[", "\\right]"):
        return True, "unbalanced_latex_paren"
    if t.count("(") != t.count(")") or t.count("（") != t.count("）"):
        return True, "unbalanced_brackets"
    return False, ""


def _normalize_skill_id_quality(skill_id: str) -> str:
    return re.sub(r"\s+", "", str(skill_id or "")).strip()


def clear_textbook_examples_for_section(volume: str, section: str) -> int:
    """Helper for one-section cleanup before re-import."""
    result = db.session.query(TextbookExample).filter(
        TextbookExample.source_volume == str(volume or "").strip(),
        TextbookExample.source_section == str(section or "").strip(),
    ).delete(synchronize_session=False)
    db.session.commit()
    return int(result or 0)


def _shield_log_missing_outline(
    section_code: str,
    *,
    queue,
    gemini_section_title: str = "",
) -> None:
    label = str(section_code or "").strip() or str(gemini_section_title or "").strip() or "?"
    msg = (
        f"[antigravity][SHIELD] missing curriculum mapping for section={label}; skip this block"
    )
    _log_info(msg)
    if queue is not None:
        queue.put(f"WARNING: {msg}")


# ---------------------------------------------------------------------------
# Phase 4
# ---------------------------------------------------------------------------


def phase4_absolute_hydrate_and_save(
    parsed_data: dict,
    question_blocks: dict[str, str],
    curriculum_info: dict,
    queue,
) -> dict[str, int]:
    """瘙箏??折?撟孵?憛思蒂 Upsert ?唾??澈??"""
    coords = _import_scope_coords(curriculum_info)
    subject, vol_num = parse_volume(coords["volume"])
    is_vocational_mathb = coords["curriculum"] == "vocational" and subject == "B"
    is_self_assessment_import = _is_chapter_self_assessment_import("", question_blocks)

    inserted = 0
    updated = 0
    hydrated = 0
    skipped = 0
    outline_shield_skipped = 0
    skills_category_fixed = 0
    skipped_fragment_count = 0
    loose_match_skipped_count = 0
    anchor_compact_map = {_compact_title_key(k): k for k in _DOCX_BLOCK_META.keys()}

    if queue is not None:
        queue.put("INFO: [antigravity] Phase4 hydrate and DB upsert (read-only outline)")

    for chapter_data in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter_data, dict):
            continue
        raw_chapter = str(chapter_data.get("chapter_title", "?芰蝡?") or "").strip()
        if not is_self_assessment_import:
            is_self_assessment_import = _is_chapter_self_assessment_import(raw_chapter, question_blocks)

        for section_data in chapter_data.get("sections", []) or []:
            if not isinstance(section_data, dict):
                continue
            gemini_section_title = str(section_data.get("section_title", "") or "").strip()
            sec_code = (
                str(section_data.get("section_code", "") or "").strip()
                or extract_section_code_from_title(gemini_section_title)
            )
            if sec_code:
                _log_info(
                    f"[antigravity] section_code from section_title: "
                    f"{gemini_section_title!r} -> {sec_code!r}"
                )
            for concept in section_data.get("concepts", []) or []:
                if not isinstance(concept, dict):
                    continue
                concept_name = str(concept.get("concept_name", "UnknownConcept") or "").strip()

                for bucket in ("examples", "practice_questions"):
                    for item in concept.get(bucket, []) or []:
                        if not isinstance(item, dict):
                            continue
                        title = get_question_title(item) or ""
                        if not title:
                            skipped += 1
                            continue
                        anchor_key = ""
                        if _DOCX_BLOCK_META:
                            anchor_key = _DOCX_BLOCK_META.get(title, {}).get("anchor", "")
                            if not anchor_key:
                                anchor_key = anchor_compact_map.get(_compact_title_key(title), "")
                            if not anchor_key:
                                skipped += 1
                                continue

                        if is_self_assessment_import:
                            source_type = "self_assessment"
                        else:
                            source_type = _normalize_source_type_v2(item)
                        if source_type == "section_exposition":
                            skipped += 1
                            continue

                        if anchor_key:
                            matched_key = anchor_key
                            block = str(_DOCX_BLOCK_META.get(anchor_key, {}).get("problem_text") or "")
                        else:
                            block, matched_key = _lookup_question_block(
                                title,
                                question_blocks,
                                is_self_assessment=(
                                    is_self_assessment_import or source_type == "self_assessment"
                                ),
                                queue=queue,
                            )
                        if not block:
                            _log_info(f"[antigravity] missing block for title={title}")
                            if queue is not None:
                                queue.put(f"WARNING: [antigravity] ?∪???憛?title={title}")
                            skipped += 1
                            if _extract_practice_number_from_title(title):
                                loose_match_skipped_count += 1
                            continue
                        if matched_key and matched_key != title:
                            _log_info(
                                f"[antigravity] block matched by question number: "
                                f"title={title!r} -> key={matched_key!r}"
                            )
                        block_meta = _DOCX_BLOCK_META.get(matched_key or "", {})
                        if block_meta.get("source_type"):
                            source_type = str(block_meta.get("source_type"))

                        item_sec_code = _resolve_authoritative_section_code(
                            curriculum_info,
                            matched_key=matched_key or "",
                            gemini_section_code=sec_code,
                            title=title,
                        )
                        concept_en_id = str(concept.get("concept_en_id", "Unknown") or "")
                        clean_en_id = re.sub(r"[^a-zA-Z0-9]", "", concept_en_id) or "Unknown"
                        if is_vocational_mathb:
                            hint_skill_id = normalize_vocational_math_skill_id(
                                subject, vol_num, clean_en_id
                            )
                        else:
                            hint_skill_id = f"vh_{clean_en_id}"

                        existing_curriculum = _lookup_readonly_curriculum_row(
                            curriculum_info,
                            item_sec_code,
                            skill_id=hint_skill_id,
                        )
                        if existing_curriculum is None:
                            _shield_log_missing_outline(
                                item_sec_code,
                                queue=queue,
                                gemini_section_title=gemini_section_title,
                            )
                            outline_shield_skipped += 1
                            continue

                        auth = _curriculum_authority_coords(existing_curriculum)
                        skill_id = _normalize_skill_id_quality(
                            str(auth["skill_id"] or hint_skill_id or "").strip()
                        )

                        if not auth["section_title"]:
                            _shield_log_missing_outline(
                                item_sec_code,
                                queue=queue,
                                gemini_section_title=gemini_section_title,
                            )
                            outline_shield_skipped += 1
                            continue

                        if not _section_code_boundary_matches(
                            item_sec_code, auth["section_title"]
                        ):
                            _log_error(
                                f"[antigravity] section_code mismatch: code={item_sec_code!r} "
                                f"db_section={auth['section_title']!r} ??skip to prevent cross-wire"
                            )
                            outline_shield_skipped += 1
                            continue
                        expected_volume = str(curriculum_info.get("volume") or coords.get("volume") or "").strip()
                        expected_chapter = str(curriculum_info.get("chapter") or "").strip()
                        expected_section = str(curriculum_info.get("section") or "").strip()
                        if (
                            (expected_volume and auth["volume"] != expected_volume)
                            or (expected_chapter and auth["chapter_title"] != expected_chapter)
                            or (expected_section and auth["section_title"] != expected_section)
                        ):
                            _log_info(
                                f"[antigravity] skip row by quality gate: volume={auth['volume']!r} chapter={auth['chapter_title']!r} section={auth['section_title']!r}"
                            )
                            skipped += 1
                            continue

                        _log_info(
                            f"[antigravity] authority-bind title={title!r} "
                            f"sec_code={item_sec_code!r} (file={curriculum_info.get('section_code')!r} "
                            f"gemini={sec_code!r}) -> "
                            f"volume={auth['volume']!r} chapter={auth['chapter_title']!r} "
                            f"section={auth['section_title']!r} skill_id={skill_id!r}"
                        )

                        hydrated += 1
                        base_problem = str(block_meta.get("problem_text") or block or "")
                        db_problem_text = _sanitize_db_latex_delimiters(
                            clean_problem_leading_title(base_problem)
                        )
                        bad_title, bad_title_reason = _is_bad_fragment_title(title)
                        if block_meta:
                            bad_title, bad_title_reason = (False, "")
                        bad_block, bad_block_reason = _is_bad_fragment_title(db_problem_text)
                        if len(db_problem_text) < 8:
                            bad_block, bad_block_reason = True, "too_short_problem"
                        if bad_title or bad_block:
                            _log_info(
                                f"[antigravity] skip bad fragment title={title!r} reason={bad_block_reason or bad_title_reason!r}"
                            )
                            skipped_fragment_count += 1
                            skipped += 1
                            continue
                        db_answer = _sanitize_db_latex_delimiters(
                            str(item.get("correct_answer") or "")
                        )
                        db_solution = _sanitize_db_latex_delimiters(
                            str(block_meta.get("detailed_solution") or item.get("detailed_solution") or "")
                        )
                        item["title"] = title
                        item["problem_text"] = db_problem_text
                        item["correct_answer"] = db_answer
                        item["detailed_solution"] = db_solution

                        source_description = _phase4_clean_source_description(
                            raw_description=str(block_meta.get("anchor") or item.get("source_description") or ""),
                            title=title,
                            source_type=source_type,
                            authority_row=existing_curriculum,
                            is_self_assessment=(
                                is_self_assessment_import or source_type == "self_assessment"
                            ),
                        )
                        item["source_description"] = source_description
                        bad_desc, _ = _is_bad_fragment_title(source_description)
                        if bad_desc and not bad_block:
                            source_description = title if not bad_title else auth["section_title"]
                            item["source_description"] = source_description
                        source_description = re.sub(r"^(例\s*[0-9０-９]+)_+$", r"\1", source_description).strip()
                        source_description = re.sub(r"^(隨堂練習\s*[0-9０-９]+)_+$", r"\1", source_description).strip()
                        source_description = source_description.replace(" ", "")
                        item["source_description"] = source_description
                        if block_meta.get("source_type"):
                            source_type = str(block_meta.get("source_type"))

                        section_coords = _coords_from_curriculum_row(
                            existing_curriculum, curriculum_info
                        )
                        lookup_coords = {
                            "curriculum": auth["curriculum"],
                            "volume": auth["volume"],
                            "grade": section_coords.get("grade", coords["grade"]),
                        }
                        existing = _find_existing_by_structural_title(
                            skill_id=skill_id,
                            curriculum_info=lookup_coords,
                            chapter_title=auth["chapter_title"],
                            section_title=auth["section_title"],
                            source_type=source_type,
                            title=title,
                        )

                        try:
                            difficulty_level = int(item.get("difficulty_level", 1))
                        except Exception:
                            difficulty_level = 1

                        category_fixed = False
                        if existing:
                            existing.problem_text = db_problem_text
                            existing.correct_answer = db_answer
                            existing.detailed_solution = db_solution
                            _, category_fixed = _phase4_propagate_curriculum_authority(
                                existing, existing_curriculum, skill_id=skill_id
                            )
                            existing.source_paragraph = concept_name
                            existing.source_description = source_description
                            existing.problem_type = source_type or existing.problem_type
                            updated += 1
                        else:
                            new_row = TextbookExample(
                                skill_id=skill_id,
                                source_curriculum=auth["curriculum"],
                                source_volume=auth["volume"],
                                source_chapter=auth["chapter_title"],
                                source_section=auth["section_title"],
                                source_description=source_description,
                                source_paragraph=concept_name,
                                problem_text=db_problem_text,
                                problem_type=source_type or "calculation",
                                correct_answer=db_answer,
                                detailed_solution=db_solution,
                                difficulty_level=difficulty_level,
                            )
                            _, category_fixed = _phase4_propagate_curriculum_authority(
                                new_row, existing_curriculum, skill_id=skill_id
                            )
                            db.session.add(new_row)
                            inserted += 1

                        if category_fixed:
                            skills_category_fixed += 1

    db.session.commit()
    total = inserted + updated
    if queue is not None:
        queue.put(
            f"INFO: [antigravity] 匯入完成 inserted={inserted} updated={updated} "
            f"hydrated={hydrated} skipped={skipped} "
            f"outline_shield_skipped={outline_shield_skipped} "
            f"skills_category_fixed={skills_category_fixed} "
            f"skipped_fragment_count={skipped_fragment_count} "
            f"loose_match_skipped_count={loose_match_skipped_count}"
        )
    return {
        "inserted": inserted,
        "updated": updated,
        "total": total,
        "hydrated": hydrated,
        "skipped": skipped,
        "curriculums_added": 0,
        "outline_shield_skipped": outline_shield_skipped,
        "skills_category_fixed": skills_category_fixed,
        "skipped_fragment_count": skipped_fragment_count,
        "loose_match_skipped_count": loose_match_skipped_count,
    }


# ---------------------------------------------------------------------------
# PDF outline (mode two) ??SkillCurriculum sync
# ---------------------------------------------------------------------------

PDF_OUTLINE_MAX_PAGES = 5

_PDF_OUTLINE_JSON_EXAMPLE = """
{
  "curriculum": "vocational",
  "volume": "數學B1",
  "grade": 10,
  "chapters": [
    {
      "chapter_title": "1 坐標系與函數圖形",
      "sections": [
        {"section_code": "1-1", "section_title": "1-1 數線與絕對值"},
        {"section_code": "1-2", "section_title": "1-2 平面坐標系與線型函數"},
        {"section_code": "1-3", "section_title": "1-3 二次函數"},
        {"section_code": "1-4", "section_title": "1-4 不等式"}
      ]
    },
    {
      "chapter_title": "2 直線與圓",
      "sections": [
        {"section_code": "2-1", "section_title": "2-1 直線方程式"},
        {"section_code": "2-2", "section_title": "2-2 圓方程式"},
        {"section_code": "2-3", "section_title": "2-3 直線與圓關係"}
      ]
    }
  ]
}
""".strip()

_OUTLINE_CN_CHAPTER_DIGITS = {
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
    "十": 10,
}

_OUTLINE_SKIP_SECTION_TOKENS = ("章末評量", "習題", "總複習", "隨堂練習", "題組", "學測題組")


def _is_outline_skip_section_title(section_title: str) -> bool:
    t = str(section_title or "").strip()
    if not t:
        return True
    return any(tok in t for tok in _OUTLINE_SKIP_SECTION_TOKENS)


def _resolve_outline_grade(curriculum_info: dict) -> int:
    """靘?curriculum_info ????(B1??0, B2??1?? 閫??撟渡???"""
    try:
        g = int(curriculum_info.get("grade", 0))
        if g >= 10:
            return g
    except (TypeError, ValueError):
        pass
    _, vol_num = parse_volume(str(curriculum_info.get("volume", "") or ""))
    if isinstance(vol_num, int) and vol_num >= 1:
        return 9 + vol_num
    return 10


def _cn_chapter_numeral_to_int(token: str) -> int | None:
    """撠???銝??銝剜??詨?頧?踵?隡舀摮?蝡??剁???"""
    s = str(token or "").strip()
    if not s:
        return None
    if s.isdigit():
        return int(s)
    if s in _OUTLINE_CN_CHAPTER_DIGITS:
        return _OUTLINE_CN_CHAPTER_DIGITS[s]
    if s.startswith("十"):
        tail = s[1:]
        if not tail:
            return 10
        tail_n = _OUTLINE_CN_CHAPTER_DIGITS.get(tail)
        return 10 + tail_n if tail_n else None
    if "十" in s:
        left, _, right = s.partition("十")
        tens = _OUTLINE_CN_CHAPTER_DIGITS.get(left, 1 if left == "" else None)
        ones = _OUTLINE_CN_CHAPTER_DIGITS.get(right, 0 if right == "" else None)
        if tens is not None and ones is not None:
            return tens * 10 + ones
    return None


def _normalize_outline_chapter_title_strict(chapter_title: str) -> str:
    """
    蝡??迂瘙箏??扳?瘣?撠? DB ???? 璅???
    靘?蝚?蝡???蝟領???1 ??蝟領佗?蝚砌?蝡???1 ?佗?蝚?2 蝡??渡?????2 ?渡???
    """
    t = unicodedata.normalize("NFKC", str(chapter_title or "").strip())
    if not t:
        return ""

    t = normalize_chapter_title_for_db(t)

    m = re.match(r"^蝚枯s*(\d+)\s*蝡?\s*(.*)$", t, flags=re.UNICODE)
    if m:
        num = str(int(m.group(1)))
        rest = str(m.group(2) or "").strip()
        return f"{num} {rest}".strip() if rest else num

    m = re.match(r"^蝚枯s*([銝鈭????凋??思??+)\s*蝡?\s*(.*)$", t, flags=re.UNICODE)
    if m:
        num_i = _cn_chapter_numeral_to_int(m.group(1))
        rest = str(m.group(2) or "").strip()
        if num_i is not None:
            return f"{num_i} {rest}".strip() if rest else str(num_i)

    t = re.sub(r"^蝚枯s*", "", t)
    t = re.sub(r"^\s*蝡s*", "", t).strip()

    m = re.match(r"^(\d+)\s*[\.?)]?\s*(.+)$", t, flags=re.UNICODE)
    if m:
        return f"{int(m.group(1))} {str(m.group(2) or '').strip()}".strip()

    m = re.match(r"^(\d+)$", t)
    if m:
        return str(int(m.group(1)))

    if "章" in t and not re.match(r"^\d+\s+\S", t):
        t = re.sub(r"章", " ", t, count=1).strip()
        t = re.sub(r"\s+", " ", t)
        m = re.match(r"^(\d+)\s+(.+)$", t)
        if m:
            return f"{int(m.group(1))} {m.group(2).strip()}"

    return t.strip()


def _canonical_outline_chapter_title(chapter_title: str, curriculum_info: dict) -> str:
    ch = _normalize_outline_chapter_title_strict(chapter_title)
    if not ch:
        return "?芰蝡?"
    if _is_vocational_math_b1(curriculum_info) and re.match(r"^1\s", ch):
        return _force_mathb1_chapter_title(ch, enabled=True)
    return ch


def _canonical_outline_section_title(section_code: str, section_title: str) -> tuple[str, str]:
    """? (section_code, section_title) 撠? DB section 甈??????-1 ?貊???撠潦?"""
    title = str(section_title or "").strip()
    code = str(section_code or "").strip() or extract_section_code_from_title(title)
    if not code:
        return "", title
    if not title:
        return code, code
    if title.startswith(code):
        return code, title
    m = re.match(r"^(\d+-\d+)\s*(.*)$", title)
    if m and m.group(1) == code:
        return code, title
    name = re.sub(r"^\d+-\d+\s*", "", title).strip()
    return code, f"{code} {name}".strip() if name else code


def _outline_placeholder_skill_id(curriculum: str, volume: str, section_title: str) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]", "", str(section_title or "")) or "UnknownSection"
    return f"outline_{curriculum}_{volume}_{clean}"


def extract_pdf_directory_text_v2(
    file_path: str,
    *,
    max_pages: int = PDF_OUTLINE_MAX_PAGES,
) -> tuple[str, int]:
    """????PDF ??N ??銝? 5嚗???嚗???(pdf_directory_text, pages_read)??"""
    path = str(file_path or "").strip()
    if not path or not path.lower().endswith(".pdf"):
        raise ValueError("???.pdf 瑼?")
    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    cap = max(1, min(int(max_pages or PDF_OUTLINE_MAX_PAGES), PDF_OUTLINE_MAX_PAGES))
    chunks: list[str] = []
    pages_read = 0

    try:
        from pypdf import PdfReader

        reader = PdfReader(path)
        page_count = len(reader.pages)
        pages_read = min(cap, page_count)
        _log_info(f"[antigravity][pdf] pypdf pages={page_count} read={pages_read}")
        for i in range(pages_read):
            text = reader.pages[i].extract_text() or ""
            if text.strip():
                chunks.append(text)
    except ImportError:
        import fitz

        doc = fitz.open(path)
        try:
            page_count = len(doc)
            pages_read = min(cap, page_count)
            _log_info(f"[antigravity][pdf] pymupdf fallback pages={page_count} read={pages_read}")
            for i in range(pages_read):
                text = doc[i].get_text() or ""
                if text.strip():
                    chunks.append(text)
        finally:
            doc.close()

    return "\n\n".join(chunks).strip(), pages_read


def _normalize_parsed_pdf_outline_payload(parsed: dict, curriculum_info: dict) -> dict:
    """Normalize Gemini PDF outline payload into canonical chapter/section titles."""
    coords = _import_scope_coords(curriculum_info)
    out_chapters: list[dict] = []
    for ch in parsed.get("chapters") or []:
        if not isinstance(ch, dict):
            continue
        chapter_title = _canonical_outline_chapter_title(
            str(ch.get("chapter_title", "") or ""), curriculum_info
        )
        sections_out: list[dict] = []
        for sec in ch.get("sections") or []:
            if not isinstance(sec, dict):
                continue
            code, title = _canonical_outline_section_title(
                str(sec.get("section_code", "") or ""),
                str(sec.get("section_title", "") or ""),
            )
            if not code:
                continue
            sections_out.append({"section_code": code, "section_title": title})
        if sections_out:
            out_chapters.append({"chapter_title": chapter_title, "sections": sections_out})
    return {
        "curriculum": coords["curriculum"] or "vocational",
        "volume": coords["volume"],
        "grade": _resolve_outline_grade(curriculum_info),
        "chapters": out_chapters,
    }


def _build_pdf_outline_gemini_prompt(pdf_directory_text: str, curriculum_info: dict) -> str:
    coords = _import_scope_coords(curriculum_info)
    grade = _resolve_outline_grade(curriculum_info)
    volume = coords["volume"] or "?詨飛B1"
    curriculum = coords["curriculum"] or "vocational"

    return "\n".join(
        [
            "System: You are a curriculum structuring assistant.",
            "請從 PDF 目錄文字抽取章節，輸出合法 JSON 供 SkillCurriculum 同步。",
            "",
            "chapter_title 規則：",
            "- chapter_title 必須可直接對應到教材章名。",
            "- 同一冊內章節名稱需一致，避免同義詞混用。",
            "",
            "section 規則：",
            "- 每筆 section 必須包含 section_code 與 section_title。",
            '- section_code 格式例如 "1-1"、"1-2"、"2-3"。',
            '- section_title 建議格式例如 "1-1 數線與絕對值"。',
            "",
            "輸出 Schema：",
            f'- "curriculum": "{curriculum}"',
            f'- "volume": "{volume}"',
            f'- "grade": {grade}',
            '- 必須包含 keys: curriculum, volume, grade, chapters',
            "",
            "Few-shot 範例：",
            _PDF_OUTLINE_JSON_EXAMPLE,
            "",
            f"Input context: volume={volume} grade={grade} curriculum={curriculum}",
            "",
            "PDF 目錄文字：",
            pdf_directory_text[:120000],
        ]
    )


def _call_gemini_pdf_outline(
    pdf_directory_text: str,
    curriculum_info: dict,
    queue,
) -> dict:
    if queue is not None:
        queue.put("INFO: [antigravity] Phase PDF: Gemini 目錄結構萃取")
    model = get_model("architect")
    prompt = _build_pdf_outline_gemini_prompt(pdf_directory_text, curriculum_info)
    raw = _call_gemini_with_retry(
        model,
        prompt,
        queue=queue,
        context_message="antigravity PDF outline sync",
        parse_json=True,
    )
    if not raw:
        raise RuntimeError("Gemini ?芸??單???JSON")
    parsed = safe_load_gemini_json(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("Gemini JSON ?寧?暺?? object")
    normalized = _normalize_parsed_pdf_outline_payload(parsed, curriculum_info)
    if queue is not None:
        for ch in normalized.get("chapters") or []:
            queue.put(f"INFO: [antigravity] outline chapter={ch.get('chapter_title')!r}")
    return normalized


def _ensure_outline_skill_info_v2(
    *,
    skill_id: str,
    section_title: str,
    chapter_title: str,
    curriculum: str,
    volume: str,
    grade: int,
) -> SkillInfo:
    """Ensure outline placeholder exists in skills_info before FK writes."""
    existing = db.session.get(SkillInfo, skill_id)
    if existing:
        if not getattr(existing, "skill_ch_name", None):
            existing.skill_ch_name = section_title or chapter_title or skill_id
        if not getattr(existing, "skill_en_name", None):
            existing.skill_en_name = skill_id
        if not getattr(existing, "category", None):
            existing.category = "outline"
        if hasattr(existing, "is_active"):
            existing.is_active = False
        if not getattr(existing, "description", None):
            existing.description = f"{volume} {chapter_title} {section_title} outline placeholder".strip()
        if not getattr(existing, "input_type", None):
            existing.input_type = "text"
        if getattr(existing, "gemini_prompt", None) is None:
            existing.gemini_prompt = ""
        return existing

    item = SkillInfo(
        skill_id=skill_id,
        skill_en_name=skill_id,
        skill_ch_name=section_title or chapter_title or skill_id,
        category="outline",
        description=f"{volume} {chapter_title} {section_title} outline placeholder".strip(),
        input_type="text",
        gemini_prompt="",
        consecutive_correct_required=3,
        is_active=False,
        order_index=9999,
    )
    db.session.add(item)
    return item


def _sync_skill_curriculum_outline_v2(parsed: dict, curriculum_info: dict, queue) -> dict[str, int]:
    """靘?Gemini 憭抒雇 JSON 撠?SkillCurriculum 撘瑕???Upsert嚗hapter / section 甈?嚗?"""
    db.session.rollback()

    curriculum = str(curriculum_info.get("curriculum", "") or parsed.get("curriculum") or "vocational").strip()
    volume = str(curriculum_info.get("volume", "") or parsed.get("volume") or "").strip()
    if not volume:
        raise ValueError("volume 銝?箇征")
    grade = _resolve_outline_grade(curriculum_info)
    try:
        gemini_grade = int(parsed.get("grade", grade))
        if gemini_grade >= 10:
            grade = gemini_grade
    except (TypeError, ValueError):
        pass

    chapters_created = 0
    sections_created = 0
    sections_updated = 0
    processed_chapters: set[str] = set()

    chapters = parsed.get("chapters") or []
    if not isinstance(chapters, list):
        raise RuntimeError("chapters must be a list")

    try:
        for ch_data in chapters:
            if not isinstance(ch_data, dict):
                continue
            chapter_title = _canonical_outline_chapter_title(
                str(ch_data.get("chapter_title", "") or ""), curriculum_info
            )
            sections = ch_data.get("sections") or []
            if not isinstance(sections, list):
                continue

            for sec_data in sections:
                if not isinstance(sec_data, dict):
                    continue
                sec_code, sec_title = _canonical_outline_section_title(
                    str(sec_data.get("section_code", "") or ""),
                    str(sec_data.get("section_title", "") or ""),
                )
                if not sec_code or _is_outline_skip_section_title(sec_title):
                    _log_info(f"[antigravity][pdf] skip section: {sec_title!r}")
                    continue

                skill_id = _outline_placeholder_skill_id(curriculum, volume, sec_title)
                with db.session.no_autoflush:
                    _log_info(f"[antigravity][pdf] ENSURE outline SkillInfo skill_id='{skill_id}'")
                    _ensure_outline_skill_info_v2(
                        skill_id=skill_id,
                        section_title=sec_title,
                        chapter_title=chapter_title,
                        curriculum=curriculum,
                        volume=volume,
                        grade=grade,
                    )

                    existing = (
                        SkillCurriculum.query.filter(
                            SkillCurriculum.curriculum == curriculum,
                            SkillCurriculum.volume == volume,
                            SkillCurriculum.grade == grade,
                            SkillCurriculum.chapter == chapter_title,
                            SkillCurriculum.section == sec_title,
                            SkillCurriculum.skill_id == skill_id,
                        )
                        .order_by(SkillCurriculum.display_order.asc(), SkillCurriculum.id.asc())
                        .first()
                    )

                    if existing is not None:
                        existing.skill_id = skill_id
                        existing.chapter = chapter_title
                        existing.section = sec_title
                        existing.display_order = 0
                        existing.difficulty_level = 1
                        sections_updated += 1
                        _log_info(
                            f"[antigravity][pdf] UPDATE SkillCurriculum section='{sec_title}' skill_id='{skill_id}'"
                        )
                    else:
                        db.session.add(
                            SkillCurriculum(
                                skill_id=skill_id,
                                curriculum=curriculum,
                                grade=grade,
                                volume=volume,
                                chapter=chapter_title,
                                section=sec_title,
                                paragraph=None,
                                display_order=0,
                                difficulty_level=1,
                            )
                        )
                        sections_created += 1
                        if chapter_title not in processed_chapters:
                            chapters_created += 1
                            processed_chapters.add(chapter_title)
                        _log_info(
                            f"[antigravity][pdf] INSERT SkillCurriculum section='{sec_title}' skill_id='{skill_id}'"
                        )

        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    if queue is not None:
        queue.put(
            f"INFO: [antigravity] 大綱同步完成 created={sections_created} "
            f"updated={sections_updated} chapters={chapters_created}"
        )
    return {
        "chapters_created": chapters_created,
        "sections_created": sections_created,
        "sections_updated": sections_updated,
    }


def process_pdf_outline_v2(
    file_path: str,
    curriculum_info: dict,
    queue=None,
    *,
    toc_pages: int = PDF_OUTLINE_MAX_PAGES,
) -> dict[str, Any]:
    """
    PDF 璅∪?鈭蜓?亙嚗? 5 ???摮???Gemini 蝯? JSON ??SkillCurriculum Upsert??
    """
    result: dict[str, Any] = {
        "success": False,
        "status": "error",
        "chapters_created": 0,
        "sections_created": 0,
        "sections_updated": 0,
        "pages_read": 0,
        "error": "",
    }
    try:
        if queue is not None:
            queue.put(f"INFO: [antigravity] PDF 大綱模式開始: {os.path.basename(file_path)}")

        cap = max(1, min(int(toc_pages or PDF_OUTLINE_MAX_PAGES), PDF_OUTLINE_MAX_PAGES))
        pdf_directory_text, pages_read = extract_pdf_directory_text_v2(file_path, max_pages=cap)
        result["pages_read"] = pages_read

        if not pdf_directory_text.strip():
            msg = "PDF 前幾頁未擷取到可用目錄文字"
            result["error"] = msg
            if queue is not None:
                queue.put(f"ERROR: [antigravity] {msg}")
            return result

        if queue is not None:
            queue.put(
                f"INFO: [antigravity] PDF 目錄文字長度={len(pdf_directory_text)} "
                f"(前 {cap} 頁)"
            )

        parsed = _call_gemini_pdf_outline(pdf_directory_text, curriculum_info, queue)
        stats = _sync_skill_curriculum_outline_v2(parsed, curriculum_info, queue)
        result.update(stats)
        result["success"] = True
        result["status"] = "success"
        _log_info(
            f"[antigravity] process_pdf_outline_v2 done "
            f"created={stats['sections_created']} updated={stats['sections_updated']}"
        )
        return result
    except ResourceExhausted as exc:
        db.session.rollback()
        result["error"] = str(exc)
        if queue is not None:
            queue.put(f"ERROR: [antigravity] Gemini 配額耗盡: {exc}")
        raise
    except Exception as exc:
        db.session.rollback()
        result["error"] = str(exc)
        _log_error(f"[antigravity] process_pdf_outline_v2 failed: {exc}\n{traceback.format_exc()}")
        if queue is not None:
            queue.put(f"ERROR: [antigravity] {type(exc).__name__}: {exc}")
        raise


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def process_textbook_file_v2(file_path: str, curriculum_info: dict, queue) -> dict:
    """Main Antigravity V2 DOCX import flow."""
    result: dict[str, Any] = {
        "success": False,
        "inserted": 0,
        "updated": 0,
        "total": 0,
        "blocks": 0,
        "block_anchor_count": 0,
        "error": "",
    }
    try:
        if queue is not None:
            queue.put(f"INFO: [antigravity] 開始處理 DOCX：{file_path}")
        _log_info(f"[antigravity] process_textbook_file_v2 path={file_path}")

        lines = phase1_extract_docx_lines(file_path)
        if queue is not None:
            queue.put(f"INFO: [antigravity] Phase1 lines={len(lines)}")

        filename_meta = parse_textbook_filename_metadata(file_path)
        file_section_code = str((filename_meta or {}).get("section_code") or "").strip()
        if file_section_code and not str(curriculum_info.get("section_code") or "").strip():
            curriculum_info["section_code"] = file_section_code
        source_scope = str((filename_meta or {}).get("source_scope") or "section_textbook").strip()
        if _is_chapter_self_assessment_scope(source_scope):
            source_scope = "chapter_self_assessment"
        question_blocks = phase2_deterministic_block_slice(lines, source_scope=source_scope)
        result["blocks"] = len(question_blocks)
        result["block_anchor_count"] = len(_DOCX_BLOCK_META)
        if queue is not None:
            queue.put(
                f"INFO: [antigravity] Phase2 question_blocks={len(question_blocks)} "
                f"block_anchor_count={len(_DOCX_BLOCK_META)}"
            )

        blocks_keys = sorted(question_blocks.keys())
        parsed = phase3_ai_metadata_alignment(blocks_keys, curriculum_info, queue)

        stats = phase4_absolute_hydrate_and_save(parsed, question_blocks, curriculum_info, queue)
        result.update(stats)
        result["success"] = True
        _log_info(
            f"[antigravity] done inserted={stats['inserted']} updated={stats['updated']} total={stats['total']}"
        )
        return result
    except ResourceExhausted as exc:
        db.session.rollback()
        result["error"] = str(exc)
        _log_error(f"[antigravity] ResourceExhausted: {exc}\n{traceback.format_exc()}")
        if queue is not None:
            queue.put(f"ERROR: [antigravity] Gemini ???: {exc}")
        raise
    except Exception as exc:
        db.session.rollback()
        result["error"] = str(exc)
        _log_error(f"[antigravity] failed: {exc}\n{traceback.format_exc()}")
        if queue is not None:
            queue.put(f"ERROR: [antigravity] {type(exc).__name__}: {exc}")
        raise



