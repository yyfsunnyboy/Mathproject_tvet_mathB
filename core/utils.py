# -*- coding: utf-8 -*-
"""
=============================================================================
模組名稱 (Module Name): core/utils.py
功能說明 (Description): 提供與資料庫互動的通用工具函式，包含技能查詢、課綱結構獲取、以及管理技能與課綱關聯的 CRUD 操作。
執行語法 (Usage): 由系統調用
版本資訊 (Version): V2.0
更新日期 (Date): 2026-01-13
維護團隊 (Maintainer): Math AI Project Team
=============================================================================
"""
"""此模組提供與資料庫互動的通用工具函式，包含查詢技能資訊、課綱結構（年級、冊別、章節）以及管理技能與課綱關聯的 CRUD 操作。"""

# core/utils.py （新建檔案）
from sqlalchemy import func
import re
from models import db, SkillInfo, SkillCurriculum
from flask import session  # 補上這行
from sqlalchemy import distinct  # 補上這行

CURRICULUM_DEFINITIONS = [
    {
        "key": "junior_high",
        "label": "國中",
        "order": 1,
        "aliases": ["junior_high", "國中", "junior"]
    },
    {
        "key": "general",
        "label": "普高",
        "order": 2,
        "aliases": ["general", "general_high", "senior_high", "普高", "senior"]
    },
    {
        "key": "vocational",
        "label": "技高",
        "order": 3,
        "aliases": ["vocational", "vocational_high", "technical", "技高"]
    }
]

def normalize_curriculum(value):
    """Normalize curriculum value or alias to canonical code."""
    if not value or value == 'all':
        return value
    val_clean = str(value).strip().lower()
    for item in CURRICULUM_DEFINITIONS:
        if val_clean == item["key"]:
            return item["key"]
        for alias in item["aliases"]:
            if val_clean == alias.strip().lower():
                return item["key"]
    return value

def get_curriculum_label(value):
    """Get Chinese display label for curriculum key or alias."""
    norm = normalize_curriculum(value)
    for item in CURRICULUM_DEFINITIONS:
        if item["key"] == norm:
            return item["label"]
    return value

def get_curriculum_options():
    """Return curriculum definitions sorted by display order."""
    return sorted(CURRICULUM_DEFINITIONS, key=lambda x: x["order"])

def get_curriculum_aliases(canonical_value):
    """Get list of aliases (including the canonical key itself) for a canonical value."""
    for item in CURRICULUM_DEFINITIONS:
        if item["key"] == canonical_value:
            return list(set([item["key"]] + item["aliases"]))
    return [canonical_value]


def get_skill_info(skill_id):
    """從 skills_info 表讀取單一技能資訊"""
    # 使用 ORM 查詢
    skill = SkillInfo.query.filter_by(skill_id=skill_id, is_active=True).first()

    if not skill:
        return None
    
    return {
        'skill_id': skill.skill_id,
        'skill_en_name': skill.skill_en_name,
        'skill_ch_name': skill.skill_ch_name,
        'category': skill.category,
        'description': skill.description,
        'input_type': skill.input_type,
        'gemini_prompt': skill.gemini_prompt,
        'consecutive_correct_required': skill.consecutive_correct_required,
        'is_active': skill.is_active,
        'order_index': skill.order_index
    }

def get_all_active_skills():
    """讀取所有啟用技能，用於 dashboard"""
    # 使用 ORM 查詢
    skills = SkillInfo.query.filter_by(is_active=True).order_by(SkillInfo.order_index).all()
    
    return [{
        'skill_id': s.skill_id,
        'skill_en_name': s.skill_en_name,
        'skill_ch_name': s.skill_ch_name,
        'category': s.category,
        'description': s.description,
        'input_type': s.input_type,
        'consecutive_correct_required': s.consecutive_correct_required,
        'order_index': s.order_index
    } for s in skills]

def get_curriculums():
    """取得所有課綱 (例如: 'general', 'vocational')"""
    # 使用 ORM 查詢，.distinct() 確保唯一性，.all() 取得所有結果
    results = db.session.query(SkillCurriculum.curriculum).distinct().all()
    return [r[0] for r in results]

