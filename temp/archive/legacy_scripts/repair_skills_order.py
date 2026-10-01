import re
import sys
from app import app, db
from models import SkillInfo, SkillCurriculum, TextbookExample

def main():
    print("====== 啟動 skills_info 唯讀排錯診查雷達 (Read-only Debugging) ======")
    
    with app.app_context():
        try:
            # 1. 撈出所有技能進行診斷
            skills = db.session.query(SkillInfo).all()
            print(f"[*] 自資料庫中撈出 {len(skills)} 個技能進行關聯寫入斷鏈排查...\n")
            
            for skill in skills:
                skill_id = skill.skill_id
                print(f"\n==========================================")
                print(f"[DIAGNOSING SKILL] {skill_id}")
                
                # --- 1. 檢查【關係鏈是否為空 (Empty Relationship Check)】 ---
                # 為了避免 AttributeError，動態取得 section 或給予 'N/A'
                skill.section = skill.curriculum_entries[0].section if skill.curriculum_entries else "N/A"
                print(f"[PROBE RELATION] Skill:{skill_id} says Section='{skill.section}' | len(curriculum_entries) = {len(skill.curriculum_entries)}")
                
                # --- 2. 檢查【直接 SQL 查詢比對測試 (Direct Query Mapping Test)】 ---
                # 改用直連 Query 方式，不要透過 ORM 關係鏈
                direct_rows = db.session.query(SkillCurriculum).filter_by(skill_id=skill_id).all()
                print(f"[DIRECT QUERY] Filter by skill_id={skill_id} | Found count = {len(direct_rows)}")
                for row in direct_rows:
                    print(f"  -> [CURRICULUM ROW] id={row.id} | curriculum={row.curriculum} | chapter='{row.chapter}' | section='{row.section}' | display_order={row.display_order}")
                    
                    # 依據條件精確查詢測試
                    matching_entries = db.session.query(SkillCurriculum).filter_by(
                        skill_id=skill_id,
                        chapter=row.chapter,
                        section=row.section
                    ).all()
                    print(f"     -> [EXACT DIRECT QUERY] Matching entries = {len(matching_entries)}")
                
                if len(direct_rows) > 0 and len(skill.curriculum_entries) == 0:
                    print(f"[!] WARNING: ORM relationship mismatch! Direct query found {len(direct_rows)} rows but relationship is empty!")
                
                # --- 3. 檢查【小節字串匹配盲區 (String Space Trap)】 ---
                # 獲取關聯例題
                examples = skill.textbook_examples
                print(f"[EXAMPLES] Count = {len(examples)} for skill_id={skill_id}")
                
                for outline in direct_rows:
                    for example in examples:
                        # 動態將 example.source_section 映射至 example.section 以符合模板要求
                        example.section = example.source_section
                        match_status = "MATCH!" if outline.section == example.section else "MISMATCH!"
                        print(f"[PROBE STRING] Outline section='{outline.section}' vs Example section='{example.section}' | Status={match_status}")
            
            print("\n====== 唯讀診斷雷達執行完畢 ======")
            
        except Exception as exc:
            import traceback
            print(f"\n[ERROR] 診斷過程中發生異常：{exc}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

if __name__ == '__main__':
    main()
