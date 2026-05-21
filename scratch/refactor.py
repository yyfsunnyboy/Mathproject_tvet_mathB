import re
import os

def main():
    filepath = "core/textbook_processor.py"
    with open(filepath, "r", encoding="utf-8-sig") as f:
        content = f.read()

    # 1. Replace _is_question_start_text and _STRUCTURAL_BOUNDARY_PATTERNS (around lines 1040-1080)
    # Let's locate them dynamically.
    is_q_start_def = "def _is_question_start_text(text: str) -> bool:"
    struct_boundary_def = "_STRUCTURAL_BOUNDARY_PATTERNS = ["
    
    idx_q_start = content.find(is_q_start_def)
    idx_struct_boundary = content.find(struct_boundary_def)
    
    if idx_q_start != -1 and idx_struct_boundary != -1:
        # Let's find the end of _STRUCTURAL_BOUNDARY_PATTERNS definition.
        # It ends with ']' followed by some newlines and is_structural_boundary_line definition.
        idx_boundary_end = content.find("def is_structural_boundary_line(", idx_struct_boundary)
        if idx_boundary_end != -1:
            old_block = content[idx_q_start:idx_boundary_end]
            new_block = """def _is_question_start_text(text: str) -> bool:
    t = str(text or "").strip()
    if not t:
        return False
    if classify_non_question_block(t) in ("concept_explanation", "figure_caption", "narration"):
        return False
    heading_patterns = [
        r"^\s*例題\s*\\d+",
        r"^\s*隨堂練習\s*\\d+",
        r"^\s*基礎題\s*\\d+",
        r"^\s*進階題\s*\\d+",
        r"^\s*(?:\\d+\\s*-\\s*\\d+\\s*)?習題(?:\\s*(?:基礎題|進階題))?\\s*\\d*",
        r"^\s*自我評量",
        r"^\s*(?:統測|學測)\\s*\\d*",
        r"^\s*挑戰\s*\\d+",
        r"^\s*\\d+[\\s\\.\\)]",
    ]
    return any(re.search(p, t) for p in heading_patterns)


_STRUCTURAL_BOUNDARY_PATTERNS = [
    r"^\\s*第\\s*\\d+\\s*章",
    r"^\\s*\\d+\\s*[^\\d\\s].*$",
    r"^\\s*\\d+\\s*-\\s*\\d+\\s+[^\\s].*$",
    r"^\\s*\\d+\\s*-\\s*\\d+\\s*\\.\\s*\\d+\\s*[^\\s].*$",
    r"^\\s*例(?:題)?\\s*\\d+",
    r"^\\s*隨堂練習\\s*\\d+",
    r"^\\s*(?:\\d+\\s*-\\s*\\d+\\s*)?習題",
    r"^\\s*基礎題\\s*\\d*",
    r"^\\s*進階題\\s*\\d*",
    r"^\\s*自我評量",
    r"^\\s*(?:統測|學測)",
]


"""
            content = content.replace(old_block, new_block)
            print("Successfully updated _is_question_start_text and _STRUCTURAL_BOUNDARY_PATTERNS")
        else:
            print("Failed to find end of _STRUCTURAL_BOUNDARY_PATTERNS block")
    else:
        print("Failed to find _is_question_start_text or _STRUCTURAL_BOUNDARY_PATTERNS definition")

    # 2. Replace fix_common_latex_errors up to extract_converted_latex_docx
    idx_fix_errors = content.find("def fix_common_latex_errors(text):")
    idx_extract_conv = content.find("def extract_converted_latex_docx(")
    if idx_fix_errors != -1 and idx_extract_conv != -1:
        old_block = content[idx_fix_errors:idx_extract_conv]
        new_block = """def clean_pandoc_output(text):
    \"\"\"
    清理 Word 轉出後 LaTeX 的額外修整。
    \"\"\"
    if not text: return text

    # 1. 修正 Pandoc 特有的度數符號重複 (^{\\^{\\circ}} -> ^{\\circ})
    text = text.replace(r'^{\\^{\\circ}}', r'^{\\circ}')
    
    # 2. 將 \\( ... \\) 替換為 $ ... $
    text = re.sub(r'\\\\\\((.*?)\\\\\\\)', r'$\\1$', text)

    # 3. 修正 sqrt 格式
    text = re.sub(r'(?:\\\\)?sqrt\\s+(\\d+|[a-zA-Z])\\b', r'\\\\sqrt{\\1}', text)
    
    return text


def _xml_local_name(tag: str) -> str:
    if not tag:
        return ""
    return tag.split("}", 1)[-1] if "}" in tag else tag


def extract_docx_paragraph_with_equations(paragraph) -> str:
    \"\"\"提取段落文字\"\"\"
    return str(paragraph.text or "").strip()


def extract_docx_table_with_equations(table) -> str:
    \"\"\"提取表格文字\"\"\"
    lines = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            segs = [str(p.text or "").strip() for p in cell.paragraphs]
            cells.append(" ".join(filter(None, segs)).strip())
        lines.append(" | ".join(cells).strip())
    return "\\n".join(lines).strip()


"""
        content = content.replace(old_block, new_block)
        print("Successfully updated fix_common_latex_errors and docx extraction helpers")
    else:
        print("Failed to find fix_common_latex_errors or extract_converted_latex_docx definition")

    # 3. Remove score_extracted_page_quality up to _build_page_analysis_payload (around page quality and OCR)
    idx_score_page = content.find("def score_extracted_page_quality(page_text: str) -> dict:")
    idx_norm_math = content.find("def _normalize_imported_math_value(")
    if idx_score_page != -1 and idx_norm_math != -1:
        old_block = content[idx_score_page:idx_norm_math]
        content = content.replace(old_block, "")
        print("Successfully removed score_extracted_page_quality and OCR page analysis functions")
    else:
        print("Failed to find score_extracted_page_quality or _normalize_imported_math_value definition")

    # 4. Simplify extract_content_from_file (only support .docx, remove PDF branch)
    idx_extract_content = content.find("def extract_content_from_file(file_path, queue, max_pages=None, import_policy=None):")
    idx_sanitize_json = content.find("def _sanitize_and_parse_json(s: str, queue=None):")
    if idx_extract_content != -1 and idx_sanitize_json != -1:
        old_block = content[idx_extract_content:idx_sanitize_json]
        new_block = """def extract_content_from_file(file_path, queue, max_pages=None, import_policy=None):
    \"\"\"Extract text content from pre-converted MathType->LaTeX DOCX.\"\"\"
    message = f"正在從 {file_path} 提取內容..."
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    global _DOCX_IMPORT_CONTEXT
    _DOCX_IMPORT_CONTEXT = {}
    
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension not in ('.docx', '.doc'):
        message = f"不支援的檔案類型: {file_extension}。請使用 .docx 檔案。"
        current_app.logger.error(message)
        queue.put(f"ERROR: {message}")
        return {}

    try:
        content_by_page, doc_meta = extract_converted_latex_docx(file_path)
        extracted_text = str((content_by_page or {}).get(1, "") or "")
        detect_meta = detect_converted_latex_docx(extracted_text)
        _DOCX_IMPORT_CONTEXT = {
            "docx_formula_source_mode": "converted_docx_latex",
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
    except Exception as e:
        message = f"提取檔案內容時發生異常 (Exception): {e}"
        current_app.logger.error(message)
        queue.put(f"ERROR: {message}")
        return {}


"""
        content = content.replace(old_block, new_block)
        print("Successfully updated extract_content_from_file")
    else:
        print("Failed to find extract_content_from_file or _sanitize_and_parse_json definition")

    # 5. Simplify _determine_target_skill_id nested inside save_to_database
    idx_det_skill = content.find("    def _determine_target_skill_id(base_clean_en_id, section_title, concept_name, example_obj):")
    if idx_det_skill != -1:
        # Let's find the start of the next statement/def inside save_to_database
        # In the original file:
        #     try:
        #         current_app.logger.info(" -> ?\uf55d?寫\uf16f\uf2ea??..")
        idx_logger_info = content.find('    try:\n        current_app.logger.info(', idx_det_skill)
        if idx_logger_info != -1:
            old_block = content[idx_det_skill:idx_logger_info]
            new_block = """    def _determine_target_skill_id(base_clean_en_id, section_title, concept_name, example_obj):
        explicit_skill_id = str(example_obj.get("skill_id", "") or "").strip()
        if explicit_skill_id:
            return explicit_skill_id

        target_clean_en_id = base_clean_en_id
        if str(target_clean_en_id or "") == "DispersionAndLinearTransformation":
            target_clean_en_id = "DispersionMeasures"
        if str(target_clean_en_id or "") == "ProbabilityOperations":
            target_clean_en_id = "ProbabilityProperties"

        if is_vocational_math:
            return normalize_vocational_math_skill_id(subject, vol_num, target_clean_en_id)
        return f"{prefix}{target_clean_en_id}"

"""
            content = content.replace(old_block, new_block)
            print("Successfully simplified _determine_target_skill_id")
        else:
            print("Failed to find try: block after _determine_target_skill_id")
    else:
        print("Failed to find _determine_target_skill_id definition")

    # 6. Remove the self_assessment B4 mapping logic block inside save_to_database
    idx_sa_check = content.find('if source_type == "self_assessment" and is_vocational_mathb and vol_num == 4:')
    if idx_sa_check != -1:
        # Let's find the end of the else block that finishes this if-else construct
        # The structure is:
        # if ...
        #    ...
        # else:
        #    linked_num = ...
        #    ...
        #    target_skill_id = _determine_target_skill_id(...)
        #    ...
        # log_msg = ...
        idx_log_msg = content.find('log_msg = (', idx_sa_check)
        if idx_log_msg != -1:
            # We want to replace the whole `if target_skill_id:` block starting from idx_sa_check
            # up to the start of log_msg line.
            # Let's find the line boundaries.
            start_pos = content.rfind('if not target_skill_id:', 0, idx_sa_check)
            if start_pos != -1:
                old_block = content[start_pos:idx_log_msg]
                new_block = """if not target_skill_id:
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

                        """
                content = content.replace(old_block, new_block)
                print("Successfully simplified self-assessment target_skill_id routing logic")
            else:
                print("Failed to find start_pos for target_skill_id routing block")
        else:
            print("Failed to find log_msg after self_assessment block")
    else:
        print("Failed to find self_assessment check")

    # 7. Remove mark review for low quality pages, is_non_skill_bucket, remap_mathb, and infer_mathb4
    # Let's locate the range between `_mark_needs_review_for_low_quality_pages` and `import_outline_structure_only`
    idx_mark_review = content.find("def _mark_needs_review_for_low_quality_pages(")
    idx_import_outline = content.find("def import_outline_structure_only(")
    if idx_mark_review != -1 and idx_import_outline != -1:
        old_block = content[idx_mark_review:idx_import_outline]
        content = content.replace(old_block, "")
        print("Successfully removed mark_needs_review, is_non_skill_bucket, remappings and self_assessment inference functions")
    else:
        print("Failed to find _mark_needs_review_for_low_quality_pages or import_outline_structure_only definition")

    # 8. Clean up Mojibake logs and comments
    # Replace all CP950-decoded strings in logger statements and comments with Traditional Chinese
    mojibake_replacements = {
        '# (???炎?亙歇蝘駁)': '# (此暫存區已刪除)',
        '# [靽?] ?典??祉? LaTeX ?靽桀儔?賢?': '# [修復] 處理並修正 LaTeX 的逸出字元',
        '# ?瑕??€憭惜 JSON object嚗?芋??敺?隤芣???': '# 尋找最大的 JSON object，並處理額外的括號問題',
        '# 靽桀儔?? JSON escape??': '# 處理內部的 JSON escape',
        '# JSON ?? escape ?芣?嚗?': '# 這是 JSON escape 的處理：',
        '# ?嗡? LaTeX escape嚗?憒?\\( \\) \\[ \\] \\frac \\binom \\times \\cdot': '# 避免 LaTeX 中的反斜線干擾 JSON 的解析',
        '# ?賡?閬 raw JSON 鋆∟?????蝺?json.loads 敺??????桀?????': '# 這些反斜線在 raw JSON 中需要被雙重逸出，避免 json.loads 失敗',
        '# ???虜閬?LaTeX ?賭誘??隞日??剖?憟賣?? JSON escape': '# 標準的 LaTeX 寫法如果被當作 JSON 逸出，最好統一做替換',
        '# (靘? \\binom, \\frac, \\times)嚗??json.loads ????嗅??€憯?MathJax??': '# 例如 \\frac 等，將其正確解開以方便載入 MathJax',
        '# 4. 靽格迤撣貉? OCR/Pandoc ?航炊': '# 4. 修正常見的 OCR/Pandoc 轉換錯誤',
        '# [NEW] 撠皜??賢?嚗?? Word (Pandoc) 頛詨??摮???': '# [NEW] 解析 Docx 段落中的 MathType 公式與 LaTeX 轉換字串',
        '# 1. 靽桀儔 Pandoc ?Ｙ?????璅漲?貊泵??(^{\\^{\\circ}} -> ^{\\circ})': '# 1. 修正 Pandoc 特有的度數符號重複',
        '# 2. 蝯曹?撠?\\( ... \\) 頧???$ ... $ (MathJax ?湔??': '# 2. 將 \\( ... \\) 替換為 $ ... $ 方便 MathJax 載入',
        '# ? Word 頧??皞?LaTeX 銵?詨??澆?嚗??典?蝡舫＊蝷箸? $ 瘥??': '# 這能確保 LaTeX 行內公式在前端正常渲染',
        '# 3. 靽桀儔 sqrt (Pandoc ???撓??sqrt 2 ????\\sqrt{2})': '# 3. 修正 sqrt 格式',
        '# ?ㄐ?芸??€靽??耨敺抬??踹?隤文??': '# 這裡做最基本的安全字元轉換',
        '# 撌脩獢?嚗頝唾?望?????雿葉?摮??寧銝剜?撘??踹??游? JSON 摮葡': '# 已知問題：有些欄位在 Gemini 回傳時可能沒有包含完整的繁體中文字串',
        '# ?芯???敺?隢挾嚗????憭葉??挾??': '# 將會進行二次比對，減少人工審查負擔',
        '# [NEW] ?脣?嚗炎?交?衣 Word ?怠???瑼?(隞?~$ ?)': '# [NEW] 排除 Word 的暫存檔 (以 ~$ 開頭)',
        '# 甇仿? 1: 敺?PDF/Word ???批捆': '# 步驟 1: 從 Word 檔案中提取內容',
        '# [V2.5] ?遣蝡?瑽芋撘?': '# [V2.5] 建立暫時性的單元對照關係',
        '# ?岫 AI TOC 閫??': '# 嘗試解析 AI TOC 結構',
        '# [V2.6] 蝘駁 OutlinePlaceholder ?摩嚗漱?勗??典神?亙撘???': '# [V2.6] 移除 OutlinePlaceholder 欄位以簡化結構',
        '# ??AI 閫??憭望?嚗???YAML Fallback': '# 如果 AI 解析失敗，則使用 YAML Fallback',
        '# 撠?YAML 頧???parsed_data ?澆?': '# 將 YAML 轉換為 parsed_data 格式',
        '# 甇仿? 2: ?澆 AI ?脰???': '# 步驟 2: 呼叫 AI 進行分析',
        '# 甇仿? 3: 閫?? AI ???JSON 摮葡': '# 步驟 3: 解析 AI 回傳的 JSON 結構',
        '# 甇仿? 4: 撠圾???????亥??澈': '# 步驟 4: 將解析出來的內容寫入資料庫',
        '# 甇仿? 5: ?芸????粹?蝔?蝣?(?舫)': '# 步驟 5: 產生對應的技能程式碼 (選用)',
        'f"INFO: [{idx+1}/{len(processed_skill_ids)}] 甇??? {skill_id}.py ..."': 'f"INFO: [{idx+1}/{len(processed_skill_ids)}] 正在寫入 {skill_id}.py ..."',
        '# [靽格迤] ???啣?亦??€?踝?撘瑕?瑁? Architect ???€?啁? Prompt': '# [修復] 呼叫 Gemini 的 Model 進行結構化分析',
        'f"ERROR: ?? {skill_id} ?????航炊: {e}"': 'f"ERROR: 技能 {skill_id} 程式碼寫入失敗: {e}"',
        'f"??隤脫?????隤? {e}"': 'f"解析教材內容時發生錯誤: {e}"',
        'message = f"甇?敺?{file_path} ???批捆..."': 'message = f"正在從 {file_path} 提取內容..."',
        'message = f"??瑼??批捆???隤?(Exception): {e}"': 'message = f"提取檔案內容時發生異常 (Exception): {e}"',
        'current_app.logger.debug(f"[JSON_DEBUG] ?????瑕漲: {len(s)} 摮泵")': 'current_app.logger.debug(f"[JSON_DEBUG] 原始 JSON 長度: {len(s)} 字元")',
        '# ===== 蝚?0 甇伐?????憪???閰喟敦鞈? =====': '# ===== 第 0 步：輸出 JSON 調試資訊 =====',
        '# ===== 蝚?1 甇伐?蝘駁 code fence wrapper =====': '# ===== 第 1 步：清除 code fence wrapper =====',
        '# ===== 蝚?2 甇伐?蝘駁??蝭??批摮? =====': '# ===== 第 2 步：移除前後不合規的字元 =====',
        '# ===== 蝚?3 甇伐????航??BOM =====': '# ===== 第 3 步：過濾潛在的 BOM =====',
        '# ===== 蝚?4 甇伐??岫憭車??蝺耨敺拍???=====': '# ===== 第 4 步：嘗試使用多種策略進行 JSON 解析 =====',
        '# 蝑 0: ??嚗?蝘駁 control chars / fences嚗?': '# 策略 0: 直接解析',
        '# 蝑 1: 靽???escape - ?芸?敺銝?? JSON escape ???? escape': '# 策略 1: 嘗試還原被額外轉義的字元',
        '# 蝑 2: 瞈€??escape - ?€?迨蝡????賡???': '# 策略 2: 移除無效逸出字元',
        '# 蝑 3: ?€敺?摨?- ?€?????賡???': '# 策略 3: 強制將畸形 JSON 還原',
        '# 蝑 4: ?岫?曉蝚砌???{ ??敺???} ??銝?': '# 策略 4: 提取第一個 { 和最後一個 } 之間的內容',
        'current_app.logger.info(f"[JSON_SUCCESS] 雿輻蝑 \'{strategy_name}\' ??閫?? JSON")': 'current_app.logger.info(f"[JSON_SUCCESS] 策略 \'{strategy_name}\' 成功解析 JSON")',
        'current_app.logger.debug(f"[JSON_FAIL] 蝑 \'{strategy_name}\' 憭望?: {error_detail}")': 'current_app.logger.debug(f"[JSON_FAIL] 策略 \'{strategy_name}\' 失敗: {error_detail}")',
        'queue.put(f"ERROR: JSON 閫??憭望?嚗?閰?{len(attempts)} 蝔桃??伐?嚗底閬撩??亥?")': 'queue.put(f"ERROR: JSON 解析失敗（已嘗試 {len(attempts)} 種策略），請管理員手動微調")',
        'current_app.logger.error(f"_call_gemini_with_retry ?潛??航炊: [{err_type}] {err_msg}\\n{tb}")': 'current_app.logger.error(f"_call_gemini_with_retry 發生錯誤: [{err_type}] {err_msg}\\n{tb}")',
        'queue.put(f"ERROR: Gemini ?澆憭望?: [{err_type}] {err_msg}")': 'queue.put(f"ERROR: Gemini 呼叫失敗: [{err_type}] {err_msg}")',
        '# 1. ?葉摨瑁???Prompt (靽??見)': '# 1. 設定基礎 Prompt',
        '# 2. ?桅?樴辰??Prompt (靽格迤??游之憿??蝭?)': '# 2. 設定大綱與對齊規範 Prompt',
        '# 3. ???Prompt': '# 3. 行內公式與結構 Prompt',
        'queue.put(f"INFO: 撌脤??擃?詨飛{subject}{vol_num} 撠??璅∪?")': 'queue.put(f"INFO: 已載入技高數學{subject}{vol_num} 專用提示詞範本")',
        'current_app.logger.error(f"AI ??憭望?: [{err_type}] {err_msg}\\n{tb}")': 'current_app.logger.error(f"AI 分析失敗: [{err_type}] {err_msg}\\n{tb}")',
        'queue.put(f"ERROR: AI ??憭望?: [{err_type}] {err_msg}")': 'queue.put(f"ERROR: AI 分析失敗: [{err_type}] {err_msg}")',
        'current_app.logger.info(" -> [OutlineOnly] ??撱箇?蝡??桅?...")': 'current_app.logger.info(" -> [OutlineOnly] 開始建立單元大綱...")',
        '# 撘瑕皜 session 銝剔?隞颱? pending 霈嚗??autoflush 閫貊????SkillInfo ?航炊': '# 清理 Session 中的暫存異動',
        '# ????蝯??啣??': '# 將結構對照關係儲存',
        '# ?冽餈質馱撌脰???蝡?嚗??銴?蝞?': '# 若為已建立的單元，則進行更新',
        '# 蝡??迂??': '# 單元大綱解析',
        '# Skip review / ?芣?閰? / 銴? sections ??these are not formal teaching': '# Skip review / 自我評量 / 複習等非正式教學單元',
        '# 撠?蝯??啣?': '# 對應到結構大綱',
        '# ?岫敺?蝭€璅??? 1-1, 1-2 蝑誨蝣?': '# 嘗試從單元名稱中提取 1-1, 1-2 等代碼',
        '# 瘙箏??€蝯?蝭€璅?': '# 找不到匹配的單元',
        '# 瘙箏??€蝯?蝭€璅?': '# 找不到匹配的章節',
        '# 瘙箏? skill_id (???箇?揣撘?銝遣蝡?SkillInfo)': '# 找不到 skill_id (僅作為大綱結構)',
        '# 雿輻 SectionTitle ?Ｙ???ID嚗?outline ?韌隞亥霅': '# 使用 SectionTitle 建立暫時性 ID',
        '# 瑼Ｘ撠??臬摮': '# 檢查該技能是否已存在',
        'current_app.logger.error(f"[import_outline_structure_only] 憭望?: {e}")': 'current_app.logger.error(f"[import_outline_structure_only] 失敗: {e}")',
        '# [NEW] 瑼?閫??????': '# [NEW] 檢驗章節數量與頁數限制',
        '# [NEW] ??蝯??啣?撠?璈 (Structure Map Alignment)': '# [NEW] 教材結構大綱對齊',
        '# [V2.6] ?€擃摮?B 蝟餃?嚗?澆?朣???暺?': '# [V2.6] 自動適配技高數學B課本單元對照',
        '# 撠?Ｘ??桅?蝭€暺?(靘? 1-1 xxx)': '# 搜尋匹配的單元起點 (例如 1-1 xxx)',
        '# 撘瑕撠?structure_meta 鋆??Ｘ?璅?鞈?嚗??蝥?銴遣蝡?璅?銝???': '# 寫入大綱結構屬性，避免重複寫入',
        '# 璅?撠???嚗??蝥粥??filename_meta fallback': '# 單元對齊成功，否則使用檔名 fallback',
        '# ?曆??唳??暺?璅?撠?憭望?': '# 若無任何對應單元，則對齊失敗',
        'current_app.logger.info(" -> ??撖怠鞈?摨?..")': 'current_app.logger.info(" -> 開始寫入資料庫...")',
        'queue.put("INFO: -> ??撖怠鞈?摨?..")': 'queue.put("INFO: -> 開始寫入資料庫...")',
        '# === ?靽格迤 1嚗??摮蒂璅???蝭€?迂 ===': '# === 標題格式修正 1: 從原始字串中解析章節與技能名稱 ===',
        '# [V2.2] ?芸?雿輻??蝯??啣?撠?': '# [V2.2] 引入結構大綱映射',
        '# ?€擃摮睬蝟餃?嚗?蝙?冽???瑽??': '# 連續數字偵測：避免解析錯誤的章節',
        '# ?葉??撠?? (靽???頛?雿?典?銝剜??瑁?)': '# 教材對齊結構 (在此處進行技能綁定)',
        '# [NEW] 餈質馱蝡???蝭€?€??': '# [NEW] 比對是否有重疊的章節或單元',
        '# 蝪∪餈質馱蝡? (甇方?蝪∪???嚗?蝭€?賣?閫貊雿????望擃?': '# 自動合併章節名稱',
        '# === SkillInfo ?啣?/?湔 (蝬剜???頛? ===': '# === SkillInfo 新增/更新 ===',
        '# === SkillCurriculum ?啣? (?嚗??交迤蝣箇? display_order) ===': '# === SkillCurriculum 新增 ===',
        '# [V2.6] ?交?€擃摮睬銝?朣仃??蝳迫撱箇??啁??暵?(?踹? 1_- ??1-1_-)': '# [V2.6] 自動填充無技能的結構大綱',
        '# === 憿撖怠嚗???source_type 甇???????頝舐 ===': '# === 題目寫入：依據 source_type 進行資料分類 ===',
        '# === ?典?蝺渡?/蝺渡?憿??函?撖怠 ===': '# === 範例題與練習題寫入 ===',
        'current_app.logger.error(f"撖怠鞈?摨怠仃?? {e}\\n{tb}")': 'current_app.logger.error(f"寫入資料庫中斷: {e}\\n{tb}")',
        'queue.put(f"ERROR: 撖怠鞈?摨怠仃?? {e}")': 'queue.put(f"ERROR: 寫入資料庫中斷: {e}")'
    }
    
    replaced_count = 0
    for old, new in mojibake_replacements.items():
        if old in content:
            content = content.replace(old, new)
            replaced_count += 1
    print(f"Replaced {replaced_count} mojibake keys")

    with open(filepath, "w", encoding="utf-8-sig") as f:
        f.write(content)
    print("All tasks executed. File saved.")

if __name__ == "__main__":
    main()
