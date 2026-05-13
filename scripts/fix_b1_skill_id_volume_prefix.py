import sys
import os
import argparse
from sqlalchemy import text

# Ensure we can import app and models
sys.path.append(os.getcwd())

from app import app
from models import db, SkillInfo, SkillCurriculum, TextbookExample

TARGETS = [
    ("skills_info", "skill_id"),
    ("skill_curriculum", "skill_id"),
    ("textbook_examples", "skill_id"),
    ("skill_prerequisites", "skill_id"),
    ("skill_prerequisites", "prerequisite_id"),
    ("skill_gencode_prompt", "skill_id"),
    ("experiment_log", "skill_id"),
    ("execution_samples", "skill_id"),
    ("progress", "skill_id"),
    ("skill_family_bridge", "skill_id"),
    ("mistake_logs", "skill_id"),
    ("mistake_notebook_entries", "skill_id"),
    ("questions", "skill_id"),
    ("student_abilities", "skill_id"),
    ("exam_analysis", "skill_id"),
    ("b4_chap2_visibility_audit_logs", "skill_id")
]

def fix_b1_prefixes(dry_run=True):
    with app.app_context():
        print(f"--- B1 skill_id Prefix Fix ({'DRY RUN' if dry_run else 'APPLY'}) ---")
        
        # 1. Identify all old IDs
        old_ids_query = text("SELECT DISTINCT skill_id FROM skills_info WHERE skill_id LIKE 'vh_mathB1_%'")
        old_ids = [r[0] for r in db.session.execute(old_ids_query).fetchall()]
        
        # Also check other tables for old IDs that might not be in skills_info
        for table, col in TARGETS:
            try:
                q = text(f"SELECT DISTINCT {col} FROM {table} WHERE {col} LIKE 'vh_mathB1_%'")
                ids = [r[0] for r in db.session.execute(q).fetchall()]
                for i in ids:
                    if i not in old_ids:
                        old_ids.append(i)
            except:
                continue

        if not old_ids:
            print("No vh_mathB1_* IDs found.")
            return

        print(f"Found {len(old_ids)} unique old IDs.")

        total_affected = 0
        report = []

        for old_id in old_ids:
            new_id = old_id.replace("vh_mathB1_", "vh_數學B1_")
            
            # Check if new_id already exists in skills_info
            new_exists = db.session.query(SkillInfo).filter_by(skill_id=new_id).first() is not None
            
            for table, col in TARGETS:
                try:
                    count_query = text(f"SELECT COUNT(*) FROM {table} WHERE {col} = :old_id")
                    count = db.session.execute(count_query, {"old_id": old_id}).scalar()
                    
                    if count > 0:
                        if table == "skills_info" and new_exists:
                            # If we are in skills_info and new_id already exists, we should merge or skip
                            # Usually, we don't want two SkillInfo for the same skill.
                            # We'll skip updating the record in skills_info but update references in other tables.
                            report.append(f"[SKIP] {table}.{col}: {old_id} (new_id exists, will merge references)")
                            if not dry_run:
                                # Delete the old SkillInfo as we are merging
                                delete_query = text(f"DELETE FROM {table} WHERE {col} = :old_id")
                                db.session.execute(delete_query, {"old_id": old_id})
                        else:
                            if not dry_run:
                                update_query = text(f"UPDATE {table} SET {col} = :new_id WHERE {col} = :old_id")
                                db.session.execute(update_query, {"new_id": new_id, "old_id": old_id})
                                report.append(f"[UPDATE] {table}.{col}: {old_id} -> {new_id} ({count} rows)")
                            else:
                                report.append(f"[MATCH] {table}.{col}: {old_id} -> {new_id} ({count} rows)")
                            total_affected += count
                except Exception as e:
                    if "no such table" in str(e).lower(): continue
                    print(f"Error processing {table}.{col} for {old_id}: {e}")

        if not dry_run:
            db.session.commit()
            print("\nDatabase changes committed.")
        else:
            print("\nDry run completed. No changes made.")

        for line in report:
            print(line)
        print(f"\nTotal affected rows: {total_affected}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix B1 skill_id volume prefix.")
    parser.add_argument("--apply", action="store_true", help="Apply changes to database.")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying.")
    
    args = parser.parse_args()
    is_dry_run = not args.apply
    fix_b1_prefixes(dry_run=is_dry_run)
