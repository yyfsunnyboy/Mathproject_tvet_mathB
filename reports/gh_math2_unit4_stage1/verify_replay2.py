import json, re, sqlite3
from pathlib import Path
OUT = Path(__file__).resolve().parent
d = json.load(open(OUT / 'formal_replay_with_regions.json', encoding='utf8'))
rows = d['attempts'][-1]['rows']
for r in rows:
    s = json.dumps(r['notes'], ensure_ascii=False)
    if 'MATH_PARSE_FAILED' in s:
        hist = r['notes'].get('stage1_auto_review')
        print(r['label'], 'in problem_text:', 'MATH_PARSE_FAILED' in r['problem_text'], [(h['kind'], h['before'][:60], '->', h['after'][:60]) for h in hist or []][:2])
con = sqlite3.connect(OUT / 'tmp' / 'replay_with_regions' / 'unit4.db')
res = con.execute("select source_description, problem_text, detailed_solution from textbook_examples where source_curriculum='general' and source_volume='數學2' and source_chapter='單元4 排列' order by id").fetchall()
for desc, pt, ds in res:
    if 'P_{' in pt or 'P_{' in (ds or ''):
        print('P-symbol row:', desc.split(' [')[0], '| stem' if 'P_{' in pt else '', '| solution' if 'P_{' in (ds or '') else '')
print('MATH_PARSE_FAILED in any stem/solution:', sum(1 for _, pt, ds in res if 'MATH_PARSE_FAILED' in pt or 'MATH_PARSE_FAILED' in (ds or '')))
