# -*- coding: utf-8 -*-
"""One-off fix for mojibake in core/textbook_processor_v2.py."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "core" / "textbook_processor_v2.py"
text = path.read_text(encoding="utf-8")

# Longest-first literal replacements (runtime strings + JSON)
LITERALS = [
    ("Antigravity ???臬蝺楝 V2??", "Antigravity 教材匯入 V2 處理器"),
    (
        "- 璅∪?銝 (docx_problems)嚗onverted_docx_latex DOCX 瘙箏??折??桀?乓?",
        "- 模式一 (docx_problems)：converted_docx_latex DOCX Phase4 絕對注水與入庫",
    ),
    (
        "- 璅∪?鈭?(pdf_outline)嚗DF ??5 ?????SkillCurriculum 憭抒雇璅孵?甇乓?",
        "- 模式二 (pdf_outline)：PDF 前 5 頁目錄 → SkillCurriculum 大綱樹同步",
    ),
    ('"chapter_title": "蝚?蝡???蝟餉??賣?耦",', '"chapter_title": "1 坐標系與函數圖形",'),
    ('"section_title": "1-4 銝??甈∩?蝑?",', '"section_title": "1-4 一元二次不等式",'),
    ('"concept_name": "銝??甈∩?蝑??圾瘜?,', '"concept_name": "一元二次不等式",'),
    ('"title": "靘?1",', '"title": "例1",'),
    ('"source_description": "靘?1",', '"source_description": "例1",'),
    ('"problem_text": "靘?1",', '"problem_text": "例1",'),
    ('"title": "?典?蝺渡?1",', '"title": "隨堂練習1",'),
    ('"source_description": "?典?蝺渡?1",', '"source_description": "隨堂練習1",'),
    ('"problem_text": "?典?蝺渡?1",', '"problem_text": "隨堂練習1",'),
    ('f"CH{ch_num}?芣?閰?"', 'f"CH{ch_num}自我評量"'),
    ('"CH1?芣?閰?"', '"CH1自我評量"'),
    ('"?芣?閰?"', '"自我評量"'),
    ("?典?蝺渡?", "隨堂練習"),
    ("?芣?閰?", "自我評量"),
    ("蝯望葫", "統測"),
    ("靘??:憿??", "例題|例"),
    ("靘s*", "例\\s*"),
    ("靘?", "例"),
    ("蝧?", "習題"),
    ("?嗡?", "其他"),
    ("?典?", "隨堂"),
    ("銝??甈∩?蝑?", "一元二次不等式"),
    ("蝚?蝡???蝟餉??賣?耦", "1 坐標系與函數圖形"),
    ("憿s*", "題\\s*"),
    ("?芰蝡?", "未知章"),
    ("?∪???憛?", "missing block for"),
]

COMMENTS = {
    "# 靘?撠嚗蝡?銵?閰唾圾韏瑟?撘???.match 銵?嚗?函?銵??圾???琿?嚗?": (
        "# 例題：詳解起點用 .match 切行；函數題用 .search 找邊界"
    ),
    "# ?典?嚗?憿?蝯望葫嚗?敺??亦?閫敹菔玨?絲??銵? .match ?喳?蝯蒂皞Ｘ? unassigned嚗?": (
        "# 隨堂：統測題在下一行才 .match；避免誤入 unassigned"
    ),
    "# 蝯望葫甇瑕?閰阡?嚗蝡????柴?撅嚗??扼?05蝯望葫A??嚗?09蝯望葫嚗ｇ?蝑???": (
        "# 統測歷屆試題：支援括號變體，如 105統測A、109統測B 等"
    ),
    "# ???斗?閮擃?銝?韌 .*嚗?靘?sub 瘣楊??銵???憿凳": (
        "# 行首若為章節碼 .*，例題 sub 需截斷後續題項"
    ),
    "# 憿摰??銵???嚗?憿??典?嚗?憿???皜祇??瑯摮?璅?/蝛箇????": (
        "# 題目邊界：例題、隨堂、習題編號或空白/空行"
    ),
    "# Phase1 瘜典?hase2 ?芸?颲刻????憿?閮?蝜? Word ?梯?蝛箇嚗?楊??": (
        "# Phase1 注入觸發與 Phase2 切題；Word 列表與空行"
    ),
    "# PDF outline (mode two) ??SkillCurriculum sync": (
        "# PDF outline (mode two) → SkillCurriculum sync"
    ),
}

DOCSTRINGS = {
    '"""蝯曹? Word ?臬撣貉??寞?蝛箇?箔??祉征?潘??踹?甇??瞍??"""': (
        '"""正規化 Word 特殊空白，避免 Phase1 誤判。"""'
    ),
    '"""?亙 Phase1 ?拍?璅????支蒂?瘛典?敺?撟寡???"""': (
        '"""Phase1 觸發前綴與淨化後內容。"""'
    ),
    '"""?菜葫 OOXML ?芸?蝺刻? (w:numPr)嚗雿?p.text ?芸?詨??韌??"""': (
        '"""偵測 OOXML 自動編號 (w:numPr)，p.text 可能不含數字。"""'
    ),
    '"""畾菔?臬??Word 皜嚗葬?楊??暺?"""': '"""判斷是否為 Word 列表段落。"""',
    '"""敺歇瘛典?憿凳銵????1??9嚗?"""': '"""從淨化行擷取題號 1–99。"""',
    '"""?典耦嚗?撖恍??交迤閬??箏?敶Ｗ之撖?A???"""': '"""正規化括號類別為 A/B/C。"""',
    '"""?芸?銝銵??斤絞皜祉???閮?靽?璅?????憿凳嚗??摮?"""': (
        '"""移除行尾統測標記，保留題幹。"""'
    ),
    '"""敺絞皜祉????瑕? (year, category)嚗??A? ?嚗?敶Ｘ??"""': (
        '"""從統測標記解析 (year, category)。"""'
    ),
    '"""敺?擐?葫撽???1??9嚗??摮??剝???? None??"""': (
        '"""從邊界行解析題號 1–99，否則 None。"""'
    ),
    '"""瘣楊銵?憿摰?????詨?憿?嚗???摮? (1)/(2)??"""': (
        '"""剝除題目前導標題與子題 (1)/(2)。"""'
    ),
    '"""??憿?銵??賭葉撘瑁圾蝑絲????瑚蒂??嚗?match嚗?甇?.search嚗?"""': (
        '"""例題行內強解起點：優先 .match，否則 .search。"""'
    ),
    '"""??銵??靘???毀蝧?嚗?典?蝺渡?璅?????head / tail??"""': (
        '"""拆分混合行：例題與隨堂練習 head / tail。"""'
    ),
    '"""蝯?+?????斗嚗?閬?瘜典?拍???璅???"""': (
        '"""正規化 + 觸發注入，需先正規化再建 key。"""'
    ),
    '    撟曆?雿????嚗ayout-Aware Deterministic Slicer嚗?\n    靘?嚗?擐圾??撘瑁圾蝑絲???瘀??典?嚗?憿??芣?閰?嚗???征銵??瑯?': (
        "    Layout-Aware 確定性題塊切分。\n"
        "    例題、強解、隨堂練習、章末自我評量、章節習題等。"
    ),
    '"""Phase1 ?拍?璅??芸???嚗???芋撘? Canonical Key??"""': (
        '"""Phase1 觸發行轉為 Canonical Key。"""'
    ),
    '"""?臬?箸憿?瑽????迨憿???current_key 蝛箇???unassigned_buffer嚗?"""': (
        '"""新題目邊界時 flush current_key 至 unassigned_buffer。"""'
    ),
    '"""??憿隤脫??脩??蝯?嚗?蝯神??buffer嚗皞Ｘ? unassigned??"""': (
        '"""課文區塊結束時 flush buffer，避免 unassigned。"""'
    ),
    '"""靘?閰唾圾?敺???敺?銵?蝳迫撖怠 buffer ??pending??"""': (
        '"""例題詳解後停止延伸，避免污染 buffer 與 pending。"""'
    ),
    '"""撠?憛?key 靘摰之撠????踹??格活 Gemini JSON ??芣??"""': (
        '"""將題目 key 分塊，避免單次 Gemini JSON 過大。"""'
    ),
    '"""?蔥憭 Phase3 JSON嚗誑 update 隤??游? chapters/sections/concepts 憿?”嚗?"""': (
        '"""合併 Phase3 JSON，update 遞迴 chapters/sections/concepts。"""'
    ),
    '"""Gemini ??朣?憿?????蝡???璅?JSON嚗之?寞活?芸????蔥嚗?"""': (
        '"""Gemini 對齊章節概念 JSON，必要時分塊合併。"""'
    ),
    '"""?亙澈?? \\[ / \\] 頧 $嚗??蝡臬撥?嗆?銵???"""': (
        '"""入庫前將 \\\\[ / \\\\] 轉 $，避免欄位錯位。"""'
    ),
    '"""敺?Gemini ?瑟?憿?摮葡擛??瑕?憿?嚗???. ?拍?芾??艾? 9嚗?"""': (
        '"""從 Gemini 標題寬鬆擷取題號（例 9）。"""'
    ),
    '"""?芣?閰?敺?箄?嚗嗾瘛冽???蝐歹?銝 dedupe ?釭??"""': (
        '"""自我評量後台標籤，含章 dedupe 前綴。"""'
    ),
    '"""撠?Gemini 撣貉??洵N蝡?璅???朣 DB ???? 璅???"""': (
        '"""將 Gemini 章標題正規化為 DB 章名。"""'
    ),
    '"""隤脩雇 + 撟渡? + ? 銝?銝擃漣璅?Phase4 ?亥岷嚗神?亙?剁???"""': (
        '"""課程 + 冊別 + 章，供 Phase4 範圍比對。"""'
    ),
    '"""隞?SkillCurriculum 撟渡?嚗??亦雁摨阡?瑁楊?炊?寥?嚗??亙?閮梢?撘?撠???"""': (
        '"""依 SkillCurriculum 冊別比對，避免跨冊誤刪。"""'
    ),
    '"""?砍憿? key ?臬撠???憿?嚗? CH1?芣?閰? 憿?嚗?"""': (
        '"""比對題號：支援 CH1自我評量 題N 等格式。"""'
    ),
    '"""隞亦?瑽漣璅?+ 憿璅?瘥??Ｘ???dedupe_hash 銝????典摰???"""': (
        '"""依結構標題 + 類型查既有列，非 dedupe_hash。"""'
    ),
    '"""憿?憭折?嚗絞皜?/ ?典? / 靘? / 蝧? / ?嗡???"""': (
        '"""題目類型：統測 / 隨堂 / 例 / 習題 / 其他。"""'
    ),
    '"""蝚砌?頠?蝯望葫憿???隞?撟港遢 + 蝯望葫 + ?? 撠??砍 key嚗? 111蝯望葫B嚗?"""': (
        '"""寬鬆匹配統測題：年分 + 統測 + 類別 → key（如 111統測B）。"""'
    ),
    '"""蝚砌?頠??典?/靘? ??擐?憿? + 憿?憭折?擛?撠???"""': (
        '"""寬鬆匹配隨堂/例：題號 + 類型關鍵字。"""'
    ),
    '"""?‵憿凳嚗?頠?撘?撠?+ LaTeX 皜?????(block_text, matched_key)??"""': (
        '"""補齊題幹：前綴 + LaTeX 正規化 → (block_text, matched_key)。"""'
    ),
    '"""擛?瘥??嚗摮睬1 / B1 / ?詨飛 B1 ???? key??"""': (
        '"""冊別寬鬆比對：數學B1 / B1 / 數學 B1 等。"""'
    ),
    '"""撠?隞?Ⅳ??蝎暹?瘥?嚗?-1 ?臬? 2-1 ??嚗?銝炊??2-10??"""': (
        '"""小節碼邊界：1-1 可對 2-10，避免前綴誤配。"""'
    ),
    '"""?撠?隞?Ⅳ嚗? 1-1嚗摰璅?????閮?prefix ?雁瘥???"""': (
        '"""解析小節碼：1-1 等，產生 section prefix 查詢。"""'
    ),
    '"""?亙? ???典???蝭隞?Ⅳ憭抒雇????"""': (
        '"""以權威小節碼查詢大綱列。"""'
    ),
    '"""Phase4 憭抒雇?航??亥岷?亙 ???? section_code 銝駁嚗蕭??Gemini 璅?嚗?"""': (
        '"""Phase4 大綱查詢僅用 section_code，忽略 Gemini 章名。"""'
    ),
    '"""撘瑕 skills_info.category = 憭抒雇 section嚗RM 甈???section嚗?? section_title嚗?"""': (
        '"""僅在 category 為空時填入 section（非 section_title）。"""'
    ),
    '"""憭抒雇甈?摨扳??喳?嚗?甇?TextbookExample 撟曆?甈? + SkillsInfo.category??"""': (
        '"""權威座標寫入 TextbookExample 與 SkillsInfo.category。"""'
    ),
    '"""?菜葫甈?撌衣宏嚗olume 隤文神??curriculum 蝑?嚗???撠撖急香?摮葡??"""': (
        '"""偵測幾何欄位錯位（volume 寫入 curriculum 等）。"""'
    ),
    '"""???詨捆?亙? ??_phase4_propagate_curriculum_authority??"""': (
        '"""委派至 _phase4_propagate_curriculum_authority。"""'
    ),
    '"""???詨捆?亙? ??_textbook_geometry_from_curriculum_row??"""': (
        '"""委派至 _textbook_geometry_from_curriculum_row。""""'
    ),
    '"""?勗之蝬勗???撠??臬摨扳?嚗神??TextbookExample ?剁???"""': (
        '"""對齊座標供 TextbookExample 使用。"""'
    ),
    '"""?亙澈蝡???100% 隞?DB chapter ?箸?嚗1 撘瑕撠?璅??? ??蝟餉??賣?耦??"""': (
        '"""章名 100% 跟 DB chapter（如 1 坐標系與函數圖形）。"""'
    ),
    '"""? [source_type=?帆section=?帆dedupe=?因 蝑?亙??豢??釭??"""': (
        '"""剝除 [source_type=...] 等污染後綴。"""'
    ),
    '"""瘙箏??折?撟孵?憛思蒂 Upsert ?唾??澈??"""': (
        '"""絕對注水題幹並 Upsert 題庫。"""'
    ),
    '"""靘?curriculum_info ????(B1??0, B2??1?? 閫??撟渡???"""': (
        '"""由 curriculum_info 推導年級（B1→10, B2→11）。"""'
    ),
    '"""撠???銝??銝剜??詨?頧?踵?隡舀摮?蝡??剁???"""': (
        '"""將第X章正規化為阿拉伯數字章名。"""'
    ),
    '"""? (section_code, section_title) 撠? DB section 甈??????-1 ?貊???撠潦?"""': (
        '"""(section_code, section_title) 對齊 DB section（1-1 等）。"""'
    ),
    '"""????PDF ??N ??銝? 5嚗???嚗???(pdf_directory_text, pages_read)??"""': (
        '"""擷取 PDF 前 N 頁目錄 → (pdf_directory_text, pages_read)。"""'
    ),
    '"""靘?Gemini 憭抒雇 JSON 撠?SkillCurriculum 撘瑕???Upsert嚗hapter / section 甈?嚗?"""': (
        '"""Gemini 大綱 JSON → SkillCurriculum Upsert（chapter / section）。"""'
    ),
}

REGEX_FIXES = [
    (
        r'\[\(\\嚗\[A-D嚗\?嚗也',
        r'[(（【][A-DＡ-Ｄa-d]',
    ),
    (
        r'\(\\d\{2,3\}\)統測\(\[A-C嚗\?嚗β\)',
        r'(\\d{2,3})統測([A-D])',
    ),
    (
        r'if any\(tok in style_name for tok in \("List", "編\?", "璇\?", "皜", "Number"\)\):',
        'if any(tok in style_name for tok in ("List", "編號", "項目", "清單", "Number")):',
    ),
    (
        r"body = re\.sub\(r'\^\[\\s\\\.\?汕愍\+', \"\", body\)\.strip\(\)",
        "body = re.sub(r'^[\s\\.、．]+', '', body).strip()",
    ),
]

MULTILINE = {
    """    憭抒雇甈?摨扳?嚗銝?靘?嚗???SkillCurriculum ORM ?????箝?
    chapter / section 甈?隤??撠? chapter_title / section_title??""": (
        """    權威座標來自 SkillCurriculum ORM 欄位；
    chapter / section 對應 chapter_title / section_title。"""
    ),
    """    ?典??之蝬梁移皞????臬 scope ??curriculum + volume + 憿?撠?隞?Ⅳ??
    隞?section.startswith(f\"{code} \") ??甈???蝳迫 LIKE %??甇?Gemini 璅?嚗?""": (
        """    動態查詢：依 scope 的 curriculum + volume + 小節碼；
    以 section.startswith(f\"{code} \") 比對，不用 LIKE % 或 Gemini 章名。"""
    ),
    """    ?潮?湔?脩?嚗玨蝬?+ ? + 摰撠??迂銝雁摨衣移皞??潭?撠?==嚗?
    ?蝎暹??賜征銝?亦?凋誨蝣潭?嚗?隞乓code} ???prefix ?雁嚗?甇?LIKE %嚗?""": (
        """    精確三維比對：課程 + 冊 + 節；
    短碼另用 prefix 查詢，不用 LIKE %。"""
    ),
    """    朣憚?⊥迤嚗extbookExample 撟曆?摨扳???SkillCurriculum 甈?銝銝撠???
    ORM: curriculum / volume / chapter / section ??憿澈: source_curriculum / source_volume /
    source_chapter / source_section嚗蝳?摨椰蝘駁雿???""": (
        """    幾何對齊：TextbookExample 欄位來自 SkillCurriculum。
    ORM chapter/section → source_chapter / source_section。"""
    ),
}

import re as _re

for old, new in LITERALS:
    text = text.replace(old, new)

for old, new in COMMENTS.items():
    text = text.replace(old, new)

for old, new in DOCSTRINGS.items():
    text = text.replace(old, new)

for old, new in MULTILINE.items():
    text = text.replace(old, new)

for old, new in REGEX_FIXES:
    text = text.replace(old, new)

# Remaining single-char mojibake in log messages
text = text.replace("??skip to prevent cross-wire", "；skip to prevent cross-wire")
text = text.replace("Gemini ???:", "Gemini 配額耗盡:")

path.write_text(text, encoding="utf-8", newline="\n")
print(f"fixed {path}")
