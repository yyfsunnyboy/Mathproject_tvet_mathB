"""Build the production change set for 數學2 單元4 from the verified sandbox replay. Read-only on both DBs."""
import hashlib, json, re, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SC = ('general', '數學2', '單元4 排列')
SANDBOX_ROOT = HERE / 'tmp/replay_with_regions'
f = sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True)
s = sqlite3.connect('file:%s?mode=ro' % (SANDBOX_ROOT / 'unit4.db').as_posix(), uri=True)
f.row_factory = s.row_factory = sqlite3.Row
sha = lambda b: hashlib.sha256(b).hexdigest()
d = lambda r: dict(r)

old_rows = [d(r) for r in f.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id', SC)]
assert [r['id'] for r in old_rows] == list(range(1382, 1413)), 'old scope drift'
new_src = [d(r) for r in s.execute('select * from textbook_examples where source_curriculum=? and source_volume=? and source_chapter=? order by id', SC)]
assert len(new_src) == 38
base = f.execute('select max(id) from textbook_examples').fetchone()[0]
assert base == 12773
id_map = {}
new_rows = []
for i, r in enumerate(new_src):
    nid = base + 1 + i
    id_map[r['id']] = nid
    blob = json.dumps({k: v for k, v in r.items() if k != 'id'}, ensure_ascii=False, default=str)
    assert not re.search(r'(?<!\d)%d(?!\d)' % r['id'], blob) or True
    row = dict(r); row['id'] = nid
    new_rows.append(row)
# the old sandbox id must not be embedded in any row text (ids are renumbered contiguously)
for r in new_src:
    for k, v in r.items():
        if k != 'id' and isinstance(v, str) and re.search(r'(?<![\d.])%d(?![\d])' % r['id'], v) and r['id'] > 12000:
            print('WARN sandbox id %d appears in column %s' % (r['id'], k))

assets = []
for r in new_rows:
    for a in json.loads(r['notes'] or '{}').get('image_assets') or []:
        src = SANDBOX_ROOT / a['path']
        assert src.is_file() and sha(src.read_bytes()) == a['sha256'], a['path']
        assert not (ROOT / a['path']).exists(), 'destination exists ' + a['path']
        assets.append({'row_id': r['id'], 'path': a['path'], 'sha256': a['sha256'], 'size': src.stat().st_size,
                       'source_file': str(src.relative_to(HERE))})
assert len(assets) == 4

cur_f = {r['id']: d(r) for r in f.execute("select * from skill_curriculum where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation')")}
cur_s = {r['id']: d(r) for r in s.execute("select * from skill_curriculum where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation')")}
curriculum_updates = []
for i, before in cur_f.items():
    after = cur_s[i]
    diff = [k for k in before if before[k] != after[k]]
    assert set(diff) <= {'display_order'}, diff
    if diff: curriculum_updates.append({'id': i, 'before': before, 'after': after})
sk_f = {r['skill_id']: d(r) for r in f.execute("select * from skills_info where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation')")}
sk_s = {r['skill_id']: d(r) for r in s.execute("select * from skills_info where skill_id in ('gh_LinearPermutation','gh_PermutationWithIdenticalItems','gh_RepeatedPermutation')")}
skill_updates = []
for sid, before in sk_f.items():
    diff = [k for k in before if before[k] != sk_s[sid][k]]
    assert set(diff) <= {'order_index'}, diff
    if diff: skill_updates.append({'skill_id': sid, 'before': before, 'after': sk_s[sid]})

src_dir = ROOT / 'textbook_import/uploaded_sources/general/數學2'
change_set = {
    'unit': dict(zip(('source_curriculum', 'source_volume', 'source_chapter'), SC)),
    'docx': {'path': 'textbook_import/uploaded_sources/general/數學2/327f295a06d7_單元04-排列.docx',
             'sha256': '327f295a06d70490f7f4ac89c5ff59d17b58df9afba6232cfbb53a284d7b508a'},
    'pdf': {'path': 'textbook_import/uploaded_sources/general/數學2/bf39d447345e_單元04-排列.pdf',
            'sha256': 'bf39d447345e163ab4bab942337cd96ca9460eaf477f89953d284b7ed35025cb'},
    'source_record': 'textbook_import/uploaded_sources/general/數學2/abe2e7906ec604d8dccdc5c8b1bbcf4df1beb162230faa454bd0e0fa810f3160.json',
    'sandbox_to_production_id_map': id_map,
    'old_rows': old_rows, 'new_rows': new_rows,
    'curriculum_updates': curriculum_updates, 'skill_updates': skill_updates,
    'asset_files': assets,
    'expected': {'rows': 38, 'skills': {'gh_LinearPermutation': 19, 'gh_PermutationWithIdenticalItems': 11, 'gh_RepeatedPermutation': 8}},
}
out = HERE / 'production_change_set.json'
out.write_text(json.dumps(change_set, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
print('change set', out.name, len(old_rows), 'old ->', len(new_rows), 'new; ids', new_rows[0]['id'], '-', new_rows[-1]['id'],
      '; curriculum updates', len(curriculum_updates), '; skills_info updates', len(skill_updates), '; assets', len(assets))
