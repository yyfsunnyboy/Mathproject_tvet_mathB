"""Negative control: replay Unit 4 on a DB copy with the U+EF08 mapping disabled; the Gate must BLOCK."""
import json, re, sqlite3, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[1]))
sys.path.insert(0, str(OUT))
import core.mtef.chars as chars
chars.SpaceTypefaceChars.clear()          # simulate the pre-fix converter (in-process only)
import replay_isolated as r

data = r.run('ef08_negative_control')
(OUT / 'formal_replay_ef08_negative_control.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf8')
for a in data['attempts']:
    print('status', a['status'], 'rows', a['row_count'])
    for l in a['logs']:
        print('  ', l[:260])
PUA = re.compile('[\ue000-\uf8ff]')
sb = OUT / 'tmp' / 'replay_ef08_negative_control' / 'unit4.db'
print('protected unchanged', data['protected_state_unchanged'])
pre = json.load(open(OUT / 'pre_review_ef08_negative_control.json', encoding='utf8'))
print('pre-review rows', len(pre), 'stems with PUA', sum(1 for x in pre if PUA.search(x['problem_text'])))
