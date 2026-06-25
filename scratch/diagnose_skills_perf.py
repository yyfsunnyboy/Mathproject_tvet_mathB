import sys
import time
import os
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app
from models import db, SkillInfo, SkillCurriculum

# Create app once
app = create_app()

def run_diagnose_compare():
    with app.app_context():
        # Get vocational skills (a subset of skills to make test fast but realistic)
        from core.utils import handle_curriculum_filters, get_curriculum_aliases
        from flask import request
        
        with app.test_request_context(query_string={'f_curriculum': 'vocational'}):
            selected, filters_data = handle_curriculum_filters(request)
            aliases = get_curriculum_aliases(selected['f_curriculum'])
            skills_data = (
                db.session.query(SkillInfo, SkillCurriculum)
                .join(SkillCurriculum, SkillInfo.skill_id == SkillCurriculum.skill_id)
                .filter(SkillCurriculum.curriculum.in_(aliases))
                .distinct()
                .all()
            )
            skills = [s[0].skill_id for s in skills_data]
            print(f"Number of vocational skills to profile: {len(skills)}")
            
            # 1. Profile with audit_skill_variation enabled (limited to 5 skills to avoid hanging forever)
            subset = skills[:3]
            print(f"Profiling first {len(subset)} skills WITH audit_skill_variation:")
            t0 = time.time()
            from core.routes.admin import _load_skills_v3_gencode_status_map
            res1 = _load_skills_v3_gencode_status_map(subset)
            t1 = time.time()
            print(f"  Time taken for {len(subset)} skills: {t1 - t0:.4f}s")
            
            # 2. Profile WITH audit_skill_variation mocked/bypassed (for all vocational skills)
            print(f"Profiling ALL {len(skills)} skills WITH audit_skill_variation BYPASSED:")
            with patch("core.gencode.services.v3_variation_audit_service.audit_skill_variation", return_value={}):
                t0 = time.time()
                res2 = _load_skills_v3_gencode_status_map(skills)
                t1 = time.time()
                print(f"  Time taken for ALL {len(skills)} skills: {t1 - t0:.4f}s (Result size: {len(res2)})")

if __name__ == '__main__':
    run_diagnose_compare()
