# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/textbook_processor.py
功能說明 (Description): 課本處理與 AI 分析模組，負責從 PDF 或 Word 檔案中自動提取課程結構與內容，並整合 Gemini LLM 進行智能分析與資料庫匯入。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""
課本處理與 AI 分析模組 (Textbook Processor & AI Analyzer) - Final Complete Version

本模組負責從教科書（PDF 或 Word 檔案）中自動提取課程結構、章節、小節、核心觀念，
並透過 Google Gemini LLM 進行智能分析，最終將結構化資料存入資料庫。

版本特點：
1. 完整保留原有的錯誤處理、備用解析與輔助函式 (Restore full logic)。
2. 新增針對 Word/Pandoc 的清洗邏輯 (clean_pandoc_output)。
3. 更新普高龍騰版 Prompt (扁平化結構)。
"""

import json
import re
import os
import hashlib
import zipfile
import xml.etree.ElementTree as ET
import uuid
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
from core.math_formula_normalizer import detect_suspicious_formula, normalize_math_text
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

_DOCX_IMPORT_CONTEXT: dict[str, Any] = {}

# (初始化檢查已移除)

# ==============================================================================
# [保留] 您原本的 LaTeX 通用修復函式
# ==============================================================================
def sanitize_gemini_json_text(raw: str) -> str:
    r"""
    修復 Gemini 回傳 JSON 中常見的格式問題。

    注意：
    這個函式只在 json.loads 前處理 raw text。
    它的目的只是讓 raw text 成為合法 JSON。
    json.loads 成功後，Python 字串中的 LaTeX 應該仍然是正常單反斜線，
    例如資料庫最後應該存入 \(x+1\)，而不是 \\(x+1\\)。
    """
    if raw is None:
        return raw

    text = str(raw).strip()

    # 移除 Markdown code fence
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)

    # 擷取最外層 JSON object，避免模型前後多說明文字
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    # 修復非法 JSON escape。
    # JSON 合法 escape 只有：
    # \" \\ \/ \b \f \n \r \t \uXXXX
    # 其他 LaTeX escape，例如 \( \) \[ \] \frac \binom \times \cdot
    # 都需要在 raw JSON 裡變成雙反斜線，json.loads 後才會還原成單反斜線。
    # 先處理常見 LaTeX 命令。部分命令開頭剛好是合法 JSON escape
    # (例如 \binom, \frac, \times)，直接 json.loads 會變成控制字元而破壞 MathJax。
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
    安全解析 Gemini 回傳 JSON。
    先直接 json.loads。
    若失敗，修復 LaTeX escape 後再 json.loads。
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
    修復 AI/Pandoc 轉換後常見的 LaTeX 語法錯誤與符號遺漏 (增強版)
    包含：三角函數正體化、希臘字母、集合符號、向量、下標處理。
    """
    if not text: return text
    
    # 0. 基礎清理
    text = text.replace('＝', '=').replace('－', '-').replace('，', ',')
    text = re.sub(r'(\S)\s*\$\$', r'\1', text)
    text = text.replace('*e*', 'e')
    text = re.sub(r'(?<!\\)->', r' \\to ', text)
    text = re.sub(r'(?<!\\)infty(?![a-zA-Z])', r'\\infty', text)

    # 1. 函數名稱正體化 (Trig & Log)
    funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln', 'exp']
    pattern_funcs = r'(?<!\\)\b(' + '|'.join(funcs) + r')\b'
    text = re.sub(pattern_funcs, r'\\\1', text)
    text = re.sub(r'\\(sin|cos|tan|log|ln)\(', r'\\\1 (', text) # 修復黏連

    # 2. 希臘字母獨立修復
    greeks = ['alpha', 'beta', 'gamma', 'delta', 'theta', 'lambda', 'mu', 'pi', 'sigma', 'omega', 'phi', 'rho', 'tau', 'Delta', 'Sigma']
    pattern_greeks = r'(?<!\\)\b(' + '|'.join(greeks) + r')\b(?![a-zA-Z])'
    text = re.sub(pattern_greeks, r'\\\1', text)

    # 3. 集合與邏輯
    sets = ['subset', 'subseteq', 'cup', 'cap', 'emptyset', 'forall', 'exists']
    for s in sets: text = re.sub(rf'(?<!\\)\b{s}\b', rf'\\{s}', text)
    text = re.sub(r'\s+in\s+', r' \\in ', text)

    # 4. Lim, Sqrt, Frac (標準修復)
    text = re.sub(r'lim_\{n\s*(?:\\to|->)\s*(?:\\)?infty\}', r'\\lim_{n \\to \\infty}', text)
    text = re.sub(r'(?<!\\)lim(?![a-zA-Z])', r'\\lim', text)
    text = re.sub(r'(?:\\)?sqrt\s*(\d+|[a-zA-Z])', r'\\sqrt{\1}', text)
    text = re.sub(r'(?<![a-zA-Z\\])sqrt(?![a-zA-Z0-9\{])', r'\\sqrt', text)
    text = re.sub(r'frac(\d+)(\d+)', r'\\frac{\1}{\2}', text)

    # 5. 向量 (Vectors)
    text = re.sub(r'vec([A-Z]{2})', r'\\overrightarrow{\1}', text) # vecAB -> \overrightarrow{AB}
    text = re.sub(r'vec\s*([a-z])\b', r'\\vec{\1}', text)

    # 6. 常見符號
    text = re.sub(r'(\d+)\s*circ', r'\1^{\\circ}', text)
    text = re.sub(r'angle([A-Z0-9]{2,3})', r'\\angle \1', text)
    for op in ['pm', 'times', 'div', 'approx', 'leq', 'geq', 'neq']:
        text = re.sub(rf'(?<![a-zA-Z\\]){op}(?![a-zA-Z])', rf'\\{op}', text)

    # 7. 次方與下標 (Superscript & Subscript)
    text = re.sub(r'(?<!\$)\b((\w+|\([^)]+\))\^(\{[\w-]+\}|[\w-]+))\b(?!\$)', r'$\1$', text) # x^2 -> $x^2$
    text = re.sub(r'(?<!\$)\b([a-zA-Z])_(\{[\w-]+\}|[\w]+)\b(?!\$)', r'$\1_{\2}$', text)   # a_n -> $a_{n}$
   
    # 4. 修正常見 OCR/Pandoc 錯誤
    replacements = {
            '\\[': '$$', '\\]': '$$',  # 將 \[ \] 統一轉為 $$
            '\\(': '$', '\\)': '$',    # 將 \( \) 統一轉為 $
            '＊': '*',                 # 全形轉半形
            '＋': '+',
            '－': '-',
            '＝': '=',
            '／': '/', 
            'div ': '\\div '           # 常見錯誤：div 沒加斜線
        }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# ==============================================================================
# [NEW] 專用清洗函式：只針對 Word (Pandoc) 輸出的文字做處理
# ==============================================================================
def clean_pandoc_output(text):
    """
    【龍騰版/Word專用】針對 Pandoc 轉換 Word 檔後的特殊格式進行清洗。
    此函式只會被 .docx 流程呼叫，絕對不會影響 PDF/OCR 流程。
    """
    if not text: return text

    # 1. 修復 Pandoc 產生的雙重上標度數符號 (^{\^{\circ}} -> ^{\circ})
    text = text.replace(r'^{\^{\circ}}', r'^{\circ}')
    
    # 2. 統一將 \( ... \) 轉換為 $ ... $ (MathJax 更支援)
    # 這是 Word 轉出的標準 LaTeX 行內數式格式，但在前端顯示時 $ 比較通用
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text)

    # 3. 修復 sqrt (Pandoc 有時會輸出 sqrt 2 而不是 \sqrt{2})
    # 這裡只做最保守的修復，避免誤傷文字
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
    image_blips = run_el.findall(".//{*}blip")
    if not image_blips:
        return ""
    placeholders = []
    for _ in image_blips:
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
        r"^\s*例\s*題?\s*\d+",
        r"^\s*隨堂練習\s*\d+",
        r"^\s*基礎題\s*\d+",
        r"^\s*進階題\s*\d+",
        r"^\s*(?:\d+\s*-\s*\d+\s*)?習題(?:\s*基礎題|\s*進階題)?\s*\d*",
        r"^\s*自我評量",
        r"^\s*(統測補給站|統測題|會考題|學測題|指考題|分科測驗)\s*\d*",
        r"^\s*題目\s*\d+",
    ]
    return any(re.search(p, t) for p in heading_patterns)


_STRUCTURAL_BOUNDARY_PATTERNS = [
    r"^\s*第\s*\d+\s*章",
    r"^\s*\d+\s*[^\d\s].*$",
    r"^\s*\d+\s*-\s*\d+\s+[^\s].*$",
    r"^\s*\d+\s*-\s*\d+\s*\.\s*\d+\s*[^\s].*$",
    r"^\s*例\s*題?\s*\d+",
    r"^\s*隨堂練習\s*\d+",
    r"^\s*(?:\d+\s*-\s*\d+\s*)?習題",
    r"^\s*基礎題\s*\d*",
    r"^\s*進階題\s*\d*",
    r"^\s*自我評量",
    r"^\s*(統測題|會考題|學測題|指考題|分科測驗|統測補給站)",
]


def is_structural_boundary_line(line: str) -> bool:
    t = str(line or "").strip()
    if not t:
        return False
    return any(re.search(p, t) for p in _STRUCTURAL_BOUNDARY_PATTERNS)


_NON_QUESTION_EXPLANATION_CUES = (
    "由上面的例題得知",
    "由上述例題得知",
    "我們把上述例題",
    "利用公式可得",
    "為了方便表示",
    "本節介紹",
    "接下來介紹",
    "如下圖",
    "上圖",
    "下圖",
    "▲圖",
)

_QUESTION_VERBS = (
    "試問",
    "試求",
    "求",
    "計算",
    "化簡",
    "證明",
    "判斷",
    "列出",
    "填入",
    "共有幾種",
    "有幾種",
    "問",
    "解",
)


def _is_figure_caption_line(text: str) -> bool:
    t = str(text or "").strip()
    return bool(re.search(r"^(?:▲\s*)?圖\s*\d+", t))


def classify_non_question_block(text: str) -> str | None:
    t = str(text or "").strip()
    if not t:
        return "narration"
    if t == "[BLOCK_IMAGE]" or _is_figure_caption_line(t):
        return "figure_caption"

    has_explain = any(cue in t for cue in _NON_QUESTION_EXPLANATION_CUES) or bool(re.search(r"^(即|因此)\b", t))
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
        r"(統測補給站\s*\d+)",
        r"(隨堂練習\s*\d+)",
        r"(例題\s*\d+)",
        r"(基礎題\s*\d+)",
        r"(進階題\s*\d+)",
        r"(自我評量[^\s，。]*)",
        r"((?:\d+-\d+\s*)?習題\s*\d*)",
    ]:
        m = re.search(pat, t)
        if m:
            return m.group(1).replace(" ", "")
    return (t[:20] or "未命名題目")


