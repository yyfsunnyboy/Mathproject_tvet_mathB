def call_gemini_for_analysis(content_by_page, curriculum_info, queue, page_analysis_payload=None, import_policy=None):
    """Call Gemini to analyze extracted textbook content."""
    message = "--- ?? AI ??瘚? ---"
    current_app.logger.info(message)
    queue.put(f"INFO: {message}")

    # ==========================
    # 1. 設定基礎 Prompt
    # ==========================
    prompt_jh_kangxuan = "Analyze textbook content and return JSON."

    # ==========================
    # 2. ?桅?樴辰??Prompt (靽格迤???游之憿??蝭?)
    # ==========================
    prompt_sh_longteng = "Analyze textbook content and return JSON."

    # ==========================
    # 3. 行內公式與結構 Prompt
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
        queue.put(f"INFO: 已載入技高數學{subject}{vol_num} 專用提示詞範本")
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

        current_app.logger.error(f"AI 分析失敗: [{err_type}] {err_msg}\n{tb}")
        if "Gemini API Key" in err_msg or "API_KEY" in err_msg:
            queue.put("ERROR: Missing Gemini API Key.")
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

        current_app.logger.error(f"AI 分析失敗: [{err_type}] {err_msg}\n{tb}")
        queue.put(f"ERROR: AI 分析失敗: [{err_type}] {err_msg}")
        return None
