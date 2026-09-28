import sqlite3
from pathlib import Path

from core.gencode.services.gencode_status_query_service import (
    build_admin_skills_gencode_status_map,
    inspect_skill_runtime_publication,
)
from core.domain.exponential_logarithmic_domain import SOURCE_SPECS

skills = sorted({s["skill_id"] for s in SOURCE_SPECS.values()})
db = Path("instance/kumon_math.db").resolve()
conn = sqlite3.connect("file:" + str(db).replace("\\", "/") + "?mode=ro", uri=True)
conn.row_factory = sqlite3.Row
status = build_admin_skills_gencode_status_map(conn, skills, project_root=Path.cwd())
for s in skills:
    pub = inspect_skill_runtime_publication(skill_id=s, project_root=Path.cwd())
    view = status.get(s) or {}
    ts = view.get("teacher_status") or {}
    print(s[-5:], pub["runtime_ready"], len(pub["selectable_components"]), ts.get("status_key"), ts.get("icon") == "\U0001f7e2", ts.get("label") == "已上線", {k: view.get(k) for k in ("total_examples", "published_count", "failed_count", "missing_tracker_count") if k in view})
conn.close()