def _is_formula_question_text(text: str) -> bool:
    t = str(text or "")
    return any(k in t for k in ("試填入下列各式", "試求下列各式之值", "設，試求自然數 n", "公式空白"))


def _is_image_question_text(text: str) -> bool:
    t = str(text or "")
    return any(k in t for k in ("如圖", "右圖", "附圖", "棋盤式街道圖", "著色", "圖形"))


def attach_docx_media_to_question_blocks(blocks):
    question_assets: dict[str, list[dict[str, Any]]] = {}
    orphan_images: list[dict[str, Any]] = []
    image_kw = ["如圖", "右圖", "附圖", "棋盤式街道圖", "著色", "標號"]

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
            if ext in ("wmf", "emf") and q.get("has_formula_kw"):
                asset_obj["media_kind"] = "formula_asset"
                if has_app_context():
                    current_app.logger.info(
                        f"[DOCX MEDIA CLASSIFY] rid={asset_obj.get('rid')} kind=formula_asset reason=formula_question_block"
                    )
            else:
                asset_obj["media_kind"] = "image_asset"
                reason = "question_contains_附圖" if q.get("has_image_kw") else "default_image_asset"
                if has_app_context():
                    current_app.logger.info(
                        f"[DOCX MEDIA CLASSIFY] rid={asset_obj.get('rid')} kind=image_asset reason={reason}"
                    )

        # Case 1: image before first question; bind to next only when question has image keywords.
        if prev_q is None and next_q is not None:
            if next_q["has_image_kw"] or next_q["has_formula_kw"]:
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
    volume_str = str(volume_str).strip()
    if not volume_str:
        return None, None

    # 支援格式:
    # 數學B4 / 數學B第4冊 / mathB4 / B4
    match = re.search(
        r'(?:數學|math)?\s*([ABCabc])\s*(?:第\s*)?(\d)\s*(?:冊)?',
        volume_str,
        flags=re.IGNORECASE,
    )
    if not match:
        match = re.search(r'([ABCabc])\s*(\d)', volume_str, flags=re.IGNORECASE)
    if not match:
        return None, None

    subject = match.group(1).upper()
    volume_num = int(match.group(2))
    return subject, volume_num


def normalize_json_text_before_parse(text):
    """在 JSON 解析前做最小、保守的文字正規化，避免破壞結構。"""
    if not text:
        return text

    normalized = str(text)
    # 已知案例：未跳脫英文雙引號包住中文句子，改為中文引號避免破壞 JSON 字串
    normalized = normalized.replace('"不能連續兩天考同一個科目"', '「不能連續兩天考同一個科目」')
    return normalized


def sanitize_detailed_solution_text(text, max_chars=500):
    """保守清理 detailed_solution：去除常見推理語句並限制長度。"""
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
        "嘗試錯誤過程",
        "多次反覆推導",
    ]
    for phrase in banned_phrases:
        cleaned = cleaned.replace(phrase, "")

    # 只保留最後結論段，避免保留過多中間推理段落
    paragraph_parts = [p.strip() for p in re.split(r"\n{2,}", cleaned) if p.strip()]
    if paragraph_parts:
        cleaned = paragraph_parts[-1]

    if len(cleaned) > max_chars:
        cleaned = cleaned[-max_chars:]

    return cleaned.strip()


def process_textbook_file(file_path, curriculum_info, queue, skip_code_gen=False):
    """
    主流程函式，包含完整的 try...except 錯誤處理。
    
    Args:
        file_path: 課本檔案路徑
        curriculum_info: 課綱資訊字典
        queue: 訊息佇列
        skip_code_gen: 若為 True，則跳過自動生成 Python 出題程式碼（預設 False）
    """

    try:
        # ======================================================
        # [NEW] 防呆：檢查是否為 Word 暫存鎖定檔 (以 ~$ 開頭)
        # ======================================================
        filename = os.path.basename(file_path)
        if filename.startswith("~$"):
            message = f"偵測到 Word 暫存鎖定檔 ({filename})，自動跳過不處理。"
            current_app.logger.warning(message)
            if queue:
                queue.put(f"WARN: {message}")
            return {"status": "skipped", "message": message}
        # ======================================================

        # 步驟 1: 從 PDF/Word 提取內容
        content_by_page = extract_content_from_file(file_path, queue)

        if not content_by_page:
            message = "檔案內容為空或提取失敗，終止處理。"
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {"status": "error", "message": "無法從檔案中提取任何內容。"}

        raw_content_by_page = dict(content_by_page)
        content_by_page = _normalize_extracted_content_math(content_by_page, queue)
        page_analysis_payload = _build_page_analysis_payload(
            raw_content_by_page,
            content_by_page,
            file_path=file_path,
            queue=queue,
        )

        # 步驟 2: 呼叫 AI 進行分析
        ai_json_result_string = call_gemini_for_analysis(
            content_by_page, curriculum_info, queue, page_analysis_payload=page_analysis_payload
        )
        # 步驟 3: 解析 AI 回傳的 JSON 字串
        if ai_json_result_string is None:
            return {"status": "error", "message": "AI 分析失敗，已中止匯入。"}
        if not ai_json_result_string:
            return {"status": "error", "message": "AI 回傳空內容，已中止匯入。"}

        ai_json_result_string = normalize_json_text_before_parse(ai_json_result_string)
        parsed_data = parse_ai_response(ai_json_result_string, queue)
        if not parsed_data:
            return {"status": "error", "message": "AI 回傳的資料格式有誤或為空，無法解析。"}

        parsed_data = _mark_needs_review_for_low_quality_pages(parsed_data, page_analysis_payload)
        parsed_data = _normalize_parsed_textbook_math(parsed_data, queue)

        # 步驟 4: 將解析後的資料存入資料庫
        result = save_to_database(
            parsed_data,
            curriculum_info,
            queue,
            source_file_path=file_path,
            content_by_page=content_by_page,
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
            f"課本處理完成。新增/更新 {skills_count} 個技能，建立 {curriculums_count} 筆課程綱要，"
            f"匯入例題 {examples_count} 筆、練習題 {practice_count} 筆（隨堂練習 {in_class_practice_count} 筆，"
            f"章節習題 {chapter_exercises_count} 筆，自我評量 {self_assessments_count} 筆，統測題 {exam_practices_count} 筆，"
            f"其他練習 {other_practices_count} 筆，需複核 {practice_needs_review_count} 筆，重複略過 {practice_skipped_count} 筆）。"
        )
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")

        # 步驟 5: 自動生成出題程式碼 (可選)
        code_gen_status = "已跳過"
        if skip_code_gen:
            message = "使用者選擇跳過程式碼生成，稍後可透過後台腳本批次生成。"
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")
        elif processed_skill_ids:
            queue.put(f"INFO: 開始自動生成 {len(processed_skill_ids)} 個技能的出題程式...")
            for idx, skill_id in enumerate(processed_skill_ids):
                queue.put(f"INFO: [{idx+1}/{len(processed_skill_ids)}] 正在生成 {skill_id}.py ...")
                try:
                    # [修正] 針對新匯入的技能，強制執行 Architect 生成最新的 Prompt
                    success, msg = auto_generate_skill_code(skill_id, queue, force_architect_refresh=True)
                    if success:
                        queue.put(f"INFO: {skill_id} 生成成功！")
                    else:
                        queue.put(f"WARN: {skill_id} 生成失敗，跳過。")
                except Exception as e:
                    queue.put(f"ERROR: 生成 {skill_id} 時發生未預期錯誤: {e}")
                    current_app.logger.error(f"Generate Error {skill_id}: {e}")
                
                time.sleep(2) # Rate Limit
            code_gen_status = f"{len(processed_skill_ids)} 個"

        return {
            "status": "success", 
            "message": (f"課本分析與匯入成功！\n"
                        f"新增/更新技能: {skills_count} 個\n"
                        f"新增課程綱要: {curriculums_count} 筆\n"
                        f"新增課本例題: {examples_count} 筆\n"
                        f"新增練習題: {practice_count} 筆\n"
                        f"隨堂練習: {in_class_practice_count} 筆\n"
                        f"練習題需複核: {practice_needs_review_count} 筆\n"
                        f"練習題略過: {practice_skipped_count} 筆\n"
                        f"自動生成程式碼: {code_gen_status}")
        }

    except Exception as e:
        current_app.logger.error(f"處理課本時發生未預期的錯誤: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": f"處理失敗: {str(e)}"}

# --- 向下相容的別名 ---
process_textbook_pdf = process_textbook_file

