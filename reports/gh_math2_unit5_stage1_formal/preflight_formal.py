"""Read-only preflight for the authorised formal Unit 5 replacement. Writes nothing."""
import hashlib, json, re, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / 'textbook_import/uploaded_sources/general/數學2'
DB = ROOT / 'instance/kumon_math.db'
SC = ('general', '數學2', '單元5 組合')
SKILLS = ('gh_Combination', 'gh_BinomialTheorem', 'gh_ComprehensiveExercises')
rec = json.loads((SRC / '12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json').read_text(encoding='utf-8'))['sources']
out = {'sources': {}}
for k in ('docx', 'pdf'):
    p = ROOT / rec[k]['stored_path']
    out['sources'][k] = {'path': rec[k]['stored_path'], 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'record_sha256': rec[k]['sha256']}
con = sqlite3.connect('file:%s?mode=ro' % DB.as_posix(), uri=True)
q = lambda s, *a: con.execute(s, a).fetchall()
rows = q('select id, skill_id from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id', *SC)
ids = [r[0] for r in rows]
out['old_rows'] = {'count': len(ids), 'ids': [ids[0], ids[-1]], 'skills': {s: sum(1 for r in rows if r[1] == s) for s in {r[1] for r in rows}}}
out['max_id'] = q('select max(id) from textbook_examples')[0][0]
out['skill_usage_outside_unit5'] = {s: q('select source_curriculum, source_volume, source_chapter, count(*) from textbook_examples where skill_id=? and not (source_curriculum=? and source_volume=? and source_chapter=?) group by 1,2,3', s, *SC) for s in SKILLS}
out['skills_info'] = {s: q('select count(*) from skills_info where skill_id=?', s)[0][0] for s in SKILLS}
out['skill_curriculum'] = {s: q('select id, curriculum, volume, chapter, section, display_order from skill_curriculum where skill_id=?', s) for s in SKILLS}
refs = {}
tables = [t[0] for t in q("select name from sqlite_master where type='table' and name not like 'sqlite_%'")]
for t in tables:
    if t in ('textbook_examples', 'skills_info', 'skill_curriculum'):
        continue
    for c in [c[1] for c in q('pragma table_info("%s")' % t)]:
        if c == 'skill_id' or c.endswith('_skill_id'):
            for s in SKILLS:
                n = q('select count(*) from "%s" where "%s"=?' % (t, c), s)[0][0]
                if n: refs[f'{t}.{c}={s}'] = n
        if re.search(r'example_id|source_example|textbook_example|question_id|item_id', c, re.I):
            n = q('select count(*) from "%s" where cast("%s" as text) in (%s)' % (t, c, ','.join('?' * len(ids))), *[str(i) for i in ids])[0][0]
            if n: refs[f'{t}.{c} old ids'] = n
out['references'] = refs
out['tables'] = len(tables)
out['quick_check'] = q('pragma quick_check')[0][0]
print(json.dumps(out, ensure_ascii=False, indent=1))
