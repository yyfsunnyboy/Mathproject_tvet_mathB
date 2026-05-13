import sys
import os

# Ensure we can import app and models
sys.path.append(os.getcwd())

from app import app
from models import db, SkillInfo

def list_b1_skills():
    with app.app_context():
        print("skill_id | skill_ch_name")
        print("-" * 50)
        skills = SkillInfo.query.filter(
            (SkillInfo.skill_id.like('vh_mathB1_%')) | 
            (SkillInfo.skill_id.like('vh_數學B1_%'))
        ).all()
        for s in skills:
            print(f"{s.skill_id} | {s.skill_ch_name}")

if __name__ == "__main__":
    list_b1_skills()
