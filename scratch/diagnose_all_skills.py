import sys
import time
import os
from pathlib import Path
from sqlalchemy import event
from sqlalchemy.engine import Engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Setup SQLAlchemy query counter globally on Engine class
query_count = 0
query_times = []

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    global query_count
    query_count += 1
    total = time.time() - conn.info['query_start_time'].pop(-1)
    query_times.append(total)

from app import create_app
from models import db, SkillInfo, SkillCurriculum

# Create app once
app = create_app()

def run_diagnose_full():
    global query_count, query_times
    query_count = 0
    query_times = []
    
    with app.app_context():
        print(f"\n--- Diagnostic Run for all skills (f_curriculum=all or empty) ---")
        
        # Phase 1: Parse filters (simulated)
        from core.utils import handle_curriculum_filters, get_curriculum_aliases
        from flask import request
        
        with app.test_request_context(query_string={}):
            t_parse_start = time.time()
            selected, filters_data = handle_curriculum_filters(request)
            t_parse_end = time.time()
            print(f"Phase 1: handle_curriculum_filters: {t_parse_end - t_parse_start:.4f}s")
            
            # Phase 2: Main skill query
            t_query_start = time.time()
            query = db.session.query(SkillInfo, SkillCurriculum).join(
                SkillCurriculum,
                SkillInfo.skill_id == SkillCurriculum.skill_id
            )
            
            if selected['f_curriculum'] != 'all': 
                aliases = get_curriculum_aliases(selected['f_curriculum'])
                query = query.filter(SkillCurriculum.curriculum.in_(aliases))
            if selected['f_grade'] != 'all' and str(selected['f_grade']).isdigit(): 
                query = query.filter(SkillCurriculum.grade == int(selected['f_grade']))
            if selected['f_volume'] != 'all':
                query = query.filter(SkillCurriculum.volume == selected['f_volume'])
            if selected['f_chapter'] != 'all': 
                query = query.filter(SkillCurriculum.chapter == selected['f_chapter'])
            if selected['f_section'] != 'all': 
                query = query.filter(SkillCurriculum.section == selected['f_section'])
            
            skills_data = (
                query
                .distinct()
                .order_by(
                    SkillCurriculum.display_order.asc(),
                    SkillInfo.skill_id.asc()
                )
                .all()
            )
            t_query_end = time.time()
            print(f"Phase 2: Main skill query executed: {t_query_end - t_query_start:.4f}s. Result count: {len(skills_data)}")
            
            # Phase 3: Compilation of skills dictionary
            t_compile_start = time.time()
            skills = []
            for skill_info, curriculum in skills_data:
                skills.append({
                    "skill_id": skill_info.skill_id,
                    "skill_en_name": skill_info.skill_en_name,
                    "skill_ch_name": skill_info.skill_ch_name,
                    "category": skill_info.category,
                    "description": skill_info.description,
                    "input_type": skill_info.input_type,
                    "gemini_prompt": skill_info.gemini_prompt,
                    "consecutive_correct_required": skill_info.consecutive_correct_required,
                    "is_active": skill_info.is_active,
                    "order_index": skill_info.order_index,
                    "display_order": curriculum.display_order,
                    "suggested_prompt_1": skill_info.suggested_prompt_1,
                    "suggested_prompt_2": skill_info.suggested_prompt_2,
                    "suggested_prompt_3": skill_info.suggested_prompt_3,
                    "curriculum": curriculum.curriculum,
                    "grade": curriculum.grade,
                    "volume": curriculum.volume,
                    "chapter": curriculum.chapter,
                    "section": curriculum.section,
                })
            t_compile_end = time.time()
            print(f"Phase 3: Compiling skills dict: {t_compile_end - t_compile_start:.4f}s")
            
            # Phase 4: gencode_status_map (V2)
            t_status_start = time.time()
            gencode_status_map = {}
            root_candidates = [
                Path(app.root_path),
                Path(app.root_path).parent,
                Path(app.root_path).parent.parent,
            ]
            project_root = next(
                (p for p in root_candidates if (p / "skills").exists()),
                Path(app.root_path),
            )
            skills_dir = project_root / "skills"
            drafts_dir = project_root / "reports" / "gencode_closed_loop" / "drafts"
            for s in skills:
                sid = str(s["skill_id"])
                formal_rel = f"skills/{sid}.py"
                draft_rel = f"reports/gencode_closed_loop/drafts/{sid}.py"
                formal_abs = skills_dir / f"{sid}.py"
                draft_abs = drafts_dir / f"{sid}.py"
                formal_exists = formal_abs.exists()
                draft_exists = draft_abs.exists()
                if formal_exists:
                    gencode_status_map[sid] = {
                        "status": "generated",
                        "label": "已產生",
                        "button_label": "重新產生",
                        "formal_exists": True,
                        "draft_exists": draft_exists,
                        "formal_path": formal_rel,
                        "draft_path": draft_rel if draft_exists else "",
                        "formal_abs_path": str(formal_abs),
                        "draft_abs_path": str(draft_abs) if draft_exists else "",
                    }
                elif draft_exists:
                    gencode_status_map[sid] = {
                        "status": "draft",
                        "label": "草稿中",
                        "button_label": "繼續",
                        "formal_exists": False,
                        "draft_exists": True,
                        "formal_path": formal_rel,
                        "draft_path": draft_rel,
                        "formal_abs_path": str(formal_abs),
                        "draft_abs_path": str(draft_abs),
                    }
                else:
                    gencode_status_map[sid] = {
                        "status": "missing",
                        "label": "未產生",
                        "button_label": "AI 產生",
                        "formal_exists": False,
                        "draft_exists": False,
                        "formal_path": formal_rel,
                        "draft_path": draft_rel,
                        "formal_abs_path": str(formal_abs),
                        "draft_abs_path": str(draft_abs),
                    }
            t_status_end = time.time()
            print(f"Phase 4: gencode_status_map (V2 file checks): {t_status_end - t_status_start:.4f}s")
            
            # Phase 5: v3_gencode_status_map
            t_v3_start = time.time()
            from core.routes.admin import _load_skills_v3_gencode_status_map
            v3_gencode_status_map = _load_skills_v3_gencode_status_map(
                [str(s["skill_id"]) for s in skills]
            )
            t_v3_end = time.time()
            print(f"Phase 5: v3_gencode_status_map generation: {t_v3_end - t_v3_start:.4f}s")
            
            # Phase 6: render_template
            t_render_start = time.time()
            from flask import render_template
            try:
                html = render_template('admin_skills.html', 
                                       skills_data=skills_data,
                                       skills=skills,
                                       gencode_status_map=gencode_status_map,
                                       v3_gencode_status_map=v3_gencode_status_map,
                                       filters=filters_data,
                                       selected_filters=selected,
                                       grade_map={str(g):str(g) for g in filters_data['grades']},
                                       curriculum_map={
                                           'junior_high': '國中',
                                           'general': '普高',
                                           'vocational': '技高',
                                           'vocational_high': '技高',
                                           'technical': '技高',
                                           'junior': '國中',
                                           'senior': '普高',
                                           'general_high': '普高',
                                           'senior_high': '普高'
                                       },
                                       username="admin")
                t_render_end = time.time()
                print(f"Phase 6: render_template: {t_render_end - t_render_start:.4f}s (HTML size: {len(html)} chars)")
            except Exception as e:
                print(f"Phase 6: render_template failed: {e}")
                
        print(f"Total query count: {query_count}")
        print(f"SQL queries executed: {len(query_times)} times, sum: {sum(query_times):.4f}s")
        if query_times:
            print(f"Average query time: {sum(query_times)/len(query_times):.4f}s")
            
if __name__ == '__main__':
    run_diagnose_full()
