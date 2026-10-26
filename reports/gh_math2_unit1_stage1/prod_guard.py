"""Read-only fingerprint of the production DB (zero-write evidence). Usage: prod_guard.py <label>"""
import hashlib, json, sqlite3, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "instance" / "kumon_math.db"
def fh(p):
    p = Path(p)
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
c = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
tables = [r[0] for r in c.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%' order by 1")]
counts = {t: c.execute(f'select count(*) from "{t}"').fetchone()[0] for t in tables}
def digest(sql):
    h = hashlib.sha256()
    for r in c.execute(sql): h.update(repr(r).encode())
    return h.hexdigest()
out = {
    "label": sys.argv[1],
    "files_sha256": {n: fh(str(DB) + s) for n, s in (("db", ""), ("wal", "-wal"), ("shm", "-shm"))},
    "row_counts": counts,
    "textbook_examples_digest": digest("select * from textbook_examples order by id"),
    "skill_curriculum_digest": digest("select * from skill_curriculum order by id"),
    "skills_info_digest": digest("select * from skills_info order by skill_id"),
    "gencode_component_tracker_digest": digest("select * from gencode_component_tracker order by id"),
}
Path(__file__).with_name(f"prod_fingerprint_{sys.argv[1]}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
print(json.dumps({k: v for k, v in out.items() if k != "row_counts"}, indent=1))
