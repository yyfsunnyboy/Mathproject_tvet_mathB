import sys
import os
sys.path.append(os.getcwd())
from app import app
from models import SkillCurriculum

def list_curriculum():
    with app.app_context():
        print("chapter | section")
        print("-" * 50)
        items = SkillCurriculum.query.all()
        for i in items:
            print(f"{i.chapter} | {i.section}")

if __name__ == "__main__":
    list_curriculum()