def get_volumes_by_curriculum(curriculum):
    """根據課綱取得所有冊別，並按年級分組"""
    # 使用 ORM 查詢
    rows = db.session.query(SkillCurriculum.grade, SkillCurriculum.volume)\
                     .filter_by(curriculum=curriculum)\
                     .distinct()\
                     .order_by(SkillCurriculum.grade, SkillCurriculum.display_order)\
                     .all()
    
    grouped_volumes = {}
    for grade, volume in rows:
        if grade not in grouped_volumes:
            grouped_volumes[grade] = []
        if volume not in grouped_volumes[grade]:
            grouped_volumes[grade].append(volume)
    return grouped_volumes

def get_chapters_by_curriculum_volume(curriculum, volume):
    """根據課綱和冊別取得所有章節"""
    # 使用 ORM 查詢
    results = db.session.query(SkillCurriculum.chapter)\
                        .filter_by(curriculum=curriculum, volume=volume)\
                        .distinct()\
                        .all()
    
    chapters = [r[0] for r in results]

    # 定義一個函式來從章節名稱中提取數字
    def extract_chapter_number(chapter_name):
        # 使用正規表示式尋找 "第" 和 "章" 之間的數字
        match = re.search(r'第(\d+)', chapter_name)
        if match:
            return int(match.group(1))
        return float('inf') # 如果找不到數字，排在最後

    # 使用自訂的排序鍵進行排序
    # [Fix] Natural Sorting
    def natural_keys(text):
        if not text: return []
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', str(text))]

    chapters.sort(key=natural_keys)
    
    return chapters

def normalize_vocational_math_skill_id(subject: str, vol_num: str, clean_en_id: str, prefix: str = "vh_") -> str:
    """
    統一技高數學 B 系列的技能 ID 命名規則。
    格式: vh_數學B1_AbsoluteValue
    """
    if subject == 'B':
        # 強制使用中文冊別，例如 vh_數學B1_...
        return f"{prefix}數學{subject}{vol_num}_{clean_en_id}"
    # 其他非 B 系列維持英文 math 前綴
    return f"{prefix}math{subject}{vol_num}_{clean_en_id}"

def format_vocational_b_section_display(chapter_name, section_name):
    """
    技高數學 B 系列專用章節顯示格式化工具。
    規則：
    1. 從 section (例如 1-2 xxx) 提取 Y (2) 作為顯示編號。
    2. 標題移除 chapter 原本的數字前綴。
    3. 自我評量顯示為「【複習】自我評量」。
    """
    if not chapter_name:
        return ""
        
    sec_str = str(section_name or "")
    # 解析小節序號 (例如 1-2 -> 2)
    sec_match = re.search(r'(\d+)-(\d+)', sec_str)
    is_review = 'review' in sec_str.lower() or '自我評量' in sec_str or '1-review' in sec_str
    
    # 清理標題：移除既有的前導數字、空格或「第x章」前綴
    # 例如 "1 數線" -> "數線", "第1章 數線" -> "數線"
    clean_title = re.sub(r'^(第\s*\d+\s*[章單元]|Unit\s*\d+|Chapter\s*\d+|\d+)\s*', '', chapter_name).strip()
    
    if is_review:
        return f"【複習】{clean_title}" if clean_title != '自我評量' else "自我評量"
    elif sec_match:
        # [V2.6修正] 使用 sec_match.group(1) 作為章節編號，並加上「第x章」前綴
        return f"第{sec_match.group(1)}章 {clean_title}"
    else:
        return chapter_name