def extract_content_from_file(file_path, queue):
    """
    從檔案中提取內容，支援 PDF (OCR) 和 Word (Pandoc) 格式。
    (包含防崩潰處理：將所有 Import 與邏輯包覆在 try-except 中)
    """
    message = f"正在從 {file_path} 提取內容..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    global _DOCX_IMPORT_CONTEXT
    _DOCX_IMPORT_CONTEXT = {}
    content_by_page = {}
    
    try:
        # 將可能的危險 Import 移至函式內部，避免 Module Level 崩潰
        import fitz  # PyMuPDF
        import pypandoc
        from PIL import Image
        import pytesseract
        
        # Wand 是一個常見的缺失套件，特別處理
        try:
            from wand.image import Image as WandImage
        except ImportError:
            WandImage = None

        file_extension = os.path.splitext(file_path)[1].lower()

        if file_extension == '.pdf':
            # --- PDF 處理邏輯 (維持原樣) ---
            ocr_import_error_logged = False
            tesseract_not_found_error_logged = False
            doc = fitz.open(file_path)
            for i, page in enumerate(doc.pages()):
                page_text = page.get_text("text")

                # 偵測大字體標題
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

                # OCR 處理
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
                        message = "無法執行 OCR，缺少 'pytesseract' 或 'Pillow' 套件。"
                        current_app.logger.warning(message)
                        queue.put(f"WARN: {message}")
                        ocr_import_error_logged = True
                except TesseractNotFoundError:
                    if not tesseract_not_found_error_logged:
                        message = "無法找到 Tesseract-OCR 引擎，請確保已正確安裝。"
                        current_app.logger.error(message)
                        queue.put(f"ERROR: {message}")
                        tesseract_not_found_error_logged = True
                except Exception as ocr_e:
                    current_app.logger.warning(f"頁 {i+1} OCR 處理時發生錯誤: {ocr_e}")

                content_by_page[i + 1] = page_text
            doc.close()

        elif file_extension in ['.docx', '.doc']:
            # --- Word (.docx) 處理邏輯 ---
            message = "偵測到 Word (.docx) 檔案，啟用段落/公式物件抽取並保留 LaTeX。"
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")

            try:
                from docx import Document
                from docx.table import Table
                from docx.text.paragraph import Paragraph

                doc = Document(file_path)
                job_id = uuid.uuid4().hex[:12]
                media_rel_root = os.path.join("uploads", "tmp_docx_media", job_id)
                media_abs_root = os.path.join(current_app.root_path, media_rel_root)
                media_leaf_rel = os.path.join(media_rel_root, "media")
                media_leaf_abs = os.path.join(current_app.root_path, media_leaf_rel)
                os.makedirs(media_leaf_abs, exist_ok=True)
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
                }

                if formula_image_count > 0:
                    current_app.logger.info(f"[DOCX EQUATION IMAGE] saved path=[FORMULA_IMAGE_*] count={formula_image_count}")
                current_app.logger.info(
                    f"[DOCX IMPORT] paragraphs={paragraphs_count} equations={equations_count} equation_failures={equation_failures}"
                )
                content_by_page[1] = extracted_text


            except (OSError, RuntimeError) as e:
                error_str = str(e)
                # 針對損壞檔案或鎖定暫存檔的特定錯誤處理 (Exit Code 63)
                if 'exitcode "63"' in error_str or 'Did not find end of central directory' in error_str:
                    warn_msg = f"WARN: 檔案似乎已損壞或非有效的 Word 檔 (Pandoc Exit 63)，已略過處理。"
                    current_app.logger.warning(warn_msg)
                    queue.put(warn_msg)
                    return {}
                
                error_msg = f"錯誤：Pandoc 執行失敗 ({e})。請確認 Pandoc 已安裝，且若需轉換圖片格式，可能需要安裝 ImageMagick。"
                current_app.logger.error(error_msg)
                queue.put(f"ERROR: {error_msg}")

        else:
            message = f"不支援的檔案類型: {file_extension}。目前僅支援 .pdf 和 .docx。"
            current_app.logger.error(message)
            queue.put(f"ERROR: {message}")
            return {}

        message = f"成功從 {file_extension} 檔案中提取了 {len(content_by_page)} 頁/區塊內容。"
        current_app.logger.info(message)
        queue.put(f"INFO: {message}")
        return content_by_page

    except Exception as e:
        message = f"提取檔案內容時發生嚴重錯誤 (Exception): {e}"
        current_app.logger.error(message)
        import traceback
        traceback.print_exc()
        queue.put(f"ERROR: {message}")
        return {}

