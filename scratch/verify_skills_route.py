import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import app, db
from models import SkillInfo, SkillCurriculum

def main():
    print("====== 驗證 /skills 查詢與排序 ======")
    with app.app_context():
        # 模擬 URL 篩選參數
        selected = {
            'f_curriculum': 'vocational',
            'f_grade': '10',
            'f_volume': '數學B1',
            'f_chapter': '2 直線方程式',
            'f_section': '2-1 斜率'
        }
        
        # 複刻後端修改後的 query 邏輯
        query = db.session.query(SkillInfo, SkillCurriculum).join(
            SkillCurriculum,
            SkillInfo.skill_id == SkillCurriculum.skill_id
        )
        
        if selected['f_curriculum'] != 'all': 
            query = query.filter(SkillCurriculum.curriculum == selected['f_curriculum'])
        if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit(): 
            query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
        if selected['f_volume'] != 'all':
            query = query.filter(SkillCurriculum.volume == selected['f_volume'])
        if selected['f_chapter'] != 'all': 
            query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])
        if selected['f_section'] != 'all': 
            query = query.filter(SkillCurriculum.section == selected['f_section'])
            
        skills_data = (
            query
            .distinct()
            .order_by(
                SkillCurriculum.display_order.asc(),
                SkillInfo.skill_id.asc()
            )
            .all()
        )
        
        print(f"1. 查詢結果筆數 (len): {len(skills_data)}")
        
        if len(skills_data) > 0:
            first_item = skills_data[0]
            print(f"2. 第一筆是否為 tuple: {isinstance(first_item, tuple)}")
            if isinstance(first_item, tuple):
                print(f"3. 元組長度是否為 2: {len(first_item) == 2}")
                print(f"4. 元素[0]是否為 SkillInfo: {isinstance(first_item[0], SkillInfo)}")
                print(f"5. 元素[1]是否為 SkillCurriculum: {isinstance(first_item[1], SkillCurriculum)}")
                
            print("\n6. 詳細排序清單：")
            for idx, (skill_info, curriculum) in enumerate(skills_data, 1):
                print(f"   [{idx}] display_order={curriculum.display_order} | skill_id={skill_info.skill_id} | name={skill_info.skill_ch_name}")
        else:
            print("沒有找到符合條件的技能資料！")
            
if __name__ == '__main__':
    main()
