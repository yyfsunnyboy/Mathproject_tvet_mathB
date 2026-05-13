from app import app
from models import SkillCurriculum

def audit_b1_full():
    with app.app_context():
        rows = SkillCurriculum.query.filter_by(curriculum='vocational', volume='數學B1').all()
        print(f"{'skill_id':<45} | {'chapter':<25} | {'section':<35} | {'display_order'}")
        print("-" * 120)
        for r in rows:
            print(f"{r.skill_id:<45} | {str(r.chapter):<25} | {str(r.section):<35} | {r.display_order}")

if __name__ == "__main__":
    audit_b1_full()
