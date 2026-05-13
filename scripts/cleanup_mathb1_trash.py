# -*- coding: utf-8 -*-
import sys
import os

# Ensure project root is in sys.path
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from models import db, SkillCurriculum

def cleanup_trash_nodes():
    app = create_app()
    with app.app_context():
        print("Starting cleanup of trash nodes in B1...")
        
        # 刪除包含 '1-1_-' 或 '1_-' 的節點
        trash_patterns = ['%1-1_-%', '%1_-%']
        
        deleted_count = 0
        for pattern in trash_patterns:
            result = SkillCurriculum.query.filter(
                SkillCurriculum.volume == '數學B1',
                (SkillCurriculum.section.like(pattern)) | (SkillCurriculum.chapter.like(pattern))
            ).all()
            
            for item in result:
                print(f"Deleting trash node: {item.chapter} / {item.section}")
                db.session.delete(item)
                deleted_count += 1
        
        # 額外檢查：如果 chapter 或 section 為 None 或 只有標點符號的
        result_empty = SkillCurriculum.query.filter(
            SkillCurriculum.volume == '數學B1',
            (SkillCurriculum.section == '') | (SkillCurriculum.chapter == '')
        ).all()
        for item in result_empty:
            print(f"Deleting empty node: {item.chapter} / {item.section}")
            db.session.delete(item)
            deleted_count += 1

        db.session.commit()
        print(f"Cleanup finished. Total deleted: {deleted_count}")

if __name__ == "__main__":
    cleanup_trash_nodes()
