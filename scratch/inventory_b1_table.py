import re
from app import app
from models import SkillCurriculum

def inventory_b1():
    with app.app_context():
        rows = SkillCurriculum.query.filter_by(curriculum='vocational', volume='數學B1').all()
        print("| skill_id | chapter | section | parsed_section_code | display_order | display_title |")
        print("|---|---|---|---|---|---|")
        for r in rows:
            sec_str = str(r.section or "")
            sec_match = re.search(r'(\d+)-(\d+)', sec_str)
            parsed_code = sec_match.group(0) if sec_match else "null"
            
            # Simulate display title logic from app.py
            display_name = str(r.chapter or "")
            clean_title = re.sub(r'^\d+\s*', '', display_name).strip()
            if 'review' in sec_str.lower() or '自我評量' in sec_str:
                display_title = f"【複習】{clean_title}"
            elif sec_match:
                display_title = f"{sec_match.group(2)} {clean_title}"
            else:
                display_title = display_name
                
            print(f"| {r.skill_id} | {r.chapter} | {r.section} | {parsed_code} | {r.display_order} | {display_title} |")

if __name__ == "__main__":
    inventory_b1()
