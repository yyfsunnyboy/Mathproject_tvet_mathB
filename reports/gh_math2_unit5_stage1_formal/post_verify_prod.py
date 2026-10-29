"""Read-only production verification after the Unit 5 Stage 1 apply (compares the formal DB with the pre-change backup)."""
import hashlib, json, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from core.textbook_stage1_gate import evaluate_stage1_gate  # noqa: E402
from types import SimpleNamespace  # noqa: E402

bk = sorted((ROOT / 'instance/backups').glob('math2_unit5_stage1_2*'))[-1]
m = json.loads((bk / 'apply_manifest.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
p = sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True)
b = sqlite3.connect('file:%s?mode=ro' % Path(m['backup']).as_posix(), uri=True)
U = ('general', '數學2', '單元5 組合')
W = 'source_curriculum=? and source_volume=? and source_chapter=?'
out = {'manifest_status': m['status'], 'backup': m['backup'], 'backup_sha256_ok': sha(m['backup']) == m['backup_sha256'],
       'prod_integrity': p.execute('pragma integrity_check').fetchone()[0], 'backup_integrity': b.execute('pragma integrity_check').fetchone()[0],
       'unit5_rows': p.execute(f'select count(*), min(id), max(id) from textbook_examples where {W}', U).fetchone(),
       'backup_unit5_rows': b.execute(f'select count(*), min(id), max(id) from textbook_examples where {W}', U).fetchone(),
       'skills': dict(p.execute(f'select skill_id, count(*) from textbook_examples where {W} group by 1', U).fetchall()),
       'old_ids_remaining': p.execute('select count(*) from textbook_examples where id between 1413 and 1440').fetchone()[0],
       'registration': p.execute("select id, skill_id, display_order from skill_curriculum where volume='數學2' and chapter='單元5 組合' order by display_order").fetchall(),
       'comprehensive_exercises_bindings_other_units': p.execute("select count(*) from skill_curriculum where skill_id='gh_ComprehensiveExercises'").fetchone()[0]}
rows = p.execute(f'select id, skill_id, problem_text, correct_answer, detailed_solution, notes, source_description from textbook_examples where {W} order by id', U).fetchall()
objs = [SimpleNamespace(id=r[0], skill_id=r[1], problem_text=r[2], correct_answer=r[3], detailed_solution=r[4], notes=r[5], source_description=r[6]) for r in rows]
gate = evaluate_stage1_gate(objs)
out['gate'] = {'status': gate['status'], 'stage1_ready': gate['stage1_ready'], 'blocked': len(gate['blocked']), 'needs_review': len(gate['needs_review'])}
imgs = {}
for r in rows:
    for a in json.loads(r[5] or '{}').get('image_assets') or []:
        f = ROOT / a['path']
        imgs[r[0]] = {'anchor': (json.loads(r[5])['question_anchor'] or {}).get('anchor_id'), 'file_ok': f.is_file() and sha(f) == a['sha256'], 'path': a['path']}
out['figure_rows'] = imgs
tabs = [r[0] for r in p.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
bad = []
for t in tabs:
    q = f'select * from "{t}"'; args = ()
    if t == 'textbook_examples': q += f' where not ({W})'; args = U
    elif t == 'skill_curriculum': q += ' where id not in (358, 359, 360)'
    if sorted(map(repr, p.execute(q, args))) != sorted(map(repr, b.execute(q, args))): bad.append(t)
out['tables_compared'] = len(tabs)
out['tables_differing_outside_scope'] = bad
for t in ('users', 'practice_attempts', 'progress', 'mistake_notebook_entries', 'adaptive_learning_logs'):
    if t in tabs: out[f'count_{t}'] = [p.execute(f'select count(*) from "{t}"').fetchone()[0], b.execute(f'select count(*) from "{t}"').fetchone()[0]]
U4 = ('general', '數學2', '單元4 排列')
d = lambda con: hashlib.sha256(repr(con.execute(f'select * from textbook_examples where {W} order by id', U4).fetchall()).encode()).hexdigest()
out['unit4_identical'] = d(p) == d(b)
out['unit4_rows'] = p.execute(f'select count(*) from textbook_examples where {W}', U4).fetchone()[0]
fixed = json.loads((ROOT / 'configs/fixed_textbook_practice.json').read_text(encoding='utf-8'))['entries']
from core.fixed_textbook_practice import stem_sha256  # noqa: E402
e = fixed.get('12834')
row = next(r for r in rows if r[0] == 12834)
out['fixed_entry'] = {'key': '12834' if e else None, 'anchor_match': bool(e) and e['question_anchor'] == json.loads(row[5])['question_anchor']['anchor_id'],
                      'stem_sha_match': bool(e) and e['problem_text_sha256'] == stem_sha256(row[2]), 'skill_match': bool(e) and e['skill_id'] == row[1],
                      'unit5_fixed_keys': sorted(k for k in fixed if int(k) in {r[0] for r in rows}), 'total_entries': len(fixed)}
out['stray_pending_files'] = [str(x) for x in (ROOT / 'uploads/question_assets/general/longteng/數學2').rglob('*.pending*')]
(HERE / 'post_verify_prod.json').write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print(json.dumps(out, ensure_ascii=False, default=str))
