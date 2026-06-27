"""Verify fix: _read_generator_specs now handles BOM correctly."""
import sys, ast
from pathlib import Path

BASE = Path(r'e:\Python\Mathproject_tvet_mathB')
sys.path.insert(0, str(BASE))

skill = 'vh_\u6578\u5b78B4_NormalDistributionAndEmpiricalRule'

# Test the fixed function directly
from core.gencode.services.gencode_status_query_service import (
    load_v3_skill_generator_specs,
    build_admin_examples_gencode_status_map,
)
import sqlite3

specs = load_v3_skill_generator_specs(
    skill_id=skill,
    production_base_dir='agent_skills_v3',
    project_root=str(BASE),
)
print(f"GENERATOR_SPECS count after fix: {len(specs)}")
for s in specs:
    print(f"  component_id={s.get('component_id')}, example_id={s.get('textbook_example_id')}")

# Now run full status map
conn = sqlite3.connect(str(BASE / 'instance' / 'kumon_math.db'))
conn.row_factory = sqlite3.Row
rows = conn.execute(
    'SELECT textbook_example_id, component_id, gencode_status FROM gencode_component_tracker WHERE skill_id=? ORDER BY textbook_example_id',
    (skill,)
).fetchall()

examples = [(int(r['textbook_example_id']), skill) for r in rows]
status_map = build_admin_examples_gencode_status_map(conn, examples)

print("\n--- Final teacher_status after fix ---")
for r in rows:
    eid = int(r['textbook_example_id'])
    data = status_map.get(eid, {})
    ts = data.get('teacher_status', {})
    print(f"  example={eid} component={r['component_id']} tracker={r['gencode_status']} "
          f"prod_contains={data.get('production_contains_latest')} "
          f"method={data.get('production_sync_method')} "
          f"=> label={ts.get('label')} status_key={ts.get('status_key')}")
