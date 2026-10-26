import sqlite3,hashlib,sys,json,os
from pathlib import Path
c=sqlite3.connect("file:instance/kumon_math.db?mode=ro",uri=True)
def dg(sql):
    h=hashlib.sha256()
    for r in c.execute(sql): h.update(repr(r).encode())
    return h.hexdigest()[:16]
out={"te_outside_unit2":dg("select * from textbook_examples where not (id between 1334 and 1361 or id between 12707 and 12743) order by id"),
"skill_curriculum":dg("select * from skill_curriculum order by id"),"tracker":dg("select * from gencode_component_tracker order by 1,2") if True else "",
"uploads_files":sum(1 for _ in Path("uploads").rglob("*") if _.is_file()),"skills_info":dg("select * from skills_info order by skill_id")}
print(json.dumps(out))
