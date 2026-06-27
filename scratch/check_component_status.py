import sqlite3
import os, sys, json
from pathlib import Path

BASE = Path(r'e:\Python\Mathproject_tvet_mathB')
os.chdir(str(BASE))
sys.path.insert(0, str(BASE))

db_path = BASE / 'instance' / 'kumon_math.db'
print(f"DB path: {db_path}, exists={db_path.exists()}")
conn = sqlite3.connect(str(db_path))
conn.row_factory = sqlite3.Row

tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print("Has gencode_component_tracker:", 'gencode_component_tracker' in tables)

skill_id = 'vh_\u6578\u5b78B4_NormalDistributionAndEmpiricalRule'
rows = conn.execute(
    'SELECT textbook_example_id, component_id, gencode_status, updated_at '
    'FROM gencode_component_tracker WHERE skill_id=? ORDER BY textbook_example_id',
    (skill_id,)
).fetchall()
print(f"\nDB rows for {skill_id}:")
for r in rows:
    print(f"  example_id={r['textbook_example_id']}, component_id={r['component_id']}, status={r['gencode_status']}, updated_at={r['updated_at']}")
print(f"Total tracker rows: {len(rows)}")

# Check production files
prod_root = BASE / 'agent_skills_v3' / skill_id
print(f"\nProduction dir: {prod_root}")
print(f"  exists: {prod_root.exists()}")
if prod_root.exists():
    init_file = prod_root / '__init__.py'
    print(f"  __init__.py exists: {init_file.exists()}")
    comp_dir = prod_root / 'components'
    if comp_dir.exists():
        comps = list(comp_dir.iterdir())
        print(f"  components/: {[c.name for c in comps]}")
    else:
        print("  components/ dir: missing")

# Run the actual status query service
from core.gencode.services.gencode_status_query_service import (
    build_admin_examples_gencode_status_map,
    load_v3_skill_generator_specs,
    inspect_component_production_sync,
)

specs = load_v3_skill_generator_specs(skill_id=skill_id)
print(f"\nGenerator specs count: {len(specs)}")
for s in specs:
    print(f"  {s.get('component_id')} / textbook_example_id={s.get('textbook_example_id')}")

if rows:
    examples = [(r['textbook_example_id'], skill_id) for r in rows]
    status_map = build_admin_examples_gencode_status_map(conn, examples)
    print("\n--- teacher_status per example ---")
    for ex_id, data in status_map.items():
        ts = data.get('teacher_status', {})
        comp_id = data.get('component_id')
        prod_sync = data.get('production_contains_latest')
        sync_method = data.get('production_sync_method')
        sync_reason = data.get('production_sync_reason')
        prod_gen_exists = data.get('production_generate_exists')
        print(f"  example={ex_id} comp={comp_id} status={data.get('gencode_status')} "
              f"-> {ts.get('label')} | prod_contains={prod_sync} method={sync_method} reason={sync_reason} prod_gen={prod_gen_exists}")
