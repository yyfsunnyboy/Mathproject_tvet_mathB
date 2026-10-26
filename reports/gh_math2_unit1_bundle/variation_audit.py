"""Run the shared variation audit on the *sandbox-published* gh_Sequence (never on the production project root)."""
import json, sqlite3, sys
from collections import Counter
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).resolve().parents[2]; sys.path.insert(0, str(ROOT))
run = ROOT / "tmp" / "gh_math2u1_rehearsal" / "run"
assert (run / "project").is_dir() and run.resolve() != ROOT
conn = sqlite3.connect(f"file:{(run / 'rehearsal.db').as_posix()}?mode=ro", uri=True); conn.row_factory = sqlite3.Row
from agent_domains_candidate.sequence_progression.sandbox_harness import register_candidate_in_memory
register_candidate_in_memory()  # in-memory only; the audit executes the published generators through the registry
from core.gencode.services.v3_variation_audit_service import audit_skill_variation
results = {}
for skill in ("gh_Sequence", "gh_RecursiveRelation"):
    res = audit_skill_variation(skill, seeds=list(range(1, 41)), source="production", project_root=str(run / "project"), conn=conn)
    by = res.get("variation_status_by_component") or {}
    results[skill] = res
    print(skill, {k: res.get(k) for k in ("status", "components_checked", "dynamic_count", "static_count", "partially_dynamic_count", "insufficient_sample_count")})
    for k, v in by.items():
        st = v.get("variation_status") if isinstance(v, dict) else v
        if st != "dynamic":
            print("  ", k, st, (v.get("error") if isinstance(v, dict) else ""))
Path(__file__).with_name("variation_audit_result.json").write_text(json.dumps(results, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
