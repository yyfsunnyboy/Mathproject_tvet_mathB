from app import app
from models import SkillCurriculum

def audit_b4():
    with app.app_context():
        rows = SkillCurriculum.query.filter_by(curriculum='vocational', volume='數學B4').all()
        print(f"{'skill_id':<45} | {'chapter':<20} | {'section':<30} | {'display_order'}")
        print("-" * 110)
        # Group by chapter to see how they are structured
        chapters = {}
        for r in rows:
            if r.chapter not in chapters:
                chapters[r.chapter] = []
            chapters[r.chapter].append(r)
        
        for ch in sorted(chapters.keys()):
            print(f"\nChapter: {ch}")
            for r in chapters[ch][:3]: # show first 3 per chapter
                 print(f"  {r.skill_id:<45} | {r.section:<30} | {r.display_order}")

if __name__ == "__main__":
    audit_b4()
