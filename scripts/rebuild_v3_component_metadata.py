from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.gencode.skill_wrapper_compiler import _build_generator_specs, _fetch_verified_components
from core.gencode.v3_component_metadata_migration import rebuild_component_metadata_from_generator_specs
from core.registry.taxonomy_registry import resolve_domain_for_skill


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rebuild V3 component metadata.py from authoritative tracker generator specs."
    )
    parser.add_argument("--skill-id", required=True)
    parser.add_argument("--db", default=str(PROJECT_ROOT / "instance" / "kumon_math.db"))
    parser.add_argument("--root", default=str(PROJECT_ROOT / "reports" / "gencode_v3_dryrun"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    try:
        components = _fetch_verified_components(conn, args.skill_id)
        _, generator_specs = _build_generator_specs(components)
    finally:
        conn.close()

    domain_meta = resolve_domain_for_skill(args.skill_id)
    if not isinstance(domain_meta, dict):
        raise SystemExit(f"domain_metadata_not_found:{args.skill_id}")
    result = rebuild_component_metadata_from_generator_specs(
        sandbox_root=args.root,
        skill_id=args.skill_id,
        generator_specs=generator_specs,
        domain_meta=domain_meta,
        write=bool(args.write),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
