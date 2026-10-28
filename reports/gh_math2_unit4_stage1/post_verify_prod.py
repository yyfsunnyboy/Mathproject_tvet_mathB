import json, sqlite3, sys, hashlib
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
bk = sorted((ROOT / 'instance/backups').glob('math2_unit4_stage1_*'))[-1]
m = json.loads((bk / 'apply_manifest.json').read_text(encoding='utf-8'))
print('manifest status', m['status'], '| backup', m['backup'], '| backup sha256 ok', hashlib.sha256(Path(m['backup']).read_bytes()).hexdigest() == m['backup_sha256'])
p = sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True)
b = sqlite3.connect('file:%s?mode=ro' % Path(m['backup']).as_posix(), uri=True)
print('prod integrity', p.execute('pragma integrity_check').fetchone(), 'backup integrity', b.execute('pragma integrity_check').fetchone())
U = ('數學2', '單元4 排列')
print('unit rows', p.execute('select count(*), min(id), max(id) from textbook_examples where source_volume=? and source_chapter=?', U).fetchone(),
      'backup unit rows', b.execute('select count(*), min(id), max(id) from textbook_examples where source_volume=? and source_chapter=?', U).fetchone())
print('skills', p.execute('select skill_id, count(*) from textbook_examples where source_volume=? and source_chapter=? group by 1', U).fetchall())
print('old ids remaining', p.execute('select count(*) from textbook_examples where id between 1382 and 1412').fetchone())
print('registration', p.execute("select skill_id, display_order from skill_curriculum where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation') order by display_order").fetchall())
# everything outside Unit 4 identical to backup, table by table (incl. students, other units, vocational)
tabs = [r[0] for r in p.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
bad = []
for t in tabs:
    q = 'select * from "%s"' % t
    if t == 'textbook_examples': q += " where not (source_volume='數學2' and source_chapter='單元4 排列' and source_curriculum='general')"
    elif t in ('skill_curriculum', 'skills_info'): q += " where skill_id not in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation')"
    if sorted(map(repr, p.execute(q))) != sorted(map(repr, b.execute(q))): bad.append(t)
print('tables compared', len(tabs), 'differing outside scope:', bad)
for t in ('users', 'practice_attempts', 'progress', 'mistake_notebook_entries', 'mistake_logs'):
    if t in tabs: print('  ', t, p.execute('select count(*) from "%s"' % t).fetchone()[0], '==', b.execute('select count(*) from "%s"' % t).fetchone()[0])
print('other-unit textbook rows', p.execute("select count(*) from textbook_examples where not (source_volume='數學2' and source_chapter='單元4 排列')").fetchone(),
      'vocational', p.execute("select count(*) from textbook_examples where source_curriculum='vocational'").fetchone())
imgs = []
for (n,) in p.execute("select notes from textbook_examples where source_volume=? and source_chapter=?", U):
    for a in json.loads(n or '{}').get('image_assets') or []:
        f = ROOT / a['path']; imgs.append(f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == a['sha256'])
print('image assets on disk with matching sha', imgs)
print('stray pending files', [str(x) for x in (ROOT / 'uploads/question_assets/general/longteng/數學2').rglob('*.pending*')])
