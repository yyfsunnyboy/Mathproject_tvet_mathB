import json, sqlite3, sys
from pathlib import Path
from core.textbook_stage1_gate import evaluate_stage1_gate

db=Path('instance/kumon_math.db')
sys.stdout.reconfigure(encoding='utf-8')
c=sqlite3.connect(f'file:{db.resolve().as_posix()}?mode=ro',uri=True)
c.row_factory=sqlite3.Row
chapters=[dict(r) for r in c.execute("select source_curriculum,source_volume,source_chapter,count(*) n,min(id) lo,max(id) hi from textbook_examples where source_volume='數學2' group by 1,2,3")]
rows=[dict(r) for r in c.execute("select * from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter like '單元3%' order by id")]
new=[r for r in rows if r['id']>=12744]
print('CHAPTERS',json.dumps(chapters,ensure_ascii=False))
print('GATE',json.dumps(evaluate_stage1_gate(new),ensure_ascii=False))
print('BINDINGS',json.dumps([dict(r) for r in c.execute("select * from skill_curriculum where volume='數學2' and chapter like '單元3%'")],ensure_ascii=False))
for r in new:
 n=json.loads(r['notes'] or '{}')
 print('ROW',json.dumps({'id':r['id'],'type':r['problem_type'],'label':r['source_description'].split(' [')[0],'skill':r['skill_id'],'stem':r['problem_text'][:300].replace('\n',' '),'anchor':(n.get('question_anchor') or {}).get('source_order'),'review':n.get('needs_review'),'pdf':n.get('pdf_visual_status'),'page':(n.get('pdf_visual_enrichment') or {}).get('page')},ensure_ascii=False))
