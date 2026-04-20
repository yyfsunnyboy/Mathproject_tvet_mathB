# -*- coding: utf-8 -*-
import re
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "core" / "routes" / "analysis.py"
new_text = path.read_text(encoding="utf-8")

_label_subs = [
    (r"'sign_handling':\s*'[^']*'", "'sign_handling': '符號處理'"),
    (r"'add_sub':\s*'[^']*'", "'add_sub': '加減運算'"),
    (r"'mul_div':\s*'[^']*'", "'mul_div': '乘除運算'"),
    (r"'mixed_ops':\s*'[^']*'", "'mixed_ops': '四則混合'"),
    (r"'absolute_value':\s*'[^']*'", "'absolute_value': '絕對值'"),
    (r"'parentheses':\s*'[^']*'", "'parentheses': '括號運算'"),
    (r"'divide_terms':\s*'[^']*'", "'divide_terms': '分項除法'"),
    (r"'conjugate_rationalize':\s*'[^']*'", "'conjugate_rationalize': '有理化'"),
]
for pat, rep in _label_subs:
    new_text = re.sub(pat, rep, new_text)

_str_repls = [
    (
        '"""Missing image, invalid payload, unreadable OCR, or unusable expression ??do not run tutoring LLM."""',
        '"""缺圖、payload 無效、OCR 無法讀取或運算式不可用時的回應；不呼叫教學用 LLM。"""',
    ),
    (
        '"skill_focus": skill_focus or "憭?撘?蝪∟???"',
        '"skill_focus": skill_focus or "依題目重點進行化簡與整理"',
    ),
    ("# AI Chat & Handwriting (AI ?叟??)", "# AI Chat & Handwriting（AI 對話與手寫）"),
    (
        "        # ?芬謘??質 skill_id (Fallback)",
        "        # 依內文關鍵字推測 skill_id（Fallback）",
    ),
    ("        if '?朱?' in context: skill_id = 'remainder'", "        if '餘式' in context: skill_id = 'remainder'"),
    ("        elif '?蹎?' in context: skill_id = 'factor_theorem'", "        elif '因式' in context: skill_id = 'factor_theorem'"),
    (
        "    # ?伍??撖??株????????????圈?鞈?????蹓??迫?堊垮??頛??湛???",
        "    # 讀寫 session 中的延伸問答狀態（與題目脈絡綁定）。",
    ),
    (
        "    # ?漱謓梢??賊??賹???啾冪?閰??嚗??????堊筑???????擏???⊿豲??????????????",
        "    # 題目脈絡變更時重置回合索引；依序產生本回合的後續引導題組。",
    ),
    (
        '            student_answer = f"?????????: {result.get(\'reply\', \'\')}"',
        '            student_answer = f"【手寫批改回覆】：{result.get(\'reply\', \'\')}"',
    ),
    (
        "                    'reason': diagnosis.get('prerequisite_explanation', '?梁????')",
        "                    'reason': diagnosis.get('prerequisite_explanation', '建議先複習相關先備概念。')",
    ),
    ("    # ?謕???update_progress ??湔?鈭????秋撒???質縐?????helper", "    # 進度更新交由其他路由／helper；此處不直接呼叫 update_progress"),
    ("        return jsonify({'success': True, 'message': '??'})", "        return jsonify({'success': True, 'message': '已儲存'})"),
    (
        '        current_app.logger.error(f"?╰??????芰?: {e}")',
        '        current_app.logger.error(f"錯題本寫入失敗: {e}")',
    ),
    (
        "    if 'file' not in request.files: return jsonify({'success': False, 'message': '????澗??'}), 400",
        "    if 'file' not in request.files: return jsonify({'success': False, 'message': '未找到上傳檔案'}), 400",
    ),
    (
        "        return jsonify({'success': False, 'message': '?澗?????'}), 400",
        "        return jsonify({'success': False, 'message': '不允許的檔案類型'}), 400",
    ),
    ("# Mistake Notebook & Diagnosis (????蟡??桃捂謘?", "# Mistake Notebook & Diagnosis（錯題本與診斷）"),
    ("# [?蝞??乾?] Mistake Notebook Helpers", "# Mistake Notebook 相關輔助函式"),
    ("# Student Diagnosis (?株???株???桃捂謘?蹓遴?)", "# Student Diagnosis（學生診斷頁）"),
    ("# Naive RAG (RAG ?潘撕??+ LLM ?豯?)", "# Naive RAG（簡易檢索 + LLM 彙整）"),
    ("# RAG??? + ???", "# RAG 查詢與進階 RAG"),
    ('        return jsonify({"results": [], "error": "???????"}), 400', '        return jsonify({"results": [], "error": "查詢字串不可為空"}), 400'),
    (
        '        return jsonify({"reply": "??????????"}), 400',
        '        return jsonify({"reply": "查詢或技能 ID 不可為空"}), 400',
    ),
]
for old, new in _str_repls:
    if old not in new_text:
        print("WARN missing:", repr(old[:65]))
    new_text = new_text.replace(old, new)

# prereq_name 預設（雙引號亂碼）
new_text, n = re.subn(
    r'^(\s*prereq_name = )"[^"]*"$',
    r'\1"未知先備課題"',
    new_text,
    flags=re.MULTILINE,
)
if n == 0:
    print("WARN: prereq_name line not regex-replaced")

new_text = re.sub(
    r'(def student_diagnosis\(\):\s*\n)(\s*)"""[\s\S]*?"""',
    r'\1\2"""顯示學生診斷（學習落點）頁面。"""',
    new_text,
    count=1,
)

path.write_text(new_text, encoding="utf-8")
print("mojibake ok")
