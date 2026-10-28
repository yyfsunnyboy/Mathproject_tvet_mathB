"""Rehearse apply_unit4 on a DB copy + temp uploads root: apply, rollback, re-apply, and post-commit failure compensation."""
import shutil, sqlite3, subprocess, sys, tempfile, json
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
tmp = Path(tempfile.mkdtemp(prefix='unit4_rehearsal_', dir=HERE / 'tmp'))
db = tmp / 'copy.db'
with sqlite3.connect('file:%s?mode=ro' % (ROOT / 'instance/kumon_math.db').as_posix(), uri=True) as s, sqlite3.connect(db) as d:
    s.backup(d)
up = tmp / 'uploads_root'; up.mkdir()
def run(*args):
    p = subprocess.run([sys.executable, str(HERE / 'apply_unit4.py'), '--db', str(db), '--uploads-root', str(up), '--backup-dir', str(tmp / 'bk'), *args],
                       capture_output=True, text=True, encoding='utf-8')
    print('$', ' '.join(args) or '(preflight)', '->', (p.stdout.strip() or p.stderr.strip().splitlines()[-1])[:400])
    return p
run()
p = run('--apply')
m = sorted((tmp / 'bk').glob('*/apply_manifest.json'))[-1]
print('assets after apply', len(list(up.rglob('*.png'))))
run('--verify')
run('--rollback', str(m))
print('assets after rollback', len(list(up.rglob('*.png'))))
run()
run('--apply')
run('--verify')
# post-commit failure compensation: break verification by making the Gate fail through a corrupted asset destination
m2 = sorted((tmp / 'bk').glob('*/apply_manifest.json'))[-1]
run('--rollback', str(m2))
sys.path.insert(0, str(HERE.parent.parent))
code = (
    "import sys,runpy;sys.argv=['apply_unit4.py','--db',r'%s','--uploads-root',r'%s','--backup-dir',r'%s','--apply'];"
    "import importlib.util as u;spec=u.spec_from_file_location('a4',r'%s');a4=u.module_from_spec(spec);spec.loader.exec_module(a4);"
    "orig=a4.verify_unit\n"
    "def bad(con,root):\n    orig(con,root);raise AssertionError('forced post-commit verification failure')\n"
    "a4.verify_unit=bad\n"
    "try:\n    a4.main()\nexcept AssertionError as e:\n    print('FORCED FAILURE ->',e)\n"
) % (db, up, tmp / 'bk', HERE / 'apply_unit4.py')
p = subprocess.run([sys.executable, '-c', code], capture_output=True, text=True, encoding='utf-8')
print(p.stdout.strip(), p.stderr.strip()[-300:])
con = sqlite3.connect(db)
rows = con.execute("select count(min(id)), min(id), max(id) from textbook_examples where source_chapter='單元4 排列' and source_volume='數學2'").fetchall()
print('after forced failure: unit rows', con.execute("select count(*), min(id), max(id) from textbook_examples where source_chapter='單元4 排列' and source_volume='數學2'").fetchone(),
      'assets left', len(list(up.rglob('*.png'))))
print('last manifest status', json.loads(sorted((tmp / 'bk').glob('*/apply_manifest.json'))[-1].read_text(encoding='utf-8'))['status'])
run()
print('rehearsal dir', tmp)
