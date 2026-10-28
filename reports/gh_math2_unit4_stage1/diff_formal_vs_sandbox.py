"""Read-only: full table-level diff between the formal DB and the verified Unit 4 sandbox replay DB."""
import json, sqlite3, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
OUT = Path(__file__).resolve().parent
FORMAL = OUT.parents[1] / 'instance/kumon_math.db'
SANDBOX = OUT / 'tmp/replay_with_regions/unit4.db'
f = sqlite3.connect('file:%s?mode=ro' % FORMAL.as_posix(), uri=True)
s = sqlite3.connect('file:%s?mode=ro' % SANDBOX.as_posix(), uri=True)
tf = {r[0] for r in f.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
ts = {r[0] for r in s.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
print('tables only in formal', tf - ts, 'only in sandbox', ts - tf)
for t in sorted(tf & ts):
    cf = [c[1] for c in f.execute('pragma table_info("%s")' % t)]
    cs = [c[1] for c in s.execute('pragma table_info("%s")' % t)]
    if cf != cs:
        print(t, 'COLUMN DIFF', set(cf) ^ set(cs)); continue
    rf = {repr(r) for r in f.execute('select * from "%s"' % t)}
    rs = {repr(r) for r in s.execute('select * from "%s"' % t)}
    if rf != rs:
        print(t, 'only_formal', len(rf - rs), 'only_sandbox', len(rs - rf))
        if t != 'textbook_examples':
            for r in list(rf - rs)[:6]: print('   F-', r[:300])
            for r in list(rs - rf)[:6]: print('   S+', r[:300])
