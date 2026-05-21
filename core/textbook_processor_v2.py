# -*- coding: utf-8 -*-
"""
Antigravity 教材匯入線路（converted_docx_latex 專用）。
僅處理 MathType 預轉 LaTeX 之 Word DOCX，不依賴 PDF / OCR / Pix2Tex。
"""

from __future__ import annotations

import hashlib
import json
import re
import traceback
from collections import deque
from typing import Any

from flask import current_app, has_app_context
from google.api_core.exceptions import ResourceExhausted

from core.ai_analyzer import get_model
from core.textbook_processor import (
    CONVERTED_DOCX_LATEX_JSON_RULES,
    _call_gemini_with_retry,
    get_question_title,
    normalize_source_type_by_title,
    parse_volume,
    safe_load_gemini_json,
)
from core.utils import normalize_vocational_math_skill_id
from models import SkillCurriculum, SkillInfo, TextbookExample, db

# ---------------------------------------------------------------------------
# Regex barriers
# ---------------------------------------------------------------------------

_LEADING_TITLE_RE = re.compile(
    r"^\s*(?:例(?:題)?|隨堂練習|習題|基礎題|進階題|自我評量)\s*\d{0,3}\s*[\s\.,、，\.：:·…·]*"
    r"|^\s*\d{1,2}\s*[\s\.,、，\.：:·…·]+"
)

# 例題專用：獨立成行的詳解起手式（僅 .match 行首，不誤傷題幹內嵌字眼）
_STRONG_SOL_START_RE = re.compile(
    r"^\s*(?:因式分解得|可化為|整理得|由[圖表]可知|移項得|設f\(x\)=|設g\(x\)=|"
    r"因為不等式|因為\[|所以\[|由此得知)"
)
# 隨堂／習題／統測：題後插入的觀念課文起手（行首 .match 即凍結並溢流 unassigned）
_PURE_CONCEPT_LINE_RE = re.compile(
    r"^\s*(?:另外|觀察|二次函數|若函數|當二次函數|填入圖中|判斷圖形)"
)

