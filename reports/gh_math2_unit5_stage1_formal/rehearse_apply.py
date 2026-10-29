"""Rehearse apply -> verify -> rollback -> re-apply of apply_unit5.py on a copy of the formal DB and a scratch uploads root."""
import hashlib, json, shutil, sqlite3, subprocess, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
T = HERE / 'tmp/rehearse_apply'
if T.exists(): shutil.rmtree(T)
(T / 'root').mkdir(parents=True)
db = T / 'kumon_math.db'
with sqlite3.connect(f"file:{(ROOT / 'instance/kumon_math.db').as_posix()}?mode=ro", uri=True) as s, sqlite3.connect(db) as d:
    s.backup(d)
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def table_dump(path):
    con = sqlite3.connect(path)
    try:
        return {t: sorted(map(repr, con.execute(f'select * from "{t}"'))) for (t,) in con.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'")}
    finally:
        con.close()


original = table_dump(db)
run = lambda *a: subprocess.run([sys.executable, str(HERE / 'apply_unit5.py'), '--db', str(db), '--uploads-root', str(T / 'root'), *a],
                                capture_output=True, text=True, encoding='utf-8')
steps = {}
r = run(); steps['preflight'] = r.stdout.strip()[-300:] + r.stderr[-300:]
r = run('--apply', '--backup-dir', str(T / 'backups')); steps['apply'] = (r.returncode, r.stdout.strip()[-600:], r.stderr[-600:])
manifest = sorted((T / 'backups').glob('math2_unit5_stage1_*/apply_manifest.json'))[-1]
r = run('--verify'); steps['verify'] = (r.returncode, r.stdout.strip()[-300:])
r = run('--rollback', str(manifest)); steps['rollback'] = (r.returncode, r.stdout.strip()[-200:], r.stderr[-300:])
restored = table_dump(db)
steps['rollback_exact'] = restored == original
steps['rollback_asset_removed'] = not any((T / 'root').rglob('*.png'))
r = run('--apply', '--backup-dir', str(T / 'backups2')); steps['reapply'] = (r.returncode, r.stdout.strip()[-200:], r.stderr[-300:])
con = sqlite3.connect(db); steps['integrity'] = con.execute('pragma integrity_check').fetchone()[0]; con.close()
(HERE / 'rehearse_apply_result.json').write_text(json.dumps(steps, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps(steps, ensure_ascii=False, indent=1))