def get_skills_by_volume_chapter(volume, chapter):
    """取得指定冊、章的所有技能（包含進度）"""
    # 使用 ORM 進行 JOIN 查詢
    # .join() 會根據我們在模型中定義的 ForeignKey 自動關聯
    results = db.session.query(SkillCurriculum, SkillInfo)\
                        .join(SkillInfo)\
                        .filter(SkillCurriculum.volume == volume,
                                SkillCurriculum.chapter == chapter,
                                SkillInfo.is_active == True)\
                        .order_by(SkillCurriculum.display_order)\
                        .all()
    
    return [{
        'curriculum': sc.curriculum,
        'grade': sc.grade,
        'volume': sc.volume,
        'chapter': sc.chapter,
        'section': sc.section,
        'paragraph': sc.paragraph,
        'skill_id': sc.skill_id,
        'display_order': sc.display_order,
        'skill_ch_name': si.skill_ch_name,
        'skill_en_name': si.skill_en_name,
        'description': si.description,
        'consecutive_correct_required': si.consecutive_correct_required
    } for sc, si in results]

def get_all_skill_curriculums():
    """
    取得 SkillCurriculum 表中的所有條目，並 JOIN SkillInfo 以獲取技能名稱。
    這是給 /admin/curriculum 管理頁面使用的。
    """
    results = db.session.query(SkillCurriculum, SkillInfo.skill_ch_name, SkillInfo.difficulty)\
                        .outerjoin(SkillInfo, SkillCurriculum.skill_id == SkillInfo.skill_id)\
                        .order_by(SkillCurriculum.curriculum, SkillCurriculum.grade, SkillCurriculum.display_order)\
                        .all()

    return [{
        'id': sc.id,
        'curriculum': sc.curriculum,
        'grade': sc.grade,
        'volume': sc.volume,
        'chapter': sc.chapter,
        'section': sc.section,
        'paragraph': sc.paragraph,
        'skill_id': sc.skill_id,
        'display_order': sc.display_order,
        'skill_ch_name': skill_ch_name,
        'difficulty': difficulty # 移除此行末尾的逗號
    } for sc, skill_ch_name, difficulty in results] # 修正：將 for 迴圈與 return 對齊

def create_skill_curriculum(data):
    """
    新增一筆 SkillCurriculum 記錄。
    'data' 是一個包含所有必要欄位資訊的字典。
    """
    try:
        new_entry = SkillCurriculum(**data)
        db.session.add(new_entry)
        db.session.commit()
        return {'success': True, 'message': '記錄新增成功。', 'id': new_entry.id}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤，但只回傳通用訊息給前端
        print(f"Create Error: {e}")
        return {'success': False, 'message': '新增失敗，請檢查資料格式或聯繫管理員。'}

def update_skill_curriculum(entry_id, data):
    """
    更新一筆指定 id 的 SkillCurriculum 記錄。
    'data' 是一個包含要更新欄位資訊的字典。
    """
    try:
        entry = SkillCurriculum.query.get(entry_id)
        if not entry:
            return {'success': False, 'message': '找不到指定的記錄。'}
        
        for key, value in data.items():
            setattr(entry, key, value)
            
        db.session.commit()
        return {'success': True, 'message': '記錄更新成功。'}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤
        print(f"Update Error: {e}")
        return {'success': False, 'message': '更新失敗，請檢查資料或聯繫管理員。'}

def delete_skill_curriculum(entry_id):
    """
    刪除一筆指定 id 的 SkillCurriculum 記錄。
    """
    try:
        entry = SkillCurriculum.query.get(entry_id)
        if not entry:
            return {'success': False, 'message': '找不到指定的記錄。'}
        
        db.session.delete(entry)
        db.session.commit()
        return {'success': True, 'message': '記錄刪除成功。'}
    except Exception as e:
        db.session.rollback()
        # 記錄詳細錯誤
        print(f"Delete Error: {e}")
        return {'success': False, 'message': '刪除失敗，可能有關聯資料，請聯繫管理員。'}

def to_superscript(n):
    """將整數轉換為上標字串。"""
    superscript_map = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹", "-": "⁻"
    }
    return "".join(superscript_map.get(char, char) for char in str(n))

