import sys
import traceback
from app import app, db
from models import SkillInfo, SkillCurriculum, TextbookExample

def main():
    print("====== 啟動 skills_info / SkillCurriculum 唯讀診斷雷達 ======")
    
    with app.app_context():
        try:
            # 撈出前 30 個技能做深度診斷
            skills = db.session.query(SkillInfo).limit(30).all()
            print(f"[*] 已載入前 {len(skills)} 個技能進行深入 ORM 與欄位匹配探針測試...\n")
            
            for skill in skills:
                sid = skill.skill_id
                print(f"--------------------------------------------------")
                print(f"[TARGET SKILL] {sid}")
                
                # --- Probe 2: 關係鏈空轉盲區檢測 ---
                curr_entries = getattr(skill, 'curriculum_entries', None)
                relation_len = len(curr_entries) if curr_entries is not None else -1
                print(f"[PROBE RELATION] Skill:{sid} | len(curriculum_entries) = {relation_len}")
                
                # --- Probe 3: 獨立 query 命中測試 ---
                direct_rows = db.session.query(SkillCurriculum).filter_by(skill_id=sid).all()
                print(f"[DIRECT QUERY] Filter by skill_id={sid} | Found count = {len(direct_rows)}")
                for row in direct_rows:
                    print(f"  -> [CURRICULUM ROW] id={row.id} | curriculum={row.curriculum} | chapter='{row.chapter}' | section='{row.section}' | display_order={row.display_order}")
                
                # --- Probe 1: 小節文字匹配與空格盲區檢測 ---
                # 撈出該技能對應的例題紀錄
                examples = db.session.query(TextbookExample).filter_by(skill_id=sid).all()
                print(f"[EXAMPLES FOUND] Count = {len(examples)} for skill_id={sid}")
                
                # 比對大綱表中的 section 與例題表中的 source_section 字串是否完全一致
                if direct_rows and examples:
                    for row in direct_rows:
                        sec_a = row.section
                        for ex in examples:
                            sec_b = ex.source_section
                            match_status = "MATCH!" if sec_a == sec_b else "MISMATCH!"
                            # 印出可見的空格標記與洗淨前後的對比
                            visible_a = sec_a.replace(" ", "·") if sec_a else "None"
                            visible_b = sec_b.replace(" ", "·") if sec_b else "None"
                            print(f"  -> [PROBE STRING] Skill:{sid} | "
                                  f"Outline section='{visible_a}' | "
                                  f"Example section='{visible_b}' | "
                                  f"Status={match_status}")
                elif not examples:
                    print(f"  -> [PROBE STRING] Warning: No textbook examples found for skill_id={sid} (Fallback to 9999)")
                elif not direct_rows:
                    print(f"  -> [PROBE STRING] Warning: No curriculum outline records found for skill_id={sid}")
            
            print("\n====== 診斷探針執行完畢 ======")
            
        except Exception as exc:
            print(f"\n[ERROR] 診斷過程中發生異常：{exc}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

if __name__ == '__main__':
    main()
