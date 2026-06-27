"""Single diagnostic script for vh_數學B4_NormalDistributionAndEmpiricalRule components."""
import sqlite3, sys, ast, hashlib, json
from pathlib import Path

BASE = Path(r'e:\Python\Mathproject_tvet_mathB')
sys.path.insert(0, str(BASE))

DB   = BASE / 'instance' / 'kumon_math.db'
SKILL = 'vh_\u6578\u5b78B4_NormalDistributionAndEmpiricalRule'
PROD  = BASE / 'agent_skills_v3' / SKILL
DRYRUN = BASE / 'reports' / 'gencode_v3_dryrun' / SKILL

conn = sqlite3.connect(str(DB))
conn.row_factory = sqlite3.Row

# 1. Tracker rows
rows = conn.execute(
    "SELECT textbook_example_id, component_id, gencode_status, induced_spec_payload, updated_at "
    "FROM gencode_component_tracker WHERE skill_id=? ORDER BY textbook_example_id",
    (SKILL,)
).fetchall()

# 2. Parse GENERATOR_SPECS from production __init__.py
init_py = PROD / '__init__.py'
gen_specs = []
if init_py.exists():
    try:
        tree = ast.parse(init_py.read_text(encoding='utf-8', errors='replace'))
        for node in tree.body:
            if isinstance(node, ast.Assign):
                for t in node.targets:
                    if isinstance(t, ast.Name) and t.id == 'GENERATOR_SPECS':
                        val = ast.literal_eval(node.value)
                        if isinstance(val, list):
                            gen_specs = val
    except Exception as e:
        print(f"  [WARN] Failed to parse __init__.py: {e}")

spec_component_ids = {str(s.get('component_id', '')).strip() for s in gen_specs}
print(f"Production __init__.py exists: {init_py.exists()}")
print(f"GENERATOR_SPECS entries: {len(gen_specs)}  component_ids={spec_component_ids}\n")

def sha256(p):
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest() if Path(p).is_file() else None
    except Exception:
        return None

print(f"{'example_id':>12} {'component_id':>12} {'tracker_status':>16} {'prod_gen':>8} {'dryrun_gen':>10} "
      f"{'in_specs':>8} {'v_hash==p_hash':>14} {'prod_contains':>13} {'sync_reason':>30} => {'teacher_label'}")
print('-'*160)

from core.gencode.services.gencode_status_query_service import (
    build_admin_examples_gencode_status_map,
    inspect_component_production_sync,
)

examples = [(int(r['textbook_example_id']), SKILL) for r in rows]
status_map = build_admin_examples_gencode_status_map(conn, examples)

for r in rows:
    eid     = int(r['textbook_example_id'])
    cid     = str(r['component_id'] or '')
    gstatus = str(r['gencode_status'] or '')
    payload = {}
    try:
        payload = json.loads(r['induced_spec_payload'] or '{}') or {}
    except Exception:
        pass

    prod_gen  = PROD / 'components' / cid / 'generate.py'
    dryrun_gen = DRYRUN / 'components' / cid / 'generate.py'
    p_hash = sha256(prod_gen)
    v_hash = sha256(dryrun_gen) or str(payload.get('verified_generate_sha256') or '') or None

    in_specs    = cid in spec_component_ids
    hash_match  = bool(p_hash and v_hash and p_hash == v_hash)
    has_p_hash  = bool(str(payload.get('published_generate_sha256') or '').strip())
    has_v_hash  = bool(str(payload.get('verified_generate_sha256') or '').strip())

    data        = status_map.get(eid, {})
    prod_contains = data.get('production_contains_latest')
    sync_method   = data.get('production_sync_method', '')
    sync_reason   = data.get('production_sync_reason', '')
    ts_label      = data.get('teacher_status', {}).get('label', '?')

    print(f"{eid:>12} {cid:>12} {gstatus:>16} {str(prod_gen.is_file()):>8} {str(dryrun_gen.is_file()):>10} "
          f"{str(in_specs):>8} {str(hash_match):>14} {str(prod_contains):>13} {sync_reason:>30} => {ts_label}")

print()
print("Payload hash fields for each component:")
for r in rows:
    cid = str(r['component_id'] or '')
    payload = {}
    try:
        payload = json.loads(r['induced_spec_payload'] or '{}') or {}
    except Exception:
        pass
    print(f"  {cid}: published_sha256={payload.get('published_generate_sha256')!r}  "
          f"verified_sha256={payload.get('verified_generate_sha256')!r}  "
          f"verified_artifact_path={payload.get('verified_artifact_path')!r}")