_JSON_EXAMPLE_METADATA_ONLY = """
{
  "chapters": [
    {
      "chapter_title": "第1章 坐標系與函數圖形",
      "sections": [
        {
          "section_title": "1-4 一元二次不等式",
          "concepts": [
            {
              "concept_name": "一元二次不等式的解法",
              "concept_en_id": "QuadraticInequalitiesSolution",
              "concept_paragraph": "",
              "examples": [
                {
                  "id": "1",
                  "title": "例題1",
                  "source_description": "例題1",
                  "problem_text": "例題1",
                  "correct_answer": "",
                  "detailed_solution": ""
                }
              ],
              "practice_questions": [
                {
                  "id": "1",
                  "title": "隨堂練習1",
                  "source_description": "隨堂練習1",
                  "problem_text": "隨堂練習1",
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
_SCAN_ZONE_HEADERS = ("基礎題", "進階題", "自我評量")
_SCAN_EXERCISE_BLOCK_HDR_RE = re.compile(r"^\s*(\d+-\d+)\s*習題\s*$")
_SCAN_ZONE_HDR_RE = re.compile(r"^\s*(基礎題|進階題|自我評量)\s*$")
_SCAN_EXAM_MARKER_RE = re.compile(
    r"[〔\[]?\s*(\d{2,3})\s*統測\s*([AB])\s*[〕\]]?",
    flags=re.IGNORECASE,
)
_SCAN_KEY_LINE_RE = re.compile(r"^\s*KEY\b", re.IGNORECASE)
_SCAN_CHAPTER_EX_NUM_RE = re.compile(r"^\s*(\d{1,2})(?:[\.、\)\t]|\s+)")
_SCAN_EXAMPLE_NUM_RE = re.compile(r"例(?:題)?\s*(\d{1,2})\b")
_EXAMPLE_BOUNDARY_CHARS = "。；;!?）)】]"
_SCAN_SUITANG_PREFIX_RE = re.compile(r"^\s*隨堂練習")
_SCAN_SUITANG_NUM_INLINE_RE = re.compile(r"隨堂練習[\s\.…·]*(\d{1,2})\b")
_SCAN_SUBSECTION_HEADING_RE = re.compile(r"^\s*\d+\s*-\s*\d+(?:\.\d+)?\s+\S")
_SCAN_MC_OPTION_RE = re.compile(r"^\s*[\(（]\s*([A-DＡ-Ｄa-dａ-ｄ])\s*[\)）]")
_SCAN_SUBPART_RE = re.compile(r"^\s*[\(（]\s*\d+\s*[\)）]")


def _log_info(msg: str) -> None:
    if has_app_context():
        current_app.logger.info(msg)


def _log_error(msg: str) -> None:
    if has_app_context():
        current_app.logger.error(msg)


def clean_problem_leading_title(text: str) -> str:
    """洗淨行首題目宣告與純數字題號；不處理子題 (1)/(2)。"""
    t = str(text or "").strip()
    if not t:
        return ""
    prev = None
    while prev != t:
        prev = t
        t = re.sub(_LEADING_TITLE_RE, "", t, count=1).strip()
    return t


def _is_example_question_key(key: str | None) -> bool:
    return str(key or "").strip().startswith("例題")


def _truncate_example_line_at_solution_start(line: str) -> tuple[str, bool]:
    """僅例題：行首命中強解答起手式時截斷並凍結（.match，禁止 .search）。"""
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
    if _SCAN_EXAM_MARKER_RE.search(s) and not re.search(r"[\(（][A-DＡ-Ｄ]", s):
        return True
    if _SCAN_SUBSECTION_HEADING_RE.match(s):
        return True
    if _SCAN_ZONE_HDR_RE.match(s):
        return True
    if _SCAN_EXERCISE_BLOCK_HDR_RE.match(s) or re.match(r"^\s*(\d+-\d+)\s*習題\s*$", s):
        return True
    ex_m = re.match(r"^\s*例(?:題)?\s*(\d{1,2})\b", s)
    if ex_m:
        return not s[ex_m.end() :].strip()
    if _SCAN_SUITANG_PREFIX_RE.match(s):
        body = _SCAN_SUITANG_PREFIX_RE.sub("", s, count=1).strip()
        body = re.sub(r"^[\s\.…·]+", "", body).strip()
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
    """同一行同時含例題與隨堂練習時，於隨堂練習標記處切為 head / tail。"""
    text = str(line or "").strip()
    if "隨堂練習" not in text:
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
        return f"隨堂練習{int(m_inline.group(1))}", first or None, False
    if pending_header and _SCAN_CHAPTER_EX_NUM_RE.match(line):
        n = int(_SCAN_CHAPTER_EX_NUM_RE.match(line).group(1))
        return f"隨堂練習{n}", line, False
    if _SCAN_SUITANG_PREFIX_RE.match(line):
        return None, None, True
    return None, None, pending_header


def _scan_line_flushes_current_block(
    line: str,
    *,
    in_chapter_exercise: bool,
    pending_suithang_header: bool = False,
) -> bool:
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
    if _SCAN_EXERCISE_BLOCK_HDR_RE.match(line) or re.match(r"^\s*(\d+-\d+)\s*習題\s*$", line):
        return True
    if re.match(r"^\s*例(?:題)?\s*(\d{1,2})\b", line):
        return True
    if _SCAN_SUITANG_NUM_INLINE_RE.search(line):
        return True
    if pending_suithang_header:
        return False
    if in_chapter_exercise and _SCAN_CHAPTER_EX_NUM_RE.match(line):
        return True
    return False


# ---------------------------------------------------------------------------
# Phase 1
# ---------------------------------------------------------------------------


def phase1_extract_docx_lines(file_path: str) -> list[str]:
    """依文件順序扁平化段落與表格儲存格文字。"""
    from docx import Document
    from docx.table import Table
    from docx.text.paragraph import Paragraph

    doc = Document(file_path)
    lines: list[str] = []
    for block in doc.element.body.iterchildren():
        if block.tag.endswith("}p"):
            text = str(Paragraph(block, doc).text or "").strip()
            if text:
                lines.append(text)
        elif block.tag.endswith("}tbl"):
            tbl = Table(block, doc)
            for row in tbl.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        text = str(para.text or "").strip()
                        if text:
                            lines.append(text)
    return lines


# ---------------------------------------------------------------------------
# Phase 2
# ---------------------------------------------------------------------------


def phase2_deterministic_block_slice(lines: list[str]) -> dict[str, str]:
    """決定性題塊切片；僅例題啟用行首詳解阻斷，其餘題型收錄至下一結構邊界。"""
    blocks: dict[str, str] = {}
    section_code: str | None = None
    current_zone = "其他"
    in_chapter_exercise = False
    current_key: str | None = None
    is_current_example = False
    buffer: list[str] = []
    stop_extend = False
    pending_lines: list[str] = []
    pending_exam_lines: list[str] = []
    awaiting_exam = False
    pending_suithang_header = False
    unassigned_buffer: list[str] = []

    work: deque[str] = deque(str(ln or "") for ln in lines)

    def clear_unassigned_buffer() -> None:
        nonlocal unassigned_buffer
        unassigned_buffer = []

    def _line_opens_new_question_block(line: str) -> bool:
        """是否為新題結構邊界（非此類則在 current_key 空窗期進 unassigned_buffer）。"""
        s = str(line or "").strip()
        if not s:
            return False
        if _SCAN_KEY_LINE_RE.match(s):
            return True
        if _SCAN_EXAM_MARKER_RE.search(s):
            return True
        if _SCAN_SUBSECTION_HEADING_RE.match(s):
            return True
        if _SCAN_EXERCISE_BLOCK_HDR_RE.match(s) or re.match(r"^\s*(\d+-\d+)\s*習題\s*$", s):
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
        return False

    def _collect_orphan_line(line_clean: str) -> None:
        if current_key is not None or awaiting_exam:
            return
        if _line_opens_new_question_block(line_clean):
            return
        unassigned_buffer.append(line_clean)

    def flush() -> None:
        nonlocal current_key, buffer, stop_extend, is_current_example
        _scan_flush_question_block(blocks, current_key, buffer)
        current_key = None
        is_current_example = False
        buffer = []
        stop_extend = False

    def clear_pending_lines() -> None:
        nonlocal pending_lines
        pending_lines = []

    def _route_practice_overflow_to_unassigned(line_clean: str) -> None:
        """非例題在課文防火牆凍結後，拒絕寫入 buffer，改溢流 unassigned。"""
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
        if _STRONG_SOL_START_RE.match(line_clean.strip()):
            head, stop = _truncate_example_line_at_solution_start(line_clean)
            if head.strip():
                buffer.append(head)
            if stop:
                stop_extend = True
            return
        if line_clean.strip() or line_clean == "":
            buffer.append(line_clean)

    def stash_frozen_line(line: str) -> bool:
        """例題詳解凍結後的跨行內容先進 pending_lines（非例題不會進入 stop_extend）。"""
        if is_current_example and current_key and stop_extend:
            pending_lines.append(line)
            return True
        return False

    def start_key(key: str, first_line: str | None = None) -> None:
        nonlocal current_key, buffer, awaiting_exam, pending_exam_lines, pending_suithang_header, stop_extend, is_current_example
        flush()
        awaiting_exam = False
        pending_exam_lines = []
        pending_suithang_header = False
        stop_extend = False
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
        line = str(raw or "").strip()

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
            if current_key:
                append_buffer_line("")
                continue
            if awaiting_exam:
                pending_exam_lines.append("")
            else:
                _collect_orphan_line("")
            continue

        if _SCAN_KEY_LINE_RE.match(line):
            flush()
            clear_pending_lines()
            pending_suithang_header = False
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
        if exam_m:
            exam_key = f"{int(exam_m.group(1))}統測{exam_m.group(2).upper()}"
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
            blk = re.match(r"^\s*(\d+-\d+)\s*習題\s*$", line)
            if blk:
                ex_hdr = blk
        if ex_hdr:
            flush()
            clear_pending_lines()
            pending_suithang_header = False
            section_code = ex_hdr.group(1)
            in_chapter_exercise = True
            current_zone = "其他"
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
            start_key(f"例題{int(ex_m.group(1))}", body or None)
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
                start_key(f"{section_code}習題 {current_zone}{n}", line)
                continue
            if current_key:
                if _SCAN_SUBPART_RE.match(line):
                    append_buffer_line(line)
                    continue
                if _SCAN_MC_OPTION_RE.match(line) or awaiting_exam:
                    begin_exam_staging(line)
                    continue
                if re.match(r"^\s*設\s", line):
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
    return blocks


# ---------------------------------------------------------------------------
# Phase 3
# ---------------------------------------------------------------------------


def _build_metadata_alignment_prompt(blocks_keys: list[str], curriculum_info: dict) -> str:
    curriculum = str(curriculum_info.get("curriculum", "") or "").strip()
    volume = str(curriculum_info.get("volume", "") or "").strip()
    subject, vol_num = parse_volume(volume)
    is_vocational_mathb = curriculum == "vocational" and subject == "B"

    base_prompt = (
        "您是一位技高數學B教材結構分析專家。本批為 converted_docx_latex 匯入："
        "題幹與 LaTeX 已由 DOCX 決定性掃描補回。您只需輸出章節結構與每題 metadata，"
        "禁止重寫完整題幹、答案或詳解。"
    )
    title_rules = (
        "【題目標題對齊規則】\n"
        "1. 每一筆 examples / practice_questions 必須同時填 title 與 source_description，且兩者完全相同。\n"
        "2. title 必須與下方清單中的 canonical_title 完全一致。\n"
        "3. problem_text 僅填與 title 相同之短字串；correct_answer、detailed_solution 填 \"\"。\n"
        "4. 禁止多行 problem_text；題幹由系統自 DOCX 補回。\n"
    )
    if is_vocational_mathb:
        title_rules += "5. 小節碼須與 section_title 一致；課文說明放 concept_paragraph，勿當成獨立題目。\n"

    parts = [
        base_prompt,
        f"【課綱】curriculum={curriculum} volume={volume}",
        CONVERTED_DOCX_LATEX_JSON_RULES,
        title_rules,
        f"【請嚴格依照以下 JSON 範例格式結構輸出】\n{_JSON_EXAMPLE_METADATA_ONLY}",
        "【題目標題清單 — 請逐題輸出對應 metadata，勿重寫題幹】",
    ]
    for key in blocks_keys:
        parts.append(f"- canonical_title={key}")
    if not blocks_keys:
        parts.append("(no titles detected — still output JSON skeleton with empty arrays)")
    return "\n".join(parts)


def phase3_ai_metadata_alignment(
    blocks_keys: list[str],
    curriculum_info: dict,
    queue,
) -> dict:
    """Gemini 僅對齊標題清單 → 章節分類樹 JSON。"""
    if queue is not None:
        queue.put("INFO: [antigravity] Phase3 Gemini metadata alignment")
    model = get_model("architect")
    prompt = _build_metadata_alignment_prompt(blocks_keys, curriculum_info)
    raw = _call_gemini_with_retry(
        model,
        prompt,
        queue=queue,
        context_message="antigravity 教材結構化對齊",
        parse_json=True,
    )
    if not raw:
        raise RuntimeError("Gemini 未回傳有效 JSON")
    parsed = safe_load_gemini_json(raw)
    if not isinstance(parsed, dict):
        raise RuntimeError("Gemini JSON 根節點必須為 object")
    return parsed


# ---------------------------------------------------------------------------
# Phase 4 helpers
# ---------------------------------------------------------------------------


def _build_source_description(
    title: str,
    source_type: str,
    *,
    linked_example_title: str | None = None,
    needs_review: bool = False,
    dedupe_hash: str = "",
    section_context: str | None = None,
) -> str:
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
    return re.sub(r"\s+", "", str(title or "").strip())


def normalize_chapter_title_for_db(chapter_title: str) -> str:
    """將 Gemini 常見的「第N章 標題」對齊為 DB 慣例「N 標題」。"""
    t = str(chapter_title or "").strip()
    if not t or not t.startswith("第") or "章" not in t:
        return t
    m = re.match(r"^第\s*(\d+)\s*章\s*(.*)$", t, flags=re.UNICODE)
    if not m:
        return t
    num = str(m.group(1)).strip()
    rest = str(m.group(2) or "").strip()
    return f"{num} {rest}".strip() if rest else num


def _extract_title_from_source_description(source_description: str) -> str:
    return str(source_description or "").split(" [", 1)[0].strip()


def _find_existing_by_structural_title(
    *,
    skill_id: str,
    curriculum_info: dict,
    chapter_title: str,
    section_title: str,
    source_type: str,
    title: str,
) -> TextbookExample | None:
    """以結構座標 + 題目標題比對既有列（dedupe_hash 不參與存在判定）。"""
    target = _compact_title_key(title)
    if not target:
        return None
    rows = TextbookExample.query.filter_by(
        skill_id=skill_id,
        source_curriculum=curriculum_info.get("curriculum"),
        source_volume=str(curriculum_info.get("volume")),
        source_chapter=chapter_title,
        source_section=section_title,
        problem_type=source_type,
    ).all()
    for row in rows:
        row_title = _extract_title_from_source_description(
            str(getattr(row, "source_description", "") or "")
        )
        if _compact_title_key(row_title) == target:
            return row
    return None


def _lookup_question_block(title: str, question_blocks: dict[str, str]) -> str:
    if not title or not question_blocks:
        return ""
    if title in question_blocks:
        return str(question_blocks[title] or "").strip()
    compact = _compact_title_key(title)
    for k, v in question_blocks.items():
        if _compact_title_key(k) == compact:
            return str(v or "").strip()
    return ""


def _ensure_skill_info(skill_id: str, concept_name: str, clean_en_id: str, section_title: str, order_index: int) -> None:
    row = SkillInfo.query.get(skill_id)
    if not row:
        db.session.add(
            SkillInfo(
                skill_id=skill_id,
                skill_en_name=clean_en_id,
                skill_ch_name=concept_name,
                category=section_title,
                description="",
                input_type="text",
                gemini_prompt=f"Generate math problems about {concept_name}.",
                is_active=True,
                order_index=order_index,
            )
        )
        return
    row.skill_en_name = clean_en_id
    row.skill_ch_name = concept_name
    row.category = section_title
    row.order_index = order_index


def _ensure_skill_curriculum(
    skill_id: str,
    curriculum_info: dict,
    chapter_title: str,
    section_title: str,
    concept_paragraph: str,
    display_order: int,
) -> bool:
    existing = SkillCurriculum.query.filter_by(
        skill_id=skill_id,
        chapter=chapter_title,
        section=section_title,
    ).first()
    if existing:
        return False
    db.session.add(
        SkillCurriculum(
            skill_id=skill_id,
            curriculum=curriculum_info.get("curriculum"),
            grade=int(curriculum_info.get("grade", 10)),
            volume=str(curriculum_info.get("volume", 1)),
            chapter=chapter_title,
            section=section_title,
            paragraph=concept_paragraph,
            display_order=display_order,
        )
    )
    return True


# ---------------------------------------------------------------------------
# Phase 4
# ---------------------------------------------------------------------------


def phase4_absolute_hydrate_and_save(
    parsed_data: dict,
    question_blocks: dict[str, str],
    curriculum_info: dict,
    queue,
) -> dict[str, int]:
    """決定性題幹回填並 Upsert 至資料庫。"""
    curriculum = str(curriculum_info.get("curriculum", "") or "").strip()
    volume = str(curriculum_info.get("volume", "") or "").strip()
    subject, vol_num = parse_volume(volume)
    is_vocational_mathb = curriculum == "vocational" and subject == "B"

    inserted = 0
    updated = 0
    hydrated = 0
    skipped = 0
    curriculums_added = 0
    skills_processed = 0
    display_base = 0

    if queue is not None:
        queue.put("INFO: [antigravity] Phase4 hydrate and DB upsert")

    for chapter_data in parsed_data.get("chapters", []) or []:
        if not isinstance(chapter_data, dict):
            continue
        raw_chapter = str(chapter_data.get("chapter_title", "未知章節") or "").strip()
        chapter_title = normalize_chapter_title_for_db(raw_chapter)
        m_ch = re.match(r"^(\d+)", chapter_title) or re.search(r"(\d+)", chapter_title)
        chapter_num = int(m_ch.group(1)) if m_ch else 999
        if chapter_title != raw_chapter:
            _log_info(f"[antigravity] chapter_title normalized: {raw_chapter!r} -> {chapter_title!r}")
        display_base = chapter_num * 10000

        for section_data in chapter_data.get("sections", []) or []:
            if not isinstance(section_data, dict):
                continue
            section_title = str(section_data.get("section_title", "") or "").strip()

            for concept_order, concept in enumerate(section_data.get("concepts", []) or [], start=1):
                if not isinstance(concept, dict):
                    continue
                concept_name = str(concept.get("concept_name", "未命名概念") or "").strip()
                concept_en_id = str(concept.get("concept_en_id", "Unknown") or "")
                concept_paragraph = str(concept.get("concept_paragraph", "") or "").strip()
                clean_en_id = re.sub(r"[^a-zA-Z0-9]", "", concept_en_id) or "Unknown"

                if is_vocational_mathb:
                    skill_id = normalize_vocational_math_skill_id(subject, vol_num, clean_en_id)
                else:
                    skill_id = f"vh_{clean_en_id}"

                if not SkillInfo.query.get(skill_id):
                    skills_processed += 1
                _ensure_skill_info(skill_id, concept_name, clean_en_id, section_title, concept_order)
                if _ensure_skill_curriculum(
                    skill_id,
                    curriculum_info,
                    chapter_title,
                    section_title,
                    concept_paragraph,
                    display_base + concept_order,
                ):
                    curriculums_added += 1

                for bucket in ("examples", "practice_questions"):
                    for item in concept.get(bucket, []) or []:
                        if not isinstance(item, dict):
                            continue
                        title = get_question_title(item) or ""
                        if not title:
                            skipped += 1
                            continue

                        source_type = normalize_source_type_by_title(item, default_source_type="textbook_example")
                        if source_type == "section_exposition":
                            skipped += 1
                            continue

                        block = _lookup_question_block(title, question_blocks)
                        if not block:
                            _log_info(f"[antigravity] missing block for title={title}")
                            if queue is not None:
                                queue.put(f"WARNING: [antigravity] 無對應題塊 title={title}")
                            skipped += 1
                            continue

                        hydrated += 1
                        db_problem_text = clean_problem_leading_title(block)
                        item["title"] = title
                        item["source_description"] = str(item.get("source_description") or title).strip()
                        item["problem_text"] = db_problem_text
                        item["correct_answer"] = ""
                        item["detailed_solution"] = ""

                        dedupe_hash = _normalize_problem_hash(
                            db_problem_text, source_type=source_type, title=title
                        )
                        source_description = _build_source_description(
                            title,
                            source_type,
                            dedupe_hash=dedupe_hash,
                        )

                        existing = _find_existing_by_structural_title(
                            skill_id=skill_id,
                            curriculum_info=curriculum_info,
                            chapter_title=chapter_title,
                            section_title=section_title,
                            source_type=source_type,
                            title=title,
                        )

                        try:
                            difficulty_level = int(item.get("difficulty_level", 1))
                        except Exception:
                            difficulty_level = 1

                        if existing:
                            existing.problem_text = db_problem_text
                            existing.correct_answer = ""
                            existing.detailed_solution = ""
                            existing.skill_id = skill_id
                            existing.source_paragraph = concept_name
                            existing.source_description = source_description
                            existing.problem_type = source_type or existing.problem_type
                            updated += 1
                        else:
                            db.session.add(
                                TextbookExample(
                                    skill_id=skill_id,
                                    source_curriculum=curriculum_info.get("curriculum"),
                                    source_volume=str(curriculum_info.get("volume")),
                                    source_chapter=chapter_title,
                                    source_section=section_title,
                                    source_paragraph=concept_name,
                                    source_description=source_description,
                                    problem_text=db_problem_text,
                                    problem_type=source_type or "calculation",
                                    correct_answer="",
                                    detailed_solution="",
                                    difficulty_level=difficulty_level,
                                )
                            )
                            inserted += 1

    db.session.commit()
    total = inserted + updated
    if queue is not None:
        queue.put(
            f"INFO: [antigravity] 匯入完成 inserted={inserted} updated={updated} "
            f"hydrated={hydrated} skipped={skipped}"
        )
    return {
        "inserted": inserted,
        "updated": updated,
        "total": total,
        "hydrated": hydrated,
        "skipped": skipped,
        "curriculums_added": curriculums_added,
        "skills_processed": skills_processed,
    }


# ---------------------------------------------------------------------------
# Main entry
# ---------------------------------------------------------------------------


def process_textbook_file_v2(file_path: str, curriculum_info: dict, queue) -> dict:
    """Antigravity 主入口：DOCX → 切片 → Gemini 對齊 → 決定性入庫。"""
    result: dict[str, Any] = {
        "success": False,
        "inserted": 0,
        "updated": 0,
        "total": 0,
        "blocks": 0,
        "error": "",
    }
    try:
        if queue is not None:
            queue.put(f"INFO: [antigravity] 開始處理 {file_path}")
        _log_info(f"[antigravity] process_textbook_file_v2 path={file_path}")

        lines = phase1_extract_docx_lines(file_path)
        if queue is not None:
            queue.put(f"INFO: [antigravity] Phase1 lines={len(lines)}")

        question_blocks = phase2_deterministic_block_slice(lines)
        result["blocks"] = len(question_blocks)
        if queue is not None:
            queue.put(f"INFO: [antigravity] Phase2 question_blocks={len(question_blocks)}")

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
            queue.put(f"ERROR: [antigravity] Gemini 配額耗盡: {exc}")
        raise
    except Exception as exc:
        db.session.rollback()
        result["error"] = str(exc)
        _log_error(f"[antigravity] failed: {exc}\n{traceback.format_exc()}")
        if queue is not None:
            queue.put(f"ERROR: [antigravity] {type(exc).__name__}: {exc}")
        raise
