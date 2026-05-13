from app import app
from models import SkillCurriculum

def audit_b1_curriculum():
    with app.app_context():
        rows = SkillCurriculum.query.filter_by(curriculum='vocational', volume='數學B1').all()
        print(f"{'skill_id':<45} | {'chapter':<20} | {'section':<30} | {'display_order'}")
        print("-" * 110)
        for r in rows:
            print(f"{r.skill_id:<45} | {str(r.chapter):<20} | {str(r.section):<30} | {r.display_order}")

if __name__ == "__main__":
    audit_b1_curriculum()
