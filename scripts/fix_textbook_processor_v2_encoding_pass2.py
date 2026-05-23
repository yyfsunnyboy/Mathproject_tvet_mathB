# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "core" / "textbook_processor_v2.py"
text = path.read_text(encoding="utf-8")

REPLACEMENTS = [
    # Comments
    (
        "# 例撠嚗蝡?銵?閰唾圾韏瑟?撘???.match 銵?嚗?函?銵??圾???琿?嚗?",
        "# 例題：詳解起點用 .match 切行；函數題用 .search 找邊界",
    ),
    (
        "# 隨堂嚗?憿?統測嚗?敺??亦?閫敹菔玨?絲??銵? .match ?喳?蝯蒂皞Ｘ? unassigned嚗?",
        "# 隨堂：統測題在下一行才 .match；避免誤入 unassigned",
    ),
    (
        "# 統測甇瑕?閰阡?嚗蝡????柴?撅嚗??扼?05統測A??嚗?09統測嚗ｇ?蝑???",
        "# 統測歷屆試題：支援括號變體，如 105統測A、109統測B 等",
    ),
    (
        "# ???斗?閮擃?銝?韌 .*嚗?例sub 瘣楊??銵???憿凳",
        "# 行首若為章節碼 .*，例題 sub 需截斷後續題項",
    ),
    (
        "# 憿摰??銵???嚗?憿?隨堂嚗?憿???皜祇??瑯摮?璅?/蝛箇????",
        "# 題目邊界：例題、隨堂、習題編號或空白/空行",
    ),
    # Broken regex / runtime
    (
        r'if _SCAN_EXAM_MARKER_RE.search(s) and not re.search(r"[\(嚗[A-D嚗?嚗也", s):',
        r'if _SCAN_EXAM_MARKER_RE.search(s) and not re.search(r"[(（【][A-DＡ-Ｄa-d]", s):',
    ),
    (
        r'body = re.sub(r"^[\s\.?汕愍+", "", body).strip()',
        r'body = re.sub(r"^[\s\\.、．]+", "", body).strip()',
    ),
    (
        r'if re.match(r"^\s*閮苒s", line):',
        r'if re.match(r"^\s*設\s", line):',
    ),
    (
        r'm = re.search(r"(\d{2,3})統測([A-C嚗?嚗β)", compact, re.I)',
        r'm = re.search(r"(\\d{2,3})統測([A-D])", compact, re.I)',
    ),
    # Docstrings
    (
        '"""??銵??例??毀習題嚗隨堂練習璅?????head / tail??"""',
        '"""拆分混合行：例題與隨堂練習 head / tail。"""',
    ),
    (
        "    撟曆?雿????嚗ayout-Aware Deterministic Slicer嚗?\n"
        "    例嚗?擐圾??撘瑁圾蝑絲???瘀?隨堂嚗?憿?自我評量嚗???征銵??瑯?",
        "    Layout-Aware 確定性題塊切分。\n"
        "    例題、強解、隨堂練習、章末自我評量、章節習題等。",
    ),
    (
        '"""例閰唾圾?敺???敺?銵?蝳迫撖怠 buffer ??pending??"""',
        '"""例題詳解後停止延伸，避免污染 buffer 與 pending。"""',
    ),
    (
        'raise RuntimeError("Gemini JSON ?寧?暺?? object")',
        'raise RuntimeError("Gemini JSON 非預期 object")',
    ),
    (
        '"""?亙澈?? \\\\[ / \\\\] 頧 $嚗??蝡臬撥?嗆?銵???"""',
        '"""入庫前將 \\\\[ / \\\\] 轉 $，避免欄位錯位。"""',
    ),
    (
        '"""自我評量敺?箄?嚗嗾瘛冽???蝐歹?銝 dedupe ?釭??"""',
        '"""自我評量後台標籤，含章 dedupe 前綴。"""',
    ),
    (
        '"""?砍憿? key ?臬撠???憿?嚗? CH1自我評量 憿?嚗?"""',
        '"""比對題號：支援 CH1自我評量 題N 等格式。"""',
    ),
    (
        '"""憿?憭折?嚗絞皜?/ 隨堂 / 例 / 習題 / 其他??"""',
        '"""題目類型：統測 / 隨堂 / 例 / 習題 / 其他。"""',
    ),
    (
        '"""蝚砌?頠?統測憿???隞?撟港遢 + 統測 + ?? 撠??砍 key嚗? 111統測B嚗?"""',
        '"""寬鬆匹配統測題：年分 + 統測 + 類別 → key（如 111統測B）。"""',
    ),
    (
        '"""蝚砌?頠?隨堂/例 ??擐?憿? + 憿?憭折?擛?撠???"""',
        '"""寬鬆匹配隨堂/例：題號 + 類型關鍵字。"""',
    ),
    (
        "    憭抒雇甈?摨扳?嚗銝?例嚗???SkillCurriculum ORM ?????箝?\n"
        "    chapter / section 甈?隤??撠? chapter_title / section_title??",
        "    權威座標來自 SkillCurriculum ORM 欄位；\n"
        "    chapter / section 對應 chapter_title / section_title。",
    ),
    (
        "    隨堂?之蝬梁移皞????臬 scope ??curriculum + volume + 憿?撠?隞?Ⅳ??\n"
        "    隞?section.startswith(f\\\"{code} \\\") ??甈???蝳迫 LIKE %??甇?Gemini 璅?嚗?",
        "    動態查詢：依 scope 的 curriculum + volume + 小節碼；\n"
        "    以 section.startswith(f\\\"{code} \\\") 比對，不用 LIKE % 或 Gemini 章名。",
    ),
    (
        '"""?亙? ??隨堂??蝭隞?Ⅳ憭抒雇????"""',
        '"""以權威小節碼查詢大綱列。"""',
    ),
    (
        "    撘瑕 skills_info.category = 憭抒雇 section嚗RM 甈???section嚗?? section_title嚗?\n"
        "    瘣? AI 隤文神??1-3 ?臭?蝑?蝭瘙⊥???",
        "    僅在 category 為空時填入 section（非 section_title）。\n"
        "    避免 AI 誤寫 1-3 節標題到 category。",
    ),
    (
        "    憭抒雇甈?摨扳??喳?嚗?甇?TextbookExample 撟曆?甈? + SkillsInfo.category??\n"
        "    ? (authority coords, category_was_fixed)??",
        "    權威座標寫入 TextbookExample 與 SkillsInfo.category。\n"
        "    回傳 (authority coords, category_was_fixed)。",
    ),
    (
        "    甇?儔朣憚?⊥迤嚗?亙?憭抒雇??ORM 撅祆扯釵?潘?蝳迫 dict/霈??銝剛??臭???\n"
        "    chapter_title ??row.chapter嚗ection_title ??row.section??",
        "    幾何對齊：權威列 ORM 欄位寫入 example，避免 dict/字串錯位。\n"
        "    chapter_title ← row.chapter；section_title ← row.section。",
    ),
    (
        "    甈?撠?蝣潸圾??蝳迫?脖縑 Gemini section_title嚗?\n"
        "    ?芸?摨?瑼?/?臬 scope section_code ??憿? key ??憿 title ??Gemini??",
        "    正式 skill 僅用 section_code 比對，不用 Gemini section_title。\n"
        "    動態座標/scope section_code 對齊題號 key 與 title，不用 Gemini。",
    ),
    (
        "    Phase4 銋暹楊?箄?嚗迤????[source_type=?帆dedupe=?因 ?釭??\n"
        "    ?∪神甇颱葉???亦蝛箏?靘之蝬望?憡?????title / source_type ???‵??",
        "    Phase4 清洗來源描述：剝除 [source_type=...] 等污染。\n"
        "    阻擋 Phase1 注入標記污染 title / source_type 欄位。",
    ),
    (
        '"""例curriculum_info ????(B1??0, B2??1?? 閫??撟渡???"""',
        '"""由 curriculum_info 推導年級（B1→10, B2→11）。"""',
    ),
    (
        "    蝡??迂瘙箏??扳?瘣?撠? DB ???? 璅???\n"
        "    例蝚?蝡???蝟領???1 ??蝟領佗?蝚砌?蝡???1 ?佗?蝚?2 蝡??渡?????2 ?渡???",
        "    章名對齊決策：與 DB 章標題一致。\n"
        "    例：第1章 坐標系 → 1 坐標系；第2章 → 2 …",
    ),
    (
        r'm = re.match(r"^蝚枯s*(\d+)\s*蝡?\s*(.*)$", t, flags=re.UNICODE)',
        r'm = re.match(r"^第\s*(\d+)\s*章\s*(.*)$", t, flags=re.UNICODE)',
    ),
    (
        r'm = re.match(r"^蝚枯s*([銝鈭????凋??思??+)\s*蝡?\s*(.*)$", t, flags=re.UNICODE)',
        r'm = re.match(r"^第\s*([一二三四五六七八九十兩\d]+)\s*章\s*(.*)$", t, flags=re.UNICODE)',
    ),
    (
        r't = re.sub(r"^蝚枯s*", "", t)',
        r't = re.sub(r"^第\s*", "", t)',
    ),
    (
        r't = re.sub(r"^\s*蝡s*", "", t).strip()',
        r't = re.sub(r"^\s*章\s*", "", t).strip()',
    ),
    (
        'volume = coords["volume"] or "?詨飛B1"',
        'volume = coords["volume"] or "數學B1"',
    ),
    (
        '"""例Gemini 憭抒雇 JSON 撠?SkillCurriculum 撘瑕???Upsert嚗hapter / section 甈?嚗?"""',
        '"""Gemini 大綱 JSON → SkillCurriculum Upsert（chapter / section）。"""',
    ),
    (
        'raise ValueError("volume 銝?箇征")',
        'raise ValueError("volume 不可為空")',
    ),
    (
        "    PDF 璅∪?鈭蜓?亙嚗? 5 ???摮???Gemini 蝯? JSON ??SkillCurriculum Upsert??",
        "    PDF 模式二：前 5 頁目錄 → Gemini 大綱 JSON → SkillCurriculum Upsert。",
    ),
    # Fix mistaken double-escape in pass1 regex replacement
    (
        r'm = re.search(r"(\\d{2,3})統測([A-D])", compact, re.I)',
        r'm = re.search(r"(\d{2,3})統測([A-D])", compact, re.I)',
    ),
]

for old, new in REPLACEMENTS:
    if old not in text:
        print(f"MISSING: {old[:60]}...")
    else:
        text = text.replace(old, new)

path.write_text(text, encoding="utf-8", newline="\n")
print("pass2 done")
