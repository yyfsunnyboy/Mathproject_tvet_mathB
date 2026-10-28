"""Read-only preflight for the (not yet authorised) formal Unit 4 replacement. Writes nothing."""
import hashlib, json, os, re, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
SRC = ROOT / 'textbook_import/uploaded_sources/general/數學2'
DB = ROOT / 'instance/kumon_math.db'
print('db size/mtime', DB.stat().st_size, DB.stat().st_mtime)
for p in (SRC / '327f295a06d7_單元04-排列.docx', SRC / 'bf39d447345e_單元04-排列.pdf'):
    print(p.name, p.is_file(), hashlib.sha256(p.read_bytes()).hexdigest())
m = json.loads((SRC / 'abe2e7906ec604d8dccdc5c8b1bbcf4df1beb162230faa454bd0e0fa810f3160.json').read_text(encoding='utf8'))
print('manifest keys', list(m), {k: {kk: (str(vv)[:70]) for kk, vv in v.items()} for k, v in m['sources'].items()})
con = sqlite3.connect('file:%s?mode=ro' % DB.as_posix(), uri=True)
q = lambda s, *a: con.execute(s, a).fetchall()
rows = q("select id, skill_id, source_description, notes from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元4 排列' order by id")
print('old Unit 4 rows', len(rows), 'id range', rows[0][0] if rows else None, rows[-1][0] if rows else None)
prov = set()
for r in rows:
    n = json.loads(r[3] or '{}')
    prov.add(((n.get('source_provenance') or {}).get('primary') or {}).get('sha256'))
print('old rows provenance sha', prov)
print('old skill ids', sorted({r[1] for r in rows}))
ids = [r[0] for r in rows]
ph = ','.join('?' * len(ids)) or 'NULL'
tables = [t[0] for t in q("select name from sqlite_master where type='table'")]
print('tables referencing textbook example ids (column hits):')
for t in tables:
    cols = [c[1] for c in q('pragma table_info(%s)' % t)]
    for c in cols:
        if re.search(r'(textbook_)?example_id|textbook_example', c, re.I) and t != 'textbook_examples':
            n = q('select count(*) from %s where %s in (%s)' % (t, c, ph), *ids)[0][0] if ids else 0
            print('  ', t, c, n)
print('other volumes unit 4 rows:', q("select source_volume, source_chapter, count(*) from textbook_examples where source_chapter like '%排列%' group by 1,2"))
# skills for the three new families
for sid in ('gh_LinearPermutation', 'gh_PermutationWithIdenticalItems', 'gh_RepeatedPermutation'):
    print(sid, 'skills_info', q('select count(*) from skills_info where skill_id=?', sid)[0][0], 'skill_curriculum', q('select count(*) from skill_curriculum where skill_id=?', sid)[0][0])
print('student data counts', {t: q('select count(*) from %s' % t)[0][0] for t in ('users', 'practice_attempts', 'quiz_attempts') if t in tables})
print('backup dir candidates', [str(p) for p in (ROOT / 'backups').glob('*')][-3:] if (ROOT / 'backups').exists() else 'no backups dir')
