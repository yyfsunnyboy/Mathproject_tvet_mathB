import sys
import os
from sqlalchemy import text

# Ensure we can import app and models
sys.path.append(os.getcwd())

from app import app
from models import db

def check_consistency():
    with app.app_context():
        print("| issue_type | skill_id | table | notes |")
        print("|---|---|---|---|")
        
        # 1. TextbookExample without SkillInfo
        query = text("""
            SELECT te.skill_id, te.id 
            FROM textbook_examples te 
            LEFT JOIN skills_info si ON te.skill_id = si.skill_id 
            WHERE si.skill_id IS NULL AND te.skill_id LIKE 'vh_%'
        """)
        results = db.session.execute(query).fetchall()
        for skill_id, ex_id in results:
            print(f"| Missing SkillInfo | {skill_id} | textbook_examples | example_id: {ex_id} |")
            
        # 2. SkillCurriculum without SkillInfo
        query = text("""
            SELECT sc.skill_id 
            FROM skill_curriculum sc 
            LEFT JOIN skills_info si ON sc.skill_id = si.skill_id 
            WHERE si.skill_id IS NULL AND sc.skill_id LIKE 'vh_%'
        """)
        results = db.session.execute(query).fetchall()
        for row in results:
            print(f"| Missing SkillInfo | {row[0]} | skill_curriculum | |")
            
        # 3. Duplicate skills with different prefixes
        # Find if any skill exists with both prefixes (ignoring the prefix part)
        query = text("""
            SELECT REPLACE(si1.skill_id, 'vh_mathB1_', '') as base_id, 
                   si1.skill_id as old_id, si2.skill_id as new_id
            FROM skills_info si1
            JOIN skills_info si2 ON REPLACE(si1.skill_id, 'vh_mathB1_', '') = REPLACE(si2.skill_id, 'vh_數學B1_', '')
            WHERE si1.skill_id LIKE 'vh_mathB1_%' AND si2.skill_id LIKE 'vh_數學B1_%'
        """)
        results = db.session.execute(query).fetchall()
        for base_id, old_id, new_id in results:
            print(f"| Duplicate ID | {old_id} / {new_id} | skills_info | Same base: {base_id} |")

if __name__ == "__main__":
    check_consistency()
