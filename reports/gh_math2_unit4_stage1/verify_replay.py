import json, re, sqlite3, hashlib, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[1]))
d = json.load(open(OUT / 'formal_replay_with_regions.json', encoding='utf8'))
PUA = re.compile('[\ue000-\uf8ff]')
for a in d['attempts']:
    ar = a.get('stage1_auto_review') or {}
    gate = ar.get('gate') or a.get('stage1_gate') or {}
    print('attempt', a['attempt'], 'status', a['status'], 'rows', a['row_count'])
    print('  gate:', gate.get('status'), 'ready', gate.get('stage1_ready'), 'rows', gate.get('rows'),
          'blocked', len(gate.get('blocked') or []), 'review', len(gate.get('needs_review') or []), 'reasons', gate.get('reasons'))
    print('  auto_review keys', list(ar), 'issues', ar.get('issues'), 'changes', len(ar.get('changes') or []))
    print('  logs', [l[:160] for l in a['logs']][-4:])
last = d['attempts'][-1]
rows = last['rows']
from collections import Counter
print('skills', Counter(r['skill_id'] for r in rows))
print('anchors', sorted(r['anchor']['source_order'] for r in rows) == list(range(1, 39)), len({r['anchor']['anchor_id'] for r in rows}))
imgs = [(r['label'], [(x.get('path'), x.get('visual_status'), x.get('visual_classification')) for x in (r['notes'].get('image_assets') or [])]) for r in rows if r['notes'].get('image_assets')]
print('rows with assets', len(imgs))
for i in imgs: print('  ', i)
print('PUA in stem', sum(1 for r in rows if PUA.search(r['problem_text'])), 'in notes', sum(1 for r in rows if PUA.search(json.dumps(r['notes'], ensure_ascii=False))))
print('markers', sum(1 for r in rows if 'MATH_PARSE_FAILED' in json.dumps(r, ensure_ascii=False)))
for r in rows:
    if r['label'].endswith('觀念澄清2'):
        print(r['label'], r['problem_text'])
sb = OUT / 'tmp' / 'replay_with_regions' / 'unit4.db'
con = sqlite3.connect(sb)
cur = con.execute("select id, source_description, problem_text, detailed_solution, correct_answer from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元4 排列'")
res = cur.fetchall()
print('sandbox rows', len(res))
ps = sol = ans = 0
perm = 0
for rid, desc, pt, ds, ca in res:
    if PUA.search(pt or ''): ps += 1
    if PUA.search(ds or ''): sol += 1
    if PUA.search(ca or ''): ans += 1
    if re.search(r'P_\{ \w \}', (pt or '') + (ds or '')): perm += 1
print('PUA stems', ps, 'solutions', sol, 'answers', ans, 'rows with P_{n}^{k} notation', perm)
print('sample solution:', [ds for _, desc, pt, ds, _ in res if 'P_{' in (ds or '')][:1])
print('empty solutions', sum(1 for r in res if not (r[3] or '').strip()))
