"""Independent read-only post-apply verification against the production backup."""
import hashlib, json, sqlite3, sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT))
from core.textbook_stage1_gate import evaluate_stage1_gate
from reports.gh_math2_unit3_stage1.apply_unit3 import outside_digests,sha,CS,SCOPE

manifest=Path(sys.argv[1]);m=json.loads(manifest.read_text(encoding='utf-8'))
assert m['status']=='applied_verified' and m['unit']==SCOPE
backup=Path(m['backup']);assert backup.is_file() and sha(backup.read_bytes())==m['backup_sha256']
prod=ROOT/'instance/kumon_math.db'
a=sqlite3.connect(f'file:{prod.as_posix()}?mode=ro',uri=True);a.row_factory=sqlite3.Row
b=sqlite3.connect(f'file:{backup.as_posix()}?mode=ro',uri=True);b.row_factory=sqlite3.Row
assert a.execute('pragma integrity_check').fetchone()[0]=='ok'
assert b.execute('pragma integrity_check').fetchone()[0]=='ok'
before=outside_digests(b);after=outside_digests(a)
assert before==after,'chapter-outside or student table digest changed'
rows=[dict(r) for r in a.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id',tuple(SCOPE.values()))]
assert len(rows)==30 and [r['id'] for r in rows]==list(range(12744,12774))
skills=Counter(r['skill_id'] for r in rows)
assert skills=={'gh_LogicAndSets':9,'gh_CountingPrinciples':21}
assert all('MATH_PARSE_FAILED' not in (r['problem_text'] or '')+(r['detailed_solution'] or '') for r in rows)
gate=evaluate_stage1_gate(rows)
assert gate['status']=='READY' and not gate['blocked'] and not gate['needs_review']
anchors=[json.loads(r['notes'])['question_anchor'] for r in rows]
assert len({x['anchor_id'] for x in anchors})==30 and sorted(x['source_order'] for x in anchors)==list(range(1,31))
assert all(r['skill_id']=='gh_LogicAndSets' for r in rows if r['id'] in (12763,12764,12766,12767))
assets=[]
for r in rows:
 for asset in json.loads(r['notes']).get('image_assets') or []:
  path=ROOT/asset['path'];assert path.is_file() and sha(path.read_bytes())==asset['sha256']
  assets.append((r['id'],asset['path']))
assert sorted(r for r,_ in assets)==[12756,12773]
assert a.execute('select count(*) from textbook_examples').fetchone()[0]==b.execute('select count(*) from textbook_examples').fetchone()[0]-20
assert a.execute("select count(*) from gencode_component_tracker where textbook_example_id between 1362 and 1381").fetchone()[0]==0
print(json.dumps({'formal_stage1':'READY','new_rows':len(rows),'old_rows_remaining':0,'skills':dict(skills),'math_parse_failed':0,'blocked':0,'needs_review':0,'anchors_unique':30,'source_order':'1-30','assets':[r for r,_ in assets],'chapter_outside_tables_unchanged':len(before),'student_attempts_unchanged':before['practice_attempts']==after['practice_attempts'],'formal_integrity':'ok','backup_integrity':'ok'},ensure_ascii=False))
a.close();b.close()
