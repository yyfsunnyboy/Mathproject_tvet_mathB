# -*- coding: utf-8 -*-
import sys
import os

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if basedir not in sys.path:
    sys.path.insert(0, basedir)

from app import create_app
from models import db, TextbookExample, SkillInfo, SkillCurriculum

app = create_app()
with app.app_context():
    # Let's count TextbookExample total:
    total_examples = db.session.query(TextbookExample).count()
    print(f"Total TextbookExample: {total_examples}")

    # Let's count examples matching the specific filter using the original query structure (inner join with SkillInfo):
    query_orig = db.session.query(TextbookExample).join(SkillInfo).join(SkillCurriculum)
    query_orig = query_orig.filter(
        SkillCurriculum.curriculum == 'vocational',
        SkillCurriculum.grade == 10,
        SkillCurriculum.volume == '數學B1',
        SkillCurriculum.chapter == '1 坐標系與函數圖形',
        SkillCurriculum.section == '1-1 數線與絕對值'
    )
    print(f"Original query (inner join SkillInfo) count: {query_orig.count()}")

    # Let's count using the proposed outer join structure:
    query_outer = db.session.query(TextbookExample).outerjoin(SkillInfo, TextbookExample.skill_id == SkillInfo.skill_id).join(SkillCurriculum, TextbookExample.skill_id == SkillCurriculum.skill_id)
    query_outer = query_outer.filter(
        SkillCurriculum.curriculum == 'vocational',
        SkillCurriculum.grade == 10,
        SkillCurriculum.volume == '數學B1',
        SkillCurriculum.chapter == '1 坐標系與函數圖形',
        SkillCurriculum.section == '1-1 數線與絕對值'
    )
    print(f"Proposed query (outer join SkillInfo) count: {query_outer.count()}")
    
    # Print first few elements from outer join to see what they are:
    results = query_outer.limit(5).all()
    for ex in results:
        print(f"ID: {ex.id}, skill_id: {ex.skill_id}, has_skill_info: {ex.skill_info is not None}")