def handle_curriculum_filters(request):
    """
    通用五層連動過濾器邏輯 (V2.0 模組化版)
    功能：自動處理網址參數、Session 記憶、以及動態選項產生。
    """
    # 1. 取得五層篩選值 (優先順序：網址參數 > Session 記憶 > 預設 'all')
    raw_curr = request.args.get('f_curriculum') or session.get('last_f_curr', 'all')
    f_curr = normalize_curriculum(raw_curr)
    f_grade = request.args.get('f_grade') or session.get('last_f_grade', 'all')
    f_vol = request.args.get('f_volume') or session.get('last_f_vol', 'all')
    f_chap = request.args.get('f_chapter') or session.get('last_f_chap', 'all')
    f_sec = request.args.get('f_section') or session.get('last_f_sec', 'all')
    
    # 2. 更新 Session 記憶，供單筆編輯後回復狀態
    session.update({
        'last_f_curr': f_curr, 'last_f_grade': f_grade,
        'last_f_vol': f_vol, 'last_f_chap': f_chap, 'last_f_sec': f_sec
    })

    # 3. 動態產生下拉選單選項 (五層連動邏輯)
    filters = {}
    
    # A. 課綱 - 使用統一權威定義的順序
    filters['curriculums'] = [opt['key'] for opt in get_curriculum_options()]

    # B. 年級 (依據課綱)
    g_q = db.session.query(distinct(SkillCurriculum.grade)).filter(SkillCurriculum.grade != None)
    if f_curr != 'all':
        aliases = get_curriculum_aliases(f_curr)
        g_q = g_q.filter(SkillCurriculum.curriculum.in_(aliases))
    filters['grades'] = sorted([r[0] for r in g_q.all()])

    # C. 冊別 (依據課綱+年級)
    v_q = db.session.query(distinct(SkillCurriculum.volume))
    if f_curr != 'all':
        aliases = get_curriculum_aliases(f_curr)
        v_q = v_q.filter(SkillCurriculum.curriculum.in_(aliases))
    if f_grade != 'all' and str(f_grade).isdigit(): v_q = v_q.filter(SkillCurriculum.grade == int(f_grade))
    filters['volumes'] = [r[0] for r in v_q.all()]

    # D. 章節 (依據前三層)
    c_q = db.session.query(distinct(SkillCurriculum.chapter))
    if f_curr != 'all':
        aliases = get_curriculum_aliases(f_curr)
        c_q = c_q.filter(SkillCurriculum.curriculum.in_(aliases))
    if f_grade != 'all' and str(f_grade).isdigit(): c_q = c_q.filter(SkillCurriculum.grade == int(f_grade))
    if f_vol != 'all': c_q = c_q.filter(SkillCurriculum.volume == f_vol)
    filters['chapters'] = [r[0] for r in c_q.all()]

    # E. 節 (依據前四層)
    s_q = db.session.query(distinct(SkillCurriculum.section))
    if f_curr != 'all':
        aliases = get_curriculum_aliases(f_curr)
        s_q = s_q.filter(SkillCurriculum.curriculum.in_(aliases))
    if f_grade != 'all' and str(f_grade).isdigit(): s_q = s_q.filter(SkillCurriculum.grade == int(f_grade))
    if f_vol != 'all': s_q = s_q.filter(SkillCurriculum.volume == f_vol)
    if f_chap != 'all': s_q = s_q.filter(SkillCurriculum.chapter == f_chap)
    filters['sections'] = [r[0] for r in s_q.all()]

    # [V2.0] 技高 B 系列標題格式化映射 (供下拉選單顯示使用)
    filters['chapter_labels'] = {}
    if f_curr == 'vocational' and f_vol != 'all' and 'B' in str(f_vol):
        for ch in filters['chapters']:
            aliases = get_curriculum_aliases(f_curr)
            rep = SkillCurriculum.query.filter(
                SkillCurriculum.curriculum.in_(aliases),
                SkillCurriculum.volume == f_vol,
                SkillCurriculum.chapter == ch
            ).order_by(SkillCurriculum.display_order).first()
            filters['chapter_labels'][ch] = format_vocational_b_section_display(ch, rep.section if rep else "")

    selected = {'f_curriculum': f_curr, 'f_grade': f_grade, 'f_volume': f_vol, 'f_chapter': f_chap, 'f_section': f_sec}
    
    return selected, filters