def _sanitize_and_parse_json(s: str, queue=None):
    """
    嘗試多種方式消毒並解析 AI 回傳的 JSON 字串。
    會回傳 (parsed_obj, used_candidate_str, original_raw_str, attempts_list)
    """
    if not s:
        return None, "", s, []

    original = s
    
    # ===== 第 0 步：先記錄原始回應的詳細資訊 =====
    current_app.logger.debug(f"[JSON_DEBUG] 原始回應長度: {len(s)} 字符")
    
    # ===== 第 1 步：移除 code fence wrapper =====
    s = re.sub(r'^```(?:json)?\s*|\s*```$', '', s, flags=re.MULTILINE).strip()
    
    # ===== 第 2 步：移除或規範化控制字元 =====
    s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', s)
    
    # ===== 第 3 步：處理可能的 BOM =====
    if s.startswith('\ufeff'): s = s[1:]
    
    # ===== 第 4 步：嘗試多種反斜線修復策略 =====
    candidates = []
    
    # 策略 0: 原始（僅移除 control chars / fences）
    candidates.append(("原始無修改", s))
    
    # 策略 1: 保守性 escape - 只將後面不是合法 JSON escape 的反斜線 escape
    escaped_conservative = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', s)
    candidates.append(("保守 escape", escaped_conservative))
    
    # 策略 2: 激進 escape - 所有孤立反斜線都雙倍
    escaped_aggressive = re.sub(r'(?<!\\)\\(?!\\)', r'\\\\', s)
    candidates.append(("激進 escape", escaped_aggressive))
    
    # 策略 3: 最後保底 - 所有反斜線都雙倍
    escaped_brutal = s.replace('\\', '\\\\')
    candidates.append(("暴力 escape", escaped_brutal))
    
    # 策略 4: 嘗試找到第一個 { 和最後一個 } 的子串
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace >= 0 and last_brace > first_brace:
        substr = s[first_brace:last_brace + 1]
        candidates.append(("提取 {} 子串", substr))
        candidates.append(("提取 {} 子串 + 保守 escape", re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', substr)))

    attempts = []
    for strategy_name, cand in candidates:
        try:
            obj = json.loads(cand)
            current_app.logger.info(f"[JSON_SUCCESS] 使用策略 '{strategy_name}' 成功解析 JSON")
            return obj, cand, original, attempts
        except json.JSONDecodeError as e:
            snippet = (cand[:200] + '...') if len(cand) > 200 else cand
            error_detail = f"{e.msg} at line {e.lineno}, col {e.colno}"
            attempts.append((strategy_name, snippet, error_detail))
            current_app.logger.debug(f"[JSON_FAIL] 策略 '{strategy_name}' 失敗: {error_detail}")

    if queue is not None:
        queue.put(f"ERROR: JSON 解析失敗（嘗試 {len(attempts)} 種策略），詳見伺服器日誌")
    
    if candidates:
        return None, candidates[-1][1], original, [(s, e, d) for s, _, (_, _, d) in zip([c[0] for c in candidates], [], attempts)]
    else:
        return None, "", original, attempts


def _call_gemini_with_retry(model, analysis_prompt, queue=None, context_message='AI 分析', parse_json=False):
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
            if queue is not None:
                queue.put(f"INFO: {context_message}，第 {attempt}/{max_retries} 次呼叫 Gemini。")

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
                        queue.put("WARNING: Gemini 回傳疑似被截斷，將重試。")
                    if queue is not None:
                        queue.put("WARNING: Gemini 回傳 JSON 不完整或格式錯誤，準備重試")
                    if attempt >= max_retries:
                        raise RuntimeError("Gemini 回傳 JSON 不完整或格式錯誤，重試 3 次後仍失敗。")
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
                            queue.put("WARNING: Gemini 回傳疑似被截斷，將重試。")
                        if queue is not None:
                            queue.put("WARNING: Gemini 回傳 JSON 不完整或格式錯誤，準備重試")
                        if attempt >= max_retries:
                            raise RuntimeError("Gemini 回傳 JSON 不完整或格式錯誤，重試 3 次後仍失敗。")
                        time.sleep(retry_delay * attempt)
                        continue
                    return merged

            raise RuntimeError("Gemini 回傳內容為空。")

        except ResourceExhausted as e:
            if attempt >= max_retries:
                err_type = type(e).__name__
                err_msg = str(e) or repr(e)
                tb = traceback.format_exc()
                current_app.logger.error(f"_call_gemini_with_retry 發生錯誤: [{err_type}] {err_msg}\n{tb}")
                if queue is not None:
                    queue.put(f"ERROR: Gemini 呼叫失敗: [{err_type}] {err_msg}")
                raise
            time.sleep(retry_delay * attempt)

        except Exception as e:
            err_type = type(e).__name__
            err_msg = str(e) or repr(e)
            tb = traceback.format_exc()

            current_app.logger.error(f"_call_gemini_with_retry 發生錯誤: [{err_type}] {err_msg}\n{tb}")
            if queue is not None:
                queue.put(f"ERROR: Gemini 呼叫失敗: [{err_type}] {err_msg}")

            raise

def call_gemini_for_analysis(content_by_page, curriculum_info, queue, page_analysis_payload=None):
    """
    使用 Gemini 分析提取出的文本 (支援 Markdown/LaTeX 格式的數學公式)。
    """
    message = "--- 開始 AI 分析流程 ---"
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    # ==========================
    # 1. 國中康軒版 Prompt (保留原樣)
    # ==========================
    prompt_jh_kangxuan = f"""
你是一位經驗豐富的數學教材編輯，你的任務是從以下課本內容中，提取出三層結構：**章節 (Chapter)**、**小節 (Section)** 和 **核心觀念 (Core Concepts)**。

請依照以下嚴格規則進行解析，並輸出為 JSON 格式：

### 1. 結構識別規則
- **章節 (Chapter)**：
    - **搜索策略**：章節大標題不一定在第一行。請在每個章 **前 5 頁**內容中尋找最顯眼的標題。
    - **識別特徵**：通常是 "Chapter X"、"第X章"、或是 **一個獨立的大數字 (如 '1') 後面緊接數學名詞**。
    - **跨行處理 (重要)**：若數字與標題分行（例如第一行是 "1"，第二行是 "二元一次聯立方程式"），請務必將其**合併**。
    - **格式強制統一**：輸出格式必須為 **"數字 章節名稱"** (去掉 "Chapter"、"第"、"章" 等贅字)。
    - **範例**：
        - 原文 "Chapter 1 整數運算" -> 輸出 "1 整數運算"
        - 原文 "1 (換行) 二元一次聯立方程式" -> 輸出 "1 二元一次聯立方程式"

- **小節 (Section)**：識別 "X-X" 格式的子標題，例如 "1-1 負數與數線"。
- **核心觀念 (Core Concept)**：**請執行以下嚴格的篩選邏輯**：
    1.  **只保留'主題 1' '主題 2' 等開頭的標題**
    2.  **不尋找「獨立標題」**
    3.  **排除規則**：忽略 "✓"、"✔"、"☑" 等符號開頭的標題，以及 "隨堂練習"、"做做看" 等。

### 2. 資料提取與格式 (JSON Key 需精準)
對於每個識別出的「核心觀念」，請生成以下欄位：
- `concept_name`: 觀念的中文標題。
- `concept_en_id`: 英文 ID，使用 **PascalCase**。
- `concept_description`: 基於內容的簡短描述(150字內)。
- `concept_paragraph`: **觀念的中文標題**
      - 絕對不允許換行
      - 絕對不允許加說明文字
      - 絕對不允許超過15個中文字
      - 如果找不到 → 填「未分類」
- **EXAMPLES (例題提取)**：
    - 務必提取「例題 X」、「隨堂練習」。
    - 每個例題包含：`source_description`, `problem_text`, `detailed_solution`, `problem_type`。

### 3. 數學與文字格式清洗
- **修復 Pandoc 上標**：`10^6^` -> `$10^{6}$`。
- **去除變數斜體**：`*c*` -> `c`。
- **保留標準公式**：保留 `$x^2$`。

輸出嚴格為 JSON 格式。
"""

    # ==========================
    # 2. 普高龍騰版 Prompt (修正版：擴大題目抓取範圍)
    # ==========================
    prompt_sh_longteng = f"""
你是一位台灣龍騰版普通高中數學教材專家，任務是從課本內容中提取資料並轉換為 JSON。

### 1. 結構識別規則 (Flatten Structure)
此版本課本結構特殊，請採用「單元 -> 觀念」的兩層式結構：

- **章節 (Chapter)**：
    - 識別標題如 "1 實數"。
    - 輸出時請標準化為 **"單元1 實數"** 。
    
- **小節 (Section) - 重要修正**：
    - **請勿輸出空字串**。
    - 請將章節名稱中的主題部分提取出來作為小節名稱。
    - 例如：若章節為 "單元1 實數"，小節名稱請設為 **"1.實數"**。

- **核心觀念 (Core Concept)**：
    - 只捕捉 **"甲"、"乙"、"丙"、"丁"**  作為觀念。
    - **排除規則**：請勿將 "綜合習題" "(一)"、"(二)" "粗體定義" "隨堂練習"、"例題"、"習題" 誤判為「觀念名稱」，但**必須提取它們的內容**放入 Examples。

### 2. 資料提取與格式
- `concept_name`: 例如 "有理數"。
- `concept_en_id`: **PascalCase** 格式 (例如 `RationalNumbers`)。
- `concept_description`: 基於內容的簡短描述(150字內)。
- `concept_paragraph`: **只能是「甲.數列」這種短標題**
      - 允許格式：甲. / 乙. / 丙.
      - 絕對不允許換行
      - 絕對不允許加說明文字
      - 絕對不允許超過15個中文字
      - 如果找不到 → 填「未分類」
### 絕對禁止事項（違反就失敗！）
- `concept_paragraph` 裡面**絕對不可以出現 $、公式、換行、完整段落說明**
- 違規範例（禁止）：
  ```json
  "concept_paragraph": "甲 數列\\n\\n一般而言，數列可以用符號..."
- **EXAMPLES (題目提取 - 關鍵修正)**：
    - **請盡可能提取所有題目**，不只是 "例題"。
    - **目標對象**：
        1. **例題** (Example): 通常有詳細解析。
        2. **隨堂練習** (Practice): 通常緊跟在例題後面。
        3. **習題** (Exercises): 位於章節末尾。
    - `source_description`: 請清楚標示來源，例如 "例題1"、"隨堂練習"、"習題 3"。
    - `problem_text`: 題目內容 (務必保留 LaTeX 格式，例如 $x^2$)。若公式遺失，標記 `[公式遺失]`。
    - `detailed_solution`: 若原文有解析則提取，若無則填 "略"。

輸出嚴格為 JSON 格式。
"""

    # ==========================
    # 3. 通用版 Prompt
    # ==========================

    prompt_generic = f"""
你是一位數學教材編輯，請從以下內容中提取：章節 (Chapter)、小節 (Section) 和核心觀念 (Concept)。
- 結構：章節 -> 小節 -> 核心觀念。
- 提取 'examples'，並保留 LaTeX 數學符號。
輸出嚴格為 JSON 格式。
"""


    prompt_vh_mathB4 = f"""
你是一位台灣技術型高中數學B教材分析專家。
你的任務是將高職數學B課本內容解析成本系統可匯入資料庫的 JSON。

請嚴格依照本系統既有三層結構輸出：

Chapter 章
→ Section 小節
→ Concept / Skill 核心技能
→ Examples 例題、隨堂練習、習題

本次教材屬性：
- curriculum: vocational
- subject: 數學B
- volume: 第四冊
- chapter 可能包含：排列組合、機率
- section 可能包含：1-1 加法原理與乘法原理、後續排列、組合、機率相關小節

【一、結構辨識規則】

1. chapter_title
請保留課本章節名稱，例如：
"1 排列組合"

2. section_title
請保留課本小節名稱，例如：
"1-1 加法原理與乘法原理"

3. concepts
請依照課本中的真正教學概念拆分，不要只用頁面標題。
以 1-1 加法原理與乘法原理為例，至少應能拆出：

- 樹狀圖
- 加法原理
- 乘法原理
- 正因數個數
- 階乘記法

後續章節請依課本內容拆成可教、可測、可補救的核心技能。

【Skill 切分核心原則】

Skill = 課本正式小節標號 x-y.z 的標題。
Subskill = 例題題型 / 解題策略 / 應用變化。
不得把例題主題升格成 Skill。

例如：
1-2.1 相異物的排列
1-2.2 不盡相異物的排列
以上兩個才是 skill。

下列僅可作為 subskill_tag 或 problem_type，不可建立成 skill：
全取排列、部分排列、相鄰排列、不相鄰排列、插空法、棋盤格路徑、數字限制、統測題、綜合題、應用題型。

【正式小節優先規則】

1. 解析教材時，必須先掃描是否存在正式小節標號，格式為：數字-數字.數字。
例如：1-1.1、1-1.2、1-2.1、1-2.2、1-3.1、1-3.2。

2. 若存在正式小節標號，concepts 只能依照這些正式小節建立。
3. 每一個 concept 對應一個正式小節。
4. concept_name 必須等於該正式小節標題，不可使用例題題型名稱。
5. concept_paragraph 必須等於該正式小節標題。
6. concept_en_id 必須依正式小節標題翻譯成 PascalCase 英文 ID。
7. 例題、隨堂練習、統測題、補充題型、習題中的題型名稱，不可升格為 concept。
8. 若某題屬於正式小節下的應用題型，放入該 concept 的 examples，並以 subskill_tag 標記題型。

【沒有正式小節時的 fallback】

若教材文字中沒有偵測到 x-y.z 正式小節標號，才允許依照課文大標題建立 concept。
但仍須遵守：
- 不得把單一例題主題升格為 skill
- 不得把統測題、補充題型、習題題型升格為 skill
- 概念數量應少而精
- 同一小節通常 2～5 個 concept，不應超過 6 個

【1-1 專用補充】

當 section_title 包含「1-1」或「加法原理與乘法原理」時，若教材出現正式小節：
1-1.1 樹狀圖
1-1.2 加法原理
1-1.3 乘法原理
1-1.4 階乘記法
則 concepts 只能輸出：
TreeDiagramCounting、AdditionPrinciple、MultiplicationPrinciple、FactorialNotation。

注意：正因數個數不是正式小節，只能歸入 MultiplicationPrinciple 的 examples，subskill_tag 可用 divisor_counting 或 mixed_application。

【1-2 專用補充】

當 section_title 包含「1-2」或「直線排列」時，若教材中出現正式小節：
1-2.1 相異物的排列
1-2.2 不盡相異物的排列
則 concepts 只能輸出兩個：
1.
concept_name: 相異物的排列
concept_en_id: PermutationOfDistinctObjects
concept_paragraph: 相異物的排列
2.
concept_name: 不盡相異物的排列
concept_en_id: PermutationOfNonDistinctObjects
concept_paragraph: 不盡相異物的排列

嚴禁把以下題型建立為 concept：
全取排列、部分排列、0!、數字排列限制、相鄰排列、不相鄰排列、插空法、棋盤格路徑、捷徑問題、統測題、綜合排列題。
以上題型應歸入 subskill_tag。

【1-3 與後續小節通用規則】

1-3、1-4、2-1、2-2 等後續內容，必須使用同一規則：
1. 先找正式小節標號 x-y.z
2. 用正式小節標題建立 concept
3. 題型變化放入 subskill_tag
4. 不自行把例題主題升格為 skill

【二、concept 欄位規則】

每個 concept 必須包含：

- concept_name：中文名稱，例如「加法原理」
- concept_en_id：PascalCase 英文 ID，例如 AdditionPrinciple
- concept_description：150 字內說明此技能在學習上的用途
- concept_paragraph：短標題，不可超過 15 個中文字

1-1 建議 concept_en_id 對照：
樹狀圖 → TreeDiagramCounting
加法原理 → AdditionPrinciple
乘法原理 → MultiplicationPrinciple
正因數個數 → NumberOfPositiveDivisors
階乘記法 → FactorialNotation

【三、題目提取規則】

請提取以下類型內容：

1. 例題
例如：[例題 1]、[例題 2]、[例題 3]、[例題 4]

2. 隨堂練習
例如：標示為「隨堂練習」後的題目

3. Touch 統測題
若題目完整，請提取為 examples

4. 習題
基礎題與進階題都可以提取，但 source_description 要標示清楚，例如：
"1-1習題 基礎題1"
"1-1習題 進階題9"

5. 每個 concept 最多輸出 20 個 examples。

6. 若題目太多，優先保留：
- 例題
- 隨堂練習
- 基礎題
- 統測題代表題

7. 不需要逐題完整收錄所有重複型題目。
8. 若原文有很多統測補給站題目，只選代表性題目，不要全部塞入同一個 JSON。

【隨堂練習匯入規則】
1. 「隨堂練習」必須視為獨立題目。
2. 「隨堂練習」請放入 practice_questions 陣列。
3. 不要把隨堂練習只附在 example.followup_practices 裡。
4. 如果為了表示版面關係，可以填 linked_example_title。
5. 隨堂練習 N 通常 linked_example_title = "例題N"。
6. 隨堂練習通常繼承對應例題的 skill_id。
7. 隨堂練習不是新的 concept。
8. 隨堂練習不是新的 skill。
9. 隨堂練習要保留題幹、答案、解法。
10. 隨堂練習的 source_type 必須是 "in_class_practice"。
11. 例題的 source_type 必須是 "textbook_example"。
12. 如果無法判斷 linked example，linked_example_title = null，needs_review = true。
13. 如果無法判斷 skill_id，使用同 concept 下最接近的 skill_id；仍無法判斷才使用 section_general 並 needs_review=true。

【四、題目欄位規則】

每個 examples 物件必須包含：

- source_description
- problem_text
- correct_answer
- detailed_solution
- problem_type
- subskill_tag
- difficulty_level

detailed_solution 必須是精簡繁體中文解析。
禁止輸出：
- Let's trace
- Let's re-do
- This is not
- English chain-of-thought
- 嘗試錯誤過程
- 多次反覆推導

problem_text 保持完整，但不要抄整頁背景文字。

subskill_tag 可用值：
- general
- all_objects_permutation
- partial_permutation
- factorial_zero
- divisor_counting
- role_assignment
- number_restriction
- odd_even_number
- adjacent_grouping
- non_adjacent_gap
- complementary_counting
- grid_path
- repeated_objects
- repeated_digits
- repeated_words
- combination_basic
- combination_application
- probability_basic
- mixed_application

如果無法判斷，填 general。

problem_type 僅能使用下列值之一：
- tree_diagram
- addition_principle
- multiplication_principle
- divisor_counting
- factorial
- permutation
- combination
- probability
- mixed_counting

difficulty_level：
1 = 基礎
2 = 中等
3 = 進階或統測題

【五、解答與詳解規則】

1. 若原文有答案，請放入 correct_answer。
2. 若原文有解析，請放入 detailed_solution。
3. 若只有答案沒有解析，detailed_solution 填 "略"。
4. 選擇題 correct_answer 請同時保留選項與數值，例如：
"B，80"
5. 不可自行亂補答案；若原文無法判斷，填空字串 ""。
6. detailed_solution 不要輸出英文推理過程，只保留精簡繁體中文最終解法。
7. detailed_solution 最多 200 字；若內容過長，僅保留最後正確解法，不保留試算錯誤過程。
8. 不要輸出：
- Let's trace
- Let's re-do
- This is not
- English chain-of-thought
- 反覆試算失敗過程

【六、清理規則】

請移除以下內容，不要當成 concept 或 example：

- What's up!
- 雲端教室
- 檔案位置
- 熟習度自評表
- Awesome / Excellent / Good / Average / Poor
- 配合 Super 講義
- 頁碼
- 圖號本身，例如「圖1」「圖2」
- 教師用書重複頁面
- QR code、圖片說明、裝飾性文字

【七、數學格式規則】

請盡量修正常見 OCR 錯誤：

- # 表示乘法時，轉為 \\times
- 600 2 3 5 3 1 2 = # # 應整理成 600 = 2^3 \\times 3^1 \\times 5^2
- 5 ! 應整理為 5!
- 階乘分式請整理成 LaTeX，例如 \\frac{{8!}}{{6!}}

若無法可靠修復，保留原文，不要亂猜。

【八、輸出格式】

只輸出 JSON，不要 markdown，不要說明文字，不要 code fence。
JSON 字串內禁止使用英文半形雙引號 "；若需要引號，請改用中文全形引號「」。

JSON 格式如下：

{{
  "chapters": [
    {{
      "chapter_title": "1 排列組合",
      "sections": [
        {{
          "section_title": "1-2 直線排列",
          "concepts": [
            {{
              "concept_name": "相異物的排列",
              "concept_en_id": "PermutationOfDistinctObjects",
              "concept_description": "處理不同物件依序排列的方法數，包含全取、選取、限制條件與應用排列問題。",
              "concept_paragraph": "相異物的排列",
              "examples": [
                {{
                  "source_description": "問題1",
                  "problem_text": "將甲、乙、丙三位同學排成一列，有多少種排法？",
                  "correct_answer": "6 種",
                  "detailed_solution": "三人全取排成一列，方法數為 3! = 6。",
                  "problem_type": "permutation",
                  "subskill_tag": "all_objects_permutation",
                  "difficulty_level": 1
                }},
                {{
                  "source_description": "例題5",
                  "problem_text": "男生3人，女生2人排成一列拍照，女生二人必須相鄰的排法有幾種？",
                  "correct_answer": "48 種",
                  "detailed_solution": "將兩位女生視為一組，與3位男生共4個單位排列，再乘上女生內部排列，得 4! × 2! = 48。",
                  "problem_type": "permutation",
                  "subskill_tag": "adjacent_grouping",
                  "difficulty_level": 2
                }},
                {{
                  "source_description": "例題7",
                  "problem_text": "棋盤格道路中，由甲到乙取捷徑的方法數。",
                  "correct_answer": "依題目數據計算",
                  "detailed_solution": "將向右與向上步數視為不盡相異物排列，例如 4 個右與 3 個上共有 7! / (4!3!) 種。",
                  "problem_type": "shortest_path",
                  "subskill_tag": "grid_path",
                  "difficulty_level": 2
                }}
              ]
            }},
            {{
              "concept_name": "不盡相異物的排列",
              "concept_en_id": "PermutationOfNonDistinctObjects",
              "concept_description": "處理含有相同物件的排列問題，需將重複排列除去。",
              "concept_paragraph": "不盡相異物的排列",
              "examples": [
                {{
                  "source_description": "例題6",
                  "problem_text": "將 google 一字中所有字母重新排列，有多少種不同排法？",
                  "correct_answer": "180 種",
                  "detailed_solution": "google 有6個字母，其中 g 有2個、o 有2個，所以排法為 6! / (2!2!) = 180。",
                  "problem_type": "permutation",
                  "subskill_tag": "repeated_words",
                  "difficulty_level": 1
                }}
              ]
            }}
          ]
        }}
      ]
    }}
  ]
}}
"""

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
        queue.put("INFO: 已選擇「國中康軒」專用分析模型。")
    elif is_vocational_mathb:
        base_prompt = prompt_vh_mathB4
        queue.put(f"INFO: 已選擇 高職數學{subject}{vol_num} 專用分析模型")
    elif curriculum == 'sh_longteng' or (curriculum == 'general' and publisher == 'longteng'):
        base_prompt = prompt_sh_longteng
        queue.put("INFO: 已選擇「普高龍騰」專用分析模型 (題目擴增版)。")
    else:
        base_prompt = prompt_generic
        queue.put("INFO: 未找到專用分析模型，使用通用模型。")

    try:
        model = get_model("architect")
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e) or repr(e)
        tb = traceback.format_exc()

        current_app.logger.error(f"AI 分析失敗: [{err_type}] {err_msg}\n{tb}")
        if "Gemini API Key" in err_msg or "API_KEY" in err_msg or "找不到" in err_msg:
            queue.put("ERROR: 找不到 Gemini API Key，請先到 AI 後台設定頁輸入並儲存。")
        else:
            queue.put(f"ERROR: AI 分析失敗: [{err_type}] {err_msg}")
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
    
    json_example = """
{
  "chapters": [
    {
      "chapter_title": "1 ???",
      "sections": [
        {
          "section_title": "1.???",
          "concepts": [
            {
              "concept_name": "?????,
              "concept_en_id": "RationalNumbers",
              "concept_description": "...",
              "concept_paragraph": "?????",
              "examples": [
                 {
                    "source_description": "???1",
                    "problem_text": "...",
                    "problem_type": "calculation"
                 },
                 {
                    "source_description": "??????",
                    "problem_text": "...",
                    "problem_type": "calculation"
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
    if is_vocational_mathb:
        json_example = """
{
  "chapters": [
    {
      "chapter_title": "1 ????",
      "sections": [
        {
          "section_title": "1-1 ?????????",
          "concepts": [
            {
              "concept_name": "????",
              "concept_en_id": "AdditionPrinciple",
              "concept_description": "??????????????????",
              "concept_paragraph": "????",
              "examples": [
                {
                  "source_description": "??2",
                  "problem_text": "?????? 3 ????????4 ???????? 5 ????????????????????????????",
                  "correct_answer": "12 ?",
                  "detailed_solution": "?????????????????????????? 3 + 4 + 5 = 12?",
                  "problem_type": "addition_principle",
                  "difficulty_level": 1
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

    analysis_prompt = f"""
{base_prompt}

圖片標記規則：
若題目包含「如圖」「下圖」「右圖」「圖」「樹狀圖」「表格」「幾何圖」「圓環圖」「路線圖」「附圖」等字樣，
請在該題 JSON 物件加上：
- "has_image": true
- "image_description": "簡短描述圖形用途，例如樹狀圖、圓環著色圖、路線圖"
- "source_page": 題目所在 PDF 頁碼（1-based，無法判定則 null）
- "page_index": 題目所在頁索引（0-based，無法判定則 null）
注意：不要輸出 base64 或虛構圖片，圖片由後端從 PDF 頁面 render 後保存。

低品質頁面輸入規則：
你可能同時收到 [RAW PDF TEXT]、[NORMALIZED TEXT]、[VISION OCR TEXT]、[FORMULA WARNINGS]。
若 VISION OCR TEXT 有內容，請優先用於題目重建；若無則用 NORMALIZED TEXT 並提高 needs_review。

重要輸出要求：
1. 只能輸出合法 JSON，不可以輸出 Markdown code block。
2. 不可以在 JSON 前後加入任何說明文字。
3. 所有 LaTeX 反斜線在 JSON 原始輸出中必須使用合法 JSON escape。
4. 錯誤："\\(x+1\\)" 若原始輸出實際只有單反斜線；正確："\\\\(x+1\\\\)"。
5. 錯誤："\\binom{{n}}{{r}}" 若原始輸出實際只有單反斜線；正確："\\\\binom{{n}}{{r}}"。
6. 錯誤："\\frac{{n!}}{{r!(n-r)!}}" 若原始輸出實際只有單反斜線；正確："\\\\frac{{n!}}{{r!(n-r)!}}"。
7. 請保留 LaTeX 語法，資料匯入資料庫後會由前端 MathJax 解析。
8. 回傳前請確認整份內容可以被 Python json.loads() 直接解析。

PDF/OCR 數學式校正要求：
1. 你會收到由 PDF 擷取而來的數學文字，其中可能包含 OCR / PDF 解析錯誤。
2. #、＃、﹟ 通常代表乘號，應轉成 \\times 或 ×。
3. 台灣高中課本中的 C_r^n 代表組合數，應理解為 C(n,r) 或 LaTeX C^n_r。
4. 台灣高中課本中的 P_r^n 代表排列數，應理解為 P(n,r) 或 LaTeX P^n_r。
5. 若看到 C_0^5 + C_1^5 + C_2^6 + C_3^7 + C_4^8 這類上下標不一致的式子，不要直接照抄，請標記 suspicious_formula 並盡可能根據上下文修正。
6. 若無法可靠修正，請保留原始文字與 normalized_formula，並設定 needs_review = true。
7. 不要把明顯錯誤的 OCR 公式直接寫成正式例題。
8. 所有 LaTeX 反斜線仍需符合合法 JSON escape。

DOCX 公式缺失安全規則（嚴格）：
1. 若題目文字包含 [FORMULA_IMAGE_x]、[WORD_EQUATION_UNPARSED]、[UNREADABLE_FORMULA]、或只有 (1)(2)(3) 但小題公式缺失，禁止自行猜測/補齊排列組合公式數字。
2. 這種情況必須保留 placeholder，並輸出 needs_review=true、needs_formula_review=true、formula_missing=true。
3. 不可把缺失公式改寫成看似完整的 P^n_r 或 C^n_r。
4. 若無法辨識公式內容，優先保留 [FORMULA_MISSING]，不要生成新公式。

隨堂練習 JSON 輸出要求：
1. examples 只放例題；practice_questions 放隨堂練習與練習題，兩者都必須是可獨立入庫的題目物件。
2. practice_questions 每題至少包含：practice_title(或 source_description)、problem、answer、solution、source_type="in_class_practice"。
3. 如果為了版面關聯需要 followup_practices，仍要同步輸出到 practice_questions，避免隨堂練習遺失。

JSON ?????? (??? section_title ?????????????
{json_example}

????????
{full_content}
"""

    try:
        ai_response = _call_gemini_with_retry(
            model, 
            analysis_prompt, 
            queue, 
            context_message="提取課本結構時，",
            parse_json=True
        )
        return ai_response
    except Exception as e:
        err_type = type(e).__name__
        err_msg = str(e) or repr(e)
        tb = traceback.format_exc()

        current_app.logger.error(f"AI 分析失敗: [{err_type}] {err_msg}\n{tb}")
        queue.put(f"ERROR: AI 分析失敗: [{err_type}] {err_msg}")
        return None

def parse_ai_response(ai_data_or_string, queue):
    """解析 AI 回傳的資料 (JSON 字串或已解析的 dict)，並進行基本驗證。"""
    message = "正在解析 AI 回傳的 JSON..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    def _save_failed_ai_response(raw_response_text, cleaned_response_text=None):
        debug_dir = os.path.join("reports", "debug_ai_response")
        os.makedirs(debug_dir, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        debug_filename = f"ai_response_failed_{timestamp}.txt"
        debug_path = os.path.join(debug_dir, debug_filename)

        raw_text = str(raw_response_text) if raw_response_text is not None else ""
        cleaned_text = str(cleaned_response_text) if cleaned_response_text is not None else ""
        payload = cleaned_text if cleaned_text else raw_text

        with open(debug_path, "w", encoding="utf-8") as f:
            f.write(payload)

        queue.put(f"ERROR: AI JSON 解析失敗，已保存原始回覆至 {debug_path}")
        current_app.logger.error(f"AI JSON 解析失敗，已保存原始回覆至 {debug_path}")
        return debug_path

    if isinstance(ai_data_or_string, dict):
        return _normalize_textbook_question_structure(ai_data_or_string, queue)

    raw_response_string = str(ai_data_or_string) if ai_data_or_string is not None else ""

    if not raw_response_string.strip():
        message = f"錯誤：無法處理的 AI 回傳類型: {type(ai_data_or_string)}"
        current_app.logger.error(message)
        queue.put(f"ERROR: {message}")
        _save_failed_ai_response(raw_response_string)
        return None

    cleaned_string = re.sub(r'^```(?:json)?\s*|\s*```$', '', raw_response_string, flags=re.MULTILINE).strip()
    try:
        parsed_obj = safe_load_gemini_json(cleaned_string)
        queue.put("INFO: AI 回應成功解析為標準 JSON。")
        return _normalize_textbook_question_structure(parsed_obj, queue)
    except ValueError as e:
        current_app.logger.warning(
            f"[TEXTBOOK IMPORTER] safe_load_gemini_json failed, fallback parser will run: {e}"
        )

    # --- 備用方案：逐章解析 (保留您原本的邏輯) ---
    queue.put("WARN: 標準 JSON 解析失敗，啟用備用方案：逐章節提取並解析。")
    current_app.logger.warning("標準 JSON 解析失敗，啟用備用方案：逐章節提取並解析。")

    chapter_chunks = re.findall(r'(\{\s*"chapter_title":.*?\}(?=\s*,\s*\{"chapter_title"|\s*\]\s*\}))', cleaned_string, re.DOTALL)

    if not chapter_chunks:
        queue.put("ERROR: 備用方案失敗：無法從文本中提取任何章節區塊。")
        _save_failed_ai_response(raw_response_string, cleaned_string)
        return None

    queue.put(f"INFO: 備用方案：偵測到 {len(chapter_chunks)} 個可能的章節區塊。")
    successful_chapters = []
    for i, chunk in enumerate(chapter_chunks):
        try:
            try:
                chapter_obj = safe_load_gemini_json(chunk)
            except ValueError:
                chapter_obj, _, _, _ = _sanitize_and_parse_json(chunk, queue=None)
            if chapter_obj:
                successful_chapters.append(chapter_obj)
            else:
                queue.put(f"WARN: 無法解析章節區塊 {i+1}，已跳過。")
        except Exception as e:
            queue.put(f"WARN: 解析章節區塊 {i+1} 時發生錯誤: {e}，已跳過。")

    if not successful_chapters:
        queue.put("ERROR: 備用方案最終失敗：沒有任何章節區塊能被成功解析。")
        _save_failed_ai_response(raw_response_string, cleaned_string)
        return None

    return _normalize_textbook_question_structure({"chapters": successful_chapters}, queue)

def to_pascal_case(snake_case_string):
    """將 snake_case 或 kebab-case 字串轉換為 PascalCase。"""
    if not snake_case_string:
        return ""
    return ''.join(word.capitalize() for word in re.split('_|-', snake_case_string))

def clean_skill_en_name(raw_en_name, queue=None):
    """
    (PascalCase 策略版) 移除多餘的結構化前綴，只保留 PascalCase 部分。
    """
    if not raw_en_name:
        return ""
    match = re.search(r'[A-Z]', raw_en_name)
    if match:
        start_index = match.start()
        return raw_en_name[start_index:]
    return raw_en_name


def _formula_context_label(path):
    return " / ".join(str(p) for p in path if p is not None and str(p).strip())


def _normalize_extracted_content_math(content_by_page, queue=None):
    """Normalize extracted page text before Gemini sees OCR/PDF math artifacts."""
    if not isinstance(content_by_page, dict):
        return content_by_page

    normalized_pages = {}
    for page_no, page_text in content_by_page.items():
        if not isinstance(page_text, str):
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
    weird = len(re.findall(r"[�□◻◼◊¤�]", text))
    symbols = len(re.findall(r"[#＃﹟]{2,}", text))
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
        prompt = (
            "請忠實讀取圖片中的數學教材文字。"
            "保留題號、例題/隨堂練習標題、多小題(1)(2)(3)、"
            "階乘、分式、乘號、上下標。"
            "不要輸出 JSON，只輸出清楚純文字。"
        )
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


def _normalize_imported_math_value(value, *, section_title="", source_description="", field_name="", queue=None):
    if value is None or not isinstance(value, str):
        return value, None

    suspicious = detect_suspicious_formula(value)
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


def _normalize_parsed_textbook_math(parsed_data, queue=None):
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
    out = re.sub(
        r"(試填入下列各式|求下列各式|填入下列各式)\s*(?:□|▢|◻|☐|（\s*　?\s*）|\(\s*　?\s*\)|＿＿|_{2,})\s*之值",
        r"\1空格之值",
        out,
    )
    if out != before:
        log["changed"] = True
        log["reasons"].append("normalized fill-blank instruction text")

    # Generic blank symbols/slots normalization.
    blank_patterns = [
        r"[□▢◻☐]",
        r"（\s*　?\s*）",
        r"\(\s*　?\s*\)",
        r"＿＿+",
        r"_{2,}",
    ]
    before = out
    for pat in blank_patterns:
        out = re.sub(pat, "[BLANK]", out)
    if out != before:
        log["changed"] = True
        log["reasons"].append("normalized fill blank symbol to [BLANK]")

    return out, log


def normalize_permutation_combination_notation(text: str) -> tuple[str, dict]:
    original = str(text or "")
    out = original
    log = {"changed": False, "reasons": []}

    # e.g., ⁷P₃ / ⁷C₃
    def _replace_pre(match):
        n = match.group(1).translate(_SUPERSCRIPT_TRANS)
        op = match.group(2)
        r = match.group(3).translate(_SUBSCRIPT_TRANS)
        return f"{op}^{{{n}}}_{{{r}}}"

    out = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)\s*([PC])\s*([₀₁₂₃₄₅₆₇₈₉₊₋]+)", _replace_pre, out)

    # e.g., P₃⁷ / C₃⁷
    def _replace_post(match):
        op = match.group(1)
        r = match.group(2).translate(_SUBSCRIPT_TRANS)
        n = match.group(3).translate(_SUPERSCRIPT_TRANS)
        return f"{op}^{{{n}}}_{{{r}}}"

    out = re.sub(r"([PC])\s*([₀₁₂₃₄₅₆₇₈₉₊₋]+)\s*([⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻]+)", _replace_post, out)

    # e.g., P^7_3 / C^7_3
    out = re.sub(r"\b([PC])\s*\^\s*\{?\s*([0-9]+)\s*\}?\s*_\s*\{?\s*([0-9]+)\s*\}?", r"\1^{\2}_{\3}", out)

    if out != original:
        log["changed"] = True
        log["reasons"].append("normalized permutation notation to P^{n}_{r}/C^{n}_{r}")
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
    if re.search(r"設\s*為", text):
        missing_slots.append("subject")
    if re.search(r"之\s*值", text):
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
        fixed = re.sub(r"設\s*為", f"設 {sym} 為", fixed, count=1)
    if "value" in missing_slots:
        fixed = re.sub(r"之\s*值", f"之 {sym} 值", fixed, count=1)

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

    explanation_cues = _NON_QUESTION_EXPLANATION_CUES + ("上述",)
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


def normalize_source_type_by_title(item: dict, default_source_type: str = "textbook_example") -> str:
    title = get_question_title(item)
    raw_source_type = str(item.get("source_type", "") or "").strip().lower() if isinstance(item, dict) else ""
    reason = ""

    if "隨堂練習" in title:
        normalized = "in_class_practice"
        reason = "title_contains_隨堂練習"
    elif "自我評量" in title:
        normalized = "self_assessment"
        reason = "title_contains_自我評量"
    elif any(k in title for k in ("統測補給站", "統測題", "統測")):
        normalized = "exam_practice"
        reason = "title_contains_統測"
    elif "基礎題" in title:
        normalized = "basic_exercise"
        reason = "title_contains_基礎題"
    elif "進階題" in title:
        normalized = "advanced_exercise"
        reason = "title_contains_進階題"
    elif "習題" in title:
        normalized = "chapter_exercise"
        reason = "title_contains_習題"
    elif re.search(r"^\s*例\s*題?\s*\d+", title):
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


def _normalize_sub_questions(raw_sub_questions):
    normalized = []
    if not isinstance(raw_sub_questions, list):
        return normalized
    for idx, item in enumerate(raw_sub_questions, start=1):
        if not isinstance(item, dict):
            continue
        sq_problem_raw = _first_non_empty_str(item, ("problem_text", "problem", "question"))
        sq_problem, _ = standardize_problem_latex(sq_problem_raw)
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
    return "；".join(parts) if parts else (answer_text or "").strip()


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
                    ex_normalized["source_description"] = example_title or ex_normalized.get("source_description", "例題")
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
                        practice_item["source_description"] = p_title or "隨堂練習"
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
                    normalized_practice["source_description"] = p_title or normalized_practice.get("source_description", "隨堂練習")
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
                if isinstance(concept.get("exercises"), list):
                    normalized_exercises = []
                    for q in concept.get("exercises", []) or []:
                        if not isinstance(q, dict):
                            continue
                        qn = dict(q)
                        qn["source_type"] = normalize_source_type_by_title(qn, default_source_type="chapter_exercise")
                        normalized_exercises.append(qn)
                    concept["exercises"] = normalized_exercises

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
    """判斷該 concept 是否屬於不可建立 skill 的桶位。"""
    name = (concept_name or "").strip()
    en_id = (clean_en_id or "").strip().lower()
    non_skill_names = {
        "習題",
        "章節介紹",
        "排列組合概論",
    }
    non_skill_en_ids = {
        "chapterintroduction",
        "exercises",
        "practice",
        "review",
    }
    return name in non_skill_names or en_id in non_skill_en_ids


def remap_mathb_non_skill_examples(section_title, concept_name, clean_en_id, example):
    """
    高職數學B4 1-1 專用：將非正式 skill bucket 例題重導到正式 skill。
    回傳 clean_en_id（TreeDiagramCounting / AdditionPrinciple / MultiplicationPrinciple / FactorialNotation）。
    """
    section = (section_title or "").strip()
    if "1-1" not in section and "加法原理與乘法原理" not in section:
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
        or "列舉" in zh_hints
    ):
        return "TreeDiagramCounting"

    if (
        "addition_principle" in signal
        or "分類討論" in zh_hints
        or "加法原理" in zh_hints
    ):
        return "AdditionPrinciple"

    if (
        "factorial" in signal
        or "階乘" in zh_hints
        or "n!" in signal
        or "n!" in zh_hints.lower()
    ):
        return "FactorialNotation"

    if (
        "multiplication_principle" in signal
        or "divisor_counting" in signal
        or "mixed_counting" in signal
        or "正因數個數" in zh_hints
        or "步驟計數" in zh_hints
        or "乘法原理" in zh_hints
    ):
        return "MultiplicationPrinciple"

    # 無法判斷時預設歸入乘法原理
    return "MultiplicationPrinciple"

def save_to_database(parsed_data, curriculum_info, queue, source_file_path=None, content_by_page=None):
    """
    將 AI 分析完的目錄資料寫入資料庫。
    """
    message = "正在將目錄結構寫入資料庫..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")
    skills_processed = 0
    curriculums_added = 0
    examples_added = 0
    practice_questions_imported = 0
    in_class_practices_imported = 0
    chapter_exercises_imported = 0
    self_assessments_imported = 0
    exam_practices_imported = 0
    other_practices_imported = 0
    practice_questions_needs_review = 0
    practice_questions_skipped = 0
    processed_skill_ids = []
    detected_titles = []
    in_class_nums = []
    missing_image_questions = []
    docx_attached_count = 0
    docx_direct_display_images = 0
    docx_vector_images = 0
    docx_conversion_success = 0
    docx_conversion_failed = 0
    docx_copied_to_question_assets = 0
    docx_formula_blocks = {}
    is_pdf_source = str(source_file_path or "").lower().endswith(".pdf")
    is_docx_source = str(source_file_path or "").lower().endswith((".docx", ".doc"))
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
                        f"[DOCX IMAGE DEBUG] attached title={t} source_type=unknown path={a.get('path')}"
                    )
    page_image_cache = {}

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

    def _extract_title_number(text):
        if not text:
            return None
        match = re.search(r'(\d+)', str(text))
        return int(match.group(1)) if match else None

    def _normalize_problem_hash(problem_text, sub_questions=None, source_type="", title=""):
        normalized = normalize_math_text(str(problem_text or ""))
        normalized = re.sub(r"\s+", " ", normalized).strip()
        sq_norm = []
        for sq in sub_questions or []:
            if not isinstance(sq, dict):
                continue
            sq_norm.append(
                {
                    "label": str(sq.get("label", "") or "").strip(),
                    "problem": re.sub(r"\s+", " ", normalize_math_text(str(sq.get("problem", "") or ""))).strip(),
                    "answer": re.sub(r"\s+", " ", normalize_math_text(str(sq.get("answer", "") or ""))).strip(),
                    "solution": re.sub(r"\s+", " ", normalize_math_text(str(sq.get("solution", "") or ""))).strip(),
                }
            )
        payload = {
            "source_type": str(source_type or "").strip().lower(),
            "title": str(title or "").strip(),
            "problem": normalized,
            "sub_questions": sq_norm,
        }
        return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()[:16]

    def _contains_perm_comb_formula(text: str) -> bool:
        t = str(text or "")
        return bool(
            re.search(r"(?:\{\}\^\{[^}]+\}[PC]_\{[^}]+\}|[PC]\s*\(|[PC]\s*\^|[PC]_\{?|[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉]P)", t)
        )

    def validate_problem_formula_not_hallucinated(item_title: str, item: dict, problem_text: str, raw_block: str):
        text = str(problem_text or "")
        block = str(raw_block or "")
        has_placeholder = bool(
            re.search(r"\[FORMULA_MISSING\]|\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]|\[UNREADABLE_FORMULA\]", block)
        )
        if is_docx_source:
            current_app.logger.info(f"[DOCX FORMULA SOURCE] title={item_title} raw_block={block[:240]}")
        if has_placeholder:
            current_app.logger.warning(f"[DOCX FORMULA WARNING] formula placeholder found title={item_title}")
        if has_placeholder and _contains_perm_comb_formula(text):
            has_ocr_source = bool(item.get("formula_ocr_source"))
            if not has_ocr_source:
                current_app.logger.warning(f"[DOCX FORMULA WARNING] formula missing before AI title={item_title}")
                fallback_text = block if block.strip() else text
                fallback_text = re.sub(r"\[FORMULA_IMAGE_\d+\]", "[FORMULA_MISSING]", fallback_text)
                fallback_text = re.sub(r"\[WORD_EQUATION_UNPARSED\]", "[FORMULA_MISSING]", fallback_text)
                fallback_text = re.sub(r"\[UNREADABLE_FORMULA\]", "[FORMULA_MISSING]", fallback_text)
                item["needs_review"] = True
                item["needs_formula_review"] = True
                item["formula_missing"] = True
                item["formula_hallucination_risk"] = True
                item["parse_warning"] = "formula generated by AI without source"
                if re.search(r"試填入下列各式|試求下列各式之值", fallback_text):
                    item["problem_unusable"] = True
                return fallback_text
        if has_placeholder and not _contains_perm_comb_formula(text):
            fallback_text = block if block.strip() else text
            fallback_text = re.sub(r"\[FORMULA_IMAGE_\d+\]", "[FORMULA_MISSING]", fallback_text)
            fallback_text = re.sub(r"\[WORD_EQUATION_UNPARSED\]", "[FORMULA_MISSING]", fallback_text)
            item["needs_review"] = True
            item["needs_formula_review"] = True
            item["formula_missing"] = True
            if re.search(r"試填入下列各式|試求下列各式之值", fallback_text):
                item["problem_unusable"] = True
            return fallback_text
        return text

    def extract_formula_images_for_question_block(item_title: str):
        if not bool(current_app.config.get("ENABLE_DOCX_FORMULA_OCR_FALLBACK", False)):
            return []
        if not is_docx_source:
            return []
        ctx = _DOCX_IMPORT_CONTEXT or {}
        q_assets = ctx.get("question_assets", {}) if isinstance(ctx, dict) else {}
        candidates = q_assets.get(str(item_title).replace(" ", ""), []) or q_assets.get(str(item_title), [])
        results = []
        if not candidates:
            return results
        try:
            from PIL import Image
            model = get_model("vision_analyzer")
        except Exception:
            return results
        prompt = (
            "請只轉錄圖片中的數學式。"
            "不要補題目，不要解題，不要猜不存在的數字。"
            "若看不清楚，輸出 [UNREADABLE_FORMULA]。"
        )
        for asset in candidates:
            rel = str(asset.get("path") or "")
            if not rel:
                continue
            abs_path = rel if os.path.isabs(rel) else os.path.join(current_app.root_path, rel)
            if not os.path.exists(abs_path):
                continue
            try:
                img = Image.open(abs_path)
                resp = model.generate_content([prompt, img], generation_config={"temperature": 0.0, "max_output_tokens": 1024})
                text = str(getattr(resp, "text", "") or "").strip()
                if text:
                    results.append(text)
            except Exception:
                continue
        return results

    def _build_source_description(title, source_type, linked_example_title=None, needs_review=False, dedupe_hash=""):
        title_text = str(title or "").strip() or "未命名題目"
        parts = [f"source_type={source_type}"]
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
            inferred = f"例題{practice_num}"
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
        all_candidates = q_assets.get(str(question_title or "").replace(" ", ""), []) or q_assets.get(str(question_title or ""), [])
        candidates = [a for a in (all_candidates or []) if str(a.get("media_kind", "image_asset")) == "image_asset"]
        if not candidates:
            combo = f"{question_title} {question_text}"
            if any(k in str(combo or "") for k in ("如圖", "右圖", "附圖", "棋盤式街道圖", "著色")):
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
        all_candidates = q_assets.get(str(question_title or "").replace(" ", ""), []) or q_assets.get(str(question_title or ""), [])
        formula_candidates = [a for a in (all_candidates or []) if str(a.get("media_kind", "")) == "formula_asset"]
        if not formula_candidates:
            return None
        current_app.logger.info(f"[DOCX FORMULA ASSET] attached title={question_title} count={len(formula_candidates)}")
        assets = []
        for a in formula_candidates:
            assets.append(
                {
                    "asset_type": "word_formula_image",
                    "source": "docx",
                    "path": str(a.get("path") or ""),
                    "content_type": str(a.get("content_type") or ""),
                    "rid": a.get("rid"),
                    "image_attach_reason": a.get("image_attach_reason"),
                }
            )
        meta = {"formula_assets": assets, "formula_placeholders": ["[FORMULA_MISSING]"] * len(assets)}
        if not _contains_perm_comb_formula(question_text):
            meta["needs_formula_review"] = True
            meta["formula_missing"] = True
            meta["needs_review"] = True
            current_app.logger.warning(f"[DOCX FORMULA WARNING] formula_asset_without_ocr title={question_title}")
        return meta

    def _build_math_metadata(raw_text, standardized_meta, needs_review=False):
        meta = {
            "math_format": "standard_latex",
            "raw_problem_backup": str(raw_text or ""),
            "math_warnings": list(standardized_meta.get("warnings", [])),
            "needs_review": bool(needs_review or standardized_meta.get("needs_review", False)),
        }
        return meta

    def _determine_target_skill_id(base_clean_en_id, section_title, concept_name, example_obj):
        target_clean_en_id = base_clean_en_id
        if is_vocational_mathb and is_non_skill_bucket(concept_name, base_clean_en_id):
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
            if subject == 'B' and vol_num == 4:
                return f"vh_數學{subject}{vol_num}_{target_clean_en_id}"
            return f"vh_math{subject}{vol_num}_{target_clean_en_id}"
        return f"{prefix}{target_clean_en_id}"

    try:
        current_app.logger.info(" -> 開始寫入資料庫...")
        queue.put("INFO: -> 開始寫入資料庫...")
        chapters = parsed_data.get('chapters', [])
        
        for chapter_data in chapters:
            raw_chapter = chapter_data.get('chapter_title', '未命名章節').strip()
            
            # === 關鍵修正 1：提取數字並標準化章節名稱 ===
            match = re.search(r'(\d+)', raw_chapter)
            if match:
                chapter_num = int(match.group(1))
            else:
                chapter_num = 999  # ?????????????

            if is_vocational_mathb:
                # ???B?? AI ???????: "1 ????"????? chapter_num ????
                chapter_title = raw_chapter
            elif match:
                # ?????????????????????????????,?????????
                clean_title = re.sub(r'^(\u55ae\u5143|Unit|\u7b2c)?\s*\d+\s*(\u55ae\u5143|\u7ae0)?\s*', '', raw_chapter).strip()
                chapter_title = f"???{chapter_num} {clean_title}" if clean_title else f"???{chapter_num}"
            else:
                chapter_title = raw_chapter

            sections = chapter_data.get('sections', [])
            
            # 國中教材專用處理 (保留原邏輯,但只在國中時執行)
            if curriculum_info.get('curriculum') == 'junior_high':
                chapter_title = chapter_title.replace('\n', ' ').strip()
                chapter_title = re.sub(r'^(?:Chapter|Unit|第)\s*(\d+)(?:\s*章)?\s*', r'\1 ', chapter_title).strip()
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
                section_title = section_data.get('section_title', '') or ''  # 龍騰版很多是空字串,允許
                concepts = section_data.get('concepts', [])
                
                for concept_order, concept in enumerate(concepts, start=1):
                    concept_name = concept.get('concept_name', '未命名觀念').strip()
                    concept_en_id = concept.get('concept_en_id', 'Unknown')
                    concept_paragraph = concept.get('concept_paragraph', '未命名').strip()
                    
                    clean_en_id = re.sub(r'[^a-zA-Z0-9]', '', concept_en_id)
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
                        if subject == 'B' and vol_num == 4:
                            final_skill_id = f"vh_數學{subject}{vol_num}_{clean_en_id}"
                        else:
                            final_skill_id = f"vh_math{subject}{vol_num}_{clean_en_id}"
                        skill_id_msg = f"INFO: vocational math skill_id = {final_skill_id}"
                        current_app.logger.info(skill_id_msg)
                        queue.put(skill_id_msg)
                    else:
                        final_skill_id = f"{prefix}{clean_en_id}"
                    
                    if not skip_skill_creation:
                        # === SkillInfo 新增/更新 (維持原邏輯) ===
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
                        
                        # === SkillCurriculum 新增 (關鍵：加入正確的 display_order) ===
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
                                display_order=chapter_num * 10000 + skills_processed  # 10000 倍數確保單元間不會互相干擾
                            )
                            db.session.add(new_curr)
                            curriculums_added += 1
                    else:
                        queue.put(
                            f"INFO: 跳過非技能桶位 concept='{concept_name}' ({clean_en_id})，僅重導 examples。"
                        )

                    # === 題目寫入：先做 source_type 正規化，再依型別路由 ===
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

                        example_title = get_question_title(ex) or "例題"
                        detected_titles.append(example_title)
                        source_type = normalize_source_type_by_title(ex, default_source_type="textbook_example")
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
                        blank_norm_text, blank_meta = normalize_fill_blank_artifacts(db_problem_text_raw)
                        perm_norm_text, perm_meta = normalize_permutation_combination_notation(blank_norm_text)
                        db_problem_text_raw = perm_norm_text
                        if blank_meta.get("changed") or perm_meta.get("changed"):
                            logs = ex.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.extend(blank_meta.get("reasons", []))
                            logs.extend(perm_meta.get("reasons", []))
                            ex["repair_log"] = logs
                        raw_formula_block = docx_formula_blocks.get(str(example_title).replace(" ", ""), "") or docx_formula_blocks.get(str(example_title), "")
                        if raw_formula_block and re.search(r"\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]", raw_formula_block):
                            ocr_formulas = extract_formula_images_for_question_block(example_title)
                            if ocr_formulas:
                                block_replaced = str(raw_formula_block)
                                for i, ftxt in enumerate(ocr_formulas, start=1):
                                    block_replaced = block_replaced.replace(f"[FORMULA_IMAGE_{i}]", ftxt)
                                ex["formula_ocr_source"] = ocr_formulas
                                raw_formula_block = block_replaced
                        db_problem_text_raw = validate_problem_formula_not_hallucinated(
                            example_title, ex, db_problem_text_raw, raw_formula_block
                        )
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
                        db_problem_text_norm = normalize_math_text(db_problem_text_raw)
                        db_problem_text, ex_math_meta = standardize_problem_latex(db_problem_text_norm)
                        if re.search(r"P\(|C\(|P\^|C\^|\{\}\^|\{\}\^\{\\\(|\\\(\{\}\^|\\\(\{\}\^\{", str(db_problem_text_raw or "")):
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={example_title} before={db_problem_text_norm}")
                            current_app.logger.info(f"[LATEX STANDARDIZE] title={example_title} after={db_problem_text}")
                        db_answer = _render_sub_questions_answer(ex.get('correct_answer', ''), sub_questions)
                        db_solution = _render_sub_questions_solution(ex.get('detailed_solution', ''), sub_questions)
                        needs_review = bool(ex.get("needs_review", False))
                        ex["problem_text"] = db_problem_text
                        ex = validate_problem_block_purity(ex)
                        needs_review = bool(ex.get("needs_review", False))
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

                        if source_type == "textbook_example":
                            title_num = _extract_title_number(example_title)
                            if title_num is not None:
                                saved_example_skill_map[title_num] = target_skill_id
                            saved_example_order.append((example_title, target_skill_id))
                            saved_example_titles.append(example_title)

                        if existing_ex:
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
                            problem_type=ex.get('problem_type', source_type or 'calculation'),
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
                            "repair_log",
                        ):
                            if ex.get(k) is not None:
                                math_meta[k] = ex.get(k)
                        attach_image_metadata(new_ex, math_meta)
                        if re.search(r"[PC]\s*\(|[PC]\s*\^|[PC]\s*_|[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉]", str(db_problem_text or "")):
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

                    # === 隨堂練習/練習題：獨立寫入 ===
                    for practice_idx, practice in enumerate(concept.get('practice_questions', []) or [], start=1):
                        if not isinstance(practice, dict):
                            continue

                        practice_problem = str(
                            practice.get("problem_text", "") or practice.get("problem", "") or practice.get("question", "")
                        ).strip()
                        if not practice_problem:
                            continue

                        practice_title = get_question_title(practice) or "隨堂練習"
                        detected_titles.append(practice_title)
                        source_type = normalize_source_type_by_title(practice, default_source_type="in_class_practice")
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
                        blank_norm_text, blank_meta = normalize_fill_blank_artifacts(practice_problem_raw)
                        perm_norm_text, perm_meta = normalize_permutation_combination_notation(blank_norm_text)
                        practice_problem_raw = perm_norm_text
                        if blank_meta.get("changed") or perm_meta.get("changed"):
                            logs = practice.get("repair_log", [])
                            if not isinstance(logs, list):
                                logs = [str(logs)]
                            logs.extend(blank_meta.get("reasons", []))
                            logs.extend(perm_meta.get("reasons", []))
                            practice["repair_log"] = logs
                        raw_formula_block = docx_formula_blocks.get(str(practice_title).replace(" ", ""), "") or docx_formula_blocks.get(str(practice_title), "")
                        if raw_formula_block and re.search(r"\[FORMULA_IMAGE_\d+\]|\[WORD_EQUATION_UNPARSED\]", raw_formula_block):
                            ocr_formulas = extract_formula_images_for_question_block(practice_title)
                            if ocr_formulas:
                                block_replaced = str(raw_formula_block)
                                for i, ftxt in enumerate(ocr_formulas, start=1):
                                    block_replaced = block_replaced.replace(f"[FORMULA_IMAGE_{i}]", ftxt)
                                practice["formula_ocr_source"] = ocr_formulas
                                raw_formula_block = block_replaced
                        practice_problem_raw = validate_problem_formula_not_hallucinated(
                            practice_title, practice, practice_problem_raw, raw_formula_block
                        )
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
                        practice_problem_norm = normalize_math_text(practice_problem_raw)
                        practice_problem, practice_math_meta = standardize_problem_latex(practice_problem_norm)
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
                            dedupe_hash=dedupe_hash
                        )

                        existing_practice = TextbookExample.query.filter_by(
                            skill_id=target_skill_id,
                            source_curriculum=curriculum_info.get('curriculum'),
                            source_volume=str(curriculum_info.get('volume')),
                            source_chapter=chapter_title,
                            source_section=section_title,
                            source_description=source_description
                        ).first()
                        if existing_practice:
                            practice_questions_skipped += 1
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
                            "repair_log",
                        ):
                            if practice.get(k) is not None:
                                math_meta[k] = practice.get(k)
                        attach_image_metadata(practice_row, math_meta)
                        if re.search(r"[PC]\s*\(|[PC]\s*\^|[PC]\s*_|[⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉]", str(practice_problem or "")):
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
            'examples_added': examples_added,
            'examples_imported': examples_added,
            'textbook_examples_imported': examples_added,
            'practice_questions_imported': practice_questions_imported,
            'in_class_practices_imported': in_class_practices_imported,
            'chapter_exercises_imported': chapter_exercises_imported,
            'self_assessments_imported': self_assessments_imported,
            'exam_practices_imported': exam_practices_imported,
            'other_practices_imported': other_practices_imported,
            'practice_questions_needs_review': practice_questions_needs_review,
            'needs_review_count': practice_questions_needs_review,
            'practice_questions_skipped': practice_questions_skipped,
            'duplicates_skipped': practice_questions_skipped,
            'processed_skill_ids': processed_skill_ids
        }
    except Exception as e:
        db.session.rollback()
        tb = traceback.format_exc()
        current_app.logger.error(f"寫入資料庫失敗: {e}\n{tb}")
        queue.put(f"ERROR: 寫入資料庫失敗: {e}")
        return {}
