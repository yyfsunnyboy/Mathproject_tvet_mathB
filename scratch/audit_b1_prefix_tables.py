import sys
import os
from sqlalchemy import text

# Ensure we can import app and models
sys.path.append(os.getcwd())

from app import app
from models import db

TABLES_TO_CHECK = [
    "skills_info",
    "skill_curriculum",
    "textbook_examples",
    "skill_prerequisites",
    "skill_gencode_prompt",
    "experiment_log",
    "execution_samples",
    "progress",
    "skill_family_bridge",
    "adaptive_learning_logs",
    "mistake_logs",
    "mistake_notebook_entries",
    "questions",
    "student_abilities",
    "exam_analysis",
    "b4_chap2_visibility_audit_logs"
]

def audit_b1_prefixes():
    with app.app_context():
        print("| table/model | old_prefix_count vh_mathB1_* | new_prefix_count vh_數學B1_* | notes |")
        print("|---|---|---|---|")
        
        for table in TABLES_TO_CHECK:
            # Check if table exists
            try:
                # Find columns that might contain skill_id
                # Usually it's skill_id or prerequisite_id
                cols = []
                if table == "skill_prerequisites":
                    cols = ["skill_id", "prerequisite_id"]
                else:
                    cols = ["skill_id"]
                
                for col in cols:
                    old_count = db.session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE {col} LIKE 'vh_mathB1_%'")).scalar()
                    new_count = db.session.execute(text(f"SELECT COUNT(*) FROM {table} WHERE {col} LIKE 'vh_數學B1_%'")).scalar()
                    
                    col_note = f" (col: {col})" if len(cols) > 1 else ""
                    print(f"| {table}{col_note} | {old_count} | {new_count} | |")
            except Exception as e:
                if "no such table" in str(e).lower():
                    # print(f"| {table} | N/A | N/A | Table not found |")
                    continue
                else:
                    print(f"| {table} | ERROR | ERROR | {str(e)[:50]} |")

if __name__ == "__main__":
    audit_b1_prefixes()
