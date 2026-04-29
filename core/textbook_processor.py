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
# import fitz  # PyMuPDF -> Moved to inside function
import time
import io
# import pypandoc -> Moved to inside function
# from pypandoc.pandoc_download import download_pandoc
from google.api_core.exceptions import ResourceExhausted
from models import db, SkillInfo, SkillCurriculum, TextbookExample
from core.ai_analyzer import get_model
from flask import current_app
import traceback
from core.code_generator import auto_generate_skill_code
from core.math_formula_normalizer import detect_suspicious_formula, normalize_math_text

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

        content_by_page = _normalize_extracted_content_math(content_by_page, queue)

        # 步驟 2: 呼叫 AI 進行分析
        ai_json_result_string = call_gemini_for_analysis(content_by_page, curriculum_info, queue)
        # 步驟 3: 解析 AI 回傳的 JSON 字串
        if ai_json_result_string is None:
            return {"status": "error", "message": "AI 分析失敗，已中止匯入。"}
        if not ai_json_result_string:
            return {"status": "error", "message": "AI 回傳空內容，已中止匯入。"}

        ai_json_result_string = normalize_json_text_before_parse(ai_json_result_string)
        parsed_data = parse_ai_response(ai_json_result_string, queue)
        if not parsed_data:
            return {"status": "error", "message": "AI 回傳的資料格式有誤或為空，無法解析。"}

        parsed_data = _normalize_parsed_textbook_math(parsed_data, queue)

        # 步驟 4: 將解析後的資料存入資料庫
        result = save_to_database(parsed_data, curriculum_info, queue)

        skills_count = result.get('skills_processed', 0)
        curriculums_count = result.get('curriculums_added', 0)
        examples_count = result.get('examples_added', 0)
        practice_count = result.get('practice_questions_imported', 0)
        in_class_practice_count = result.get('in_class_practices_imported', 0)
        practice_needs_review_count = result.get('practice_questions_needs_review', 0)
        practice_skipped_count = result.get('practice_questions_skipped', 0)
        processed_skill_ids = result.get('processed_skill_ids', [])

        message = (
            f"課本處理完成。新增/更新 {skills_count} 個技能，建立 {curriculums_count} 筆課程綱要，"
            f"匯入例題 {examples_count} 筆、練習題 {practice_count} 筆（隨堂練習 {in_class_practice_count} 筆，"
            f"需複核 {practice_needs_review_count} 筆，重複略過 {practice_skipped_count} 筆）。"
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
            # --- Word (.docx) 處理邏輯 (使用 Pandoc) ---
            message = "偵測到 Word (.docx) 檔案，使用 Pandoc 轉換以保留數學公式..."
            current_app.logger.info(message)
            queue.put(f"INFO: {message}")

            try:
                # 建立一個暫存資料夾來存放從 Word 中提取的圖片
                temp_media_dir = os.path.join(os.path.dirname(file_path), "media")
                os.makedirs(temp_media_dir, exist_ok=True)

                # 設定 Pandoc 參數
                extra_args = [
                    '--wrap=none',
                    f'--extract-media={temp_media_dir}'
                ]

                # 執行轉換
                markdown_output = pypandoc.convert_file(file_path, 'markdown', extra_args=extra_args)

                # 呼叫專用清洗函式
                markdown_output = clean_pandoc_output(markdown_output)

                # --- 圖片 OCR 邏輯 ---
                # (局部函式：需要使用外層的 WandImage)
                def ocr_image_and_replace(match):
                    image_path_in_md = match.group(1)
                    from urllib.parse import unquote
                    image_path_in_md = unquote(image_path_in_md)
                    
                    full_image_path = os.path.join(os.path.dirname(file_path), image_path_in_md)

                    if os.path.exists(full_image_path):
                        try:
                            image_to_ocr_path = full_image_path
                            # 在 OCR 前先轉換 WMF/EMF 檔案
                            if full_image_path.lower().endswith(('.wmf', '.emf')):
                                if WandImage is None:
                                    queue.put(f"WARN: 略過 WMF/EMF 圖片轉換 ({image_path_in_md})，因為系統未安裝 Wand/ImageMagick。")
                                    return match.group(0) # 保持原樣

                                png_path = os.path.splitext(full_image_path)[0] + '.png'
                                try:
                                    with WandImage(filename=full_image_path) as img:
                                        img.format = 'png'
                                        img.save(filename=png_path)
                                    image_to_ocr_path = png_path
                                except Exception as wand_e:
                                    queue.put(f"WARN: 轉換圖片 {image_path_in_md} 失敗: {wand_e}")
                                    return match.group(0)

                            tesseract_path = current_app.config.get('TESSERACT_CMD')
                            if tesseract_path:
                                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                            
                            img = Image.open(image_to_ocr_path)
                            ocr_text = pytesseract.image_to_string(img, lang='chi_tra')
                            return f" {ocr_text.strip()} "
                        except Exception as ocr_e:
                            queue.put(f"WARN: OCR 辨識圖片 '{image_path_in_md}' 失敗: {ocr_e}")
                    
                    return match.group(0)

                # 使用 Regex 替換 Markdown 圖片標記
                final_output = re.sub(r'!\[.*?\]\((.*?)\)', ocr_image_and_replace, markdown_output)
                content_by_page[1] = final_output

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

def call_gemini_for_analysis(content_by_page, curriculum_info, queue):
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

    return parsed_data


def _first_non_empty_str(mapping, keys):
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


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
                    source_type = _first_non_empty_str(ex, ("source_type",)).lower() or "textbook_example"

                    ex_normalized = dict(ex)
                    ex_normalized["source_description"] = example_title or ex_normalized.get("source_description", "例題")
                    if problem_text:
                        ex_normalized["problem_text"] = problem_text
                    if answer:
                        ex_normalized["correct_answer"] = answer
                    if solution:
                        ex_normalized["detailed_solution"] = solution
                    ex_normalized["source_type"] = source_type if source_type else "textbook_example"
                    normalized_examples.append(ex_normalized)

                    for fp in ex.get("followup_practices", []) or []:
                        if not isinstance(fp, dict):
                            continue
                        p_title = _first_non_empty_str(fp, ("practice_title", "title", "source_description"))
                        p_problem = _first_non_empty_str(fp, ("problem_text", "problem", "question"))
                        p_answer = _first_non_empty_str(fp, ("correct_answer", "answer"))
                        p_solution = _first_non_empty_str(fp, ("detailed_solution", "solution"))
                        p_source_type = _first_non_empty_str(fp, ("source_type",)).lower() or "in_class_practice"
                        linked_example_title = _first_non_empty_str(fp, ("linked_example_title",)) or ex_normalized["source_description"]

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
                    p_source_type = _first_non_empty_str(practice, ("source_type",)).lower() or "in_class_practice"
                    linked_example_title = _first_non_empty_str(practice, ("linked_example_title",))

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

                    normalized_practices.append(normalized_practice)

                concept["examples"] = normalized_examples
                concept["practice_questions"] = normalized_practices

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

def save_to_database(parsed_data, curriculum_info, queue):
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
    practice_questions_needs_review = 0
    practice_questions_skipped = 0
    processed_skill_ids = []

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

    def _normalize_problem_hash(problem_text):
        normalized = normalize_math_text(str(problem_text or ""))
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]

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

                    # === 例題處理 (維持原邏輯) ===
                    saved_example_skill_map = {}
                    saved_example_order = []
                    for ex in concept.get('examples', []):
                        problem_text = ex.get('problem_text')
                        if not problem_text:
                            continue

                        example_title = str(ex.get("source_description", "") or ex.get("example_title", "") or "例題").strip()
                        source_type = str(ex.get("source_type", "textbook_example") or "textbook_example").strip().lower()
                        target_skill_id = _determine_target_skill_id(clean_en_id, section_title, concept_name, ex)

                        dedupe_hash = _normalize_problem_hash(problem_text)
                        source_description = _build_source_description(
                            example_title,
                            source_type=source_type,
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

                        title_num = _extract_title_number(example_title)
                        if title_num is not None:
                            saved_example_skill_map[title_num] = target_skill_id
                        saved_example_order.append((example_title, target_skill_id))

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
                            problem_text=problem_text,
                            problem_type=ex.get('problem_type', 'calculation'),
                            correct_answer=ex.get('correct_answer', ''),
                            detailed_solution=sanitize_detailed_solution_text(ex.get('detailed_solution', ''), max_chars=500),
                            difficulty_level=difficulty_level
                        )
                        db.session.add(new_ex)
                        examples_added += 1

                    # === 隨堂練習/練習題：獨立寫入 ===
                    for practice in concept.get('practice_questions', []) or []:
                        if not isinstance(practice, dict):
                            continue

                        practice_problem = str(
                            practice.get("problem_text", "") or practice.get("problem", "") or practice.get("question", "")
                        ).strip()
                        if not practice_problem:
                            continue

                        practice_title = str(
                            practice.get("source_description", "") or practice.get("practice_title", "") or "隨堂練習"
                        ).strip()
                        source_type = str(practice.get("source_type", "in_class_practice") or "in_class_practice").strip().lower()
                        linked_example_title = str(practice.get("linked_example_title", "") or "").strip() or None
                        needs_review = bool(practice.get("needs_review", False))

                        if not linked_example_title:
                            practice_num = _extract_title_number(practice_title)
                            if practice_num is not None:
                                linked_example_title = f"例題{practice_num}"

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

                        dedupe_hash = _normalize_problem_hash(practice_problem)
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
                            correct_answer=practice.get('correct_answer', ''),
                            detailed_solution=sanitize_detailed_solution_text(practice.get('detailed_solution', ''), max_chars=500),
                            difficulty_level=difficulty_level
                        )
                        db.session.add(practice_row)

                        practice_questions_imported += 1
                        if source_type == "in_class_practice":
                            in_class_practices_imported += 1
                        if needs_review:
                            practice_questions_needs_review += 1
                        saved_msg = (
                            f"[PRACTICE IMPORT] saved independent question title={practice_title} "
                            f"table=textbook_examples id=pending_commit"
                        )
                        current_app.logger.info(saved_msg)
                        queue.put(f"INFO: {saved_msg}")

        db.session.commit()
        return {
            'skills_processed': skills_processed, 
            'curriculums_added': curriculums_added,
            'examples_added': examples_added,
            'examples_imported': examples_added,
            'practice_questions_imported': practice_questions_imported,
            'in_class_practices_imported': in_class_practices_imported,
            'practice_questions_needs_review': practice_questions_needs_review,
            'practice_questions_skipped': practice_questions_skipped,
            'processed_skill_ids': processed_skill_ids
        }
    except Exception as e:
        db.session.rollback()
        tb = traceback.format_exc()
        current_app.logger.error(f"寫入資料庫失敗: {e}\n{tb}")
        queue.put(f"ERROR: 寫入資料庫失敗: {e}")
        return {}
