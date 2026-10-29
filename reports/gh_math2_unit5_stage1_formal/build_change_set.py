"""Build the production change set for 數學2 單元5 from the verified replay (live teacher-approved region). Read-only on both DBs."""
import hashlib, json, re, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SC = ('general', '數學2', '單元5 組合')
SKILLS = ('gh_Combination', 'gh_BinomialTheorem', 'gh_ComprehensiveExercises')
REPLAY = HERE / 'tmp/replay'
f = sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True)
s = sqlite3.connect('file:%s?mode=ro' % (REPLAY / 'unit5.db').as_posix(), uri=True)
f.row_factory = s.row_factory = sqlite3.Row
sha = lambda b: hashlib.sha256(b).hexdigest()
d = lambda r: dict(r)
SCOPE_SQL = 'source_curriculum=? and source_volume=? and source_chapter=?'

old_rows = [d(r) for r in f.execute(f'select * from textbook_examples where {SCOPE_SQL} order by id', SC)]
assert [r['id'] for r in old_rows] == list(range(1413, 1441)), 'old scope drift'
new_src = [d(r) for r in s.execute(f'select * from textbook_examples where {SCOPE_SQL} order by id', SC)]
assert len(new_src) == 37
base = f.execute('select max(id) from textbook_examples').fetchone()[0]
assert base == 12811, base
id_map = {r['id']: base + 1 + i for i, r in enumerate(new_src)}
assert all(k == v for k, v in id_map.items()), 'replay ids are expected to equal the production ids'
new_rows = [dict(r) for r in new_src]
for r in new_rows:
    blob = json.dumps(r, ensure_ascii=False, default=str)
    assert str(REPLAY) not in blob and REPLAY.as_posix() not in blob and 'tmp/replay' not in blob and 'tmp\\\\replay' not in blob, f"sandbox path leaked into row {r['id']}"

# every other table must be identical between formal and replay, except skill_curriculum / skills_info rows of the Unit 5 skills
tables = [r[0] for r in f.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by name")]
drift = []
for t in tables:
    sql = f'select * from "{t}"'
    args = ()
    if t == 'textbook_examples':
        sql += f' where not ({SCOPE_SQL})'; args = SC
    elif t in ('skill_curriculum', 'skills_info'):
        sql += ' where skill_id not in (?,?,?)'; args = SKILLS
    elif t == 'skill_family_bridge':  # re-seeded by create_app() in the replay process (new bridge_id/timestamps); not written by this change set
        cols = [c[1] for c in f.execute('pragma table_info(skill_family_bridge)') if c[1] not in ('bridge_id', 'created_at', 'updated_at')]
        sql = 'select ' + ','.join(cols) + ' from skill_family_bridge'
    if sorted(repr(tuple(r)) for r in f.execute(sql, args)) != sorted(repr(tuple(r)) for r in s.execute(sql, args)):
        drift.append(t)
assert not drift, drift

cur_f = {r['id']: d(r) for r in f.execute('select * from skill_curriculum where skill_id in (?,?,?)', SKILLS)}
cur_s = {r['id']: d(r) for r in s.execute('select * from skill_curriculum where skill_id in (?,?,?)', SKILLS)}
assert set(cur_s) <= set(cur_f), 'replay added skill_curriculum rows'
curriculum_updates, curriculum_deletes = [], []
for i, before in cur_f.items():
    if i not in cur_s:
        assert (before['skill_id'], before['curriculum'], before['volume'], before['chapter']) == ('gh_ComprehensiveExercises', *SC), before
        curriculum_deletes.append(before)
        continue
    diff = [k for k in before if before[k] != cur_s[i][k]]
    assert set(diff) <= {'display_order'}, diff
    if diff: curriculum_updates.append({'id': i, 'before': before, 'after': cur_s[i]})
sk_f = {r['skill_id']: d(r) for r in f.execute('select * from skills_info where skill_id in (?,?,?)', SKILLS)}
sk_s = {r['skill_id']: d(r) for r in s.execute('select * from skills_info where skill_id in (?,?,?)', SKILLS)}
assert sk_f == sk_s, 'skills_info changed'

assets = []
for r in new_rows:
    for a in json.loads(r['notes'] or '{}').get('image_assets') or []:
        src = REPLAY / a['path']
        assert src.is_file() and sha(src.read_bytes()) == a['sha256'], a['path']
        assert not (ROOT / a['path']).exists(), 'destination exists ' + a['path']
        assets.append({'row_id': r['id'], 'path': a['path'], 'sha256': a['sha256'], 'size': src.stat().st_size,
                       'source_file': str(src.relative_to(HERE))})
assert [a['row_id'] for a in assets] == [12834]

rec = json.loads((ROOT / 'textbook_import/uploaded_sources/general/數學2/12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json').read_text(encoding='utf-8'))['sources']
change_set = {
    'unit': dict(zip(('source_curriculum', 'source_volume', 'source_chapter'), SC)),
    'docx': {'path': rec['docx']['stored_path'], 'sha256': rec['docx']['sha256']},
    'pdf': {'path': rec['pdf']['stored_path'], 'sha256': rec['pdf']['sha256']},
    'source_record': 'textbook_import/uploaded_sources/general/數學2/12f0850f70a4f4bb1fe149c078a1b9d5f3f9927285122d4c70c09c13eb5a89d6.json',
    'verified_region': {'file': 'configs/stage1_verified_visual_regions.json', 'label': '5習題 進階題12', 'verified_by': 'teacher', 'verified_on': '2026-10-29'},
    'sandbox_to_production_id_map': id_map,
    'old_rows': old_rows, 'new_rows': new_rows,
    'curriculum_updates': curriculum_updates, 'curriculum_deletes': curriculum_deletes, 'skill_updates': [],
    'asset_files': assets,
    'expected': {'rows': 37, 'skills': {'gh_Combination': 23, 'gh_BinomialTheorem': 14}, 'figure_rows': [12834]},
}
out = HERE / 'production_change_set.json'
out.write_text(json.dumps(change_set, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print('change set', len(old_rows), 'old ->', len(new_rows), 'new; ids', new_rows[0]['id'], '-', new_rows[-1]['id'],
      '; curriculum updates', [(u['id'], u['before']['display_order'], u['after']['display_order']) for u in curriculum_updates],
      '; curriculum deletes', [c['id'] for c in curriculum_deletes], '; assets', [(a['row_id'], a['sha256'][:12]) for a in assets],
      '; other tables identical', len(tables))
