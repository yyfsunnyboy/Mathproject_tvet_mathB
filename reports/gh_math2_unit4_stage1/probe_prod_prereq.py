"""Read-only prerequisites probe: sandbox-specific leakage, id ranges, journal mode, logical references of old rows."""
import hashlib, json, re, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
f = sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True)
s = sqlite3.connect('file:%s?mode=ro' % (OUT / 'tmp/replay_with_regions/unit4.db').as_posix(), uri=True)
SC = ('general', '數學2', '單元4 排列')
print('journal_mode', f.execute('pragma journal_mode').fetchone(), 'foreign_keys', f.execute('pragma foreign_keys').fetchone())
print('formal max id', f.execute('select max(id) from textbook_examples').fetchone(), 'sandbox max id', s.execute('select max(id) from textbook_examples').fetchone())
print('seq formal', f.execute("select * from sqlite_sequence where name='textbook_examples'").fetchall(), 'sandbox', s.execute("select * from sqlite_sequence where name='textbook_examples'").fetchall())
new = s.execute('select id from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id', SC).fetchall()
print('new ids', new[0], new[-1], len(new))
print('new id collisions in formal', f.execute('select count(*) from textbook_examples where id between ? and ?', (new[0][0], new[-1][0])).fetchone())
ddl = f.execute("select sql from sqlite_master where name='textbook_examples'").fetchone()[0]
print('autoincrement' in ddl.lower())
# sandbox leakage inside new rows
cols = [c[1] for c in s.execute('pragma table_info(textbook_examples)')]
leak = 0
for row in s.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=?', SC):
    blob = json.dumps(dict(zip(cols, row)), ensure_ascii=False, default=str)
    for pat in (r'reports[/\\\\]gh_math2_unit4', r'unit4\.db', r'[A-Z]:\\\\', r'replay_', r'/tmp/', r'staging'):
        if re.search(pat, blob):
            leak += 1
            print('LEAK?', row[0], pat, re.findall(r'.{40}%s.{40}' % pat, blob)[:1])
print('leaks', leak)
# image assets
assets = []
for rid, notes in s.execute('select id, notes from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=?', SC):
    for a in json.loads(notes or '{}').get('image_assets') or []:
        p = OUT / 'tmp/replay_with_regions' / a['path']
        ok = p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest() == a['sha256']
        dst = ROOT / a['path']
        assets.append((rid, a['path'][-60:], ok, dst.exists()))
print('assets', assets)
# old rows: images & references
old = f.execute('select id, notes, problem_text from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id', SC).fetchall()
oldpaths = set()
for rid, notes, pt in old:
    n = json.loads(notes or '{}')
    for a in n.get('image_assets') or []:
        oldpaths.add(a.get('path'))
    for k in ('image_path', 'image_paths', 'figure_path'):
        if n.get(k): oldpaths.add(str(n[k]))
print('old rows with image assets paths', len(oldpaths), list(oldpaths)[:5])
ids = [r[0] for r in old]
tables = [r[0] for r in f.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
skills = ('gh_LinearPermutation', 'gh_PermutationWithIdenticalItems', 'gh_RepeatedPermutation')
print('--- tables with skill_id column referencing the 3 skills')
for t in tables:
    cn = [c[1] for c in f.execute('pragma table_info("%s")' % t)]
    for c in cn:
        if c in ('skill_id', 'skill', 'skill_name') or c.endswith('skill_id'):
            n = f.execute('select count(*) from "%s" where "%s" in (?,?,?)' % (t, c), skills).fetchone()[0]
            if n: print('  ', t, c, n)
print('--- tables with columns that look like example/question refs')
for t in tables:
    cn = [c[1] for c in f.execute('pragma table_info("%s")' % t)]
    for c in cn:
        if re.search(r'example|question|textbook|source_id|item_id|problem', c, re.I) and t != 'textbook_examples':
            vals = f.execute('select "%s" from "%s" where "%s" is not null limit 3' % (c, t, c)).fetchall()
            n_old = 0
            try:
                n_old = f.execute('select count(*) from "%s" where cast("%s" as text) in (%s)' % (t, c, ','.join('?' * len(ids))), [str(i) for i in ids]).fetchone()[0]
            except Exception as e:
                n_old = 'err'
            print('  ', t, c, 'old-id hits', n_old, 'sample', [str(v[0])[:30] for v in vals])
print('--- any text column containing old image paths or unit chapter')
if oldpaths:
    for t in tables:
        for c in [c[1] for c in f.execute('pragma table_info("%s")' % t)]:
            for p in oldpaths:
                try:
                    n = f.execute('select count(*) from "%s" where instr(cast("%s" as text), ?)>0' % (t, c), (p,)).fetchone()[0]
                except Exception:
                    continue
                if n and t != 'textbook_examples': print('  ', t, c, p[-40:], n)
print('--- chapter-name references outside textbook_examples/skill_curriculum')
for t in tables:
    if t in ('textbook_examples', 'skill_curriculum'): continue
    for c in [c[1] for c in f.execute('pragma table_info("%s")' % t)]:
        try:
            n = f.execute('select count(*) from "%s" where cast("%s" as text) = ?' % (t, c), ('單元4 排列',)).fetchone()[0]
        except Exception:
            continue
        if n: print('  ', t, c, n)
print('practice_attempts sample question_uid', f.execute('select question_uid, source, skill_id from practice_attempts order by rowid desc limit 3').fetchall())
