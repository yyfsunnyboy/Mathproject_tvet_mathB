import sys
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app import create_app
from models import db, TextbookExample

app = create_app()
with app.app_context():
    rows = TextbookExample.query.filter_by(
        source_curriculum='vocational',
        source_volume='數學B2',
        source_section='1-1 角度的基本性質'
    ).order_by(TextbookExample.id.asc()).all()

    by_skill = {}
    for r in rows:
        by_skill.setdefault(r.skill_id, []).append({
            'id': r.id,
            'source_description': r.source_description,
            'problem_type': r.problem_type,
            'problem_text': r.problem_text,
            'correct_answer': r.correct_answer,
            'detailed_solution': r.detailed_solution,
        })

    for s, items in by_skill.items():
        print(f"=== Skill: {s} (count={len(items)}) ===")
        for it in items:
            text_preview = (it['problem_text'] or '').replace('\n', ' ')[:60]
            sol_preview = (it['detailed_solution'] or '').replace('\n', ' ')[:40]
            print(f"  ID {it['id']}: [{it['source_description']}] {text_preview} | sol={bool(sol_preview)}")

    Path('reports/b2_1_1_audit/gencode_candidates.json').write_text(
        json.dumps(by_skill, ensure_ascii=False, indent=2), encoding='utf-8'
    )
