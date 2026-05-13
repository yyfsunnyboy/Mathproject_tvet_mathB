import sys
import os
sys.path.append(os.getcwd())
from app import app
from models import SkillInfo, SkillCurriculum

def list_all():
    with app.app_context():
        print("--- SkillInfo ---")
        skills = SkillInfo.query.all()
        for s in skills:
            print(f"{s.skill_id} | {s.skill_ch_name}")
            
        print("\n--- SkillCurriculum ---")
        items = SkillCurriculum.query.all()
        for i in items:
            print(f"{i.skill_id} | {i.chapter} | {i.section}")

if __name__ == "__main__":
    list_all()
