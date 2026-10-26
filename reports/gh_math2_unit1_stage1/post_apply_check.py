import glob, hashlib, json, sqlite3, sys
sys.stdout.reconfigure(encoding="utf-8")
mp = sorted(glob.glob("instance/backups/apply_manifest_*.json"))[-1]
m = json.load(open(mp, encoding="utf-8"))
bk = m["backup"].replace("\\", "/")
print("manifest", mp, "| backup", bk, m["backup_sha256"][:16], "rows", m["backup_textbook_examples"])
print("backup file sha matches manifest:", hashlib.sha256(open(bk, "rb").read()).hexdigest() == m["backup_sha256"])
print("created files", len(m["created_files"]), "all sha ok:", all(hashlib.sha256(open(c["path"], "rb").read()).hexdigest() == c["sha256"] for c in m["created_files"]))
b = sqlite3.connect(f"file:{bk}?mode=ro", uri=True); c = sqlite3.connect("file:instance/kumon_math.db?mode=ro", uri=True)
print("integrity backup/now:", b.execute("pragma integrity_check").fetchone()[0], c.execute("pragma integrity_check").fetchone()[0])
print("textbook_examples rows backup->now:", b.execute("select count(*) from textbook_examples").fetchone()[0], c.execute("select count(*) from textbook_examples").fetchone()[0])
outside = "select * from textbook_examples where not (id between 12667 and 12706) order by id"
print("rows outside 12667-12706 identical:", list(b.execute(outside)) == list(c.execute(outside)))
for t in [r[0] for r in c.execute("select name from sqlite_master where type='table' and name not in ('textbook_examples') and name not like 'sqlite_%'")]:
    if list(b.execute(f'select * from "{t}"')) != list(c.execute(f'select * from "{t}"')):
        print("TABLE CHANGED (may be live app activity):", t)
print("other tables compared")
